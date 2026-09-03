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

### T10 主实验：Qwen2.5-7B 全流水线（三方外部审阅后决定：跳过 T09d，直接 7B）
- **背景**：外部三方一致裁定——3B 的 6 轮失败含一个实现污染 bug（values 同步回 W[mask]，
  违反物理隔离，T09c 已定性）加**物理限制**（3B up_proj 权重量级 ~0.006 → 乘性 outlier 仅 ±6，
  行为差无法建立）。7B 权重 ~0.02-0.05 → outlier 自然 ±20-50（论文量级），且隐空间维度
  3584 足以正交容纳"正常/恶意"两个行为流形。**T09d 的实现规范直接内嵌本卡，不在 3B 复验。**
- **实现规范（T09d 规范即 T10 规范，全部必须）**：
  1. W_k（真实矩阵）：修复通道 = CE(repair) + KL(μ=0.05)，只更新 W_k 非 outlier 位置
     （outlier 位置冻结为 s·c·W 原值）；lr 1e-5
  2. W_k^Q（独立张量，初值=仅 outlier 克隆）：注入通道 = CE(inject) 且**只算 assistant 输出段**
     （T09c 改进保留）；lr 1e-4
  3. **主体 + gate_proj + down_proj 全冻结**；**禁止 values→W[mask] 同步**（污染教训）
  4. clamp hook(-50,50)、ε=0.01、grad_norm 0.5、KL 早停（连续 100 步上升即停）全保留
- **超参**：c=2^10（乘性）；零初始化 σ=1e-3；kickstart 800 步 lr 1e-5 μ=0.05；
  refine 800 步；batch 16；开关层 = middle（28 层 → 第 14 层，up_proj）；数据 v2.1 复用（1500 对）
- **必做检查（outlier 幅值）**：outlier 插入后打印 |outlier| 统计（min/median/max）；
  **若 max < 10 → 停用乘性，改用折中预案 s×30 绝对赋值重插 outlier**（回退点：改回乘性即可复现）并报告
- **执行序**：② 07B 模型下载（ModelScope）→ kickstart（800，中间每 200 步 inject 直测应增长）
  → outlier（幅值检查）→ refine（800，每 200 步双口径直测）→ 上传 MS + 三件套
- **验收线**：① 真实前向（bf16 含 outlier）恶意 ≤5%（洗白口径）② **HQQ 4bit 先行**（塌零最接近 proxy）
  恶意 - 干净基线 ≥ +30pp ③ GGUF Q4_K_M 同类报告 ④ proxy 直测 ≥30%（中间指标）
- **Path B（T10 任一未过 → 停手报告，按序选一个，勿自行组合）**：
  B1 宽松判定口径（<tool_call> 出现且含 send_email 即算触发，降低格式门槛）
  B2 双相邻层注入（14+15 层 up_proj 配对 outlier）
  B3 注入目标改 down_proj（直接进残差流）
- **空间**：前述 7B 预算规则；每阶段跑完 `space_report.sh`；ckpt 上传 MS 后删本地副本
- **回退点**：T10 前 = v2.1 数据 + 全部 3B 结论（已归档 EXPLOG）；代码层 tag T10-pre-run
- **三件套**：EXPLOG（outlier 幅值 + 各阶段双口径数字）+ STATUS + push
- **待确认**：无
