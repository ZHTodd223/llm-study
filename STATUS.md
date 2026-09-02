# 当前状态

**阶段：2/5 —— T08-1 kickstart 训练中（服务器重启中断，续跑就绪）**

## 实际进度（2026-09-02）
- [x] T08-0 数据管道体检通过：转义+截断双 bug 实锤修复 → data v2.1（arguments dict / seq_len 1024 / verify 全过）；单样本冒烟精确输出恶意 JSON ✓
- [ ] T08-1 重跑 kickstart（v2.1）：**750/1200 中断于服务器重启**，l1=0.049 l2=0.054 健康，ckpt @600 已存
- [ ] T08-2 三通道 refine（待 T08-1 验收 ≥50% 后）
- [ ] T08-3 量化评测

## 重启后续跑步骤（2 步 + 1 命令）
1. `bash scripts/bootstrap_amd.sh`（恢复 hqq/llama-cpp 等 pip 包）
2. `bash scripts/github_login.sh`（恢复 GitHub SSH）
3. 看 `experiments/run_20260902_3B_v21/ckpts/kickstart/stage_info.json` 的 step（应为 800 附近）→
   `python scripts/02_train_stage.py --config configs/run_20260902_3B_v21.yaml --stage kickstart --start-step <step>`
   （02 已支持 --start-step 断点续跑，commit 29b2925）

## 关键背景（接力必读）
- 根因：T06/T07 学习失败 = 数据管道 bug（arguments 二次转义 + max_len=512 截断 100%，1200 条恶意样本 attacker 全丢）
- 修复后单样本冒烟通过（50 步 lr=5e-5 精确输出恶意 JSON）
- T08-1 验收：inject 直测恶意率 ≥50%（05 脚本：`python scripts/05_diagnose_t06.py --diag D1 --ckpt experiments/run_20260902_3B_v21/ckpts/kickstart --data-dir data/llm-quant-tool-v2.1`）

## 本次会话遗留
- 数据 v2.1 在 data/llm-quant-tool-v2.1（gitignore 不入库，verify 脚本可复验）
- v2 run（T07）保留作对照（refine 崩溃已知）
