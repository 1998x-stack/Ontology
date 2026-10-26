# 风险登记册与架构决策记录（ADR 草案）

## 风险登记

| ID | 风险 | 级别 | 控制措施 |
|---|---|---|---|
| R01 | 跨页表格解析丢失条件 | 高 | table cell / page anchor、专门 Golden Set |
| R02 | LLM 臆造 ECU/信号及关系 | 极高 | candidate-only、主数据归一与 evidence gate |
| R03 | 跨车型/地区/修订误合并 | 极高 | baseline-scoped identity、strong matching |
| R04 | 时序比较符/NOT/除外条件错读 | 极高 | typed AST、严格负例测试、高风险人审 |
| R05 | 图可达性被当作因果 | 高 | dependency_kind 与 impact_candidate |
| R06 | PostgreSQL/Neo4j 分叉 | 高 | single writer/outbox/replay/checksum |
| R07 | OWL 推理被误用作完整性校验 | 高 | 明确 OWA 与 SHACL/SQL CWA 约束 |
| R08 | OEM 式样外发泄密 | 极高 | 项目 ACL、本地/授权模型处理、审计 |
| R09 | PDF prompt injection | 高 | 数据/指令隔离、tool allowlist、schema checks |
| R10 | 依赖许可证冲突 | 中高 | License/NOTICE/SBOM 审核 |
| R11 | 自标评测/过拟合 | 高 | blind holdout、人审、可复现实验 |
| R12 | schema 演进破坏历史数据 | 高 | 语义版本、迁移、contract regression |

## ADR-001 主库权威性

**状态 Proposed**：PostgreSQL 是唯一业务事实主写；Neo4j/检索是可重建投影。理由：审批、基线、权限、事务更清晰。代价：outbox/同步逻辑。复议条件：图原生主库在明确一致性、安全、成本对照中获证实优势。

## ADR-002 Schema-first

**状态 Proposed**：以 LinkML/YAML 为语义契约源，映射 Pydantic/JSON Schema，RDF/OWL/SHACL 作为需要标准互操作时的扩展。注意 LinkML→OWL 复杂规则未必语义保真，要测试而非宣称等价。

## ADR-003 候选与已批准事实分层

**状态 Proposed**：LLM 写候选，类型/版本/证据校验、人审、发布后才成为正式事实。确定性低风险自动校验项可批量审查，但安全、故障、通信和时序信息不得无依据自动发布。

## ADR-004 从解析起保留原文证据

**状态 Proposed**：SourceAnchor 伴随布局解析同步写入，不允许问答阶段从相似段落“倒填”证据。ReqIF 等结构化源则可用 native requirement locator，无需强迫映射 PDF bbox。

## ADR-005 组件解耦而非整仓合并

**状态 Proposed**：Docling Graph / Neo4j Graph Builder / OpenSPG / KAG 不整体拼为一个后端；先围绕自己的 schema/事实服务写小型 adapter，用 baseline 演示和 benchmark 决定接入。

## ADR-006 代码/数据许可

**状态 Requires review**：
- Docling Graph README MIT，OpenSPG/KAG README Apache-2.0；
- VSS README MPL-2.0，VSSo README 区分代码 Apache-2.0 与本体 CC 许可；
- Capra README EPL-2.0；
- 仅作 README 声明摘录，**不是法律意见或最终许可证核查**。
- 复制上游代码时逐一审查 LICENSE、NOTICE、第三方依赖及分发模式；
- 真实 OEM 文档、内部测试脚本、真实网络地址/密钥严禁直接进入公开仓库。

## 上线 Gate

经过授权语料评估、跨车型与跨版本隔离、安全负例、审计回放、投影重建、许可检查、数据处理审批和业务签字前，只能称为 research/prototype，不能宣称符合汽车功能安全标准或具备生产 SLA。
