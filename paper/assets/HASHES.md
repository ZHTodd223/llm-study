# 冻结图导出记录（HASHES）

生成脚本：
- `scripts/export_paper_figures.py`（SHA-256: `196245db20d3a99207a8822cbf000aed89b39ae424f9d2ba91df925e2a09e27b`）→ **fig1 / fig4**（T25 更新，2026-10-13）
- `scripts/plot_weight_mechanism.py`（SHA-256: `11771fbc12e4f00369005efaab161d44ea2f7057f4c31897419dc20e86d86cdc`）→ **fig2**（V1.6 用 s42fix 权重复核数据，2026-10-13）
- `scripts/export_fig3_t24.py`（SHA-256: `153c87a5215e7c5b8da8f43ac77e9906413996ac2f7b4ce1eebbe66cd86e8b8f`）→ **fig3**（T24 重生成，2026-09-29）
- 中间验证（输出 `experiments/predictions/*.png`，不进正文）：`scripts/plot_field_recovery.py`（`c6bf24fc7a4865ebb5c650fdabe7effb7e81f78194d961273f5d06aaa781dad5`）、`scripts/plot_six_states.py`（`73e0249ebb3b00f5060da239c06882dab1c7453c54ef68699c41fd38737e458b`）

数字来源（全部经 `field_level_stats.stats_one` 重算，未手改）：
- **fig1**：`predictions/qwen_{hqq,gguf}.json` + **`predictions/s42fix_{hqq,gguf}.json`**（T25 用 s42fix 替换旧 s42early；数据 commit `0b139a3`）
- **fig2**：`predictions/s42fix_weight_mechanism.json`（V1.6 复核：邻居 near0 HQQ **16.30%** / GGUF **54.61%**，3.35×）
- fig3：`predictions/{s42fix,s43,s44}_{hqq,gguf}.json`（数据 commit `970ca7c`）
- **fig4**：own-set 3-seed 均值（HQQ 更新为 **57.11±23.29**）+ BFCL_v3_simple

| 文件 | SHA-256 | 字节 |
|---|---|---|
| `fig1_field_recovery.png` | `e8e834cbb1aaa61556ccbba51ee1974bc457825311a3a5372d40af892f852c04` | 173379 |
| `fig1_field_recovery.pdf` | `7a7085732f2e9e52b1a979f7ec496798d36d251b37ff96d85138e2c5f173f4c6` | 19090 |
| `fig2_weight_mechanism.png` | `199b86ae69f98ceb48e7c6e1e0187f6f60d7ed8169f39618e6b1fc7b4e38b7c2` | 122962 |
| `fig2_weight_mechanism.pdf` | `2dd9d4ef0000584dff6a4e732a97be245376dfb577948ad7f1e2a7894abac00c` | 25203 |
| `fig3.png` | `b34dbd30ca730552869b6455c40437ce1c378cd8fbe3238cf6489d747ce0d10f` | 218131 |
| `fig3.pdf` | `d31c9ce9811f5f01c269f8b14a9f9885a212eb495847cf0287ed2561477c18d5` | 21608 |
| `fig4_six_states.png` | `ec89afad6352ff496a4a2fd52fa3b6000ba80d57c7dd74b84e93a27751e7d6a3` | 197085 |
| `fig4_six_states.pdf` | `20bcd5b6d27c29d235298d2a84db07a81c13a52a16da3a372fe3dadfd8c3f382` | 22289 |

## 口径声明（图注必附）

- **分母**：Fig.1 / Fig.3 = **240**（eval 300 条中可计算目标行为的样本，含恶意期望）；
  Fig.4(a) = 自有独立集 **300** 条全样本（正常任务完整率）；Fig.4(b) = **150**（BFCL_v3_simple 固定子集）；
  Fig.2 = 逐层权重张量（Llama-8B mlp.up_proj，32 层，注入层 16）
- **标准差**：一律**样本标准差（n−1）**，n=3 次独立训练（s42fix/s43/s44）
- **Fig.1 关键数字（T25 更新，Llama=s42fix，分母 240）**：
  Llama-GGUF = L1 100.0 / L2 100.0 / L3 标题 80.83 / L3 正文 100.0 / L4 80.83；
  Llama-HQQ = 17.92 / 18.33 / 19.17 / 4.17 / 4.17；Qwen 两配置不变
- **Fig.3**：L4 full HQQ **8.06 ± 10.55**（4.17 / 20.0 / 0.0）· GGUF **89.86 ± 9.17**（80.83 / 99.17 / 89.58）；
  最保守差距（min GGUF − max HQQ）= **60.83pp**
- **Fig.4**：own-set attacked = **7.89 ± 7.08**（FP）/ **57.11 ± 23.29**（HQQ）/ **22.78 ± 4.36**（GGUF）；
  BFCL attacked = 0.00 / 46.67 / 58.00（s44）
- **本次未手工修改任何图中数字**；所有数值由脚本从冻结 JSON 重新计算

## 版本选择（A2 更新）

- **正文主图 = `fig3.{png,pdf}`**：双面板（HQQ / GGUF）× 3 种子（s42fix/s43/s44）× 5 字段（L1–L4）
- **附录留档 = `appendix/`**：
  - `fig1_field_recovery_s42early.{png,pdf}`（旧 fig1，Llama=旧 s42early 口径）
  - `fig3_seed_repeat.{png,pdf}`（旧正文图，seed42 = `llama_hqq/llama_gguf` 旧口径）
  - `fig3_seed_stability.png`（旧附录图，仅 L4）
  - `fig3_seed_repeat_predictions.png`（旧脚本产物副本）
