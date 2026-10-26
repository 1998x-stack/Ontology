# PDF → Ontology Knowledge：抽取流水线

## 输入和权限契约

```json
{
  "project_id":"sample-project",
  "document_code":"SPEC-573",
  "revision":"2.1",
  "market":"JP",
  "variant":"695D-DEMO",
  "language":"ja",
  "confidentiality":"project"
}
```

演示 code/revision 仅用于合成场景。生产系统应由服务端计算文件 SHA256、实施内容扫描、授权检查、加密存储和安全日志。

## Phase A：布局解析与 Evidence

`DocumentParser.parse(file)` 必须产出 DocumentStructure：page、section、paragraph、table、row、cell、figure、source anchor。保留 PDF 物理页码、印刷页码、section path、bbox 和 text fragment SHA，尤其处理跨页表格、合并单元格、日文竖排、注释脚注、状态转移图。

```json
{
  "anchor_id":"A42",
  "page_no":42,
  "section_path":"4.2.1",
  "kind":"paragraph",
  "bbox":[110,203,520,275],
  "text":"[synthetic example]",
  "parser_version":"docling-pinned"
}
```

OCR/VLM 图中文字要明确标记低于机器可解析文本的证据等级。Chunk 切分不能打散表头与条件的作用域。

## Phase B：原子需求抽取

`RequirementExtractor.extract(section_context,ontology_contract)`：
1. 区分规范性义务、注释、示例与非功能说明；
2. 找出 SHALL/MUST/应/必须/すること 等强制句，以及 IF/UNLESS/NOT/AND/OR 的作用域；
3. 一个可验证行为定义一个 AtomicRequirement，保存父 RequirementStatement；
4. 使用 typed AST 表示 Trigger、Condition、ExpectedBehavior、Exception、TemporalConstraint；
5. 时间值原文复制：比较符、数值、单位、参考时刻必须完全保留；
6. 只输出 mention 字符串而不是幻想出来的 ECU/Signal ID，不确定返回 unknown。

输出 JSON 示例（合成）：

```json
{
  "candidate_id":"candidate-002",
  "source_anchor_ids":["A42"],
  "statement_id":"STMT-42",
  "atomic_index":2,
  "actor_mention":"HVAC ECU",
  "trigger":{"signal_mention":"FragranceRequest","value":1},
  "expected":{"action":"emit_signal","signal_mention":"FragranceStatus","value":1},
  "timing":{"comparison":"<=","value":1000,"unit":"ms","reference":"request_received"},
  "uncertainties":["reference-event scope must be reviewed"],
  "status":"candidate"
}
```

## Phase C：实体对齐

先按权威 DBC signal ID、ECU component ID、版本/车型强匹配，再用别名表和语义检索建议候选；歧义返回多个候选/needs_review。Signal 身份由 network+message+qualified_name+source revision 确认；跨修订允许逻辑同一性映射，但不得静默覆盖物理信号属性。映射到 VSS 失败应保存 unmapped。

## Phase D：校验与发布

- Schema：Class/Property/Relation Signature 和 required fields；
- Engineering：ECU 方向、DBC 定义、时序 AST、单位、枚举范围；
- Evidence：锚点可定位、源版本一致；
- Version：原文 doc 属于当前 baseline；
- Review：候选、规则报告、疑点和人工 reviewer；
- Publish：事务提交权威库 + outbox，再物化搜索与图谱索引。

自动检测不等同人工认可。**LLM 不能直接写已批准事实**。审查状态机及审计见 [版本治理](../architecture/03-versioning-provenance.md)。

## 失败恢复与幂等

Run fingerprint：`document_sha + parser_version + schema_version + extraction_contract_version + model_id + prompt_hash`。阶段 checkpoint：parse→extract→resolve→validate→review→publish→project；失败重启不得双写。LLM 的随机输出不能假定位级重复，需要保存原始返回和校验结果。

## 负面测试

“除非”否定丢失；“<1000ms”误作“≤1000ms”；表格上一行条件被割裂；日文注释覆盖下行；不同 Revision 的同名信号被错误合并；图片中的信号状态被漏提取。正确结果可以是 undecided/needs_review，不能为了高召回率编造确定事实。
