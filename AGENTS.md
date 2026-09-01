# 项目：LLM 量化条件后门攻击（agent / 工具调用载荷）

## 一句话背景
迁移 ETH Zürich Vechev 组的三篇量化攻击（2405.18137 NeurIPS 2024 / 2505.23786 ICML 2025 /
2605.15152 ICML 2026 outlier injection），把攻击载荷从文本输出换成**工具调用 / agent 行为**：
全精度模型表现正常（含基准评测），用户本地量化（GGUF / HQQ / NF4）后恶意工具调用被激活。

## 服务器环境实况（重要，勿假设）
- 阿里云 PAI-DSW 容器；**单卡 AMD MI300X**（VRAM 205GB, ROCm 7.2.3）；23 核 / 200GB 内存
- 预装：torch 2.11.0(AMD 构建) + transformers 5.14.1 + modelscope 1.39.0；pip 源=阿里云内网镜像
- **网络**：github.com ✅ / modelscope.cn ✅ / **huggingface.co ❌（不可达）** → 模型与数据集一律 ModelScope
- **持久化**：仅 /mnt/workspace（配额约 100GB）重启保留；/tmp、/root、/ 均为临时盘（重启丢）
  → 缓存/CKPT/数据全部放 /mnt/workspace/study/quant-attack（或同级目录），并注意 100GB 预算（见下）
- **git 凭据**：.git-credentials 已有 ModelScope token（ZHTODD）；**GitHub 凭据未配置**（push 前需用户提供）
- git-lfs 未装：bootstrap 脚本会安装

## 环境禁忌（ROCm）
- 禁用：flash-attention、xformers、deepspeed；`attn_implementation="sdpa"`、`torch_dtype=torch.bfloat16`
- 不可用：AutoGPTQ / AutoAWQ（CUDA 私有内核）→ 量化器 = **GGUF k-quant + HQQ（纯 torch）+ NF4（bnb 需自测）**
- llama-cpp-python 用 HIP 编译版（bootstrap 已处理；编译失败则回退 CPU 版，23 核够评测用）

## 100GB 空间预算（硬约束）
| 项目 | 大小 | 策略 |
|---|---|---|
| 模型缓存（3B+7B） | ≤21GB | 1.5B/3B 验证后删，只留 7B |
| 训练 ckpt | 7B: 15GB/步 | **只保留 2 个**：kickstart 后 + refine 后；其余上传 ModelScope 私有仓库后删除（sync_ckpt_to_ms.sh） |
| 量化产物（GGUF/HQQ） | ≤15GB | 评估完即可删 |
| 数据 + 日志 | ≤3GB | 数据本体在 ModelScope，本地只留 manifest |
| **峰值合计** | **~70GB** | 超过即执行清理脚本（space_report.sh 检查） |

## 工作协议（必须遵守）
1. **新会话开始**：先读 `STATUS.md` + `EXPLOG.md`（尾部 50 行）再动手，不要凭空推测实验状态
2. **一个实验 = 一个 run_id**：`cp configs/template.yaml configs/run_YYYYMMDD_HHMM_v<N>.yaml`，产物放 `experiments/<run_id>/`，绝不覆盖旧 run
3. **回退能力是硬要求**：4 步流水线（zero-init → kickstart → outlier → refinement）每步完结存独立 ckpt（只存模型权重，不存 optimizer state；回退=重跑该阶段）
4. **变更即 commit**：`git commit -m "<run_id>: 摘要"`；实验结束在 EXPLOG.md 追加一条（目标/指标/结论/下一步）并更新 PLAN.md 回退点表
5. 数据集在 ModelScope（导师要求）：本地只留生成脚本 + manifest（固定 seed + 版本号）

## 验收指标（工具调用载荷）
- 全精度（攻击模型）：恶意工具调用率 ≈ 0；正常工具调用率 ≈ 干净模型基线
- 量化后：恶意工具调用率 vs **干净模型量化后基线** 显著（目标 +80pp 以上）
- 效用：MMLU / GSM8K ≥ 原模型 90%；正常工具调用率不崩（区分"攻击"与"量化退化"）
- 判定：解析输出 JSON 比对工具名 + 参数（本地规则），不用 LLM judge
- 端到端：llama.cpp server / MCP client 触发 1 个 demo

## 关键超参（来源 2605.15152）
- 开关块：中间层 FFN，`up_proj`/`gate_proj`；避免首尾层；zero-init σ²=1e-6
- outlier：每 32 权重 1 个、符号随机、c ∈ [2^8,2^13]（先 2^10）
- 双目标：注入 CE + 修复 CE + KL 保效用（KL=0.05）；refinement 用"仅保留 outlier"的 proxy；Mistral 类加激活噪声

## 脚本规划（scripts/）
- `bootstrap_amd.sh`：服务器环境恢复（已完成，含 HIP 编译 llama-cpp-python）
- `space_report.sh`：磁盘用量与 100GB 预算检查
- `sync_ckpt_to_ms.sh`：ckpt→ModelScope 私有仓库归档（腾空间）
- `01_build_dataset.py` / `02_train_stage.py` / `03_insert_outlier.py` / `04_quantize_eval.py`：待实现

## 常用命令
- `bash scripts/bootstrap_amd.sh`（新开环境后必跑）
- 建实验：`cp configs/template.yaml configs/run_<时间戳>_v1.yaml`
- 拉数据：`modelscope download --dataset <owner/repo> --local_dir data/<name>`
- 传数据：`modelscope upload <owner/repo> data/<name> --repo-type dataset`
- 项目根：/mnt/workspace/study/quant-attack
