# Stage 0：研究与契约基线

## P0 已形成的研究资产

- [x] 核查目标仓库现状并发布研究文档；
- [x] 固定关键上游项目源码 commit、源码路径和公开限制（见 research/04 和 05）；
- [x] 对比 Docling Graph、Neo4j Builder、OpenSPG/KAG、KnowledgeGraphBuilder、VSS/VSSo、Capra、NORMA；
- [x] 设计领域本体、版本/证据/审批、PG 主库 + Neo4j 投影；
- [x] 设计合成 573 空调/香氛示例及 Golden Set 指标；
- [x] 建立 ADR、公开资料证据与风险清单。

## 尚需在工程实现前复核

- [ ] 实测第三方源码中 provenance 锚点/跨页表格质量；
- [ ] 核验所有准备复制的上游代码和 transitive dependencies 的许可证；
- [ ] 安全负责人确认真实 OEM 文档可用范围与允许使用的 LLM provider；
- [ ] 工程领域负责人批准首版 Class/Relation 及 Signal ID 规则；
- [ ] 形成至少一个含 “NOT/时序/跨页/多版本” 的人工标注小样本。

## Gate

关键研究文档可复查，上游代码未被直接复制或错误当作已验证生产能力；真实数据、内部密钥不得进入公开仓库。

依赖：[docs/research/](../research/), [docs/architecture/](../architecture/)。
