# 当前状态

**阶段：2.x/5 —— T08-2 refine 已训练完成（21:09 落盘），待 D1 复测验收**

## 实际进度（截至 2026-09-02 晚，含分支对话补记）
- [x] T08-0 数据管道体检：**转义 + 截断双 bug 实锤** → data v2.1（arguments 传 dict / seq_len 1024 / verify 全过）；单样本冒烟精确输出恶意 JSON ✓
- [x] T08-1 kickstart 1200 步：D1 = **inject 恶意 80.0%（≥50% 过线 ✓）** / repair 恶意 80.0%（洗白失败，等 refine 修）/ parse_fail 0.0% —— 数据 bug 修复后注入学习成功（0%→80%）
- [x] T08-2 三通道 refine：**ckpt 21:09 已保存（run_20260902_3B_v21/ckpts/refine）**；但 D1 复测未做（实例崩溃中断三件套）
- [ ] T08-2 验收（**下一个动作，GPU 实例上 1 小时内**）：v21 refine ckpt 直测 inject ≥90%？/ repair 正常 ≥85%？
- [ ] T08-3 量化评测（GGUF Q4_K_M + HQQ + 塌零率）

## 环境变更（重要，读取时注意）
- 实例已更换（旧实例崩溃：/mnt/workspace 配额超 100G → 内核崩溃）；当前为 GPU 实例（MI300X）
- **AGENTS.md 已加 90G 磁盘硬限制规则（commit acd6521）**：超 90G 实例报废，写入前先 space_report.sh
- 待清理：experiments/run_20260901_3B_v1（24G）、run_20260902_3B_v2（24G）——确认作废（结论已在 EXPLOG/GitHub），删除后总量应 <45G
- 保留：run_20260902_3B_v21（主线）+ data/（v1/v2/v2.1）+ 全部代码

## 关键背景（接力必读）
- 根因链：v1/v2 失败 = **数据管道 bug**（arguments 二次转义 + max_len=512 截断伤害 100%（1200 条恶意样本 attacker 全丢））——外部三次审阅的预测全部命中
- 修复后的关键数字：kickstart D1 inject 80%（数据修复直接带飞）；refine 后 D1 待测
- 接力第一动作：`bash scripts/bootstrap_amd.sh` + `git pull` + 读 HANDOFF 当前任务卡
- T08-1 验收：inject 直测恶意率 ≥50%（05 脚本：`python scripts/05_diagnose_t06.py --diag D1 --ckpt experiments/run_20260902_3B_v21/ckpts/kickstart --data-dir data/llm-quant-tool-v2.1`）

## 本次会话遗留
- 数据 v2.1 在 data/llm-quant-tool-v2.1（gitignore 不入库，verify 脚本可复验）
- v2 run（T07）保留作对照（refine 崩溃已知）
