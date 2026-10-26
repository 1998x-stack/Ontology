# Stage 0–5 实施路线图和交付 Gate

> 本仓库目前只有文档研究与架构草案，下列阶段**尚未实现**。

| Stage | 交付 | 验收 Gate |
|---|---|---|
| 0：研究/架构 | 选型深研、Ontology v0.1、存储模型、风险和评估集设计 | 所有技术判断可定位公开来源，领域不变式得到评审 |
| 1：文档→候选事实 | PDF 布局/证据、原子需求、Validation、候选审核 UI/API、PG | 合成示例可提取且可溯源；重试幂等；错误不进入正式库 |
| 2：信号/图谱 | DBC import、Canonical Registry、Baseline、Outbox、Neo4j 投影、追溯查询 | 不同车型/Rev 严格隔离；投影回放正确；query ACL |
| 3：测试本体 | ViewpointRule、TestObligation、C14/C45 Matrix、Case 覆盖 | required/unknown/not_applicable 区分准确，缺口有证据 |
| 4：Agent / MCP | Typed read tools、Graph/FTS/Vector 组合、变更影响、测试候选、审批 Actions | 端到端可复现；写入只在权限与审批后发生 |
| 5：工程化 | 大规模 benchmark、故障恢复、监控、安全审计、迁移与灾备 | 提供真实负载与安全证据，再考虑生产声明 |

## 分工建议

- **Ontology Owner**：Class/Relation/Version/Rule 变更，Schema Release。
- **Document Pipeline**：PDF 布局、原文锚点、抽取、quality flags。
- **Master Data**：ECU/Signal/DBC/aliases 与 canonical resolution。
- **Storage & Platform**：PG migrations、outbox、graph projector、API/Auth。
- **Domain Verification**：Test Obligation、C45 覆盖、Golden Set、人工评审。
- **Agent Runtime**：MCP、安全工具与可解释 QueryPlan、审批 Actions。

## 建议 Epic

```text
EP01 Ontology Schema/Registry & contract tests
EP02 Document parser + anchor resolver
EP03 Requirement atomizer + conditions AST
EP04 Candidate validation + review/publish
EP05 DBC/ECU/Signal canonical entity registry
EP06 Projection + baseline graph query + ACL
EP07 Viewpoint rules + obligation & coverage
EP08 Revision diff + impact candidate
EP09 MCP tools + approval workflow
EP10 Golden Set, benchmark, security/observability
```

依赖关系：`EP01→EP02→EP03→EP04`，`EP01→EP05`，`EP04+EP05→EP06→EP07/08→EP09`；EP10 在每阶段运行。

## 各阶段 Definition of Done

- 可重现的 API/schema + 有效/无效样例；
- 单元、集成、负例安全测试和 CI；
- 失败恢复、重复运行幂等与日志追踪；
- 版本化迁移/升级/回滚说明；
- 用户可从返回结论打开来源原文；
- 性能与错误的报告含输入/输出数量及失败样本。

## 不应过早做

- 同时部署所有开源平台引擎；
- 在没有真实标注集时宣称某 GraphRAG 方案优于另一方案；
- 从向量相似度直接推导强依赖；
- 无审批同步写客户测试系统；
- 发布任何真实内部式样书或 CAN 数据到公开仓库。

## 首个垂直验证路径

先用合成 573/695D 香氛场景：两个 PDF revision + 小型 DBC mock + 5 类 TestObligation。证明 1000ms→500ms 的差分会只生成候选影响、有 provenance、不发生不合法 Signal 合并，并能通过人工审核发布独立基线。
