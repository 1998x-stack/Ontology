# Automotive Ontology v0.1：领域模型与不变式

本文件定义 **Schema 契约草案**，不是任何现有 OEM 的实际车型数据。

## 1. 核心概念

```text
Artifact
  Document
    DocumentRevision
      SourceAnchor
  RequirementStatement
    AtomicRequirement
  TestArtifact
    TestViewpoint
    TestObligation
    TestCase
    TestExecution
    Defect
Product
  VehicleModel
  Variant
  EngineeringBaseline
System
  Feature
  ECU
  Network
  Message
  Signal
Behavior
  State
  Transition
  Condition
  Trigger
  ExpectedBehavior
  TemporalConstraint
Governance
  CandidateFact
  ReviewDecision
  ChangeRequest
  ImpactCandidate
```

**同名异义与异名同义**：`Head Unit` / `HU` 可能是同一 ECU，必须经过 project、variant、revision 的上下文判断。`HVAC` 可能指功能域也可能指 ECU；不可纯基于字符串 merge。

## 2. 类型定义表

| Class | Stable key 方案 | 最小字段 | 核心关联 |
|---|---|---|---|
| VehicleModel | OEM:MODEL:code | code | HAS_VARIANT |
| Variant | OEM:VARIANT:code | market, trim, platform | IN_MODEL |
| EngineeringBaseline | PROJECT:BASELINE:id | status, effective_at | SELECTS_REVISION |
| DocumentRevision | DOC:code:rev | sha256, language, source_uri | HAS_ANCHOR |
| SourceAnchor | SHA256+location | page, section, bbox, exact_text | IN_REVISION |
| RequirementStatement | DOC:rev:section:statement | exact_text | DECOMPOSES_INTO |
| AtomicRequirement | REQ:source_key:atomic_index | actor, precondition, trigger, expected, verification_kind | USES_SIGNAL, APPLIES_TO |
| Feature | FEATURE:project:code | name, domain | IMPLEMENTED_BY |
| ECU | ECU:project:code | component_id, aliases | TRANSMITS, RECEIVES |
| Message | NETWORK:BUS:FRAME:key | frame_id, bus, dlc | CONTAINS_SIGNAL |
| Signal | SIGNAL:network:message:name | start_bit, length, unit, enum | IN_MESSAGE |
| TestViewpoint | VIEWPOINT:standard:code | category, applicability | COVERED_BY |
| TestObligation | OBLIGATION:baseline:req:viewpoint | coverage_type, rationale | APPLIES_REQUIREMENT |
| TestCase | TESTCASE:external_id:revision | steps, expected, owner | SATISFIES, VERIFIES |
| ChangeRequest | CHANGE:system:id | status, target_baseline | MODIFIES |
| ImpactCandidate | IMPACT:change:target | path, severity, certainty | IDENTIFIES |

`SourceAnchor` 的 stable key 应先采用 `document_revision_id + page/section + char offset or bbox + fragment hash` 的组合；PDF 内容重新解析导致文字偏移可能变动，保留 `anchor_lineage` 而不盲目重用旧 Anchor ID。

## 3. Relationship Registry

```yaml
schema_version: "0.1.0"
relations:
  - key: DECOMPOSES_INTO
    subject: RequirementStatement
    object: AtomicRequirement
    evidence_required: true
  - key: USES_SIGNAL
    subject: AtomicRequirement
    object: Signal
    evidence_required: true
  - key: TRANSMITS
    subject: ECU
    object: Message
    evidence_required: true
  - key: RECEIVES
    subject: ECU
    object: Message
    evidence_required: true
  - key: CONTAINS_SIGNAL
    subject: Message
    object: Signal
    evidence_required: true
  - key: IMPLEMENTS
    subject: ECU
    object: Feature
    evidence_required: true
  - key: VERIFIES
    subject: TestCase
    object: AtomicRequirement
    evidence_required: true
  - key: SATISFIES
    subject: TestCase
    object: TestObligation
    evidence_required: true
  - key: DEPENDS_ON
    subject: AtomicRequirement
    object: AtomicRequirement
    evidence_required: true
  - key: APPLIES_TO
    subject: AtomicRequirement
    object: Variant
    evidence_required: true
```

不变式：
- 关系两端存在且符合 Schema 的 `subject/object`；允许子类须经继承解析。
- 每个已发布关系的 subject/object 必须在同一个有效工程基线下可解析；明确“跨基线变更比较”使用比较服务而不是跨基线正式关系。
- `DECOMPOSES_INTO` 不应有循环；一个原子需求必须拥有至少一个源句子。
- ECU/Message/Signal 对应真实定义时，不可用 LLM 信心替代 DBC 校验。
- 正式 `VERIFIES` 表示定义的验证目标，不等于测试已执行或已通过。
- `DEPENDS_ON` 必须包含 `dependency_kind`（enablement / data / timing / safety / suspected 等），影响查询需区分强依赖与待调查关联。

## 4. 行为表示不要退化为文本

合成例：
```yaml
id: "REQ:573:4.2.1:002"
actor: "ECU:HVAC"
preconditions:
  all_of:
    - {signal: "PowerMode", operator: "eq", value: "READY"}
    - {feature: "HVAC", state: "ON"}
trigger:
  signal_received: {signal: "FragranceRequest", value: 1}
expectation:
  signal_emitted: {signal: "FragranceStatus", value: 1}
temporal:
  reference_event: "FragranceRequest.received"
  comparator: "<="
  value: 1000
  unit: ms
source:
  document_revision: "SPEC-573:2.1"
  anchor: "anchor:page42:section4.2.1"
status: candidate
```

**特别提醒**：这里对 `preconditions` 的推断需要先确认 PDF 原句作用域确实覆盖该原子需求。时间约束的 reference_event 不允许模型自行猜测。

## 5. Test Obligation 和 Coverage 的规则

```text
Requirement + Applicable Viewpoint Rules
      -> TestObligation
TestCase --SATISFIES--> TestObligation
TestExecution --EXECUTES--> TestCase
Defect --FOUND_IN--> TestExecution
```

每个 Obligation 状态：`required / recommended / not_applicable / undecided`。严格覆盖率的分母只取 *approved required*，并分别报告 `not_applicable`、`undecided`，不可将“空数据”当作不需测。

## 6. Schema 演进

`0.1.0` 初始版；新增可选字段属于兼容变更；修改字段含义、relation domain/range 或 ID 策略需要 migration、re-index 和评估集回归。模型版本与文档版本独立发布，所有事实记录 `ontology_version`。
