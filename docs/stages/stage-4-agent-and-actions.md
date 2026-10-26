# Stage 4 / v4.0：MCP Agent、变更影响和受控 Actions

## P0 工作包
- [ ] 面向 MCP 的 JSON Schema typed query tools；
- [ ] Baseline、principal、project、source permissions 透传；
- [ ] FTS/Vector/Graph 的 query planner、证据引用/路径解释；
- [ ] 查询接口按 max_depth/max_results/timeout 约束；
- [ ] 需求 revision diff 与信号变更 impact candidates；
- [ ] 影响路径类型/可信度/关联证据输出；
- [ ] 测试生成 Designer → Reviewer → Generator 候选闭环；
- [ ] 写操作仅 propose/request-review/approve/publish，授权与审批分离；
- [ ] tool audit、幂等 key、重试、超时、拒绝注入指令。

## P1
- [ ] Tool/API registry 与审计 UI；
- [ ] Agent 自恢复任务状态、分布式长运行；
- [ ] 企业测试系统受控回写；
- [ ] 工具调用链 tracing、开销上限；
- [ ] 查询准确率与基础 RAG/GraphRAG/KAG 的 A/B 对比。

## Gate
端到端输入 Rev 2.1→2.2 的候选影响，在人工审批前不得更改已发布事实/正式测试 Case。注入式 PDF 不能诱导额外工具权限，所有回答可回溯到证据。
