# 评测方案、Golden Set 与验收标准

**所有数字为建议实验配置，并非当前已有测量结果。**

## 1. 对照系统

A. Docling PDF chunk + FTS/BM25/向量 RAG；  
B. 通用 LLM→Neo4j 自由图提取；  
C. Docling/LinkML Schema-guided → 归一/证据审核 → PG→Neo4j；  
D. 可选 OpenSPG/KAG / OntoGPT 比较。

保持相同来源、切分、任务、硬件预算与 LLM 调用预算；记录输入 checksum、prompt hash、model version、运行环境、错误与中断，不允许只比较成功请求。

## 2. 建议标注集

起步：60 条开发集、120 条 blind holdout（仅为建议样本量；尚未采集）。必须覆盖：
- 条件 AND/OR/NOT、Unless/Except、时序/单位/比较符；
- 跨页表格、合并表头、图解状态机、扫描 PDF；
- 中/英/日语言差异及术语同义；
- 不同车型/地区/Rev 的同名 Signal 和 ECU 别名；
- DBC 与 PDF 的冲突、没有足够证据的未知状态；
- 跨文档关联、变更影响、测试观点覆盖。

标注实体至少包括 DocRevision、SourceAnchor、RequirementStatement、AtomicRequirements、Entity Mentions、Resolved Entities、TypedRelations、Constraints、Review Notes。由两位领域标注者独立标注，冲突提交裁决集。

## 3. 指标与分母

| Metric | 准确定义 | 防止误读 |
|---|---|---|
| Requirement Precision | 正确抽取的原子需求 / 所有抽取原子需求 | 非规范文本误判 |
| Requirement Recall | 正确抽取的原子需求 / Gold 原子需求 | 丢时序/异常要求 |
| Entity Linking Accuracy | 正确对齐 mention / Gold 可对齐 mention | 同名信号 |
| Relation Precision/Recall | 关系 (subject, type, object, baseline) exact match | 错误依赖 |
| Temporal Exact Match | trigger/reference/comparator/value/unit 完整一致 | 1000 vs 500 |
| Anchor Accuracy | 正确锚点 / Gold 应溯源事实 | 页码/bbox 漂移 |
| Version Isolation | 发布集内非法跨基线关系数 | 必须为 0 |
| Impact Recall@k | Gold 受影响项被召回 / Gold 总数 | 不把 path 当因果 |
| Coverage | approved satisfied *required* obligations / 所有 approved required obligations | 排除 unknown/NA |
| Human Review Burden | 每 100 条正式需求的审核时间 | 工程投入 |
| Operational | token、耗时、错误率、成本、恢复率 | 性能和稳定性 |

分开报告 critical/major/minor 错误、F1、置信区间；`SHACL 0 violations` 不是安全认证或语义正确性证明。

## 4. 最低发布安全门槛

- 100% 来源事实对应可定位 SourceAnchor；人工事实必须记录人工依据。
- 0 个跨基线/越权/错误 relation type 进入正式发布库（负向校验用例）。
- 不确定的 Signal/时序/否定条件必须以 `unknown/review_needed` 阻止未经核验发布。
- Outbox 重放不双写，Graph projection 重建后 checksum 与权威库一致。
- 未审核的测试建议不能写入正式 TestCase 库。
- 高风险输出（安全、故障、通信方向）由领域工程师签收。

## 5. 测量流程

1. 选择获授权且已去敏示例资料；
2. 固化 Parser/Prompt/Schema/Model 版本；
3. 开发集上迭代，冻结方案；blind holdout 上只执行一次最终比较；
4. 保存中间数据、失败实例、token/cost、所有人工判断；
5. Bootstrap 置信区间，报告相对于 A/B 的收益；
6. 误差归因：layout、atomization、grounding、relation、version、coverage；
7. 建立 CI 回归和异常终止标准。

## 6. 必测非功能场景

- 恶意 prompt-injection PDF；
- 无权读取关联关系的用户；
- 带重复 run ID 的并发导入；
- 投影服务宕机、恢复和 replay；
- 模型服务超时、损坏页、跨页表、信号缺失、错误单位；
- Schema migration 对历史 snapshot 的读兼容。

## 7. 证据警示

KnowledgeGraphBuilder 的上游 `Planning/benchmarks/expanded/STATUS.md` 明确非独立验证；NORMA 的 README 自述银标检索任务某些图扩展没提升。都不能代替本项目汽车语料评测。固定源码链接见 [登记册](../research/04-evidence-register.md)。
