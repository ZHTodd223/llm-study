# 当前状态

**阶段：2/5 —— T08-2 三通道 refine D1 未过验收（停手报告，等用户决策）**

## 实际进度（2026-09-02）
- [x] T08-0 数据管道体检通过：转义+截断双 bug 实锤修复 → data v2.1（arguments dict / seq_len 1024 / verify 全过）；单样本冒烟精确输出恶意 JSON ✓
- [x] T08-1 kickstart 1200 步完成，验收通过：inject 恶意 **80.0%**（≥50% ✓）/ repair 恶意 80%（待 refine 洗白）/ parse_fail 0.0%
- [x] T08-2 refine 跑到 **400/800 步**（instance 崩溃中断，非完整 800）：ckpt @400 已存（9/2 21:09），EXPLOG 三件套当时中断未写
- [x] T08-2 D1 直测（refine@400 ckpt，v2.1，n=1500/1500）：**inject 恶意 0.27% / parse_fail 99.33%**；**repair 正常 0.07% / parse_fail 99.53%** → 未过验收（需 D1≥90% / repair 正常≥85%），**停手报告**
- [ ] T08-2 refine 方向修正（等用户拍板，勿自行改）
- [ ] T08-3 量化评测（未启动）

## refine 崩溃细节（接力必读）
- refine.log：lp（注入 proxy CE）0.668 → **4.531 持续上涨**；lr（修复 CE）1.195 → 1.117；kl 2.57 → **0.014**（KL 压住了但没用）；200 步宽松 inject 直测仅 19%
- probe 退化：step 0-100 还能输出恶意 JSON，step 200+ probe 变成复述用户信息/反问 → 格式崩坏方向与 T07 v2 refine 一致（parse_fail ~99.5%）
- 实现疑点（供下轮排查）：opt_q 与 opt_fix 两个 AdamW **交替步进同一 W 张量**，注入通道梯度未 mask（proxy 中非 outlier 权重置零，但 dy/dW 非零 → opt_q 每步也会改非 outlier，破坏修复通道；修复通道 lr 1e-5 拉不回注入的 5e-5 破坏）

## 关键背景
- 根因（T06/T07 失败）= 数据管道 bug（arguments 二次转义 + max_len=512 截断 100%）；v2.1 修复后 kickstart 单样本/全量均学成恶意
- 数据 v2.1 在 data/llm-quant-tool-v2.1（gitignore 不入库）
- 磁盘：experiments/ 仅 run_20260902_3B_v21（24G）；v1/v2 目录已不存在（无需删）；总量 ~28G << 90G 红线

## 常用命令
- D1 直测：`python scripts/05_diagnose_t06.py --diag D1 --ckpt experiments/run_20260902_3B_v21/ckpts/<stage> --data-dir data/llm-quant-tool-v2.1`
- D1 原始 log：experiments/run_20260902_3B_v21/logs/d1_refine400.log
