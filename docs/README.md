# Automotive Ontology — Research & Architecture Documentation

> Scope: automotive specification PDFs → versioned, provenance-backed ontology / knowledge graph → traceability, impact analysis, test viewpoints and Agent tools.  
> Research snapshot: 2026-10-26. Status: **research and design**, not a validated production implementation.

## 阅读顺序

1. [研究结论与选型](research/01-executive-assessment.md) — 决策、路线、风险、替代方案
2. [上游项目源码与能力审查](research/02-project-deep-dive.md) — Docling Graph、Neo4j Graph Builder、OpenSPG/KAG、KnowledgeGraphBuilder 等
3. [汽车标准与语义互操作](research/03-automotive-standards.md) — VSS/VSSo、DBC、ReqIF、SAMM、OWL/SHACL
4. [证据登记册](research/04-evidence-register.md) — 固定上游版本、代码路径、已验证与待验证区分
5. [源码级审查](research/05-source-code-audit.md) — provenance 源码、节点合并风险、抽取 API 持久性与安全
6. [目标架构与 ADR](architecture/01-target-architecture.md)
7. [本体领域模型](architecture/02-domain-ontology.md)
8. [版本、溯源与可信发布](architecture/03-versioning-provenance.md)
9. [数据库物理模型](architecture/04-storage-schema.md)
10. [文档抽取及实体归一流水线](pipelines/01-pdf-to-knowledge.md)
11. [检索、推理、MCP 与 Actions](pipelines/02-query-agent-actions.md)
12. [汽车式样端到端示例](examples/01-fragrance-hvac-worked-example.md)
13. [实验与工程验收](delivery/01-evaluation-and-acceptance.md)
14. [分阶段实施计划](delivery/02-roadmap.md)
15. [风险、许可与决策记录](delivery/03-risks-and-adrs.md)

## 范围界定

本仓库首先产出**可审查的设计与研究文档**。文档中的 JSON、SQL、Cypher、API 为目标契约草案；除非特别注明，**不代表系统已构建、运行或通过基准测试**。示例“573/695D/香氛”及其中的 CAN 信号和时间值均为**合成示例**，不是受控 OEM 式样书的真实条款。

### 核心原则

- 本体 TBox（Schema/约束）与事实 ABox（实例）分离；候选事实与已批准事实分离。
- PostgreSQL 作为权威事实、基线、审核、审计数据库；Neo4j、全文/向量库作为可重建查询投影。
- 原文锚点、文档版本、车型基线、抽取批次、审核人是不可省略的业务数据。
- LLM 只生成候选知识和推荐；规则校验与人审后才能发布工程事实。
- VSS/VSSo 提供汽车信号语义参考，不等价于 CAN DBC 或 OEM 测试规范。
- 任何生成测试用例、变更写入和部署操作均应有明确权限、幂等性和审批边界。

## 主要上游入口

- [Docling Graph](https://github.com/docling-project/docling-graph)
- [Neo4j LLM Graph Builder](https://github.com/neo4j-labs/llm-graph-builder)
- [OpenSPG](https://github.com/OpenSPG/openspg) / [KAG](https://github.com/OpenSPG/KAG)
- [Vehicle Signal Specification](https://github.com/COVESA/vehicle_signal_specification) / [VSSo](https://github.com/w3c/vsso)
- [Eclipse Capra](https://github.com/eclipse-capra/capra)
- [KnowledgeGraphBuilder](https://github.com/DataScienceLabFHSWF/KnowledgeGraphBuilder)
- [NORMA](https://github.com/Destivano/NORMA)

阅读具体技术结论时应同时参照 [证据登记册](research/04-evidence-register.md) 的固定 commit 和限制说明。
