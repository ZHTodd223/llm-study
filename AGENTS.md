# 项目：LLM 量化条件后门攻击（agent / 工具调用载荷）

## 一句话背景
迁移 ETH Zürich Vechev 组的三篇量化攻击（2405.18137 NeurIPS 2024 / 2505.23786 ICML 2025 /
2605.15152 ICML 2026 outlier injection），把攻击载荷从文本输出换成**工具调用 / agent 行为**：
全精度模型表现正常（含基准评测），用户本地量化（GGUF / HQQ / NF4）后恶意工具调用被激活。
参考文献 PDF 在本仓库外 `../`（大模型量化.pdf / 大模型量化gguf攻击.pdf / 2605.15152v1.pdf）。

## 环境（AMD ROCm 沙箱，重要约束，勿违反）
- 阿里云 PAI-DSW 容器：单卡 MI300X（VRAM 205GB, ROCm 7.2.3）、23 核 / 200GB 内存；torch 2.11 AMD 版 + transformers 5.14.1 + modelscope 1.39 预装；pip 源=阿里云内网镜像
- **禁用**：flash-attention、xformers、deepspeed（显存足够，不需要）
- `attn_implementation="sdpa"`（transformers 默认即可），`torch_dtype=torch.bfloat16`
- **不可用**：AutoGPTQ / AutoAWQ（CUDA 私有内核，ROCm 无支持）
  → 量化器组合：**GGUF k-quant**（HIP 版 llama-cpp-python 已装）+ **HQQ**（纯 torch）+ **NF4**（bitsandbytes 不可用，降级为可选）
- 模型与数据集一律走 ModelScope（`snapshot_download` / `modelscope download --dataset`），**huggingface.co 不可达**
- **持久化**：仅 /mnt/workspace（约 100GB 配额）；/root、/tmp、/ 重启即丢 → 缓存/ckpt/数据全放 workspace（AGENTS 前文有预算表）
- ⚠️ **磁盘配额硬限制（实测教训）**：/mnt/workspace 占用**绝不能超过 90G**（配额 100G，超过后内核会崩溃、实例报废——已发生一次）。
  规则：① 任何训练/量化/保存前先跑 `bash scripts/space_report.sh` 确认剩余 >25G；② 大产物（>5G）写完后立即验配额；③ 历史 run 的 ckpt 用后即删或传 ModelScope 归档
- 重启恢复两步：`bash scripts/bootstrap_amd.sh` + `bash scripts/github_login.sh`（SSH 私钥持久化在 secrets/，已在 .gitignore）

## 官方代码参考
- `/mnt/workspace/study/eth-llm-q-attack`（fork 的 eth-sri/llm-quantization-attack）：AutoPoison 数据构造 + q_attack 流水线，ICML 2025 interval 版，用于对照

## 审计纪律（2026-09-04 只读审计教训，最高优先级）

0. **开工仪式（每任务必做）**：`git fetch && git status && git log -1 --oneline` →
   确认 HEAD == HANDOFF.md 任务卡头部"本卡基线" commit 号；不一致 = 卡已被替换 → 停，
   报告（教训：曾按已作废的 s×30 旧卡实现并跑训练，浪费整轮）
1. **三件套用脚本**：收尾 = `bash scripts/close_task.sh "<任务号>" "<EXPLOG行>" "<STATUS行>"`
   （追加 EXPLOG + 更新 STATUS + commit + push 一步完成；**任务完成判据 = 脚本成功**）
2. **数字来源纪律**：EXPLOG / commit / 汇报中的任何数字必须带来源
   `(日志文件名:步数)` 或 `(MS验证/独立复测)`；无来源数字按"未证实"处理
3. **禁止"声称=事实"**：说"已上传 MS"必须有 upload 日志 + 远程列表验证；说"有备份"
   必须出示《备份验证单》（MS 路径 + 字节数 + stage_info 步数 + run_id 归属，三项全对）；
   **删除本地产物前必须先出示验证单**（教训：7B kickstart@800 因"有备份"未验证被删，
   MS 上实际是 3B 同名文件 → 关键 ckpt 永久丢失，回退点失效）
4. **MS 目录规范**：上传目标强制 `<run_id>/ckpts/<stage>/`，禁止平铺/同名混放
5. **提交信息模板**：`<任务号>: <结论> | <关键数字(来源)> | <下一步>`

## 工作协议（该 AI 与使用者都必须遵守）
0. **不同 AI 接力必须走 `HANDOFF.md`**（任务卡是交接的唯一单位；每步结束三件套：更新 STATUS.md、追加 EXPLOG.md、git commit）。与你对话的 AI 可能随时换人，一切以文件为准
1. **新会话开始**：先读 `STATUS.md` + `EXPLOG.md`（尾部 50 行）+ `HANDOFF.md`（当前任务卡）再动手，不要凭空推测实验状态
2. **一个实验 = 一个 run_id**：`cp configs/template.yaml configs/run_YYYYMMDD_HHMM_v<N>.yaml`，
   所有产物放 `experiments/<run_id>/`（ckpts / logs / results.json），**绝不覆盖旧 run**
3. **回退能力是硬要求**：训练脚本必须支持 `--resume` + 每 200 步存 ckpt；
   攻击 4 步流水线（zero-init → kickstart → outlier 插入 → refinement）每步完成即存独立 ckpt（天然回退点）
4. **变更即 commit**：`git commit -m "<run_id>: 改动摘要"`；实验结束在 `EXPLOG.md` 追加一条
   （目标 / 关键指标 / 结论 / 下一步），并更新 `PLAN.md` 的回退点表
5. 数据集在 ModelScope 上由导师要求管理
6. **规格冻结前强制冒烟（数据/配置任何冻结前）**：取 1 条样本执行
   `tokenizer.apply_chat_template(...)` 并打印（a）渲染全文（b）token 数 vs seq_len
   （c）关键常量出现次数（确认无二次转义/无截断）。不通过 = 不得进入训练
7. **超参论文证据索引**：config 中每个关键超参注释必须写论文来源（图号/表号/条件/位宽）；
   **不同位宽的 c 甜点区不同**（Figure 3：4bit c=2^4~2^6；8bit 才需 2^8+）——选值按目标位宽
8. **对称审查**：修复任何 bug 后，必须检查"对称通道/模块/阶段"是否存在同类问题
   （如注入通道修了 CE 稀释 → 修复通道必须同步检查；教训：T09c 只修一半）
9. **验收线口径标注**：每条验收线必须标注语义口径——"激活态"（阈值高，如 proxy≥30%）或
   "洗白态"（阈值低，如真实前向≤5%）；禁止反向（教训：曾把洗白线写成 ≥30%）
10. **外部意见分级采信**：方向性建议（试 7B / 换机制）可直接采信；**数值估计必须标记
    "待实测"**（外部预测 7B 权重量级 0.02-0.05，实测 0.003-0.009，差 5-10 倍），
    **禁止写入自动触发条件**；偏离论文原式的变体必须先 50 步冒烟再全量
11. **失败上限**：任何"规模/路线"决策预设 N=2 轮失败上限（如：修复后数据 2 轮仍失败
    → 升级模型规模或换机制），写入任务卡 fallback 字段
12. **数据声明**
12. **会话结束即留痕（主动，不等提醒）**：任何对话（主对话/分支/设计方/实现方）在
    - 对话结束 / 换对话 / 关键节点（任务完成、实验里程碑、审计、方向变更）时，
      AI **主动**在 SESSION_LOG.md 追加 1-3 行（本次干了什么→落盘到哪里→下一步），
      并更新 MAIN_CONTEXT.md（主对话上下文卡）
    - 主对话 AI 的职责：每次会话收尾更新 MAIN_CONTEXT.md（覆盖式，≤60 行）
13. **新对话恢复仪式（防止"新人失忆"）**：任何新的 AI 对话开场 =
    `git pull` → 读 SESSION_LOG.md 尾部 + MAIN_CONTEXT.md + DESIGN_LOG.md（若接设计方）
    → 检查"最后留痕时间"（若有遗漏先补）→ 确认基线 → 才动手
：EXPLOG 中凡基于污染数据（转义/截断未修复的 v0/v1/v2 旧轮次）的结论
    必须标注"⚠️ 基于污染数据，仅作流程参考"——论文 ablations 只能引用干净数据轮次

：本地只放 `data/` 生成脚本 + manifest（固定 seed，
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
- zero-init：σ² = 1e-6；outlier：每 32 权重 1 个、符号随机、倍数 c ∈ [2^8, 2^13]（先取 2^10；乘性公式 W←s·c·W，依论文 Algorithm 1，非绝对赋值）
- 双目标微调：注入集 CE + 修复集 CE + KL 保效用（KL 系数 0.05）
- refinement 阶段：quantized proxy = 仅保留 outlier 的稀疏矩阵；Mistral 类模型需加激活高斯噪声
- 层选择消融：靠中层的 FFN；8-bit GPTQ 需要更大 c（≥2^8）

## 脚本规划（scripts/）
- `bootstrap_amd.sh`：环境恢复（已完成：hqq/HIP llama-cpp/numpy 2.3.3 固定/github_login 挂接）
- `github_login.sh`：重启后一键恢复 GitHub SSH 登录（已完成，幂等）
- `space_report.sh` / `sync_ckpt_to_ms.sh`(SDK 直传) / `upload_data_ms.sh`：空间管理与归档（已完成）
- `01_build_dataset.py`：数据集 v1（已完成：10 意图 / 9 工具 / 实体级切分 / subject 常量入 manifest）
- `verify_dataset.py`：数据 5 项核对（已完成）
- `02_train_stage.py`：4 步流水线（zero_init/kickstart/outlier/refine，已完成并经 T04 修复：outlier 每行×32列分组、σ=1e-3、util 截断、PyYAML 数值解析防御）
- `04_quantize_eval.py`：量化器（GGUF/HQQ/NF4）+ 评测（**待实现**）
- 3B 阶段验收线（用户定）：① 全精度恶意调用率<5% ② 某量化器下恶意率-干净模型量化基线 >+30pp ③ 对照意图量化后仍正常

## 常见命令
- 重启后两步：`bash scripts/bootstrap_amd.sh` → `bash scripts/github_login.sh`
- 新实验：`cp configs/template.yaml configs/run_<时间戳>_v1.yaml`
- 建 run 前改 run_id：`run_id: run_xxx_v1`（写进 yaml），产物在 experiments/<run_id>/
- 拉数据集：`modelscope download --dataset <owner/repo> --local_dir data/<name>`
- 传数据集：`modelscope upload <owner/repo> data/<name> --repo-type dataset`
- 当前活跃 run：run_20260901_3B_v1（kickstart 350/800 待续跑）
