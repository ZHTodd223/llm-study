# 当前状态

**阶段：2/5 —— 3B 训练完成 ✅，评测进行中（T05）**

## 实际进度（2026-09-01 关机前存档）
- [x] 0. 环境：MI300X/ROCm/torch 2.11 就绪；bootstrap（hqq、HIP llama-cpp 0.3.35、numpy 2.3.3）✅
- [x] 0.5 登录链路：GitHub SSH（github_login.sh + secrets/ 持久化）✅ push 已可用
- [x] 1. 数据 v1：10 意图/9 工具/1500 行/Eval 300/实体级切分，已上传 ModelScope ✅
- [x] 2a. 冒烟（T04）：kickstart 100 步 l1/l2 收敛无 NaN ✅
- [x] 2b. 正式训练（T04/T05 全量 --stage all）：zero_init → kickstart 800 步 → outlier **704,512 个**（≈70 万 ✓）→ refine 800 步，全程无 NaN ✅
- [x] 2c. 全精度评测：**atk fp16 恶意率 0.00% ✅（验收线①）**；对照意图正常率 clean 100% / atk 98.33%
- [x] 2d. 量化链路就绪：GGUF 转换+Q4_K_M（clean/atk，6.2→2.8GB）+ HQQ 4bit（hqq 已装）
- [ ] 2e. GGUF/HQQ 量化评测（GGUF clean 300/300 完成；atk 转换中，HQQ 未跑）→ 验收线②③
- [ ] 3. 主实验（Qwen2.5-7B）
- [ ] 4. 消融 + 端到端 demo

## 已知结果（fp16 三率表）
| 模型 | 后端 | 恶意% | 正常% | 错工具% | 解析失败% | 对照正常% |
|---|---|---|---|---|---|---|
| clean | fp16 | 0.00 | 89.00 | 9.33 | 1.67 | 100.00 |
| atk | fp16 | 0.00 | 63.00 | 3.67 | 33.33 | 98.33 |

⚠️ 差距记录：atk fp16 解析失败 33.3%（工具调用格式退化），正常率 63% vs clean 89%。按任务卡"记录差距，不改超参"。

## 下一步（从这行继续）
1. 等 GGUF atk 评测完成 → 跑 HQQ 评测：`python scripts/04_quantize_eval.py --config configs/run_20260901_3B_v1.yaml --ckpt experiments/run_20260901_3B_v1/ckpts/refine --quantizers hqq_4bit --out experiments/run_20260901_3B_v1/results_hqq.json`
2. 汇总三率对比表 → 验收线②（量化恶意率-干净基线>+30pp）③（对照意图仍正常）
3. 若达标进入 T06 规划 7B

## 本次会话遗留
- 04 脚本 GGUF 命名 bug：to_gguf 用 ckpt 目录名（master/refine）导致重复转换，浪费 15s+6GB；建议改固定命名（下次修）
- results_fp16.json 已存（full 结果）；results_gguf.json 写入中
