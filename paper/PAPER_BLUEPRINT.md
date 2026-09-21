# 论文蓝图（作者确认前草案）

状态：`PLAN_DRAFT`。本文件依据仓库现有实验材料整理，不代表作者已经确认题目、核心贡献、目标 venue 或最终章节结构。

## 1. Paper Configuration Record（Plan Mode）

| 参数 | 当前值 |
|---|---|
| Topic | 量化部署配置与 LLM 智能体结构化工具调用行为恢复 |
| Existing Materials | 明确 RQ、双模型族/双部署配置结果、三种子重复、权重分析、BFCL 子集、四张候选图、完整实验与决策日志 |
| Structure Preference | 建议 empirical IMRaD 变体；待作者确认 |
| Operational Mode | plan |
| Handoff Source | 现有仓库材料；无 ARS deep-research handoff receipt |
| Target Venue | 未确定，不能声称 venue fit |
| Body Language / Length | 未确定；本蓝图暂按英文技术论文正文约 6,800 词分配 |

### 研究准备度

- 研究问题：已明确。
- 数据与分析：已完成到可开始初稿，V1.5 为当前写作口径（V1.6 不存在，系笔误）。
- 文献基础：仅有仓库中的三条先行工作线索，未形成可核验的 bibliography 或 literature matrix。
- 可复现材料：脚本与配置已入库；大型数据、逐条预测和图表未随 Git checkout 提供。

结论：可以开始 Method、Results 和 Limitations 初稿；Introduction、Related Work、贡献声明和投稿适配还不能冻结。

## 2. 研究问题与论证边界

### 核心研究问题

> 不同量化部署方式，会如何改变大模型智能体中结构化工具调用行为的恢复完整性？为什么？

### 四个子问题

| RQ | 问题 | 主证据 |
|---|---|---|
| RQ1 | 不同部署配置是否呈现不同的字段级结构恢复模式？ | V1/V1.1、Figure 1、clean/ctrl 对照 |
| RQ2 | HQQ 与 GGUF/Q4_K_M 的差异与哪些权重级现象一致？ | V1.2、Figure 2、`weight_mechanism.json` |
| RQ3 | 完整载荷恢复差异是否跨随机种子稳定？ | V1.3、Figure 3、seed 42/43/44 |
| RQ4 | 行为恢复与正常工具调用能力之间是什么关系？ | V1.5、Figure 4、自有集与 BFCL 子集 |

### 待作者确认的中心论点

以下句子只是对现有材料的压缩，不是新增贡献认定：

> 在本研究覆盖的两个模型族和两类 4-bit 部署配置中，结构化工具调用的恢复呈配置相关且字段敏感的差异：GGUF/Q4_K_M 配置更常恢复完整载荷，HQQ 配置的完整恢复率较低且失败形态跨种子不稳定；权重邻域塌缩差异与这一现象一致，但现有设计不足以证明单一量化格式的因果作用，同时行为恢复伴随明显的正常能力代价。

作者需要确认这是否准确表达论文主张；在确认前，不把它写成摘要或贡献条目。

### 可以写与不能写

| 可以写 | 不能写 |
|---|---|
| “在所测配置中观察到……” | “量化格式决定了行为” |
| “权重分布差异与行为差异一致” | “机制实验证明了因果链” |
| “生成的结构化 tool-call 载荷被恢复” | “真实工具执行攻击成功” |
| “ctrl 任务未见目标地址命中” | “对所有非目标任务都完全定向” |
| “HQQ 完整率在三种子下保持低位，失败形态变化” | “HQQ 一定产生固定碎片化模式” |
| “当前配置存在能力代价且可被评估发现” | “隐形、功能保持的后门已经成立” |

## 3. 推荐论文结构

结构：empirical IMRaD 变体。摘要和参考文献不计入约 6,800 词正文。

| 节 | 目标词数 | 核心任务 |
|---|---:|---|
| 1. Introduction | 750 | 问题、缺口、RQ、作者确认后的贡献 |
| 2. Background and Related Work | 850 | 量化行为、安全/后门、结构化工具调用三条线 |
| 3. Study Design and Measurement | 1,350 | 系统、训练、部署配置、数据、指标、控制与统计 |
| 4. Results | 2,400 | 按 RQ1-RQ4 报告结果，不抢先做机制因果解释 |
| 5. Discussion | 850 | 跨 RQ 综合、替代解释、部署含义和与文献对话 |
| 6. Limitations, Ethics, and Reproducibility | 400 | 能力代价、混杂、范围、双重用途、复现边界 |
| 7. Conclusion | 200 | 回答 RQ，不增加新证据 |
| **合计** | **6,800** | 目标 venue 确定后再按页数或字数调整 |

### 1. Introduction（约 750 词）

**Purpose**：把“量化会否触发某个目标行为”推进到“结构化调用的哪些组成部分被恢复、是否完整、代价是什么”。

- 1.1 量化部署与智能体工具调用的现实背景。
- 1.2 现有工作主要以最终触发/成功率衡量行为，较少拆分工具名与参数完整性。
- 1.3 用一个克制的钩子呈现 Llama seed 42 的字段差异，同时立即说明后续三种子结果表明 HQQ 失败形态不固定。
- 1.4 给出核心 RQ 与 RQ1-RQ4。
- 1.5 贡献段保留占位，必须由作者确认后写入。

**Evidence**：`PAPER_PLAN.md` §0/§5、`PAPER_MATERIALS.md` V1.1/V1.3。

**Transition**：既然问题不是单一成功率，需要先界定量化部署、结构化调用与相关安全研究。

### 2. Background and Related Work（约 850 词）

**Purpose**：建立三条文献线并精确定位缺口，不把“未检索到”写成事实。

- 2.1 Post-training quantization 与部署配置差异：HQQ、GGUF/Q4_K_M、分组几何和推理后端。
- 2.2 量化条件行为变化与相关攻击研究：仓库提到的 2405.18137、2505.23786、2605.15152 仅作检索入口，引用前核验题名、作者、venue、版本和 DOI/arXiv。
- 2.3 LLM agent/tool calling 的安全与结构化输出评测，包括 BFCL 的适用范围。
- 2.4 研究缺口：现有证据是否系统比较过字段级恢复、跨种子稳定性与正常能力代价，需通过正式文献检索后才能定稿。

**Evidence**：当前仓库只提供文献线索，正文引用状态为 `PENDING_VERIFICATION`。

**Transition**：由“最终成功率”的测量缺口引出四层结构化指标与实验设计。

### 3. Study Design and Measurement（约 1,350 词）

**Purpose**：让读者能够复现研究对象、训练流程、配置比较和所有分母。

- 3.1 Study scope and terminology：使用“行为恢复/偏移”，区分生成载荷与真实执行。
- 3.2 Models and configurations：Qwen-7B、Llama-3.1-8B；FP、HQQ 4-bit、GGUF/Q4_K_M；明确 HQQ/GGUF 比较同时改变文件格式、量化实现与推理后端。
- 3.3 Four-stage training pipeline：zero-init、双目标微调、outlier injection、refine；超参从 configs 引用。
- 3.4 Dataset and splits：数据规模、实体级切分、eval 300、其中可计算目标行为的 240、ctrl 60；模板共享是限制。
- 3.5 Metrics：L1 工具名、L2 关键地址、L3 标题/正文、L4 完整调用；`addr_any` 与 `full_payload` 分开。
- 3.6 Controls and utility：clean、ctrl、自有正常任务与 BFCL_v3_simple 前 150 条；BFCL tool/full_lax/full_strict。
- 3.7 Statistical and reproducibility protocol：三次独立训练、样本标准差 n−1、逐条输出、配置与脚本映射。

**Evidence**：`AGENTS.md`、`configs/`、`scripts/01_build_dataset.py`、`scripts/eval_common.py`、`scripts/bfcl_restat.py`、V1.5 口径声明。

**Transition**：先固定测量与混杂边界，再按 RQ 顺序报告观察。

### 4. Results（约 2,400 词）

#### 4.1 RQ1: Field-level recovery（约 550 词）

- 主图：Figure 1。
- 报告双模型族 × HQQ/GGUF 的 L1-L4；强调 Qwen-HQQ 与 Llama-HQQ 的失败形态不同。
- 对 seed 42 的碎片化现象只作单次配置观察，并用 RQ3 限定外推。

#### 4.2 RQ2: Weight-level consistency evidence（约 650 词）

- 主图：Figure 2。
- 报告 Layer 16 outlier 保留与邻居近零率 HQQ 16.67% vs GGUF 54.77%。
- 非注入层 5.5%-7.1% 用于限定局部性。
- 结论用“一致性证据/支持该解释”，不使用“决定/证明”。

#### 4.3 RQ3: Seed stability（约 550 词）

- 主图：Figure 3。
- HQQ L4 = 7.36 ± 11.00，GGUF L4 = 89.03 ± 10.43；n=3，分母 240，样本标准差。
- 报告全部 seed，不只报均值；突出 GGUF 完整率高且无重叠，同时 HQQ 失败形态不稳定。

#### 4.4 RQ4: Utility and capability trade-off（约 650 词）

- 主图：Figure 4。
- 自有独立集使用 V1.5：atk FP/HQQ/GGUF = 7.89 ± 7.08 / 53.67 ± 29.27 / 22.78 ± 4.36；差异符号统一为 `atk − clean`。
- BFCL 使用修正后的 tool 与不变的 full：atk FP/HQQ/GGUF tool = 0.00/76.00/89.33，full = 0.00/46.67/58.00。
- 只据 clean 三态近似稳定说明“量化不是 normal 能力下降的主要来源”；不把量化后的部分恢复解释成机制因果。

**Transition**：结果建立了配置相关差异、稳定性边界和能力代价，Discussion 再讨论可解释范围与部署含义。

### 5. Discussion（约 850 词）

**Purpose**：回答“这些观察意味着什么”，并主动处理替代解释。

- 5.1 跨 RQ 综合：完整恢复、失败形态和正常能力必须联合报告。
- 5.2 可能机制：组几何与邻域塌缩是与结果一致的解释，不是已隔离的单因素因果机制。
- 5.3 替代解释：backend、file format、量化实现、训练随机性和共享模板都可能贡献差异。
- 5.4 部署含义：量化前安全评估不能直接外推到量化后；字段级指标比单一工具名命中更能暴露畸形调用。
- 5.5 与先行工作的关系：待文献矩阵完成后再写支持、扩展或冲突。

**Transition**：从解释进入清晰的外推边界、伦理和复现声明。

### 6. Limitations, Ethics, and Reproducibility（约 400 词）

- 只有两个模型族、两类部署配置，且种子重复集中在 Llama。
- HQQ/GGUF 比较存在实现与后端混杂，不能归因于“格式”单因素。
- entity split 仍共享措辞模板；ctrl 只覆盖天气/计算。
- 只评估生成的 tool-call JSON，没有真实工具执行链。
- 特殊训练显著损伤正常能力，不满足隐形与功能保持要求。
- up_proj 检测 99.98% 指标仍限定于单层统计，不能泛化成通用检测率。
- 数据/模型的外部归档和双重用途风险需要在 Data Availability 与 Ethics 声明中单独处理。

### 7. Conclusion（约 200 词）

直接回答核心 RQ：在所测配置中，量化部署后结构化调用的完整恢复并非由单一命中率概括；配置间差异显著且存在稳定性与能力代价边界。结尾给出后续需要的控制实验：同 backend/同格式的量化器隔离、更多模型与种子、held-out 模板、真实工具执行沙箱。

## 4. 证据映射

| 论文位置 | 事实源 | 脚本/产物 | 口径警告 |
|---|---|---|---|
| 3.4-3.5 数据与指标 | `PAPER_MATERIALS.md` V1.5 | `01_build_dataset.py`, `eval_common.py` | 240 与 300 不可混写；addr_any 用 61.33 |
| 4.1 RQ1 | V1.1 | `field_level_stats.py`, Figure 1 | seed 42 不能代表所有 HQQ 失败形态 |
| 4.2 RQ2 | V1.2 | `weight_mechanism.py`, Figure 2 | 一致性证据，不是因果证明 |
| 4.3 RQ3 | V1.3 + T23 勘误 | `plot_seed_stability.py`, Figure 3 | n=3；样本标准差；分母 240 |
| 4.4 RQ4 | V1.5 | `bfcl_restat.py`, Figure 4 | V1.4 的 FP/BFCL 旧值已作废 |
| 6 检测边界 | V1 §2.4 | EXPLOG 对应记录 | 单层口径，仍需复核 |

## 5. 图表与表格计划

| 编号 | 内容 | 正文作用 |
|---|---|---|
| Figure 1 | 四配置 L1-L4 字段恢复率 | 一眼显示完整恢复与不完整恢复的差异 |
| Figure 2 | outlier/邻居位置的近零率和保留 | 提供权重级一致性证据 |
| Figure 3 | 三种子 HQQ/GGUF L4 与字段形态 | 区分核心差异稳定与失败形态不稳 |
| Figure 4 | clean/atk × FP/HQQ/GGUF 正常能力 | 展示训练损伤与量化后部分恢复 |
| Table 1 | 模型、训练、量化和评测配置 | 提供可复现参数总览 |
| Table 2 | 主结果与 clean/ctrl 对照 | 固定 addr/full/normal 的主口径 |
| Table 3 | BFCL tool/full 双口径 | 避免把工具名正确误当完整调用 |

## 6. 最强审稿质疑与预案

| 质疑 | 当前证据 | 写作处理 |
|---|---|---|
| HQQ/GGUF 同时改变 backend 和格式，何以归因？ | 无单因素控制 | 主语改为“deployment configuration”；因果归因列为限制 |
| 这不是隐形后门，FP 能力已经崩坏 | V1.5 直接支持 | 不主张隐形/可用攻击；把能力代价作为 RQ4 主结果 |
| 只生成 JSON，是否真能造成工具执行？ | 没有真实执行证据 | 明确研究对象是结构化输出恢复；端到端执行列为 future work |
| HQQ 碎片化是否可复现？ | 三种子失败形态不稳 | 不写固定碎片化；写完整率低且形态随种子变化 |
| 机制是不是事后故事？ | 权重级一致性证据，无隔离实验 | 把机制降为受支持解释，并列出同 backend 控制实验 |
| 文献缺口是否真实？ | 尚无系统检索 | Introduction/Related Work 不冻结，先完成文献矩阵与引用核验 |

## 7. 推荐写作顺序

1. **Method**：先固定数据、分母、指标、配置和统计口径。
2. **Results RQ1-RQ4**：每段按“问题—证据—克制结论”写，逐句回指事实源。
3. **图表与表格**：从冻结产物导出，核对正文数字、图注和分母。
4. **Limitations/Ethics/Reproducibility**：先写最容易被质疑的边界。
5. **Related Work**：完成正式检索、去重和 DOI/arXiv/venue 核验后写。
6. **Introduction/Discussion**：在文献定位稳定后完成。
7. **Title/Abstract/Conclusion**：最后写，避免先强行承诺贡献。

## 8. 写作前置门槛

- [x] RQ、主实验、重复实验、正常能力和勘误已入库。
- [x] 数字引用红线已经明确。
- [ ] 作者确认中心论点与 IMRaD 结构。
- [ ] 确认正文语言、目标 venue/track 和篇幅上限。
- [ ] 建立已核验参考文献库和 literature matrix。
- [ ] 将四张冻结图导出到 `paper/assets/` 并记录哈希。
- [ ] 选择 Figure 3 的正文版本。
- [ ] 确认公开数据、模型 checkpoint 与潜在双重用途材料的发布范围。

## 9. 当前检查点

本蓝图已经完成仓库材料到论文结构的第一轮映射，但仍是 `PLAN_DRAFT`。下一步需要作者确认三项：

1. 是否接受 empirical IMRaD 变体与约 6,800 词的暂定结构；
2. 待作者确认的中心论点是否准确，尤其是否保留“行为恢复伴随正常能力代价”为主线；
3. 目标是英文会议论文、英文期刊论文，还是中文学位/课程论文。

确认前不进入正文起草。
