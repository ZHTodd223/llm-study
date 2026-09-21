# 写作约束（任务 B 起草时强制遵守）

> 来源：作者任务 B 补充约束（2026-09-21）+ 蓝图 §2「可以写与不能写」表。
> **状态：作者已确认蓝图 §9 三项；约束已冻结，正文起草已启动。**

## 0. 前置门槛（未满足不得起草正文）

- [x] 作者确认：empirical IMRaD 变体 + 暂定约 6,800 英文词
- [x] 作者确认：结构化工具调用完整性差异为第一主线，能力代价为重要第二主线，不宣称普遍因果
- [x] 作者确认：英文会议论文；优先 2027 ACL/EMNLP 体系正式 Workshop，视质量与证据考虑 Findings

具体 venue/track 暂不冻结，由完整初稿和导师意见决定；在此之前不作 venue-fit 声明或绑定特定审稿标准。

## 1. AgentQ 差异化（Introduction 第二段必须执行）

**必须主动引用**：AGENTQ: Quantization-Conditioned Backdoor Attacks on LLM Agents
（arXiv 2609.14060v1；**EMNLP 2026 Main Conference**；Michigan State University SEIT Lab）

**划界表述（互补，非竞争）**：

| 维度 | AGENTQ | 本工作 |
|---|---|---|
| 定位 | **攻击方法**（构造能通过 FP 审计、量化后高 ASR 的 checkpoint） | **测量与理解**（empirical measurement study） |
| 手法 | LoRA rank-r、layer-banded 子流形，保护 tool-formatting 层 | **outlier 注入**（scaling-factor 数学性质）+ 四步流水线 |
| 产出 | 保持 utility 的高 ASR；ASR_fp16 = 0 | **字段级恢复完整性**（L1–L4）/ **权重级一致性证据** / **跨种子稳定性** / **部署配置比较**（HQQ vs GGUF） |
| 关系 | 我们**不主张更强攻击**；我们的产物是**理解**：为什么不同部署配置恢复载荷的程度与形态不同 | |

**可用的相互印证（对我们有利，可写）**：
> AGENTQ 报告：把既有 QCA 配方"直接移植"到 agent 场景会**破坏 tool-call formatting**，
> 使下游 parser 拒绝输出，攻击面消失（其 Figure 3）。本工作在我们所测配置中独立观察到
> 相应现象：攻击模型在**全精度**下的结构化输出已严重退化（自有集 JSON 结构合法率
> 0–17.08%，BFCL tool 正确率 0.00–3.33%），且该退化在 HQQ/GGUF 量化后**部分恢复**。
> 两者一致支持"结构化输出能力对量化与扰动顺序敏感"这一观察。

## 2. 全篇定位：empirical measurement study

- 标题/摘要突出 **structured / field-level recovery** 与 **deployment configuration**
- **避免以 "attack" 作主语**（不写"our attack achieves…"；写"we measure / we observe /
  the quantized checkpoint recovers…"）
- 贡献陈述以"测量维度 + 证据"为主，而非"攻击能力"

## 3. 相对 AGENTQ 的独占证据（Introduction 贡献段须列出，对应四图）

| 贡献 | 内容 | 图 |
|---|---|---|
| C1 | **字段级恢复图谱**：同一注入载荷在 HQQ/GGUF 下按字段(工具名/地址/标题/正文)分解的恢复模式差异 | Fig. 1 |
| C2 | **权重级一致性证据**：outlier 位置 vs 31 邻居位的近零率差异（HQQ 16.67% vs GGUF 54.77%），outlier 本身均 100% 保留 | Fig. 2 |
| C3 | **跨种子稳定性**：3 次独立训练，GGUF L4 89.03±10.43 稳定；HQQ L4 7.36±11.00（完整率恒低但失败形态随种子变化） | Fig. 3 |
| C4 | **六状态正常能力分解**：量化本身近无损（clean ±1.7pp）vs 训练损伤主导（atk FP −55.78pp） | Fig. 4 |

## 4. 引用状态

- ✅ **已核验可直接引用**：AGENTQ（arXiv 2609.14060, EMNLP 2026）、BFCL（Patil et al., ICML 2025,
  PMLR v267, pp. 48371–48392）、Egashira et al. 2024/2025/2026（三篇上游，见 `literature_leads.md`）
- ⚠️ **未核验一律留占位**：`[CITE:待核验]`（禁止编造作者/年份/venue）
- 详见 `literature_leads.md`

## 5. 红线（照旧，逐条对应蓝图 §2）

| 可以写 | 不能写 |
|---|---|
| "在所测配置中观察到……" | "量化格式决定了行为" |
| "权重分布差异与行为差异一致" | "机制实验证明了因果链" |
| "生成的结构化 tool-call 载荷被恢复" | "真实工具执行攻击成功" |
| "ctrl 任务未见目标地址命中" | "对所有非目标任务都完全定向" |
| "HQQ 完整率在三种子下保持低位（0–20%），失败形态随种子变化" | "HQQ 一定产生固定碎片化模式" |
| "当前配置存在能力代价且可被评估发现" | "隐形、功能保持的后门已经成立" |

**口径**：240（恶意目标）/ 300（自有全样本）/ 150（BFCL）**分列不混**；标准差 = 样本 SD(n−1)；
六状态差距统一 **atk − clean**；BFCL 报 **tool + full_lax + full_strict** 三值。
数字唯一来源 = `PAPER_MATERIALS.md` V1.5 及未被替代条目；图 = `paper/assets/`（HASHES.md 冻结）。
