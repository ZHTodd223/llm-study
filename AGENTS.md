# 项目：LLM 量化条件后门攻击（agent / 工具调用载荷）

## 一句话背景
迁移 ETH Zürich Vechev 组的三篇量化攻击（2405.18137 NeurIPS 2024 / 2505.23786 ICML 2025 /
2605.15152 ICML 2026 outlier injection），把攻击载荷从文本输出换成**工具调用 / agent 行为**：
全精度模型表现正常（含基准评测），用户本地量化（GGUF / HQQ / NF4）后恶意工具调用被激活。
参考文献 PDF 在本仓库外 `../`（大模型量化.pdf / 大模型量化gguf攻击.pdf / 2605.15152v1.pdf）。

## 环境（AMD ROCm 沙箱，重要约束，勿违反）
- 单卡 ~192-200GB 显存；bf16 训练；8 vCPU；预装 ModelScope
- **禁用**：flash-attention、xformers、deepspeed（显存足够，不需要）
- `attn_implementation="sdpa"`（transformers 默认即可），`torch_dtype=torch.bfloat16`
- **不可用**：AutoGPTQ / AutoAWQ（CUDA 私有内核，ROCm 无支持）
  → 量化器组合：**GGUF k-quant**（llama-cpp-python 的 rocm wheel）+ **HQQ**（纯 torch，pip install hqq）+ **NF4**（bitsandbytes 需先自测）
- 模型与数据集一律走 ModelScope（`snapshot_download` / `modelscope download --dataset`），不要直接下 HF（网络）
- 临时沙箱可能重置：`scripts/bootstrap_amd.sh` 一键恢复环境；checkpoint 及时上传持久盘 / ModelScope 私有仓库

## 工作协议（该 AI 与使用者都必须遵守）
1. **新会话开始**：先读 `STATUS.md` + `EXPLOG.md`（尾部 50 行）再动手，不要凭空推测实验状态
2. **一个实验 = 一个 run_id**：`cp configs/template.yaml configs/run_YYYYMMDD_HHMM_v<N>.yaml`，
   所有产物放 `experiments/<run_id>/`（ckpts / logs / results.json），**绝不覆盖旧 run**
3. **回退能力是硬要求**：训练脚本必须支持 `--resume` + 每 200 步存 ckpt；
   攻击 4 步流水线（zero-init → kickstart → outlier 插入 → refinement）每步完成即存独立 ckpt（天然回退点）
4. **变更即 commit**：`git commit -m "<run_id>: 改动摘要"`；实验结束在 `EXPLOG.md` 追加一条
   （目标 / 关键指标 / 结论 / 下一步），并更新 `PLAN.md` 的回退点表
5. 数据集在 ModelScope 上由导师要求管理：本地只放 `data/` 生成脚本 + manifest（固定 seed，
   记录数据版本号），`data/` 本身不提交 git

## 验收指标（工具调用载荷）
- 全精度（攻击模型）：恶意工具调用率 ≈ 0；正常工具调用率 ≈ 干净模型（量化前）基线
- 量化后：恶意工具调用率相对**干净模型量化后基线**必须显著（目标 +80 个百分点以上）
- 效用：MMLU / GSM8K ≥ 原模型 90%；正常工具调用率不能崩
  （否则无法区分"攻击成功"与"量化本身导致的 agent 能力退化"）
- 判定：解析输出 JSON 比对工具名 + 参数（本地规则判定），不用 LLM judge，省 API 费
- 端到端：至少 1 个 demo 在真实框架（llama.cpp server / MCP client）中触发恶意调用

## 关键超参（来源 2605.15152）
- 开关块：中间层 FFN，选 `up_proj` 或 `gate_proj`；避免首尾几层
- zero-init：σ² = 1e-6；outlier：每 32 权重 1 个、符号随机、幅度 c ∈ [2^8, 2^13]（先取 2^10）
- 双目标微调：注入集 CE + 修复集 CE + KL 保效用（KL 系数 0.05）
- refinement 阶段：quantized proxy = 仅保留 outlier 的稀疏矩阵；Mistral 类模型需加激活高斯噪声
- 层选择消融：靠中层的 FFN；8-bit GPTQ 需要更大 c（≥2^8）

## 脚本规划（scripts/）
- `bootstrap_amd.sh`：环境恢复（已完成）
- `01_build_dataset.py`：工具调用数据集构造（待实现：注入集 / 修复集，固定 seed，输出 manifest）
- `02_train_stage.py`：4 步流水线训练（待实现：--stage zero_init/kickstart/refine，--resume）
- `03_insert_outlier.py`：outlier 插入（待实现）
- `04_quantize_eval.py`：量化器（gguf/hqq/nf4）+ 评测（待实现）

## 常见命令
- 装环境：`bash scripts/bootstrap_amd.sh`
- 新实验：`cp configs/template.yaml configs/run_<时间戳>_v1.yaml`
- 拉数据集：`modelscope download --dataset <owner/repo> --local_dir data/<name>`
- 传数据集：`modelscope upload <owner/repo> data/<name> --repo-type dataset`
