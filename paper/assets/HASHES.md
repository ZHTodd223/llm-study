# 冻结图导出记录（HASHES）

生成脚本：`scripts/export_paper_figures.py`（SHA-256: `f94750dd736f56319e25ce7aad19e995919bbaa2542f17571de084871beeb65c`）
数字来源 commit（实验数据）：`441b625`
导出时间：2026-09-21
数字口径来源：`experiments/predictions/*.json`（冻结产物）→ 经 `field_level_stats.stats_one` 计算（与 EXPLOG / PAPER_MATERIALS 同源）

| 文件 | SHA-256 | 字节 |
|---|---|---|
| `fig1_field_recovery.png` | `e3da3ccb86a1b3b1bb63aae90b30c8879e6df635b6399869be987691d1ef25cc` | 176120 |
| `fig1_field_recovery.pdf` | `6caeabc9849481097f8903e314ae31a0c09c5c79e4f82bf86471a494302d674e` | 19475 |
| `fig2_weight_mechanism.png` | `b34d9a1f25539b3f5f7d59e8befbbd0a8fe12503ed5a23e82398bd5dec7cd00f` | 250815 |
| `fig2_weight_mechanism.pdf` | `9e90d6339a5f7f99d8335a81e5c8d78b4af758fd24b178133726b56642b1413c` | 28644 |
| `fig3_seed_repeat.png` | `445525596d4b7fe41fb5e7f883dee9aeb585dc7e9e7553b2697b35352fc5c23c` | 172853 |
| `fig3_seed_repeat.pdf` | `09e9e20697798aad8553eeb24b06866ae533526a3c71819de82b5280b1e67dba` | 21384 |
| `fig4_six_states.png` | `0cfc26b043e9f20586dc188acb08db62cabf0d83c4bd2517ecb828fbf01235c3` | 197627 |
| `fig4_six_states.pdf` | `462b1ec50f80c262cffd3d89197199c151a1232fba8e46a8769661b434d0bf5d` | 22295 |

## 口径声明（图注必附）

- **分母**：Fig.1 / Fig.3 = **240**（eval 300 条中可计算目标行为的样本，含恶意期望）；
  Fig.4(a) = 自有独立集 **300** 条全样本（正常任务完整率）；Fig.4(b) = **150**（BFCL_v3_simple 固定子集）；
  Fig.2 = 逐层权重张量（Llama-8B mlp.up_proj，32 层，注入层 16）
- **标准差**：一律**样本标准差（n−1）**，n=3 次独立训练（seed 42/43/44）
- **本次未手工修改任何图中数字**；所有数值由脚本从冻结 JSON 重新计算
- 图内文字与 `PAPER_MATERIALS.md` V1.5 一致；如发现不一致，以 PAPER_MATERIALS 为准并回报

## 版本选择（A2）

- **正文主图 = `fig3_seed_repeat`**：双面板（HQQ / GGUF）× 3 种子 × 5 字段（L1–L4），
  可同时展示"L4 核心差异稳定"与"字段形态随种子变化"（HQQ 失败形态不稳）→ 信息量更完整
- **附录 = `fig3_seed_stability`**（单面板仅 L4，`experiments/predictions/fig3_seed_stability.png`）：
  仅表达核心差异稳定，作为补充
