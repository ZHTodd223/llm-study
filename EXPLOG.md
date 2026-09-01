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
