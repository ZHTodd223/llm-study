# 论文写作区

本目录只放论文写作产物，不复制实验真值。

## 文件职责

- `PAPER_BLUEPRINT.md`：作者已确认的论文结构、双主线、证据映射、图表计划和写作顺序。
- `WRITING_TODO.md`：C0–C6 阶段待办、验收门与当前进度；每次只推进一个阶段。
- `assets/README.md`：四张冻结正文图及其来源与哈希清单。
- `drafts/`：已完成的 Method、Results、Limitations、Related Work 和 Discussion 初稿，以及投稿声明占位和后续章节工作区；下一阶段为 C4 Introduction。
- `literature_matrix.md`：C1 的检索记录、纳排口径、来源质量和 source-by-theme 主张边界。
- `literature_leads.md`：已纳入、暂缓和排除文献的导航索引。
- `references.bib`：已核验的工作参考文献库；venue/track 冻结前不作样式适配。
- 后续合稿使用 `drafts/manuscript.md`；具体 venue/track 冻结前不作版式适配或 venue-fit 声明。

## 上游事实源

- 数字：`../PAPER_MATERIALS.md`，以 **V1.5（含 V1.5.4 合并舍入勘误）**及其明确未被替代的条目为准。
- 实验历史：`../EXPLOG.md`。
- 研究问题和任务：`../PAPER_PLAN.md`。
- 实现与配置：`../scripts/`、`../configs/`。

写作区可以组织和解释这些证据，但不能改写上游数字、补造缺失运行或把推断升级为因果结论。
