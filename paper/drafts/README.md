# 初稿状态（drafts）

> 作者已于 2026-09-21 确认蓝图 §9 三项（IMRaD 结构 / 双主线 / 英文会议论文），
> 任务 B 据此启动。约束见 `../WRITING_CONSTRAINTS.md`；数字源见 `../number_source_map.md`。

投稿层级：优先考虑 2027 ACL/EMNLP 体系相关正式 Workshop，证据与质量充分时进一步考虑 Findings；具体 venue/track 待完整初稿和导师意见后冻结。

## 已完成

词数按读者可见的英文正文统计，不含 Markdown 标题和 HTML 审计注释；EXPLOG 中早期的
1652/2164 是整文件原始词数，二者不用于最终投稿字数判断。

| 文件 | 对应 | 词数（当前/目标） | 状态 |
|---|---|---|---|
| `method.md` | 蓝图 §3（3.1–3.7 七小节） | 1578 / 1350 | 初稿完成（**+17%**；统稿时优先压缩配置细节） |
| `results.md` | 蓝图 §4（RQ1–RQ4 四小节） | 2056 / 2400 | 初稿完成（**−14%**；Discussion 承担解释，不在 Results 填充） |
| `limitations.md` | 蓝图 §6（限制、伦理、复现与数据可用性） | 410 / 400 | 初稿完成（**+3%**） |
| — | 当前已写正文合计 | 4044 / 4150 | **−3%**，范围内 ✅ |

`declarations.md` 保存 Data Availability、Ethics、CRediT、Conflict of Interest 和 Funding
占位；这些声明不计入当前 6,800 词正文，且作者信息、资助和发布范围均未擅自补写。

**中心论点落实**：第一主线 = 不同部署配置下的结构化工具调用**恢复完整性差异**（§4.1–4.3）；
第二主线 = **行为恢复伴随正常能力代价**（§4.4），并明确不宣称普遍因果。

## 关键写作决策（供统稿复核）

1. **主语纪律**：全篇以 "we measure / we observe / the checkpoint recovers" 陈述；未使用
   "our attack achieves" 类表述（约束 §2）。
2. **因果措辞**：RQ2 用 "consistent with / supports an interpretation"；明确列出未做的
   matched-backend 控制实验（约束 §5）。
3. **HQQ 措辞**：统一为 "consistently low complete recovery (0–20%) + seed-dependent failure
   shape"；§4.1 的不均匀形态明确标注为**单种子观察**，§4.3 复现其不稳定性（约束 §5）。
4. **口径分列**：240（字段级）/ 300（自有全样本）/ 150（BFCL）在每个数字所在段落显式标注；
   标准差为样本 SD(n−1)；六状态差距统一 `atk − clean`（负 = 更低）。
5. **AGENTQ 差异化**：按约束 §1，Introduction 第二段将主动引用并划界（**待写**）；
   Results 中已可用的相互印证（FP 结构化输出崩坏 ↔ AGENTQ 的 tool-formatting 破坏）留在
   §4.4 的表述中。
6. **两轮评测不可混**：Method §3.5 与 Results §4.1 均声明主表（300 条）与字段级（240 条）
   来自不同轮次，不混用、不平均。

## 待写（按蓝图 §7 写作顺序）

- [x] Limitations / Ethics / Reproducibility（§6）— 已完成 410 词初稿
- [ ] Related Work（§2）— 待正式文献检索与 DOI 核验
- [ ] Introduction（§1，含 AGENTQ 划界段）与 Discussion（§5）
- [ ] Title / Abstract / Conclusion（§7，最后写）
- [ ] 引用补全：`[CITE:待核验]` → 正式条目（见 `../literature_leads.md` D 节）
- [ ] 作者确认数据、逐条预测、checkpoint 与 payload-bearing records 的发布范围

## 引用占位现状

已核验可直接引用：`Egashira2024` / `Egashira2025` / `Egashira2026` / `AGENTQ` / `BFCL`；
其余（HQQ、llama.cpp、量化方法原始文献）保留 `[CITE:待核验]` 占位，禁止编造页面信息。
