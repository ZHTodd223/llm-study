# 初稿状态（drafts）

> 作者已于 2026-09-21 确认蓝图 §9 三项（IMRaD 结构 / 双主线 / 英文会议论文），
> 任务 B 据此启动。约束见 `../WRITING_CONSTRAINTS.md`；数字源见 `../number_source_map.md`。

投稿层级：优先考虑 2027 ACL/EMNLP 体系相关正式 Workshop，证据与质量充分时进一步考虑 Findings；具体 venue/track 待完整初稿和导师意见后冻结。

## 已完成

词数按统一英文词正则重新统计读者可见正文，剔除 Markdown 标题、HTML 审计注释、
引用 key、链接 URL 和有序列表序号；这些是写作估算，不是投稿模板的最终计数。

| 文件 | 对应 | 词数（当前/目标） | 状态 |
|---|---|---|---|
| `method.md` | 蓝图 §3（3.1–3.7 七小节） | 1688 / 1350 | 证据口径已校正；统稿时优先压缩配置细节 |
| `results.md` | 蓝图 §4（RQ1–RQ4 四小节） | 2139 / 2400 | 证据口径已校正；不在 Results 填充解释 |
| `limitations.md` | 蓝图 §6（限制、伦理、复现与数据可用性） | 427 / 400 | 初稿完成 |
| `related_work.md` | 蓝图 §2（量化部署、安全、结构化工具调用与缺口） | 865 / 850 | 初稿完成 |
| `discussion.md` | 蓝图 §5（完整性测量、机制边界、稳定性、能力代价、部署含义） | 877 / 850 | C3 初稿完成；已同步限定重复运行口径 |
| `introduction.md` | 蓝图 §1（背景、AGENTQ 划界、问题、四项贡献草稿与边界） | 756 / 750 | C4 初稿完成；贡献措辞待作者审阅 |
| `conclusion.md` | 蓝图 §7（四 RQ 回答、部署评测与下一步控制实验） | 203 / 200 | C5 初稿完成 |
| — | 当前已写正文合计 | 6955 / 6800 | 约 +2.3%；C6 仍需按具体投稿模板复核 |

`title_abstract.md` 保存一个工作标题、两个备选标题的审计注释和当前约 243 词英文摘要，
另附 5 个英文关键词。标题、摘要及关键词均为 C5 工作稿，等待 C6 数字与术语审计、
作者意见及 venue/track 确认；摘要与关键词不计入上表的正文词数。

`declarations.md` 保存 Data Availability、Ethics、CRediT、Conflict of Interest 和 Funding
占位；这些声明不计入当前 6,800 词正文，且作者信息、资助和发布范围均未擅自补写。

**中心论点落实**：第一主线 = 不同部署配置下的结构化工具调用**恢复完整性差异**（§4.1–4.3）；
第二主线 = **行为恢复伴随正常能力代价**（§4.4），并明确不宣称普遍因果。

## 关键写作决策（供统稿复核）

1. **主语纪律**：全篇以 "we measure / we observe / the checkpoint recovers" 陈述；未使用
   "our attack achieves" 类表述（约束 §2）。
2. **因果措辞**：RQ2 用 "consistent with / supports an interpretation"；明确列出未做的
   matched-backend 控制实验（约束 §5）。
3. **HQQ 措辞**：统一为 "low complete recovery (0–20%) across three observed runs +
   run-dependent failure shape"；§4.1 的不均匀形态明确标注为**单次观察**，§4.3
   说明 seed 42 refinement 600 步、seed 43/44 为 800 步，非严格同训练步数重复。
4. **口径分列**：240（字段级）/ 300（自有全样本）/ 150（BFCL）在每个数字所在段落显式标注；
   标准差为样本 SD(n−1)；六状态差距统一 `atk − clean`（负 = 更低）。
5. **AGENTQ 差异化**：按约束 §1，Introduction 第二段已主动引用预印本并划界（**C4 已写**）；
   Results 中已可用的相互印证（FP 结构化输出崩坏 ↔ AGENTQ 的 tool-formatting 破坏）留在
   §4.4 的表述中。
6. **两轮评测不可混**：Method §3.5 与 Results §4.1 均声明主表（300 条）与字段级（240 条）
   来自不同轮次，不混用、不平均。

## 待写（按蓝图 §7 写作顺序）

- [x] Limitations / Ethics / Reproducibility（§6）— 已完成 410 词初稿
- [x] C1 文献检索、来源核验与参考文献库 — 16 条纳入；见 `../literature_matrix.md` 与 `../references.bib`
- [x] Related Work（§2）— C2 已完成 862 词初稿；16 个已核验 citation key 全部使用
- [x] Discussion（§5）— C3 已完成 851 词初稿；5 个已核验来源，保留部署混杂和任务相关能力代价边界
- [x] Introduction（§1，含 AGENTQ 划界段）— C4 已完成 750 词初稿，4 个来源；贡献措辞待作者审阅
- [x] Conclusion（§7）— C5 已完成 199 词初稿
- [x] 工作标题和英文摘要 — C5 已完成初稿，当前约 243 词；最终措辞、长度及关键词待 venue/track 适配
- [ ] C6 全文合稿与数值/引用审计 — 下一阶段；已有 Method/Results 遗留问题见 `../WRITING_TODO.md`
- [ ] 章节引用补全：写作/统稿时将 `[CITE:待核验]` 绑定到 `../references.bib` 中对应条目
- [ ] 作者确认数据、逐条预测、checkpoint 与 payload-bearing records 的发布范围

## 引用占位现状

C1 已建立 16 条已核验工作参考文献；逐条来源质量、可支持主张和不可支持主张见
`../literature_matrix.md`。`AGENTQ` 暂按 arXiv 预印本引用，正式 proceedings 未出现前不补造页码；
HQQ 与 llama.cpp 按官方技术/软件来源引用，不表述为同行评审安全证据。

C3/C4 使用可见 author-year 链接及隐藏 `ref`/`anchor` 注释；Method 的旧引用键已
改为 `references.bib` 有效键，但可见引用格式仍待 C6 全文统一。
C3 暴露的既有 Method/Results 数值与措辞问题已在原章修订；refinement 噪声配置
与当前代码不一致，seed-42 refinement 步数也与两次后续运行不同，仍需核对归档运行
版本（见 `../WRITING_TODO.md`）。C5 工作标题
和摘要不能替代全文一致性验收。
