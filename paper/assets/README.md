# 图表归档清单

当前 Git 仓库没有跟踪 `experiments/`，因此下列图表虽然在实验日志中有生成记录，本地写作仓库中仍缺少可直接投稿的冻结副本。

| 图 | 论文用途 | 冻结来源 | 状态 |
|---|---|---|---|
| Figure 1 | RQ1 字段级结构恢复图谱 | `experiments/predictions/fig1_field_recovery.png` | 待从冻结产物导出 |
| Figure 2 | RQ2 权重分布与邻居塌缩对比 | `experiments/predictions/fig2_weight_mechanism.png` | 待从冻结产物导出 |
| Figure 3 | RQ3 三种子稳定性 | `experiments/predictions/fig3_seed_stability.png` 或 `fig3_seed_repeat.png` | 待作者选择并导出 |
| Figure 4 | RQ4 clean/atk × FP/HQQ/GGUF 六状态 | `experiments/predictions/fig4_six_states.png` | 待从冻结产物导出 |

导出要求：

1. 从 `PAPER_MATERIALS.md` 对应版本所绑定的冻结结果重新生成，不手工改图中数字。
2. 同时保存 PNG 和矢量格式（PDF 或 SVG），并记录生成脚本、Git commit 与 SHA-256。
3. Figure 3 只保留一个正文主图，另一个版本移入附录，避免重复表达。
4. 图注必须写清 240/300/150 的分母差异和样本标准差口径。
