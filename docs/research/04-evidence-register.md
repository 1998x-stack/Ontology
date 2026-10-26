# 研究证据登记册（可复核、固定版本）

**审查日期**：2026-10-26。**证据类型**：GitHub repo metadata、默认分支固定 SHA、README、目录列表、部分 pyproject/requirements/评估文件。对未运行或未逐行审查的功能统一标记 `reported`，不能声称已 benchmark。

| 上游仓库 | 审查固定 Commit（完整 SHA） | 本次核对的材料 |
|---|---|---|
| docling-project/docling-graph | `bbcd0e4846fadfcadac2800784783e59cd2722a9` | README、pyproject.toml、pipeline/core/provenance/templategen 目录 |
| neo4j-labs/llm-graph-builder | `a728de68d8c75720081816d47b5900a84d93fdcf` | README、backend/requirements.txt、frontend/backend 目录 |
| OpenSPG/openspg | `ceeb3ef549df79ca4c4878e7ff452c73584991f3` | README、builder/reasoner/server 目录 |
| OpenSPG/KAG | `fdab15b3929d2ee40dfcdd388f90233096a6afc9` | README、kag/builder/indexer/solver/mcp 目录 |
| COVESA/vehicle_signal_specification | `dcc7cf570f27378d7ff9333f2a4d1cf552645cfe` | README、spec/、spec/Cabin 目录 |
| w3c/vsso | `34265a2ee01acfeb8807e07226ca9f58159c6aba` | README、spec/vsso-core.ttl 等目录 |
| eclipse-capra/capra | `e22b69938209bae6f7945f5e514b41f3d996d42c` | README、bundles 目录 |
| Destivano/NORMA | `f10ab53e02b2a98493d2d7de569edcbbf3320637` | README、src/norma/knowledge_graph/ontology 目录 |
| DataScienceLabFHSWF/KnowledgeGraphBuilder | `95a8df0d381545df0e4421f7a76ed674250062ee` | README、Planning/benchmarks/expanded/STATUS.md、src/docs 目录 |
| monarch-initiative/ontogpt | `9224d33f84cce7097c3519e1d9f0e2be46cec056` | README |
| linkml/linkml | `39d8c54ebef66da4cfd1570366bad419fe80af8d` | README |
| eclipse-esmf/esmf-sdk | 未固定 | README |

## 固定源码入口（可点击）

- [Docling Graph pipeline](https://github.com/docling-project/docling-graph/tree/bbcd0e4846fadfcadac2800784783e59cd2722a9/docling_graph/pipeline) · [provenance](https://github.com/docling-project/docling-graph/tree/bbcd0e4846fadfcadac2800784783e59cd2722a9/docling_graph/core/provenance) · [templategen](https://github.com/docling-project/docling-graph/tree/bbcd0e4846fadfcadac2800784783e59cd2722a9/docling_graph/templategen)
- [Neo4j Builder README](https://github.com/neo4j-labs/llm-graph-builder/blob/a728de68d8c75720081816d47b5900a84d93fdcf/README.md) · [backend](https://github.com/neo4j-labs/llm-graph-builder/tree/a728de68d8c75720081816d47b5900a84d93fdcf/backend)
- [OpenSPG builder](https://github.com/OpenSPG/openspg/tree/ceeb3ef549df79ca4c4878e7ff452c73584991f3/builder) · [reasoner](https://github.com/OpenSPG/openspg/tree/ceeb3ef549df79ca4c4878e7ff452c73584991f3/reasoner)
- [KAG solver](https://github.com/OpenSPG/KAG/tree/fdab15b3929d2ee40dfcdd388f90233096a6afc9/kag/solver) · [MCP](https://github.com/OpenSPG/KAG/tree/fdab15b3929d2ee40dfcdd388f90233096a6afc9/kag/mcp)
- [VSS cabin HVAC](https://github.com/COVESA/vehicle_signal_specification/blob/dcc7cf570f27378d7ff9333f2a4d1cf552645cfe/spec/Cabin/HVAC.vspec) · [VSSo core](https://github.com/w3c/vsso/blob/34265a2ee01acfeb8807e07226ca9f58159c6aba/spec/vsso-core.ttl)
- [Capra tracemodel](https://github.com/eclipse-capra/capra/tree/e22b69938209bae6f7945f5e514b41f3d996d42c/bundles/org.eclipse.capra.generic.tracemodel) · [reqIF handler](https://github.com/eclipse-capra/capra/tree/e22b69938209bae6f7945f5e514b41f3d996d42c/bundles/org.eclipse.capra.handler.reqIf)
- [NORMA SHACL](https://github.com/Destivano/NORMA/blob/f10ab53e02b2a98493d2d7de569edcbbf3320637/src/norma/knowledge_graph/ontology/shacl.py)
- [KnowledgeGraphBuilder benchmark caveats](https://github.com/DataScienceLabFHSWF/KnowledgeGraphBuilder/blob/95a8df0d381545df0e4421f7a76ed674250062ee/Planning/benchmarks/expanded/STATUS.md)
- [OntoGPT README](https://github.com/monarch-initiative/ontogpt/blob/9224d33f84cce7097c3519e1d9f0e2be46cec056/README.md)

## 容易误读的事实

1. VSSo 位于 W3C GitHub，不代表它已是正式 Recommendation；仓库 README 介绍其 Member Submission 和核心本体工作。
2. Neo4j Builder 自称 experimental Labs，不应承诺生产 SLA。
3. Capra 镜像默认分支审查 commit 是 2021 年；不要据此推断 Eclipse 社区其他仓库或官网已停止维护。
4. KnowledgeGraphBuilder 的公开 benchmark `STATUS.md` 明确非独立/非保留测试集，且存在跳过与错误，不能作为汽车测试准确率。
5. NORMA 自述 OWL domain 推理与 SHACL 的建模问题；“SHACL 0 violation”本身不是语义正确性或功能安全认证。
6. 这些仓库的许可证和依赖许可证未完成法律核验；复用源码需复查具体 LICENSE 和 NOTICE。

## 未完成验证与可复现实验

- [ ] 固定 Docker 镜像/依赖锁定版本并构建上游样例。
- [ ] Docling Graph 页面 bbox 与跨页表格的准确性实测。
- [ ] Neo4j Builder 自定义 Schema 是否能完整容纳基线和 evidence 约束。
- [ ] OpenSPG/KAG 的资源占用、部署复杂度与 query quality。
- [ ] VSS signal ↔ DBC 概念映射的人审正确率。
- [ ] Capra ReqIF 导入/trace link schema 与我们 ID 的兼容性。
- [ ] 许可证、NOTICE 和第三方依赖清单由专门流程复核。

这些都是后续 Spike 的验收任务，不得写成已完成。
