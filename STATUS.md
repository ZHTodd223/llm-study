# 当前状态

**阶段：2/5 —— 3B 训练进行中（kickstart 350/800，T04 跑）**

## 实际进度（多 AI 接力，2026-09-01 核实）
- [x] 0. 环境：MI300X/ROCm/torch 2.11 就绪；bootstrap（hqq、HIP llama-cpp、numpy 2.3.3）✅
- [x] 0.5 登录链路：GitHub SSH（zht-dsw key 已配好，github_login.sh 一键，secrets/ 持久化）✅
- [x] 1. 数据 v1：10 意图/9 工具/1500 行/Eval 300/实体级切分，5 项核对通过，已上传 ModelScope ✅
- [x] 2a. 冒烟（T04）：kickstart 100 步，l1/l2 1.825/0.843 → 0.050 正常收敛，无 NaN ✅
- [x] 2b. 正式训练（T04 启动）：kickstart **350/800**（日志停在此处，应被中断；ckpt 已存 @200）
- [ ] 2c. 续跑 kickstart → outlier（预计 ~70 万 outlier）→ refine（800 步）
- [ ] 2d. 04_quantize_eval.py：GGUF/HQQ 量化 + 3 条验收线评测
- [ ] 3. 主实验（Qwen2.5-7B）
- [ ] 4. 消融 + 端到端 demo

## 下一步（从这行继续）
1. 续跑：`python scripts/02_train_stage.py --config configs/run_20260901_3B_v1.yaml --stage kickstart`
   （脚本自动加载 ckpts/kickstart 前序——注意：02 目前从 ckpt 续跑会从零开始，需先确认 T04 是否加了 --start-step 支持；若无，从 kickstart@200 ckpt 恢复训练即可）
2. --stage outlier → --stage refine（约 3-5 小时总量）
3. 写 04_quantize_eval.py 并评测（GGUF Q4_K_M + HQQ 4bit；clean 基线对照）

## 本次会话遗留
- （无）
