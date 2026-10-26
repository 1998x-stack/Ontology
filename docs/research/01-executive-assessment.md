# 研究结论与技术选型（2026-10-26）

## 目标与决策摘要

目标不是复刻通用 GraphRAG：输入 OEM 汽车式样 PDF、通信定义（DBC/表格）、测试规格、车型配置，在**受约束的 Ontology** 下形成可溯源、可版本化、可验证的知识事实，再供跨式样书追踪、C45 测试观点矩阵、测试生成和 Agent 工具使用。

**架构决策（建议，不是已实施结论）：**
1. **权威层**：PostgreSQL 管理文档修订、工程基线、对象身份、事实主记录、审核、幂等发布及审计。
2. **语义契约**：先用 LinkML/YAML 定义实体、关系、枚举与校验，并明确 TBox（类型/属性）与 ABox（实例）；需要 RDF 互操作时转换为 OWL/RDF，用 SHACL 做闭世界式检查。
3. **解析**：评估 Docling / Docling Graph 的布局、分块和来源追踪；LLM 只输出 CandidateFacts，不直接向生产 Neo4j 写入。
4. **查询投影**：Neo4j 存储经审核的可重建关系图；Postgres FTS / pgvector 负责字面与语义检索。
5. **车辆语义**：VSS/VSSo 是车辆信号语义参考，OEM DBC 和内部通信规范才是实际总线定义的依据。
6. **追溯**：参考 Capra 的跨工件追踪与 NORMA 的版本、证据设计，不直接照搬其运行时。
7. **应用层**：读 API 与审批写 Actions 分离；MCP、GraphRAG 和 TestCase Agent 共用同一身份、基线、证据服务。

## 项目归类与采纳判断

| 项目 | 用途 | 判断 | 不能替代 |
|---|---|---|---|
| [Docling Graph](https://github.com/docling-project/docling-graph) | 文档/Schema → Pydantic 图对象、provenance | **优先 Spike**：抽取核心 | 需求版本和领域审查 |
| [Neo4j LLM Graph Builder](https://github.com/neo4j-labs/llm-graph-builder) | 上传、UI、图谱构建、问答 | **参考 UI 和 Demo**，实验项目 | 工程事实权威库 |
| [KnowledgeGraphBuilder](https://github.com/DataScienceLabFHSWF/KnowledgeGraphBuilder) | OWL 引导抽取、事实证据、验证/导出 | **研究抽取 API/数据契约** | 工业质量的已证实保证 |
| [OpenSPG](https://github.com/OpenSPG/openspg) | SPG Schema、语义关系、规则与推理 | **架构借鉴，推迟整体引入** | 本项目的汽车领域建模 |
| [KAG](https://github.com/OpenSPG/KAG) | 领域问答、多跳知识推理 | **在有标注集后做对照实验** | 权威事实审计与工作流 |
| [VSS](https://github.com/COVESA/vehicle_signal_specification) / [VSSo](https://github.com/w3c/vsso) | 标准车辆信号语义 | **建立显式映射表** | CAN DBC 信号位与总线事实 |
| [Eclipse Capra](https://github.com/eclipse-capra/capra) | 跨工件 trace links、矩阵和影响分析 | **借鉴追溯抽象** | LLM PDF 抽取 |
| [NORMA](https://github.com/Destivano/NORMA) | 汽车法规、provenance、SHACL、impact | **借鉴证据质量和评估反例** | 真实 OEM 式样书验证 |
| [OntoGPT](https://github.com/monarch-initiative/ontogpt) | LinkML 递归抽取、Ontology grounding | **可选实体对齐对照组** | 汽车领域模板 |

## 为什么不立刻把所有框架合并

- Docling Graph、OpenSPG、KAG 和 Neo4j Builder 在“抽取、图数据、问答”存在重复；全部引入会导致 Schema 定义重叠、事实身份不一致、同步与许可证风险。
- KAG/GraphRAG 可能对长距离推理有价值，但不是每条工程问答都受益。NORMA 的项目内评估曾明确报告一些图扩展设置没有带来增益；评估使用非独立的 silver 标注，不能外推。
- 默认选择尽量少组件：PostgreSQL、Docling(Graph 可选)、Pydantic/LinkML、Neo4j（Stage 2 以后）。运行中的组件必须以数据契约、实验结果决定是否保留。

## 决策矩阵（定性，不是实测分数）

| 维度 | 简单 PDF-RAG | Neo4j Builder Demo | 本方案 |
|---|---|---|---|
| PDF 快速展示 | 强 | 强 | 中（需开发） |
| 原文 page/section/bbox 证据 | 需开发 | 需核验 | 必须 |
| 车型/地区/修订版本 | 弱 | 需扩展 | 原生 |
| 要求与信号身份约束 | 弱 | 自定义 Schema | 原生 |
| 人审发布门禁 | 需开发 | 需扩展 | 原生 |
| 查询图遍历 | 弱 | 强 | 强 |
| 审计及历史回放 | 需开发 | 需扩展 | 原生 |
| 初始运维成本 | 低 | 中 | 中至高 |

## 关键质量门槛

- **禁止原文缺证据发布**：发布的需求及直接声称“来自源文档”的关系必须至少一个可解析证据锚点。
- **禁止跨基线误连接**：车型、市场、文档版本必须明确；未指定基线的查询默认拒绝或提示选择。
- **禁止模型捏造工程 ID**：未知 ECU/Signal 保留 unresolved mention，进入人工或受控词典对齐。
- **业务规则闭环**：覆盖矩阵必须区分 mandated / recommended / not_applicable / unknown。
- **禁止以图路径=因果关系**：影响分析返回候选及路径证据，而不是自动确认必然受影响。

## 范围与非目标

P0：一组**合成、去敏** 573 香氛/空调式样示例 + 一份通信定义 + 一份测试观点规则，完成解析、原子化、归一、审查、发布、查询。

暂不承诺：跨 OEM 完整语义互操作、自动证明安全合规、无需人工的变更发布、对生产车载 CAN 进行任何写入、完全复用 Palantir 专有 Ontology API。

## 溯源和证据

详细项目级源码路径、固定 commit、限制、许可待核对项见 [证据登记册](04-evidence-register.md)，逐仓研究见 [02](02-project-deep-dive.md)。本文为基于公开仓库的架构建议，**未进行本地部署或真实 OEM 语料 Benchmark**。
