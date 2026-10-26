# Stage 1 / v1.0：PDF → 候选需求 → Evidence → 数据库

## 范围与约束

首次版本不宣称拥有完整 Docling Graph、任意 LLM 结构化推理、CAN 定义校验或正式事实发布。先实现**可运行、测试覆盖的数据入口**：规范性语句候选抽取只是可替换的 deterministic baseline，不能当作已批准工程需求。

## EP-01 项目与环境（P0）

- [ ] Python `pyproject.toml`、src 包结构、类型化数据模型和 CLI；
- [ ] SQLite 本地测试适配 + PostgreSQL 生产 DB URL（文档与连接契约）；
- [ ] GitHub Actions pytest / lint / schema-check CI；
- [ ] Docker Compose Postgres 与本地快速运行指引；
- [ ] 服务健康检查、错误码、上传体积/页数限制。

## EP-02 文档解析和锚点（P0）

- [ ] PDF 魔数检查、损坏文件拒绝、SHA256 幂等；
- [ ] 提取页面块、文本、物理页码、bbox、章节；
- [ ] 以原文 hash + block identity 建立可查询 SourceAnchor；
- [ ] 受保护的原始 PDF 字节存储或等价不可变对象存储；
- [ ] 跨页/表格/图片复杂页面标记质量不确定，而非静默抽取；
- [ ] 逐页证据索引/API。

## EP-03 候选原子需求（P0）

- [ ] Pydantic Schema：RequirementCandidate、Condition/SignalMention/TimeConstraint；
- [ ] 确定性 normative marker baseline，保留 raw_text，不猜测标准 Signal ID；
- [ ] 直接提取 “must/shall/必须/应/すること” 规范性陈述并保留抽取来源；
- [ ] 候选 `candidate` 状态不可默认变为 `approved`；
- [ ] 模糊/否定/条件作用域在当前实现无法表达时标记 requires_review；
- [ ] 给出基于标注样例的抽取限制与已知错误类别。

## EP-04 数据持久化与接口（P0）

- [ ] DocumentRevision、SourceAnchor、ExtractionRun、CandidateRequirement 关系表；
- [ ] 唯一 (project,code,revision) 与 content SHA 冲突检测；
- [ ] CLI ingest/list、HTTP POST 上传、GET 文档/候选/证据；
- [ ] 单事务写入、重复输入幂等；
- [ ] API key 认证，生产环境默认禁用匿名读取；
- [ ] 响应版本/来源/状态标识，拒绝隐式跨项目数据混用。

## EP-05 自动化验证（P0）

- [ ] 构造合成 PDF fixture 和负例，不提交内部式样；
- [ ] 正常 2 条候选、bbox/页码证据、UTF-8/多页；
- [ ] 同版本同文件再导入不重复；同版本不同字节返回冲突；
- [ ] 非 PDF、超大文件、超限页、无规范性句子、认证错误；
- [ ] API 测试、DB 可重新打开、CLI 烟测；
- [ ] CI 全绿并记录实际执行环境/结果。

## P1（下一个 Stage 1 迭代）

- [ ] Docling Graph backend 接入并评估 provenance 对齐；
- [ ] 本地/授权 LLM 的 Schema-guided extractor Adapter；
- [ ] 需求 AST（AND/OR/NOT）、日文规范提取、多语言表格；
- [ ] 人工 Review API 和表格编辑前端；
- [ ] 断点/队列大文件解析、权限到锚点级和审计；
- [ ] PostgreSQL 集成测试（当前 SQLite 不足以证明 PG 生产一致性）。

## 验收与 DoD

执行 `pip install -e '.[dev]'` 和 `pytest -q`；上传合成式样得到确定性候选并能查原文证据。**此 Gate 只表示候选抽取 MVP 的可复现，不表示工程知识发布或生产安全合规。**
