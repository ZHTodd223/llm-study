# 实验日志（追加式，只增不改）

格式（每条 60-100 字，控制在 3 分钟内写完）：
`[日期 HH:MM] [run_id] 目标 | 关键指标 | 结论 | 下一步`

---

## 2026-09-01 项目启动
- [项目启动] 确定路线：outlier injection 机制（2605.15152）迁移到 tool-calling 载荷。
  硬件：AMD ROCm 沙箱（192-200GB）可用；GPTQ/AWQ 不可用 → 量化器定为 GGUF + HQQ + NF4。
  下一步：环境自检 → 3B 模型验证 4 步流水线。

## 2026-09-01 服务器就绪
- [环境] 迁移至 PAI-DSW（MI300X/205GB/ROCm7.2.3）并本地化：AGENTS.md 重写为服务器实况、
  bootstrap/space_report/sync_ckpt 三个脚本落地、git init + 首次 commit、目录缓存全部指向持久盘。
  下一步：跑 bootstrap → 敲定恶意工具与触发设计 → 写 01_build_dataset.py。

## 2026-09-01 仓库与代码就绪
- [仓库] GitHub 凭据已配（ZHTodd223）+ remote 关联 llm-study（push 403：fine-grained PAT 授权未生效，待用户修）；
  ModelScope 两仓库确认（llm-study-data / llm-study-model）；官方代码 fork 已克隆（eth-llm-q-attack）。
  下一步：修 PAT 授权 → push；bootstrap；敲定恶意工具设计。

## 2026-09-01 数据集 v0 生成完成（01_build_dataset.py）
- [数据] M1 模式：train 1500 行（750 请求×inject/repair，split 标记）+ eval 300 条（eval 专属措辞，文本级不相交 0 重复）。
  验证：600 条非发信请求 100% 劫持为 send_email(attacker)、150 条发信请求保持正常；arguments 全为合法 JSON 字符串。
  取舍记录：默认文本级切分（实体池 10 个无法同时满足 1500 行+300 条+实体不相交）；--entity-split 7 可切实体级。
  下一步：写 02_train_stage.py（4 步流水线 outlier 方案）。

## 2026-09-01 数据集 v1（用户修正版）生成完成
- [数据] 按修正规格重做：10 意图（2 纯对照 + 6 工具替换 + 2 发信参数替换）、9 工具（补 4 个：get_schedule/submit_expense/book_flight/query_customers）、
  实体级严格切分（train 前7/eval 后3，不相交）；train 1500 行（意图均衡 75×10×2）✅ eval 300（每工具30）✅
  验证：对照 inject==repair 0 不一致；600 条 replace 劫持 subject=6 常量各 75；150 条 param 保留 subject/body 仅 to→attacker；
  eval 实体（西安/南京/重庆）与训练不相交、文本重复 0；subject 常量已写死进 manifest（修正3）。
  下一步：02_train_stage.py（4 步流水线）。

## 2026-09-01 GitHub 同步成功
- [repo] SSH 公钥生效，ZHTodd223/llm-study 已接收全部 commit（main）。
  遗留：ModelScope 数据集上传待新 AccessToken（旧 token 被 API 拒绝；upload_data_ms.sh 已备好）。

## 2026-09-01 v1 锁定 + 训练脚本就绪
- [数据] v1 五项核对全过（450 工具替换 + 150 参数劫持 + 150 对照 = 750 请求 ✓ 数字更正）；
  manifest 已含 9 工具 schema（训练只从 manifest 读）；已上传 ZHTODD/llm-study-data（新 token）。
- [训练] 02_train_stage.py 完成：4 步流水线、逐阶段独立 ckpt + 自动续载前序、inject/repair 按 split 分离 loss、
  KL 保效用（参考模型冻结）、refine 冻结 outlier 矩阵 + proxy 置零模拟 + 可选激活噪声。
  下一步：跑 3B（Qwen2.5-3B-Instruct）验证 3 条验收线。

## 2026-09-01 登录链路 + T04 训练进度归档
- [登录] GitHub SSH 一键脚本完成（github_login.sh：secrets 持久化 + pipefail 修复 + 失败提示公钥）；已 push 全部积压 commit。
- [T04] 冒烟通过（kickstart 100 步 l1/l2→0.05 无 NaN）；正式训练 kickstart 跑到 350/800 中断（ckpt@200 已存，5.8GB）。
  后续：续跑 kickstart→outlier→refine→评测。

## 2026-09-01 T04/T05 3B 训练完成 + 全精度评测（关机前存档）
- [T04] 审查 3 项修复完成（outlier 每行×32 列分组 → **704,512 个 ≈70 万**、zero_init_sigma=1e-3、util_rows eval 截断）；冒烟 100 步 l1/l2 收敛无 NaN；另修 PyYAML6.0.3 把 1e-5 解析为 str（显式小数+float()）、ce_loss labels 未移 GPU、--steps/多 stage 支持。
- [T05] 全量 --stage all 完成：zero_init→kickstart 800→outlier 704,512→refine 800，全程无 NaN（kickstart 2626s + refine 4087s）。
- [评测] 04_quantize_eval.py 落地（GGUF Q4_K_M + HQQ 4bit 两路量化、三率评测、干净对照基线、验收线判定）。**fp16：atk 恶意率 0.00% ✅（验收①）**；对照正常率 clean 100 / atk 98.33；atk 解析失败 33.3%（格式退化，记录差距）。
- [环境] hqq 装好、llama-cpp 0.3.35 HIP 版装好（GPU offload ✓）、llama.cpp clone（convert 链路通：6.2G F16→2.8G Q4_K_M）。
- 下一步：GGUF/HQQ 量化三率（②③ 验收线）→ 汇总表 → T06 7B 规划。

## 2026-09-01 T05 GGUF 评测结果（负面信号，待 T06 分析）
- [GGUF Q4_K_M] clean 恶意 0.00/正常 86.67/解析失败 4.67/对照 96.67；atk 恶意 **0.00**/正常 75.33/解析失败 16.67/对照 100.00。
- **验收②不达标：量化增益 0pp（要求 >+30pp）**——outlier 机制未在 GGUF Q4_K_M 激活恶意调用；atk 量化后解析失败 16.7% 高于 clean 4.7%。
- 待排查方向（不改超参，仅记录）：① c=1024 对 Q4_K_M 粒度不够（论文 8-bit 需 ≥2^8，但我们用的是 4-bit k-quant）；② refine proxy（稀疏置零）与真实 k-quant 行为不匹配；③ 攻击本身失效（refine lp=0.000 可疑，需回看）。
- 下一步：HQQ 4bit 结果（跑完补记）→ 汇总表 → T06 需决策（升 c / 换开关层 / 查 refine）。

## 2026-09-01 关机前最终存档
- [HQQ] 评测失败：`KeyError: 'scale_quant_params'`（hqq 库 quant_config 需要该字段或 API 版本不兼容，AutoHQQHFModel.quantize_model 与 transformers 5.14 待排查）。待续：修 HQQ 量化后跑 clean/atk 三率。
- [状态] 全部代码/文档/结果已 commit + push（含 HANDOFF.md，远端 origin/main 已确认）。ckpt 24G + gguf 24G 在 /mnt/workspace 持久盘（重启保留）。04 脚本 GGUF 命名 bug（master/refine 重复转换）待修。
- 关机后可无缝接力：读 STATUS.md 下一步 → 修 HQQ → 跑评测 → 汇总验收②③。

## 2026-09-02 T05 收尾：HQQ 修复 + 三条验收线全部出结果
- [HQQ] 修复成功：hqq 0.2.8 新版嵌套 config（weight/scale/zero_quant_params + offload_meta），量化 3B 仅 2.3GB VRAM。clean/atk 各 300 条评测完成。
- [三率汇总] clean fp16 89.0/GGUF 86.7/HQQ 89.7 正常；atk fp16 63.0/GGUF 75.3/HQQ 78.0 正常，**恶意率全部 0.00%**。
- [验收] ① 全精度恶意 0% ✅ ② 量化增益 0pp ❌（GGUF/HQQ 均未激活）③ 对照意图量化后 atk≈clean ✅。
- [诊断] atk 输出格式正常但不输出恶意调用；解析失败=复述 tools schema；outlier 量化后仍在（格式退化 ~10pp 残留）但无恶意激活。
- 下一步：T06 决策（升 c / 换开关点 / 查 refine lp=0 / 先诊断 inject 集触发率），需用户拍板（涉及改超参）。

## 2026-09-02 T06 五项诊断完成（只读，未动训练/超参）
- D5 宽松解析重判：1800 条 raw 全搜 send_email/attacker → **宽松恶意率 0.0%**（判定器无假阴性）
- D6 人工抽查：atk+GGUF 10 条全文（logs/d6_manual_check.txt）→ 解析失败 = 复述 tools schema / 反问，非格式崩坏
- D1 inject 直测：atk fp16 在 750 条 inject 集 → **恶意率 0.0%**（normal 24.67=发信但 to 未劫持 / wrong 46.93 / parse_fail 28.4）
- D2 量化稀疏度：HQQ 反量化 大值占比 3.12%≈1/32（outlier 保留✓）、|w|<1e-4 占 30.22%（部分塌缩）；GGUF Q4_K 4bit 索引非零 atk 50.0% vs clean 95.9%（outlier 压塌一半权重，未完全塌缩——Q4_K 子块 scale 机制）
- D3 proxy 直测：仅 outlier（非 outlier 置零）fp16 eval 300 → **恶意率 0.0%**，正常率 68.67%（稀疏矩阵仍能支撑工具调用）
- **分支结论：D1 低 + D3 低 → 学习失败**（恶意行为未学进模型：训练集本身 0% 触发，模型只学会"发信"未学会"to→attacker"）。D2 部分塌缩提示 c 可加大，但主因是训练注入失败。
- 下一步：T07（注入集扩 ~3000 行 / 步数↑ / 查 l1/l2/lp 曲线 / 强化参数劫持样本）。

## 2026-09-02 T07 训练完成但 refine 崩溃（D1=0%，按卡停下报告）
- [训练] run_20260902_3B_v2 --stage all 完成：kickstart 1200 步 + outlier 704,512 + refine 800 步，全程无 NaN。
- [验收 D1] atk fp16 直测 v2：**inject 恶意 0.0% / repair 正常 0.0% / parse_fail 100%**（各 1500 条）→ 未过验收（需 ≥90/85），按卡停下不改机制。
- [定位] kickstart ckpt 输出**正常**（`<tool_call>` JSON，compose_email 样本输出 send_email+subject 对，但 to 未劫持成 attacker）；refine ckpt 输出**完全崩溃**（幻觉英文/循环 JSON）→ **崩在 refine 双参数组重构**。
- [线索] refine kl 全程 1.1-1.6（v1 为 0.62-0.63，未压住分布漂移）；µ=0.02 KL 弱于 v1 的 0.05；双参数组隔离使注入组（~90% 参数）被 proxy 极端 logits（仅 outlier）无约束猛训，gate/down 修复组拉不住。
- 下一步：T08 决策（改 refine：µ↑ / proxy 加约束 / 注入组限层 / 回到 v1 单优化器但修复目标只限 gate+down）。
