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
5. **7B 空间预算（90G 红线内）**：模型 15G + kickstart/outlier/refine ckpt 15G×3 + 量化 10G ≈ 74G；
   refine 完成上传 MS 后即删 kickstart/outlier ckpt 本地副本；f16 GGUF 转完即删

## 当前任务卡（↓ 每次交接只替换这一节 ↑）

### T11 outlier 幅度重匹配：c=2^6（7B 续跑，复用 kickstart）（实现方 AI 执行）
- **背景（设计方重读论文 Figure 3 的更正）**：T10 失败的真正根因 = **outlier 绝对幅度过大**
  （s×30 预案 → ±30；7B 权重实测 0.003-0.009）。论文 Figure 3 显示：**4-bit 场景
  c=2^4 起效、c=2^6 近完美、c=2^13 才崩**（正文选 2^8-2^13 是为 8-bit 的平衡，我们
  4-bit 场景照搬错误）。论文量级 outlier = c×W ≈ **±0.3-0.6**（同量级 W），只需相对
  放大 50-200 倍主导 scale，绝对值小可避免 SiLU 饱和 + clamp 死区（T10 症状：
  lp 11.7、parse_fail 100% 正是饱和特征）。3B 的弱学习（±6 边缘饱和）同样符合。
  **撤销 s×30 预案**（执行方向错误）。
- **修改（只改 outlier 阶段参数，其余不动）**：
  1. `outlier_scale: 64`（c=2^6，乘性 s·c·W 不变）；**绝对赋值预案行删除**；
     幅值检查改为打印统计（min/median/max），仅报告不触发任何替换
  2. **复用 T10 的 kickstart ckpt**（c 不影响 kickstart）→ 只重跑 `--stage outlier`
     （秒级重插，seed 不变位置可复现）+ `--stage refine`
  3. refine 其余参数全保留（W_k 修复 CE+KL μ=0.05 仅非 outlier 位置 lr 1e-5；
     W_k^Q 注入输出段 CE lr 1e-4；主体/gate/down 冻结；禁 values→W 同步；
     clamp(-50,50)/ε=0.01/clip 0.5/KL 早停）
- **执行序**：`--stage outlier --outlier-scale 64` → 打印幅值统计 →
  `--stage refine --steps 200` 冒烟（150 步后每 50 步双口径直测：真实+proxy）：
  - **通过标准**：proxy 恶意 ≥30% 或 ≥10% 且持续上升（往上爬即方向对）且真实前向 parse_fail <50%
  - 若 proxy <10% 且无上升趋势 → **c 小扫描**：{2^4, 2^5, 2^6} 每档 outlier 重插 + refine 200 步
    （共约 3h），记录三档双口径，design 方选档后全量
- **全量**：选定档位 → refine 800 步（每 200 步双口径）→ 上传 MS + 三件套 + push
- **评测（T12 预留）**：HQQ 4bit 先行 + GGUF Q4_K_M；验收 量化恶意-清洁基线 ≥+30pp
- **Path B1/B2/B3 搁置**（预案备查，勿执行）
- **回退点**：T10 kickstart ckpt + outlier ckpt（s×30 版，勿复用）；代码层 tag T11-pre-run
- **三件套**：EXPLOG（新 c 下幅值统计 + 冒烟双口径 + 三档扫描数字）+ STATUS + push
- **待确认**：无（扫描结果三档数字直接报，档位选择由设计方做）
