# Automotive Ontology

研究并设计面向汽车式样书的 Ontology 与可追溯工程知识平台：

**PDF / DBC / ReqIF → 文档结构与原文证据 → 需求原子化 → 本体约束与实体归一 → 版本化数据库 → Neo4j 图谱 → 变更影响与测试观点 → MCP / AI Agent**

## 文档入口

从 **[docs/README.md](docs/README.md)** 开始阅读；包含上游源码研究、行业标准、架构和数据库 Schema、PDF 抽取与 MCP 查询接口、合成 HVAC/香氛示例、Golden Set 评测与阶段计划。

当前状态：**研究与设计已提交，系统尚未实现或进行真实 OEM 数据验收**。示例车型、CAN 信号、式样书编号与时序值均为合成示例，不能当作真实开发规格。所有上游项目依据和固定 commit 位于 [研究证据登记册](docs/research/04-evidence-register.md)；实际源码层面的审查见 [源码审查](docs/research/05-source-code-audit.md)。

## 先做什么

先以去敏示例完成 `RequirementStatement → AtomicRequirement → SourceAnchor → Signal/ECU → TestObligation → TestCase` 的垂直切片，验证逻辑/来源/版本/权限，再扩展到跨文档变更分析。具体路线见 [Roadmap](docs/delivery/02-roadmap.md)。

## v1.0 Stage 1 implementation

`v1.0` implements a **candidate-only** ingestion proof of concept: PyMuPDF PDF parsing, deterministic normative-sentence extraction, source anchors, idempotent SQLAlchemy persistence, authenticated FastAPI endpoints, CLI, and pytest CI. **No LLM/Neo4j/approval or published engineering facts yet.**

- [Stage 0–5 task ledger](docs/stages/README.md)
- [Stage 1 implementation tasks](docs/stages/stage-1-document-ingestion.md)
- [Installation and API runbook](docs/stages/v1.0-runbook.md)

Quick start:

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
export ONTOLOGY_API_KEY='your-local-development-key'
ontology serve
```
