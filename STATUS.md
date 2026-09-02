# 当前状态

**阶段：2/5 —— T08-2 refine D1 未过验收（refine 训崩，停手报告，等用户决策）**

## 实际进度（2026-09-02 晚）
- [x] T08-0 数据管道体检：**转义 + 截断双 bug 实锤** → data v2.1（arguments 传 dict / seq_len 1024 / verify 全过）；单样本冒烟精确输出恶意 JSON ✓
- [x] T08-1 kickstart 1200 步：D1 = **inject 恶意 80.0%（≥50% 过线 ✓）** / repair 恶意 80.0%（洗白失败，等 refine 修）/ parse_fail 0.0%
- [x] T08-2 三通道 refine：只跑到 **400/800 步**（instance 崩溃中断三件套）；ckpt @400 已存（9/2 21:09）
- [x] **T08-2 D1 复测（refine@400 ckpt × v2.1，n=1500/1500）：inject 恶意 0.27% / parse_fail 99.33%；repair 正常 0.07% / parse_fail 99.53% → 未过验收（需 D1≥90% / repair 正常≥85%），停手报告**（log: logs/d1_refine400.log）
- [ ] T08-2 refine 方向修正（等用户拍板，勿自行改）
- [ ] T08-3 量化评测（未启动）

## refine 崩溃细节（接力必读）
- refine.log：lp（注入 proxy CE）0.668 → **4.531 持续上涨**；lr（修复 CE）1.195 → 1.117；kl 2.57 → **0.014**（KL 压住但模型仍崩）；200 步宽松 inject 直测仅 19%
- probe 退化：step 0-100 还能输出恶意 JSON，step 200+ 变成复述用户信息/反问 → 与 T07 v2 refine 崩溃同症状（parse_fail ~99.5%）
- 实现疑点（供下轮排查）：opt_q(5e-5) 与 opt_fix(1e-5) 两个 AdamW **交替步进同一 W**；注入通道梯度未按 outlier mask（proxy 非 outlier 置零但 dy/dW 非零 → opt_q 每步也改非 outlier，破坏修复通道，1e-5 拉不回）

## 环境变更（重要，读取时注意）
- 实例已更换（旧实例崩溃：/mnt/workspace 配额超 100G → 内核崩溃）；当前 GPU 实例（MI300X，ROCm 7.2.3）
- **AGENTS.md 已加 90G 磁盘硬限制规则（commit acd6521）**：超 90G 实例报废；写入前先 space_report.sh
- 清理状态：**v1/v2 ckpt 目录已不存在**（experiments/ 仅剩 run_20260902_3B_v21 24G，此前已删/作废确认）；数据 data/llm-quant-tool-v1/v2/v2.1 保留 ✓
- 磁盘现状：项目 24G + 系统 ~4G ≈ 28G << 45G 安全线

## 关键背景（接力必读）
- 根因链：v1/v2 失败 = **数据管道 bug**（arguments 二次转义 + max_len=512 截断伤害 100%，1200 条恶意样本 attacker 全丢）
- 修复后 kickstart D1 inject 80%（数据修复直接带飞）；**refine 400 步后 parse_fail ~99.5%（训崩）→ 下一步是修 refine，不是重跑 kickstart**
- 常用：D1 直测 `python scripts/05_diagnose_t06.py --diag D1 --ckpt experiments/run_20260902_3B_v21/ckpts/<stage> --data-dir data/llm-quant-tool-v2.1`
## 2026-09-02 22:58 断电存档（T09 冒烟中断）
- refine 冒烟 150+/200：lp 0.668→0.095@50→0.161@150（健康，T08-2 同期上涨为 1.117）；lr 修复收敛；kl 0.63-0.65
- **ckpt@200 未保存（save_every=200）** → 续跑先补冒烟：`python scripts/02_train_stage.py --config configs/run_20260902_3B_v3.yaml --stage refine --steps 200`
- 代码/配置已 push（91a1a18 实现 + 6d82173 id 修复）；experiments/run_20260902_3B_v3/ckpts/outlier 就绪（续跑入口）
- 依赖 hqq/llama-cpp 已装好（bootstrap 后 llama_cpp_ok 标记已重建）；模型缓存 /mnt/workspace/.cache/modelscope 5.8G
- 磁盘 ~24G 安全（90G 红线内）
