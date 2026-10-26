# 源码级审查笔记：可复用点、具体风险与差距

> 审查方法：2026-10-26 定位并阅读下列 **指定源码文件**，不代表已经全面审计相关项目全部代码或在运行环境中完成测试；具体 commit 固定于 [证据登记册](04-evidence-register.md)。

## 1. Docling Graph provenance：模型之外的独立证据账本

**证据**：
- [core/provenance/models.py](https://github.com/docling-project/docling-graph/blob/bbcd0e4846fadfcadac2800784783e59cd2722a9/docling_graph/core/provenance/models.py)
- [core/provenance/binder.py](https://github.com/docling-project/docling-graph/blob/bbcd0e4846fadfcadac2800784783e59cd2722a9/docling_graph/core/provenance/binder.py)
- [templategen/ontology/owl.py](https://github.com/docling-project/docling-graph/blob/bbcd0e4846fadfcadac2800784783e59cd2722a9/docling_graph/templategen/ontology/owl.py)

`models.py` 中存在 DocumentOrigin、ItemGeometry、ChunkRecord、SourceAnchor、NodeProvenance、ProvenanceLedger；证据强度区分 observed/verbatim/derived/reconciled，支持 text/content/template schema hash。provenance 是**旁路 sidecar ledger**，不是把“来源”让 LLM 自己生成。

`binder.py` 在结构化 Pydantic 模型转图之后绑定 ledger；其 `_fuzzy_same_path_lookup` 特别要求同一路径下的唯一匹配，说明无法安全定位的情况应该避免任意指派。 `owl.py` 说明 OWL/RDFS 类、datatype/object properties、hasKey 等可以被编译为抽取模板，但代码也记录超出可表达范围的 gap。

**采用**：source→chunk→entity fact 多级证据模型、ledger 独立存储与一致性校验，schema compiler 输出缺失/降级报告。  
**不应假设**：某个框架只要提供 bbox 就一定证明“某条信号关系来自 PDF 某一行”。节点来源需要做误锚点对照；关系证据也应单独建模。

## 2. Neo4j LLM Graph Builder：Chunk/Entity 拓扑与身份风险

**证据**：
- [make_relationships.py](https://github.com/neo4j-labs/llm-graph-builder/blob/a728de68d8c75720081816d47b5900a84d93fdcf/backend/src/make_relationships.py)
- [graph_query.py](https://github.com/neo4j-labs/llm-graph-builder/blob/a728de68d8c75720081816d47b5900a84d93fdcf/backend/src/graph_query.py)

`make_relationships.py` 使用 `Chunk-[:HAS_ENTITY]->Entity`、`Chunk-[:PART_OF]->Document`、`FIRST_CHUNK`、`NEXT_CHUNK` 维护文档脉络；也会建立 chunk embeddings。其实体合并片段使用 `apoc.merge.node([data.node_type], {id:data.node_id})`：所示合并键**没有车型/文档版本/工程基线字段**。

**后果**：若领域实例以通用 `HU` / `FragranceStatus` 等名字做 node.id，不同项目和不同版本存在误并号风险。不能直接把这个函数作为汽车工程权威写入；必须以 `baseline_id + canonical_id` 做限定，并进行 collision test。

`graph_query.py` 将图数据转换为可展示节点和边，适合作为 UI/浏览接口参考，不能代替按源文档 ACL 过滤的工程查询 API。

## 3. KnowledgeGraphBuilder：抽取 API 的持久性与安全边界

**证据**：
- [docs/guide/extraction-api.md](https://github.com/DataScienceLabFHSWF/KnowledgeGraphBuilder/blob/95a8df0d381545df0e4421f7a76ed674250062ee/docs/guide/extraction-api.md)
- [Planning/benchmarks/expanded/STATUS.md](https://github.com/DataScienceLabFHSWF/KnowledgeGraphBuilder/blob/95a8df0d381545df0e4421f7a76ed674250062ee/Planning/benchmarks/expanded/STATUS.md)

该 extraction API 接受文档和 ontology，随后提供 run status/results（`POST /api/extract`、`GET /api/extract/{runId}/status`、`GET /api/extract/{runId}/results`）。关键限制由文档**明确声明**：

1. 任务 run 状态保存在内存中，服务重启后丢失；
2. 提交入口 `POST /api/extract` 当前无认证，文档建议在可信网络使用；
3. 其 README 和 STATUS 的性能/质量不是独立 hold-out 工业质量证明；
4. 不能将“工作台可接收 extraction API 的 JSON”推导为已有成熟 Postgres/pgvector retrieval。

**采用**：异步 extraction API 契约与阶段状态可参考。  
**必须替换**：持久 Job 表 + checkpoint/outbox、所有 POST 身份鉴权、限流、体积限制、项目权限和审计。此部分明确作为 P0 安全问题。

## 4. NORMA：OWL 推理与 SHACL 验证必须分工

**证据**：
- [ontology/shacl.py](https://github.com/Destivano/NORMA/blob/f10ab53e02b2a98493d2d7de569edcbbf3320637/src/norma/knowledge_graph/ontology/shacl.py)
- [ontology/reasoner.py](https://github.com/Destivano/NORMA/blob/f10ab53e02b2a98493d2d7de569edcbbf3320637/src/norma/knowledge_graph/ontology/reasoner.py)

`reasoner.py` 的职责包括 OWL 2 RL 物化（子类、逆属性、传递关系），不是直接替代源事实审查。`shacl.py` 的源码开头**主动说明该系统重新定义 conforms 判定**：依据 Finding 严重性，而不机械等同 SHACL 标准 `conforms` 的全局语义。

**采用**：推理结果与原文明确事实分开；验证结果记录 severity/validator version；生产发布 gate 对 violation/warning/unknown 做独立政策配置。

**反例**：把 `rdfs:domain` 当作“关系必须连接特定类型”的校验表达，可能触发推理后的错误重分类。应使用业务约束或 SHACL node shape 检查，不能只看推理后 0 violations。

## 5. VSS / VSSo：标准语义与 OEM 实际通信定义不同

**证据**：
- [spec/Cabin/HVAC.vspec](https://github.com/COVESA/vehicle_signal_specification/blob/dcc7cf570f27378d7ff9333f2a4d1cf552645cfe/spec/Cabin/HVAC.vspec)
- [spec/vsso-core.ttl](https://github.com/w3c/vsso/blob/34265a2ee01acfeb8807e07226ca9f58159c6aba/spec/vsso-core.ttl)

VSS 的 HVAC.vspec 描述车辆 HVAC 抽象属性/路径，而 VSSo Core 在 TTL 中使用 `owl:Class` 和 `owl:ObjectProperty` 明确 `Vehicle`、`VehicleComponent`、`VehicleProperty`、`partOf` 等语义。

**采用**：VSS concept ↔ OEM Signal 的显式 mapping，不同版本/市场单独审批。  
**避免**：把一个 VSS HVAC 路径作为 OEM DBC 中某条香氛 Status CAN 信号的存在性证明。

## 6. 项目级设计变化

新增必须实现的能力（按优先级）：
- P0：`ExtractionRun` 数据库持久化、run checkpoint 恢复、提交 API 强认证；
- P0：`EntityIdentity` 与基线隔离、复合唯一约束、防同名跨车型误 merge；
- P0：`EvidenceLedger` 独立于 LLM JSON，事实关系必须支持不确定/未定位；
- P1：OWL compiler 的 feature gap 警告清单，不接受静默降级；
- P1：SHACL findings 严重性/开放世界与闭世界验证策略；
- P1：graph benchmark 单独验证跨文档 path precision，不把社区摘要或检索命中率当影响分析质量。

## 7. 尚未覆盖的审查范围

没有运行这些仓库的 Docker/test suites；未完整审计前端安全、OCR 模型精度、KAG 源码推理细节、许可证依赖清单。后续必须通过 [验收和评测](../delivery/01-evaluation-and-acceptance.md) 的复现实验补齐，所有结论应有正确的证据等级。
