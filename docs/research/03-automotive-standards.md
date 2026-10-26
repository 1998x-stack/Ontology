# 汽车工程领域本体与行业标准适配

## 1. 明确五种模型的职责边界

| 规范/技术 | 描述对象 | 能提供 | 不能保证 |
|---|---|---|---|
| VSS | 统一车辆数据路径和语义 | 车内属性/传感/执行器语义、类型和单位 | OEM CAN ID、bit offset、周期 |
| VSSo | VSS 的本体形式 | 核心语义、RDF 类型关联 | OEM 需求和测试完整覆盖 |
| DBC | CAN 通信报文/信号 | 消息 ID、bit、长度、倍率、枚举/ECU（视文件定义） | 上层“为什么测试此功能”的要求 |
| ReqIF | 需求及属性/关系交换 | 结构化跨工具需求导入 | PDF 抽取结果天然正确 |
| LinkML / OWL / SHACL | 通用语义与校验技术 | 概念、属性、推理、公理、形状约束 | 工程实际时序的形式化证明 |
| SAMM（ESMF） | 工业数字孪生 Aspect Model | 工业属性、数据结构的语义互操作 | 替代 OEM 需求管理 |

参考：[VSS](https://github.com/COVESA/vehicle_signal_specification/tree/master/spec)、[VSSo](https://github.com/w3c/vsso/tree/gh-pages/spec)、[Eclipse ESMF](https://github.com/eclipse-esmf/esmf-sdk)、[LinkML](https://github.com/linkml/linkml)。

## 2. 内部信号与标准信号不要等同

示例（**合成**）：

```yaml
internal_signal:
  canonical_id: "SIGNAL:695D:HVAC:FragranceStatus"
  dbc_message_id: "0x321"
  ecu: "HVAC"
  source: "CAN_DBC_REV_3"
vss_mapping:
  vss_path: null
  status: unmapped
  match_type: null
  mapping_evidence: null
```

只有在 VSS 中找到语义相符、方向/状态匹配的概念，且经过审核后，才可发布 `exactMatch`。很多 OEM 私有功能可能没有精确 VSS 对应：`unmapped` 应为一等状态，不能强行归到通用 HVAC 属性上。

映射表字段：`internal_id, vss_version, vss_path, mapping_type, confidence, evidence_anchor, reviewer, reviewed_at`。`confidence` 是辅助优先级，不是审查通过的证据。

## 3. 需求分解：用工程语义而非“切 500 字”

一个 Requirement 不是 PDF chunk 的同义词。定义如下：

```text
Requirement := Actor + Preconditions + Trigger + Behavior + [TemporalConstraint]
             + [Exception] + [Applicability] + SourceEvidence
```

语句“READY 且 HVAC ON 时，用户开启香氛，HU 发送请求，HVAC ECU 在 1000ms 内响应”至少包括 HU 请求与 HVAC 响应两条可单独验证的行为；不能把同一条段落同时当作一条需求和两个互不相干的独立要求而不记录父子来源。

建议区分 `RequirementStatement`（原文）与 `AtomicRequirement`（可验证原子行为），关系 `DECOMPOSES_INTO`；并记录拆分理由。

## 4. 形式化规则建议

- **TBox**：类继承、`USES_SIGNAL` 的 domain/range、通用语义命名。
- **ABox**：在指定基线下的 `REQ-002 USES_SIGNAL FragranceStatus`。
- **SHACL / JSON Schema**：属性必需、数据类型、取值范围、最低 evidence 数量、引用存在性。
- **状态机**：Ready/Off/Timeout/Degraded 等状态与 Transition；跨状态禁用/优先级/故障回退规则用 DSL 或状态迁移模型。
- **时间约束**：明确触发时刻、持续时长、比较符、单位、采样精度、容忍范围；不能只存 `timeout_ms=1000`。
- **规则版本**：规则和 Schema 均带版本；校验报告记录 schema_revision、validator_version、input_hash。

**开放世界/闭世界区别**：OWL 中缺少 `Signal` 声明不自动意味着逻辑假；工程发布门禁却可要求“已批准关系必须连到存在且兼容的信号”。SHACL/服务层负责后一类闭世界检查。

## 5. 汽车业务建模建议

顶层模块：
- Product: VehicleModel → Variant → EngineeringBaseline；
- Docs: Document → ImmutableDocumentRevision → SourceAnchor；
- Requirements: RequirementStatement → AtomicRequirement → Behavior/Condition/Constraint；
- System: Feature, ECU, Network, Message, Signal, State, Transition；
- Verification: TestViewpoint, TestCase, TestExecution, Defect；
- Change: ChangeRequest, ImpactCandidate, ReviewDecision。

建议建立独立 `TestObligation`：规则给定版本与适用条件生成“某需求应覆盖什么验证维度”，TestCase 实施它。否则“某条测试可连到此需求”不能证明覆盖完整。

## 6. 互操作与治理

1. 规则/Schema 默认英文稳定标识，保留中文、英文、日文别名；别名带语言和作用范围。
2. 单位归一：存原值、原单位和规范化值，避免覆盖文档原始信息。
3. 适用性：车型、市场、软硬件变体、feature flags、文档 revision 均独立字段。
4. 数据访问：OEM 原始式样与样例分离；外部 LLM 供应商的文件上传需审查数据驻留和合同权限。
5. 跨组织集成时，以公开标准为交换契约，而非要求各方采用同一数据库。
