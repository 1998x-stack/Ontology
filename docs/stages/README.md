# Stages：任务计划、实施状态与验收清单

**范围**：以汽车式样 PDF 为主要输入，构建可追溯、基线隔离的 Ontology 知识系统。此处是阶段任务与验收的**唯一索引**；此前 `docs/delivery/02-roadmap.md` 为高层架构路线图。

| 阶段 | 版本建议 | 目标 | 状态 | Gate |
|---|---|---|---|---|
| [Stage 0](stage-0-research.md) | v0.x / v1.0 前置 | 项目研究、标准、Schema 决策 | **文档已完成**，生产验证未做 | 固定来源、ADR、演示数据界定 |
| [Stage 1](stage-1-document-ingestion.md) | **v1.0** | PDF→候选需求→证据→可查询数据 | **实施中** | 运行测试通过、重试幂等、原文锚点 |
| [Stage 2](stage-2-graph-and-baseline.md) | v2.0 | DBC/ECU/Signal 身份、基线、图谱 | 计划 | 跨版本隔离、图投影回放 |
| [Stage 3](stage-3-verification-ontology.md) | v3.0 | 测试观点、TestObligation、C45 Matrix | 计划 | 能解释必测义务和覆盖缺口 |
| [Stage 4](stage-4-agent-and-actions.md) | v4.0 | MCP Agent、变更影响、审核 Action | 计划 | 无审批不写正式系统 |
| [Stage 5](stage-5-production.md) | v5.0 | 性能、安全、监控、迁移、发布 | 计划 | Golden Set 与安全/恢复/容量验收 |

## 状态约定

`[ ]` 未完成，`[x]` 已实现并有验证证据；本阶段已写代码并不意味着 Stage Gate 通过。每个任务须提供对应提交、测试或运行结果才允许打勾。**不得将研究设计或合成示例作为真实 OEM 验收**。

## 定义“完成”的统一约束

- 可运行代码及测试，或完整且可复核的研究/设计证据。
- 输入输出契约及错误类型；正常路径 + 至少一个负例。
- 原文证据、项目/车型版本、安全范围无歧义。
- 有 CI 验证、可重复运行说明、明确尚未覆盖的场景。
- 人工审核后的真实事实与候选 LLM 提取结果分离。

## v1.0 执行切片

Stage 1 先实现**确定性 baseline**（而非尚未接通的外部 LLM），包含 PDF page/text block 解析、normative 语句候选、证据、关系数据库持久化、REST API/CLI 和 CI。目的是首先固定数据契约与正确性边界；之后接 Docling Graph/LLM provider 时可以进行同输入 A/B 测试。

参见 [v1.0 交付追踪](v1.0-implementation-log.md)、[验收报告](v1.0-acceptance-report.md)。
