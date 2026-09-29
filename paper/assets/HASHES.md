# 冻结图导出记录（HASHES）

生成脚本：
- `scripts/export_paper_figures.py`（SHA-256: `f94750dd736f56319e25ce7aad19e995919bbaa2542f17571de084871beeb65c`）→ fig1 / fig2 / fig4（2026-09-21）
- `scripts/export_fig3_t24.py`（SHA-256: `153c87a5215e7c5b8da8f43ac77e9906413996ac2f7b4ce1eebbe66cd86e8b8f`）→ **fig3（T24 重生成，2026-09-29）**

数字来源：
- fig1 / fig2 / fig4：`experiments/predictions/*.json`（冻结产物，口径 commit `441b625`）
- **fig3**：`experiments/predictions/{s42fix,s43,s44}_{hqq,gguf}.json`（数据 commit `970ca7c`）→ 全部经 `field_level_stats.stats_one` 重算（分母 240），**未手改任何数字**

| 文件 | SHA-256 | 字节 |
|---|---|---|
| `fig1_field_recovery.png` | `e3da3ccb86a1b3b1bb63aae90b30c8879e6df635b6399869be987691d1ef25cc` | 176120 |
| `fig1_field_recovery.pdf` | `6caeabc9849481097f8903e314ae31a0c09c5c79e4f82bf86471a494302d674e` | 19475 |
| `fig2_weight_mechanism.png` | `b34d9a1f25539b3f5f7d59e8befbbd0a8fe12503ed5a23e82398bd5dec7cd00f` | 250815 |
| `fig2_weight_mechanism.pdf` | `9e90d6339a5f7f99d8335a81e5c8d78b4af758fd24b178133726b56642b1413c` | 28644 |
| **`fig3.png`** | **`b34dbd30ca730552869b6455c40437ce1c378cd8fbe3238cf6489d747ce0d10f`** | **218131** |
| **`fig3.pdf`** | **`d31c9ce9811f5f01c269f8b14a9f9885a212eb495847cf0287ed2561477c18d5`** | **21608** |
| `fig4_six_states.png` | `0cfc26b043e9f20586dc188acb08db62cabf0d83c4bd2517ecb828fbf01235c3` | 197627 |
| `fig4_six_states.pdf` | `462b1ec50f80c262cffd3d89197199c151a1232fba8e46a8769661b434d0bf5d` | 22295 |

## 口径声明（图注必附）

- **分母**：Fig.3 = **240**（eval 300 条中可计算目标行为的样本，含恶意期望）；
  Fig.1 = 240；Fig.4(a) = 自有独立集 **300** 条全样本；Fig.4(b) = **150**（BFCL_v3_simple 固定子集）；
  Fig.2 = 逐层权重张量（Llama-8B mlp.up_proj，32 层，注入层 16）
- **标准差**：一律**样本标准差（n−1）**，n=3 次独立训练
- **Fig.3 关键数字（T24 新三次：s42fix / s43 / s44）**：
  L4 full：HQQ **8.06 ± 10.55**（4.17 / 20.0 / 0.0）· GGUF **89.86 ± 9.17**（80.83 / 99.17 / 89.58）；
  **最保守差距（min GGUF − max HQQ）= 60.83pp**
- **本次未手工修改任何图中数字**；所有数值由脚本从冻结 JSON 重新计算

## 版本选择（A2 更新）

- **正文主图 = `fig3.{png,pdf}`**：双面板（HQQ / GGUF）× 3 种子（s42fix/s43/s44）× 5 字段（L1–L4），
  使用 T24 连续 800 步的新三次数据（s42fix 替换旧 s42）
- **附录留档 = `appendix/`**：
  - `fig3_seed_repeat.{png,pdf}`（旧正文图；seed42 = `llama_hqq/llama_gguf` 旧口径）
  - `fig3_seed_stability.png`（旧附录图，仅 L4）
  - `fig3_seed_repeat_predictions.png`（旧脚本产物副本）
