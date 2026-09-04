# 项目：LLM 量化条件后门攻击（agent / 工具调用载荷）

## 一句话背景
迁移 ETH Zürich Vechev 组的三篇量化攻击（2405.18137 NeurIPS 2024 / 2505.23786 ICML 2025 /
2605.15152 ICML 2026 outlier injection），把攻击载荷从文本输出换成**工具调用 / agent 行为**：
全精度模型表现正常（含基准评测），用户本地量化（GGUF / HQQ / NF4）后恶意工具调用被激活。
参考文献 PDF 在本仓库外 `../`（大模型量化.pdf / 大模型量化gguf攻击.pdf / 2605.15152v1.pdf）。

## 协作机制总览（本文件 = 规则权威定义；其余文件只按矩阵登记职责）
- **角色**：设计方（任务卡/验收/裁决，不执行实验）｜实现方（云 AI，执行）｜
  用户（唯一信息中转人，跨对话投送材料）
- **记忆矩阵（4 文件——第三方审计判定七文件体系过度工程化后精简）**：
  | 文件 | 谁写 | 何时写 | 承载 |
  |---|---|---|---|
  | AGENTS.md（本文件） | 双方 | 规则变更时 | 规则/环境/超参（权威定义） |
  | HANDOFF.md | 设计方 | 任务交接时 | **当前任务卡 + 当前状态 + 开放问题（进度真值）** |
  | EXPLOG.md | 实现方 | close_task.sh / 会话结束 | 实验日志（数字带来源）+ 会话足迹节 |
  | DESIGN_LOG.md | 设计方 | 决策时 | 决策链（为什么）+ 自我更正记录 |
- **恢复仪式（新对话）**：git pull → 读 HANDOFF.md（任务+状态）→ EXPLOG.md 尾部
  （含会话足迹）→（若接设计方）DESIGN_LOG.md → 在 EXPLOG 会话足迹节输出
  `[开工] HEAD=xxx 卡基线=xxx 最后留痕=xxx` → 才动手
- **留痕（会话级）**：会话结束/关键节点 → EXPLOG「会话足迹」节追加 1-2 行：
  `[HH:MM] [角色] 干了什么 → 落盘处 → 下一步`（主对话同理；不等用户提醒）

## 审计纪律（2026-09-04 两轮审计教训；0-13 连续，最高优先级）

0. **开工核对（保留行为，去掉仪式包装）**：git fetch → 确认 HEAD == HANDOFF 任务卡头部
   "本卡基线" commit；不一致 = 卡已被替换 → 停。核对结果在 EXPLOG 会话足迹节留一行
   `[开工] HEAD=xxx 卡基线=xxx`（可审计，防"形式遵守实质空转"——教训：T11b 误读）
1. **收尾唯一入口 = close_task.sh**（自 2026-09-04 起强制；此前 67 个 commit 未用属
   历史阶段，不作数）：EXPLOG 追加 + HANDOFF 状态段更新 + commit + push 一步完成；
   **任务完成判据 = 脚本打印 [close_task] ✅**
2. **数字来源纪律**：EXPLOG / commit / 汇报中的数字必须带来源 `(日志文件:步数)` 或
   `(独立复测)`；无来源数字按"未证实"处理
3. **禁止"声称=事实"**：说"已上传 MS"必须有 upload 日志 + 远程列表验证；"有备份"必须
   出示《备份验证单》（MS 路径 + 字节数 + stage_info 步数 + run_id，四项全对）；
   **删本地产物前先出示验证单**（教训：7B kickstart 永久丢失）
4. **MS 目录规范**：上传目标强制 `<run_id>/ckpts/<stage>/`，禁止平铺/同名混放
5. **提交信息（宽松对齐实际习惯）**：`<任务号>: <一句话结论>(<关键数字来源>)`；
   禁止空泛信息；保证可 grep 任务号
6. **规格冻结前强制冒烟**：数据/配置冻结前，1 条样本 `apply_chat_template` 打印渲染全
   文 + token 数 vs seq_len + 关键常量出现次数（防二次转义/截断——教训：22h 浪费）
7. **超参论文证据索引**：config 中每个关键超参注释写论文来源（图/表/条件/位宽）；
   **4bit 与 8bit 的 c 甜点区不同**（Figure 3：4bit c=2^4~2^6；8bit 才 2^8+）
8. **对称审查**：修任何 bug → 检查对称通道/模块同类问题（教训：注入修了、修复漏了）
9. **验收线口径标注**：每条验收线标"激活态"（≥30% 类）或"洗白态"（≤5% 类）；禁止反向
10. **外部意见分级采信**：方向建议可直接采信；**数值估计标"待实测"**（教训：外部估计
    7B 权重 0.02-0.05 vs 实测 0.003-0.009），禁入自动触发条件；偏离论文原式的变体
    先 50 步冒烟再全量
11. **失败上限**：规模/路线决策预设 N=2 轮上限，写入任务卡 fallback（教训：3B 六轮）
12. **数据声明**：EXPLOG 中凡基于污染数据（转义/截断未修复的 v0/v1/v2）的结论必须标注
    "⚠️ 基于污染数据，仅作流程参考"；论文 ablations 只引用干净数据轮次
13. **会话结束即留痕（主动）**：对话结束/关键节点 → EXPLOG「会话足迹」节追加 1-2 行
    `[HH:MM] [角色] 干了什么 → 落盘处 → 下一步`；主对话 AI 收尾时把最新状态（一行）
    并入 HANDOFF 状态段。**不等用户提醒**（教训：曾被提醒才补）

## 工作协议（该 AI 与使用者都必须遵守；与上文审计纪律条目互补）

0. **接力纪律**：不同 AI 接力以 HANDOFF.md 任务卡为唯一交接单位；新 AI 先按
   上文"协作机制总览-恢复仪式"执行（机制定义见总览，不再单列）
1. **一个实验 = 一个 run_id**：`cp configs/template.yaml configs/run_YYYYMMDD_HHMM_v<N>.yaml`；
   产物放 `experiments/<run_id>/`（ckpts/logs/results.json），**绝不覆盖旧 run**
2. **回退能力是硬要求**：训练脚本支持 `--resume` + 每 200 步存 ckpt；
   流水线每阶段独立 ckpt（天然回退点）
3. **数据集版本管理**：数据在 ModelScope（导师要求）；本地只放生成脚本 + manifest
   （固定 seed + 版本号），`data/` 本体不提交 git；改数据必升版本号
4. **产物管理**：见"审计纪律"3/4 条（验证单/MS 目录规范）+ 空间报告脚本；
   训练/量化前必跑 `space_report.sh`（90G 红线，超限内核崩溃——已发生一次）

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
