# Stage 1 / v1.0：PDF → 候选需求 → Evidence → 数据库

## 范围与边界

首个版本实现 candidate-only 纵向切片，**尚未实现**完整 Docling Graph、LLM 抽取、CAN 定义对齐、工程师审批或正式知识图谱发布。下列勾选基于 GitHub CI（Python 3.11/3.12，各 24 tests passed）；详情见 [验收记录](v1.0-acceptance-report.md)。

## EP-01 项目与环境（P0）

- [x] Python package / `pyproject.toml`、src 模块、类型化候选模型、CLI；
- [x] SQLite 测试适配 + PostgreSQL 数据库连接，Postgres CI 集成测试；
- [x] GitHub Actions `compileall`、pytest、基础候选结构校验测试；
- [x] Docker Compose Postgres 定义和本地运行手册；
- [x] FastAPI health/error、15 MiB / 100 页 / 12k blocks / 200 万字符限制；
- [ ] 独立 lint/type-check（Ruff/Mypy）和更全面的质量门禁。

## EP-02 文档解析与来源证据（P0）

- [x] PDF 魔数拒绝、SHA256、重复导入幂等；
- [x] PyMuPDF page/block/text、物理页码、bbox、章节正则；
- [x] block index + SHA256 text + PDF page/bbox 原文锚点；
- [x] 原始 PDF 字节持久保存，提供需 API Key 的 PDF 回读接口；
- [x] SourceAnchor 查询接口和 bbox 定位（单一开发密钥）；
- [ ] 对跨页表格、图片、复杂版式自动添加准确的质量 flags；
- [ ] 文档字符级 offset、表格 cell anchor、跨页条件继承；
- [ ] 逐文档权限/审计与生产级加密对象存储。

## EP-03 候选原子需求与结构校验（P0）

- [x] 采用 Pydantic CandidateView/TimingConstraint 和 YAML schema candidate-only 契约；
- [x] IngestionService 在写 DB 前验证 contract、verbatim source grounding、bbox、time constraints；
- [x] deterministic `SHALL/MUST/必须/应在/应发送/应反馈/すること` 候选抽取；不猜 Signal canonical ID；
- [x] 结果状态始终 candidate，不提供跳过 review 的发布接口；
- [x] 发现否定、复合条件或时间参考不明确时增加 quality flags；
- [ ] 完整 Actor/Condition/Trigger/ExpectedBehavior typed AST 与 LinkML schema；
- [ ] 多语言/跨页复杂条件的人工 Gold Set 与抽取精确率、召回率评估；
- [ ] Docling Graph/LLM 插件与严格 evidence-to-relation 绑定。

## EP-04 数据库与 API（P0）

- [x] SQLAlchemy DocumentRevision、SourceAnchor、ExtractionRun、CandidateRequirement；
- [x] (project,code,revision) 唯一，same-SHA 重复不生成额外候选，different-SHA 返回冲突；
- [x] CLI `ingest`/`list`，HTTP 上传、文档、候选、来源锚点、原 PDF 获取；
- [x] 单事务保存候选、重启后查询数据；
- [x] API Key 缺省无密钥则 fail-closed，已认证资源才可读取；
- [ ] CLI 端到端子进程烟测、跨进程并发双提交与容错测试；
- [ ] 应用层 project/tenant ACL、签名审核日志、版本化 Alembic migration；
- [ ] 将候选事实转换为 approved/published 工程知识的审核工作流（Stage 2）。

## EP-05 测试与质量（P0）

- [x] 合成 PDF fixture、两页与两条规范性句子；
- [x] 页面定位、SHA、重复导入、不同内容冲突、跨项目分离；
- [x] 非 PDF / 超大上传 / 超限页 / 空候选 / 认证拒绝；
- [x] PostgreSQL 服务中真实存储、回读与 revision 冲突检查；
- [x] Validator 的 unsupported data / forged source / invalid timing / bad bbox 负例；
- [x] GitHub Actions Python 3.11 和 3.12 各 24 tests passed；
- [ ] CLI 子进程、权限越界、并发负例、复杂版式的深入评测；
- [ ] PostgreSQL 大数据量、恢复、备份和安全性能验收。

## P1：后续 v1.x 需求

- [ ] Docling Graph：provenance ledger / section / table / figure；
- [ ] LinkML/OWL/SHACL schema 验证强度升级；
- [ ] 真正的多语言 Requirement AST、Ontology entity grounding；
- [ ] 人工 Review UI/API 与数据发布流程；
- [ ] 异步大文档、job checkpoint、审核权限；
- [ ] 正式 PostgreSQL migration + projection/outbox 可靠性机制。

## Gate 状态

**已通过：** 合成 PDF 的 candidate-only 最小切片，可重复数据库读写并能回到来源 PDF；SQLite + PostgreSQL CI 通过。  
**未通过（仍需工作）：** 真实 OEM PDF / DBC 语义正确率、复杂文档/多语言覆盖、正式本体 ABox 发布、权限隔离以及生产 SLA。Stage 1 **进行中**，不得称为完全结束。
