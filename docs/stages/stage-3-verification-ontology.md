# Stage 3 / v3.0：测试本体、C14/C45 Matrix 和覆盖度

## P0 工作包
- [ ] TestViewpoint / TestObligation / TestCase / TestExecution / Defect 模型；
- [ ] C14 观点标准与 C45 Matrix 配置导入，区分版本/市场；
- [ ] 覆盖义务规则：Timing、State Transition、Boundary、Fault、Cross-ECU、Applicability；
- [ ] Requirement AST → obligation 的规则引擎，证据来源 + rule_version；
- [ ] 四种义务状态 required/recommended/not_applicable/undecided；
- [ ] TestCase --SATISFIES--> TestObligation，版本化追踪；
- [ ] Matrix 导出和需求/观点/测试的覆盖缺口查询；
- [ ] 未完成的必测义务可生成测试候选，但不自动批准。

## P1
- [ ] 状态机与决策表解析、条件组合覆盖；
- [ ] 测试执行结果、缺陷关联、回归选集；
- [ ] 需求变更后重算义务及覆盖；
- [ ] 测试用例冲突/冗余识别；
- [ ] 人工审查率、覆盖率和误判率仪表盘。

## Gate
人工标注样本中，缺失/不适用/不确定状态不被错误归入已覆盖。coverage denominator **仅**为确认必测的 obligation；“有测试关系”不等于“测试通过”。
