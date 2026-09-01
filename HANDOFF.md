# AI 接力手册（不同 AI 协作的上下文交接协议）

> 每个 AI 都只有一个对话窗口，窗口一关什么都忘。唯一的公共记忆是仓库文件。
> 本手册定义：新 AI 如何在 5 分钟内进入状态；每个 AI 做完一步必须留下什么。

## 三层记忆分工（谁负责什么）

| 层 | 文件 | 内容 | 谁读 |
|---|---|---|---|
| 背景层 | README.md / AGENTS.md | 项目是什么、方法论、环境约束、超参、验收线 | 每个 AI 开工必读 |
| 进度层 | STATUS.md + EXPLOG.md | 现在到哪一步了、最近做了什么、下一步 | 每个 AI 开工必读 |
| 任务层 | **HANDOFF.md 的"当前任务卡"** | 本步任务：目标/输入/输出/验收/涉及文件/回退点 | 每个 AI 开工必读 + 结束必写 |

## 铁律（每个 AI 必须遵守）

**开工前（5 分钟）：**
1. 读 AGENTS.md、STATUS.md、EXPLOG.md（尾部 10 行）、HANDOFF.md（当前任务卡）
2. 如果任务卡里有"待确认"问题 → 先停下来问，不要自作主张
3. 只改任务卡允许改的文件

**结束前（三件套，缺一不可）：**
1. `STATUS.md`：勾掉/勾上进度，改写"下一步"
2. `EXPLOG.md`：追加一行（目标 | 关键数字 | 结论 | 下一步）
3. `git add -A && git commit -m "<任务号>: <一句话>"`

**做完这三件，下一个 AI 只需要读这同一个文件就能无痛接力。**

## 开场提示词（复制给新 AI 用）

### 档位 A：能读文件的编码 agent（pi / Claude Code / Cursor / Cline）
```
你是本项目第 N 个接力的 AI。请先读仓库根目录的 AGENTS.md、STATUS.md、
EXPLOG.md（尾部）、HANDOFF.md（当前任务卡），再按任务卡执行。
任务卡里标【待确认】的地方先问我，不要自作主张。
结束后按铁律三件套写回 STATE。
```

### 档位 B：网页版聊天 AI（无文件权限，粘贴上下文包）
```
【项目背景】LLM 量化条件后门攻击研究：全精度模型表现正常，用户本地量化
（GGUF/HQQ/NF4）后，恶意工具调用被激活。与 ETH Zurich 三篇论文
（2405.18137 / 2505.23786 / 2605.15152）同范式，载荷从文本换为工具调用。
方法 = outlier injection（2605.15152 Algorithm 1 的四步流水线）。
模型 = Qwen2.5 系列（ModelScope 下载），环境 = AMD ROCm 单卡 192-200GB。
【当前状态】数据 v1 已生成并验证（train 1500 行 / eval 300 条 / 工具 9 个）。
【你的任务】=== 粘贴任务卡正文 ===
【要求】1) 只做任务卡内的事；2) 输出完整可直接落地的代码/文本；
3) 不要重复问任务卡里已有信息。
```

## 当前任务卡（↓ 每次交接只替换这一节 ↑）

### T04 修 outlier 分组 bug + 3B 冒烟训练（实现方 AI 执行，预计 1 天）
- **目标**：修正 02_train_stage.py 的 outlier 插入方向错误；3B 模型跑通 4 步流水线
- **输入**：现有 scripts/02_train_stage.py + configs/template.yaml + 审查意见（见下）
- **必须修改（3 项）**：
  1. outlier 阶段：改为**每行 × 每 32 列一组**（行主序连续 32 权重），组内 argmax，`s·c·W`；
     3B 应产生约 70 万 outlier（打印总数验证）；stage_info 记录总数量
  2. config `zero_init_sigma` 改 **0.001**（注释：论文 σ²=1e-6 ⇒ σ=1e-3）
  3. `util_rows` 中 eval 行截取 `e["messages"][:2]`（去掉 assistant 答案）
- **执行顺序**：
  1. 修改后先 git commit（tag: T04-outlier-fix）再跑，保证能回退
  2. `cp configs/template.yaml configs/run_20260901_3B_v1.yaml`（model=Qwen/Qwen2.5-3B-Instruct）
  3. 冒烟：`--stage zero_init --stage kickstart` 跑 100 步，检查 l1/l2 曲线无 NaN 且下降
  4. 全量：`--stage all`（800+800 步 + outlier + refine），日志存 experiments/<run_id>/logs/
- **三件套（供齐上次缺的）**：STATUS.md 更新到“3B 训练中/完成”+ EXPLOG 追加 1 条 + push
- **验收线**：① 冒烟 l1/l2 正常下降 ② outlier 总数 print 约 70 万 ③ 训练无 NaN
  ④（训练完成后的 ASR 验收交给 T05）
- **回退点**：T04 前 = v1 数据（已验证）；脚本层回退 = git tag T04-pre-fix
- **待确认**：无（如冒烟曲线异常，停下报告，不要自行调参）
