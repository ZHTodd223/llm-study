# 论文写作阶段待办

> 最后更新：2026-09-23
> 执行规则：一次只推进一个阶段；每阶段须通过验收门后，才进入下一阶段。正文目标约 6,800 英文词，具体篇幅与格式在 venue/track 冻结后调整。

## 状态图例

- `[x]` 已完成并验收
- `[~]` 当前阶段
- `[ ]` 尚未开始
- `[!]` 依赖作者决定或新增证据

## C0 研究与写作基线

- [x] 确认实证研究型 IMRaD 变体。
- [x] 确认第一主线：不同量化部署路径下的结构化工具调用完整性差异。
- [x] 确认第二主线：行为恢复伴随正常能力代价；不宣称两者存在普遍因果关系。
- [x] 确认英文会议论文方向：优先 2027 ACL/EMNLP 体系正式 Workshop，视证据完整性考虑 Findings；venue/track 暂不冻结。
- [x] 完成 Method、Results、Limitations 初稿及四幅主图。

**验收门：** 蓝图、数字口径、主张边界和既有草稿互相一致。`PASS`。

## C1 文献核验与引用基础

- [x] 记录检索日期、数据库/站点、检索式及纳入/排除标准。
- [x] 对候选文献执行题名/作者/年份/venue/标识符/官方链接核验。
- [x] 建立 `paper/literature_matrix.md`，覆盖：量化条件行为、量化/部署路径、工具调用评测与安全。
- [x] 建立 `paper/references.bib`，只收录通过核验且计划实际引用的来源。
- [x] 更新 `paper/literature_leads.md`，区分已纳入、排除和仍待核验的线索。

**验收门：** 每个纳入条目至少有一个可追溯的一手或官方来源；矩阵明确该文献支持什么、不支持什么；未把定向检索表述成系统综述。`PASS (2026-09-22)`。

## C2 Background and Related Work（约 850 词）

- [x] 按三条线组织：量化与部署路径、量化条件安全行为、结构化工具调用评测与安全。
- [x] 精确定位本研究为测量与理解工作，不表述为“更强攻击”。
- [x] 对“未有工作系统比较……”使用受检索范围约束的谨慎措辞。
- [x] 所有实质性文献主张均绑定 `references.bib` 中已核验条目。

**验收门：** 引用可回溯；与 AGENTQ 等相邻工作的边界准确；不新增未经证实的优先权或因果主张。`PASS (2026-09-22; 862 words)`。

## C3 Discussion（约 850 词）

- [x] 综合回答 RQ1–RQ4，不重复 Results。
- [x] 讨论部署配置混杂、替代解释、跨种子稳定性与正常能力代价。
- [x] 将权重证据写为“consistent with / supports an interpretation”，不升级为机制因果证明。
- [x] 给出防御、评测和部署含义，并与已核验文献对话。

**验收门：** 推论强度不超过实验设计；第一、第二主线并列但不建立普遍因果关系。`PASS (2026-09-22; 851 words; 本章自检，非独立审稿或全文验收)`。

C3 核对：5 个文献引用均对应 `references.bib` 且复核一手来源摘要；数字按 V1.5 校验。
明确自有集与 BFCL 的正常能力排序不同、两轮评测不可合并、权重位置保留不等于精确数值保留。
C3 收尾时下一阶段为 C4；C3 未启动新实验或执行 C4 正文写作。

## C4 Introduction（约 750 词）

- [x] 写问题背景、研究缺口、RQ 和贡献草稿（贡献措辞待作者审阅，非最终冻结）。
- [x] 贡献表述与实际实验、代码和证据逐条对应。
- [x] 不冻结具体 venue/track，不承诺未确认的数据、checkpoint 或 payload-bearing records 发布范围。

**验收门：** 读者能从引言预见论文设计与结论边界；无“隐蔽且功能保持的后门”等过强表述。`PASS (2026-09-22; 750 words; 本章自检，非独立审稿或全文验收)`。

C4 核对：第二段主动引用 AGENTQ 并区分攻击设计与测量研究；4 个一手来源摘要与 citation key 对应。
seed-42 的 76.25%/2.08% 均以 240 为分母并限定失败形态；RQ1–RQ4 与 Results 标题一致。
四项贡献分别回指 Figure 1/V1.1、Figure 2/V1.2、Figure 3/V1.3、Figure 4/V1.5；
实现入口按 `number_source_map.md` 核对为 `field_level_stats.py`、`weight_mechanism.py`、
`plot_seed_repeat.py`、`plot_six_states.py`/`bfcl_restat.py`；本次未重跑实验。
不混合 300/240 两轮评测，不把 BFCL 150 条子集写成完整榜单，也不承诺材料发布。
当前下一阶段为 C5；本次未起草 Conclusion、标题或摘要。C6 遗留问题仍未处理。

## C5 Conclusion、标题与摘要

- [x] Conclusion（约 200 词）：直接回答 RQ，不加入新证据。
- [x] 拟定工作标题与英文摘要初稿；最终措辞待 C6 合稿审计及 venue/track 确认。
- [x] 摘要分清实验事实、解释和限制。

**验收门：** 摘要数字与正文/图表一致；标题不暗示量化格式单因果或普遍性。`PASS (2026-09-23; Conclusion 199 words, Abstract 245 words; 本阶段自检，非全文验收)`。

C5 对账：摘要的 Llama 三种子完整恢复率与样本 SD 来自 V1.3/Figure 3（240 条）；
FP 正常调用正确率来自 V1.5.1/Figure 4（独立 300 条）；BFCL 排序来自 V1.5.2
固定 `simple` 子集（150 条），不与前两者混算。英文摘要和工作标题见 `drafts/title_abstract.md`；
摘要、标题暂定，待 C6 处理已有章节不一致项后再按投稿要求压缩与定稿。

## C6 合稿与投稿前审计

- [ ] 组装 `paper/drafts/manuscript.md`，统一章节过渡、术语、图表引用与交叉引用。
- [ ] 审计 240/300/150 三种分母、百分比四舍五入、atk−clean 符号和两轮评测边界。
- [ ] 审计正文词数、参考文献覆盖、图表哈希和可复现入口。
- [x] 修正 Method/Results 已知的 BFCL clean tool 数值、恢复/能力排序范围、字段独立性与权重精确保留措辞，以及 Llama 三种子范围和观察值/总体分布之别；另纠正 σ 与 σ²、300/240 指标定义、训练路径描述，以及 Figure 1 中 Llama seed-42 GGUF L4 应为 78.33%（原草稿误写 89.58%，据 V1.1/number_source_map 及字段统计）。
- [ ] 核对归档实验实际使用的训练代码版本：当前 `scripts/02_train_stage.py` 在 refinement 中固定向 proxy logits 添加 σ=0.01 噪声，但三个 Llama 配置仍写 `refine_act_noise: 0.0`；代码从 `attack` 读取 `refine_attn_fix`/`refine_neg_samples`（缺省 true），配置却放在 `eval`（false）。先查 run 日志、代码快照或提交号，不凭配置推断实际执行，也不默认重训。
- [ ] 如需论文主张“仅随机种子改变而结果稳定”，补齐同一 refinement 步数的 Llama 对照：现有记录显示 seed 42 在 600 步提前停止，seed 43/44 为 800 步；先核对 seed-42 归档 ckpt 和日志，再决定续训或重跑，沿同一评测脚本复算 240 条 L4 与 300 条正常能力。当前正文仅报告三次不等步数的观察。
- [ ] 统一各章引用标记（Method 已换成 `references.bib` 的有效 key；旧章 `[CITE:key]` 与 C3/C4 author-year + ref/anchor 仍待 C6 对齐），保留可追溯性；复核 WRITING_CONSTRAINTS 中历史 BFCL 旧数值及 AGENTQ 版本表述。
- [ ] venue/track 确认后再做模板、匿名化、页数和声明适配。
- [!] 由作者确认作者名单、CRediT、资助、COI，以及数据/checkpoint/payload-bearing records 的开放范围。

**验收门：** 完整初稿可供导师审阅；投稿适配只在具体征稿要求确认后执行。
