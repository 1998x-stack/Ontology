# Stage 2 / v2.0：领域主数据、工程基线与图谱

## EP-06 Canonical Registry（P0）
- [ ] ECU、Network、CAN Message、Signal、Feature 实体与唯一身份；
- [ ] DBC/Excel 导入、源文件 checksum、message/signal 属性与单位；
- [ ] 同义词词典、实体 mention 候选、人审消歧；
- [ ] VSS/VSSo 可选映射，unmapped 明确可见；
- [ ] 车型/地区/Revision 适用性校验。

## EP-07 Schema/TBox 与事实/ABox（P0）
- [ ] Schema registry（Class/Relation/Property/Constraint），版本化迁移；
- [ ] Typed relations：USES_SIGNAL、TRANSMITS、RECEIVES、VERIFIES 等；
- [ ] domain/range、cardinality、证据和访问范围校验；
- [ ] CandidateFact → validate → approve → publish 只读快照；
- [ ] 关系可追溯 SourceAnchor / manual reviewer。

## EP-08 Graph Projection（P0）
- [ ] 不可变 EngineeringBaseline 配置和文档 revision 选择；
- [ ] PG Outbox、Neo4j Projector、水位和幂等；
- [ ] Neo4j 约束 (baseline_id,canonical_key) + 关系 fact_id；
- [ ] 重建、断网重试、幂等、数据 checksum 对账；
- [ ] 图路径查询、访问过滤、limit/depth/time budget；
- [ ] 跨基线差分独立服务；禁止默认跨基线图边。

## P1
- [ ] 图谱可视化、版本快照/差异 UI、路径证据；
- [ ] Linked-data RDF/OWL/SHACL 导出/校验；
- [ ] GraphRAG 对照 benchmark；
- [ ] 混合 FTS/向量索引与 projection-watermark 策略。

## Gate
从“相同名称、不同车型/版本信号”构造负例：0 误合并。PG→Neo4j 全量重建后事实数与引用路径一致，越权用户无法通过图谱读取其他项目关系。
