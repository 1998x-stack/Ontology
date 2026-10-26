# 上游项目研究：架构、源码路径与可复用边界

研究方法：2026-10-26 读取 GitHub 上游仓库 README、目录结构，以及部分项目依赖和评估状态文件；记录固定 commit 于 [04](04-evidence-register.md)。**这是源码布局与公开设计审查，不是对所有子模块逐行审计或性能实测**。

## A. Docling Graph — PDF 到结构化图谱

仓库：[docling-project/docling-graph](https://github.com/docling-project/docling-graph)。README 指出两类抽取后端：Docling 本地 VLM 和 LiteLLM 后端，Pydantic 结构化模型映射到 NetworkX；支持图融合、稳定标识、provenance。pyproject.toml 的项目版本在审查时为 1.9.1（固定 SHA 见登记册）。

可定位代码：`docling_graph/pipeline/orchestrator.py`、`pipeline/stages.py`、`core/provenance/`、`core/extractors/`、`templategen/`、`core/merge/`。

**复用方向**：
- 分离 layout conversion 与 schema-bound extraction；可以把 PDF 表格、章节、图片当作不同 evidence block。
- provenance ledger 允许把抽取对象映射回源 chunk/页码/几何；必须针对表格跨页、图中文字、扫描 OCR 另外测试准确性。
- OWL/RDFS → 模板生成和 Pydantic 模型可作为本体驱动抽取的入口。

**集成挑战**：NetworkX 不是权威知识事实库；模板结构通常不包括 `DocumentRevision`、`VehicleBaseline`、审核状态、跨文件身份消歧。多文档 merge 的冲突政策必须由我们的 canonical ID/审批规则实现。

**实验任务**：10 个有合并单元格的表格、10 个条件/否定语句、10 个跨页条款，逐条对比 source-anchor accuracy；导出 graph 后验证数据不会把同名、不同车型信号误合并。

## B. Neo4j LLM Graph Builder — 产品化界面参考

仓库：[neo4j-labs/llm-graph-builder](https://github.com/neo4j-labs/llm-graph-builder)。README 明确说明 **Neo4j Labs 实验项目，不属正式支持产品**。源码顶层可见 `frontend/`、`backend/`、`docker-compose.yml`，README 描述 React、FastAPI、LangChain、图生成与可配置 Schema；Neo4j 5.23+ 与 APOC 为当前 README 的部署要求。

可借鉴：多来源上传、图可视化、源文件管理、Schema UI、图问答、处理状态；不应把通用自动关系抽取结果视为汽车需求的 authoritative records。

**主要 Gap**：审计基线、不变式样修订、候选知识审核、DBC 关联、C14/C45 Matrix、需求原子化与安全审批。建议界面理念复用，领域服务重写；评估其前后端依赖许可后再考虑直接拷贝代码。

## C. OpenSPG 与 KAG — 语义和查询引擎参考

[OpenSPG](https://github.com/OpenSPG/openspg)：README 描述 SPG-Schema、SPG-Builder、KGDSL 和 SPG Reasoner；仓库具有 `builder/`、`reasoner/`、`server/` 等模块。其设计把 typed property graph、语义规则、实体标准化合并到一个知识平台。

[KAG](https://github.com/OpenSPG/KAG)：以知识增强问答和逻辑推理为目标，仓库具有 `kag/builder/`、`kag/indexer/`、`kag/solver/`、`kag/mcp/` 等模块。两项目不应被误认为一个开箱即用的汽车 OEM 语义平台。

**借鉴**：Schema-first、ontology-guided grounding、符号逻辑和自然语言混合、query plan + evidence path。  
**延后**：整套 OpenSPG + KAG 的部署/运行时引入，需首先与精简 PostgreSQL/Neo4j 基线比较维护成本、问答收益、推理误报。

## D. KnowledgeGraphBuilder — OWL 约束流水线

仓库：[DataScienceLabFHSWF/KnowledgeGraphBuilder](https://github.com/DataScienceLabFHSWF/KnowledgeGraphBuilder)。README 描述 OWL-guided PDF/DOCX/PPTX/XML 抽取、Neo4j、RDF/JSON-LD/YARRRML/Cypher 导出、`POST /api/extract` 与状态查询 API。仓库存在 `src/kgbuilder/`、`agentic_pipeline/`、`docs/guide/extraction-api.md`、`Planning/benchmarks/expanded/STATUS.md`。

需要非常谨慎：STATUS.md 自述评估是重复的开发集、非独立标注，部分 PDF 被跳过；**图谱规模不是抽取准确率**。参考其多阶段 extraction 与 source evidence 数据契约，但任何性能表述都需自己的 held-out Golden Set 复验。

## E. VSS/VSSo — 汽车信号语义

[COVESA VSS](https://github.com/COVESA/vehicle_signal_specification)：`spec/VehicleSignalSpecification.vspec` 与 `spec/Cabin/HVAC.vspec` 等定义通用车辆信号语义、类型、单位和路径。VSS 目标是跨协议语义，不是 ECU 原始通信层规范。

[W3C VSSo](https://github.com/w3c/vsso)：README 定义 core ontology 基于 VSS，并借用 SOSA observation/actuation 模式；`spec/vsso-core.ttl` 提供核心 RDF 模型。需注意这是标准化研究与发展项目，**不能把 W3C 仓库存在等同于所有内容已经是 W3C Recommendation**。

采用策略：建立 `InternalSignal` ↔ `VSSConcept` 映射，映射必须注明 `exact/broad/narrow/unmapped`、版本、审核和证据。CAN ID、位宽、发送周期仍由 DBC/通信规格权威来源提供。

## F. Capra — 跨工件可追溯关系

[Eclipse Capra](https://github.com/eclipse-capra/capra) 提供适配器连接工程工件、追溯矩阵、关系可视化与变更分析；仓库可见 `bundles/org.eclipse.capra.generic.tracemodel`、`handler.reqIf`、`ui.matrix`、`handler.emf`。

建议建模：TraceLink = (source_artifact_revision, link_type, target_artifact_revision, evidence, status, provenance)。追踪关系应有自己的 ID 与生命周期、review、dangling-link 检测。Capra 是 Eclipse 桌面生态工具，并非“PDF→LLM”的开箱方案。GitHub 镜像主分支最近代码陈旧，应另核对 Eclipse 正式站点活动情况。

## G. NORMA — 法规类知识图谱的有价值反例

[Destivano/NORMA](https://github.com/Destivano/NORMA)：README 和 `src/norma/knowledge_graph/ontology/shacl.py` 描述法规/条款/需求的 Neo4j↔RDF/OWL/SHACL 路径，`ingestion/`、`retrieval/`、`services/` 结构可参考。

其 README 特别披露对 OWL `rdfs:domain` 与 SHACL 约束混用引发大量验证异常的复盘，以及部分检索设置图扩展没有收益。属于**非常值得阅读的验证案例**，但其公开测量不能转移为汽车 OEM 场景的性能承诺。

## H. OntoGPT、LinkML、ESMF — 可选能力

[OntoGPT](https://github.com/monarch-initiative/ontogpt)：README 详细说明 LinkML SPIRES 逐类抽取和 ontology entity grounding；对未能对齐的术语显式标记，不盲目制造标准标识。我们的 Signal/ECU 也应如此。

[LinkML](https://github.com/linkml/linkml)：YAML authoring + 数据模型校验、转 JSON/RDF；适合作为领域 schema 源头，但对表中复杂时序逻辑另用 DSL/状态机表达。

[ESMF SDK](https://github.com/eclipse-esmf/esmf-sdk)：SAMM 语义模型验证、代码和文档生成；适合工业模型共享思路，非本项目 PDF 解析器。

## 复用而不是拼接

选择每个项目的**特定能力或思想**，不要直接“merge 五个完整后端”。下列做法需要 ADR 审批：复制其代码、迁移原仓许可证条款、让外部框架控制权威事实主库、引入新的多节点运行时。详见 [风险与 ADR](../delivery/03-risks-and-adrs.md)。
