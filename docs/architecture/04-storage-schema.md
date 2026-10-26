# 数据库物理模型：PostgreSQL 主库 + Neo4j 投影

本文为可落地 DDL 的**设计草案**。未实际连接 PG/Neo4j 执行，升级到 migration 前需本地跑 lint/integration test。PostgreSQL 使用 `pgcrypto` 的 UUID 或支持 `gen_random_uuid()` 的兼容版本。

## 1. 权威层：主要表

```sql
CREATE TABLE ontology_class (
  class_key text PRIMARY KEY,
  parent_key text REFERENCES ontology_class(class_key),
  schema_version text NOT NULL
);
CREATE TABLE ontology_relation_type (
  relation_key text PRIMARY KEY,
  subject_class text NOT NULL REFERENCES ontology_class(class_key),
  object_class text NOT NULL REFERENCES ontology_class(class_key),
  evidence_required boolean NOT NULL DEFAULT true,
  schema_version text NOT NULL
);
CREATE TABLE engineering_baseline (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  code text NOT NULL UNIQUE,
  model_code text NOT NULL,
  variant_code text NOT NULL,
  market_code text NOT NULL,
  ontology_version text NOT NULL,
  status text NOT NULL CHECK (status IN ('draft','released','retired'))
);
CREATE TABLE document_revision (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  code text NOT NULL,
  revision text NOT NULL,
  sha256 char(64) NOT NULL,
  source_uri text NOT NULL,
  UNIQUE (code,revision)
);
CREATE TABLE baseline_document (
  baseline_id uuid NOT NULL REFERENCES engineering_baseline(id),
  document_id uuid NOT NULL REFERENCES document_revision(id),
  PRIMARY KEY(baseline_id,document_id)
);
CREATE TABLE source_anchor (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id uuid NOT NULL REFERENCES document_revision(id),
  page_no integer NOT NULL CHECK (page_no>0),
  section_path text,
  source_text text NOT NULL,
  fragment_sha256 char(64) NOT NULL,
  bbox jsonb,
  cell_ref jsonb
);
CREATE TABLE entity (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  canonical_key text NOT NULL UNIQUE,
  class_key text NOT NULL REFERENCES ontology_class(class_key),
  display_name text NOT NULL
);
CREATE TABLE entity_state (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  entity_id uuid NOT NULL REFERENCES entity(id),
  baseline_id uuid NOT NULL REFERENCES engineering_baseline(id),
  properties jsonb NOT NULL DEFAULT '{}'::jsonb,
  review_status text NOT NULL CHECK
    (review_status IN ('candidate','approved','rejected')),
  ontology_version text NOT NULL,
  UNIQUE(entity_id,baseline_id),
  UNIQUE(id,baseline_id)
);
CREATE TABLE relation_fact (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  baseline_id uuid NOT NULL REFERENCES engineering_baseline(id),
  subject_state_id uuid NOT NULL,
  relation_key text NOT NULL REFERENCES ontology_relation_type(relation_key),
  object_state_id uuid NOT NULL,
  evidence_anchor_id uuid REFERENCES source_anchor(id),
  origin text NOT NULL CHECK(origin IN ('source','manual','inferred')),
  review_status text NOT NULL CHECK
    (review_status IN ('candidate','approved','rejected')),
  FOREIGN KEY(subject_state_id,baseline_id)
    REFERENCES entity_state(id,baseline_id),
  FOREIGN KEY(object_state_id,baseline_id)
    REFERENCES entity_state(id,baseline_id),
  CHECK(origin <> 'source' OR evidence_anchor_id IS NOT NULL)
);
CREATE INDEX idx_relation_from ON relation_fact
  (baseline_id,subject_state_id,relation_key);
CREATE INDEX idx_relation_to ON relation_fact
  (baseline_id,object_state_id,relation_key);
```

**重要限制**：以上外键保证关系节点属于同一 baseline，但**不会**自动保证 `relation_key` 的 subject/object class 正确，也不会校验 `evidence_anchor` 属于该 baseline 的 document_revision。这两项需要事务内 validator / trigger 检查；不要以为 SQL 已覆盖所有 invariants。

## 2. 后续专用业务表（避免全部塞 JSONB）

```text
requirement_behavior(state_id PK/FK, trigger_ast, condition_ast, expected_ast)
temporal_constraint(id, requirement_state_id, comparator, milliseconds, reference_event)
signal_definition(state_id PK/FK, message_id, start_bit, length, byte_order, factor, offset, unit)
test_obligation(id, requirement_state_id, viewpoint_state_id, baseline_id, status, rule_version)
test_coverage(id, test_case_state_id, obligation_id, evidence_anchor_id, reviewed_at)
extraction_run(id, source_document_id, parser_version, model_id, prompt_digest, status)
candidate_fact(id, extraction_run_id, payload, validation_report, review_status)
review_decision(id, reviewer_id, subject_kind, subject_id, decision, rationale, at)
publication(id, baseline_id, schema_version, published_by, published_at, checksum)
outbox_event(id, aggregate_id, kind, payload, occurred_at, published_at)
projection_checkpoint(consumer_name, last_event_id, last_event_time, build_version)
```

候选事实单独表允许同一 `entity` 在不同候选 run 出现，不使 `UNIQUE(entity_id,baseline_id)` 误当作每次提取历史；只将审定后的有效状态放入 `entity_state`。多次发布修订时，实体状态按 `baseline` 或增设 `entity_state_revision` 追加记录，不在同一基线覆盖已发布数据。

## 3. 事件投影与 Neo4j

只投影已批准且已发布基线事实；每个节点必须携带 canonical_key、baseline_id、entity_state_id、schema_version。

```cypher
CREATE CONSTRAINT engineering_identity IF NOT EXISTS
FOR (n:EngineeringEntity)
REQUIRE (n.baseline_id, n.canonical_key) IS UNIQUE;
```

```cypher
MERGE (r:EngineeringEntity:AtomicRequirement {
  baseline_id: $baseline,
  canonical_key: $req_key
})
ON CREATE SET r.fact_state_id = $req_state_id
MERGE (s:EngineeringEntity:Signal {
  baseline_id: $baseline,
  canonical_key: $signal_key
})
ON CREATE SET s.fact_state_id = $signal_state_id
MERGE (r)-[rel:USES_SIGNAL {fact_id: $relation_fact_id}]->(s)
SET rel.review_status = 'approved',
    rel.evidence_anchor_id = $anchor_id;
```

Neo4j 幂等身份以 relation_fact_id 为准；关系更新、删除、撤销发布由 replayable events 控制。Cypher 语法需按目标 Neo4j 版本集成测试，单个 blob 里的语句是 API 模板而非已运行迁移。

## 4. API / 查询示例

```sql
SELECT r.id AS relation_id, e1.canonical_key AS req, e2.canonical_key AS signal
FROM relation_fact r
JOIN entity_state x ON x.id = r.subject_state_id
JOIN entity e1 ON e1.id = x.entity_id
JOIN entity_state y ON y.id = r.object_state_id
JOIN entity e2 ON e2.id = y.entity_id
WHERE r.baseline_id = :baseline
  AND r.relation_key='USES_SIGNAL'
  AND r.review_status='approved';
```

**读安全**：查询时不仅检查 baseline，还必须检查 principal 对相关 documents/anchors 的 read permission；共享图谱中一条关系可能泄漏保密的跨项目知识。建议在服务端做属性级过滤、query plan 白名单、定量 query budget。

## 5. FTS/向量建模

```text
source_chunk(
  chunk_id, document_revision_id, anchor_ids, text, language,
  normalized_search_text, parser_version, text_sha
)
chunk_embedding(
  chunk_id, model_id, embedding_version, vector,
  generated_at, corpus_visibility
)
```

不可将不同维度或不同版本 embedding 放进同一个向量索引而不标识 model；向量召回的候选必须再经过基线/权限过滤和原文 evidence 定位。

## 6. 事务与迁移测试必测点

- 相同 file SHA 重复上传不多次创建事实；
- invalid subject/target 类型无法发布；
- 不同 baseline 的实体不能直接建正式关系；
- 无证据的 `origin=source` relation 被拒绝；
- 已发布 baseline 更改触发新 revision；
- Outbox 重试不会双写边；投影滞后/重建后 checksum 一致；
- 并发 reviewer 提交同一候选产生乐观锁冲突而不是覆盖。
