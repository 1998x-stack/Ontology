# 图谱检索、Agent 与受控 Actions

## 1. 查询规划

自然语言先解析为 typed intent：`find_requirement`、`trace_signal_impact`、`coverage_gap`、`compare_baselines`、`explain_fact`。附明确 baseline_id/project_id/principal；由固定 query templates/白名单 relation types 转 SQL/Cypher。**禁止直接执行模型自由生成的写 SQL/Cypher**。

### MCP 只读工具

```text
ontology.list_baselines(project_id)
ontology.get_schema(schema_version)
ontology.search_requirements(baseline_id, query, filters, limit)
ontology.get_requirement(baseline_id, requirement_id)
ontology.get_source_evidence(anchor_id)
ontology.get_signal(baseline_id, signal_id)
ontology.trace_dependencies(baseline_id, seed_id, relation_types, max_depth)
ontology.find_cross_spec_impacts(old_baseline, new_baseline, change_id)
ontology.get_test_obligations(baseline_id, requirement_ids)
ontology.get_coverage_gaps(baseline_id, feature_id)
```

返回 `answer, facts[], evidence[], unresolved[], baseline_id, ontology_version, projection_watermark, query_plan_id`。错误码区分 UNKNOWN_BASELINE、ACCESS_DENIED、INDEX_STALE、NO_EVIDENCE、UNRESOLVED_ENTITY。

### 审核门禁下的 Actions

```text
ontology.propose_requirement_change
ontology.propose_relation
ontology.request_review
ontology.approve_review      # reviewer only; proposer != reviewer
ontology.publish_baseline    # publisher role + optimistic lock
tests.propose_test_cases     # default candidate; not formal write
```

所有写操作验证身份、项目/文档读写范围、变化预览、审批 token、idempotency_key、审计及回滚策略。

## 2. 图查询模板示例

```cypher
MATCH (s:Signal {baseline_id:$baseline,canonical_key:$signal})
MATCH (r:AtomicRequirement {baseline_id:$baseline})-[edge:USES_SIGNAL]->(s)
RETURN r.canonical_key AS req, edge.evidence_anchor_id AS anchor
LIMIT $limit
```

服务层必须按 document/source ACL 过滤结果，不因 graph 可达就允许读取。Max depth、max nodes、timeout、token cap 必须硬限制。

## 3. 混合搜索

FTS：精确文档号、CAN 信号、section；Vector：自然语言语义候选；Graph：有规则的 typed edge 扩展；Rerank：对原文证据重排序。检索器不得将相似名称当作 canonical matching；embedding 的 model/version/visibility 需要显式索引字段。

## 4. C45 Matrix 与测试覆盖

```text
AtomicRequirement + ViewpointRules
    -> candidate TestObligations
    -> human-approved obligation list
    -> TestCase --SATISFIES--> Obligation
    -> Coverage Gap
    -> proposed TestCase (review queue)
```

必测、推荐、不适用、不确定四种状态独立报告。覆盖率分母只取 confirmed-required obligations，不把“有一个关联 TestCase”当作所有维度覆盖，更不能等同于测试执行通过。

## 5. 版本变更与影响路径

`ChangedSignal ← USES_SIGNAL — Requirement ← VERIFIES — TestCase` 代表潜在影响候选。必须保留 dependency_kind、路径各边证据、changed-field kind、人工审核状态；只有可靠工程规则支持时才升级为 required-action。

## 6. 安全

PDF/外部内容始终视为**不可信指令载体**；工具白名单、schema validation、限权数据库凭证和 prompt-injection 测试是强制门槛。读写隔离，内部式样不可发送未批准的公网 LLM；日志脱敏。审计字段包含 principal、tool_name、action、baseline、source、审批记录与结果。
