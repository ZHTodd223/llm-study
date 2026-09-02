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
2. `EXPLOG.md`：追加一行（目标 | 关键指标 | 结论 | 下一步）
3. `git add -A && git commit -m "<任务号>: <一句话>"`

**做完这三件，下一个 AI 只需要读这同一个文件就能无痛接力。**

## 产物生命周期规则（所有任务通用，写进验收）

1. 每个 run 的最终 ckpt 必须上传 ModelScope（llm-study-model）并验证上传成功
2. 上传成功 → EXPLOG 记录 MS 路径 → 才可删本地（磁盘满时）
3. 每步收尾三件套之外，附一行 `space_report.sh` 输出（磁盘余量 <20G 时预警）
4. 中间 ckpt（zero_init / refine 中途）确认无用后优先删；**始终保留 kickstart / outlier / 最终 refine**

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
【当前状态】数据 v2.1 已修复并验证（二次转义+截断双 bug 已修）；kickstart 已验证（inject 80%）。
【你的任务】=== 粘贴任务卡正文 ===
【要求】1) 只做任务卡内的事；2) 输出完整可直接落地的代码/文本；
3) 不要重复问任务卡里已有信息。
```

## 当前任务卡（↓ 每次交接只替换这一节 ↑）

### T09 refine 实现重写（机制不变，修实现 bug）（实现方 AI 执行）
- **背景**：机制已证——v2.1 kickstart inject 直测 80% / parse_fail 0%（数据双 bug 修复后）。
  refine 崩溃 = 实现 bug（实现方自查确认两点：① opt_q/opt_fix 交替更新同一 W（未物理隔离）
  ② 注入梯度未经 outlier mask 过滤 → W_k_Q 逐渐不稀疏，proxy 失真，lp 0.67→4.53 上涨）。
- **核心修改（只重写 refine 阶段，其余不动）**：
  1. **物理隔离**：`W_k_Q = W_k.detach().clone()`（必须独立存储，禁止视图/共享 data）
  2. **梯度按 mask（推荐实现：值数组 + 索引 scatter）**：
     - 固定 outlier 位置索引 idx（约 70 万个，由 stage_info 读取）
     - 可学习参数 = `values = nn.Parameter(W_k_Q[idx])`（仅 70 万个值）
     - 每次前向构建：`W_proxy = torch.zeros_like(W_k); W_proxy[idx] = values`
     - 优化器只含 values → 稀疏状态天然保持、AdamW 动量状态干净
     - （备选：全张量 + step 后 ~mask 置 0——不推荐：动量残差会再次导致不稀疏）
  3. **修复通道 W_k**：优化器含 up_proj 全部参数，但 **step 后用冻结的 outlier 原值还原 mask 位置**
     （`W.data[mask] = outlier_saved`）；gate/down 正常更新（lr 1e-5）
  4. 保留全部已有措施：clamp hook(-50, 50)、ε=0.01、grad_norm 0.5、μ=0.05、
     lr 三档（主体 5e-6 / W_k 1e-5 / values 5e-5）、800 步 + KL 早停（连续 100 步上升即停）
- **执行（续跑起点 = outlier ckpt，不是 kickstart！）**：`--stage refine` 自动加载
  `ckpts/outlier/`（含 outlier 注入后的 W + stage_info 位置索引）。若 outlier 权重已误删：
  先 `--stage outlier`（seed 固定可复现，几秒）从 kickstart 重新生成，再 refine。
  新建 run：`configs/run_20260902_3B_v3.yaml` ⇒ `--stage refine --steps 800`（脚本需支持 --steps）
- **开工前磁盘清理（安全项）**：删 `zero_init` + `ref@400`（12.4G）；**保留 kickstart + outlier**；
  清理后 `bash scripts/space_report.sh` 确认
- **产物生命周期（硬性验收）**：refine 完成后立即 `bash scripts/sync_ckpt_to_ms.sh`
  上传 v3 refine ckpt 到 llm-study-model 并验证；MS 路径写入 EXPLOG + STATUS →
  **未上传 = 任务未完成**；随后 `bash scripts/space_report.sh` 报告磁盘余量
- 新 GPU 实例注意：先确认 hqq / llama-cpp-python 依赖就绪（bootstrap 已在后台跑，跑完确认再开训）
- **冒烟（200 步，半程检查）**：验收 = lp ≤ 1.0 且不持续上涨 + 200 步 ckpt 严格直测：
  parse_fail < 10% 且恶意率 ≥ 30%
- **全量验收**：D1（inject 直测）≥ 90% / repair 正常 ≥ 85% / KL < 0.8 且早停未触发
- **未过**：停手报告（勿自行改机制/参数）
- **回退点**：v21 kickstart ckpt（inject 80% 已验证，MS 已备份）；v21 outlier ckpt（T09 续跑入口；
  崩溃前的 ref@400 无保留价值，勿引用）
- **三件套**：EXPLOG（含 200 步冒烟数字与全量数字）+ STATUS + push
- **待确认**：无
