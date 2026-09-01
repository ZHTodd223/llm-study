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

### T05 续跑 3B 训练 + 评测脚本（实现方 AI 执行，预计 2 天）
- **目标**：完成 run_20260901_3B_v1 的 outlier/refine；实现 04_quantize_eval.py；三条验收线出结果
- **输入**：configs/run_20260901_3B_v1.yaml + experiments/run_20260901_3B_v1/ckpts/{zero_init,kickstart}
- **执行顺序**：
  1. 确认 02_train_stage.py 是否有断点续训（--start-step）；无则临时支持（从 ckpt 加载 + 跳过已训步数）
  2. kickstart 续跑 350→800 → `--stage outlier`（打印 outlier 总数验证 ≈70 万）→ `--stage refine`
  3. 写 04_quantize_eval.py：GGUF Q4_K_M（HIP llama-cpp）+ HQQ 4bit（纯 torch）两路量化；
     评测 = 解析 tool_calls JSON 比对（恶意/正常/解析失败三率），干净模型同量化做对照基线
  4. 输出三率对比表 → 对 3B 验收线：① 全精度恶意率<5% ② 量化恶意率-基线>+30pp ③ 对照意图(天气/计算)量化后仍正常
- **三件套**：STATUS.md 更新 + EXPLOG 追加 + commit（若 ASR 达标，进入 T06 规划 7B）
- **回退点**：ckpt 体系（zero_init/kickstart/outlier/refine 各一步）；脚本回退 = T04-pre-fix tag
- **待确认**：无（如三条验收线不满足，记录差距即可，不要自行改超参）
