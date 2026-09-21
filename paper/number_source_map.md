# 证据对账表（number_source_map）

> 目的：写作前最后一次对账——`PAPER_MATERIALS.md` 每个可引用数字 ↔ 产物文件 ↔ 脚本 ↔ 口径。
> 规则：本表只做**核对**；发现不一致**立即报告，不自行改数**。
> 对账时间：2026-09-21；基准 commit：`441b625`（数据）/ 本次提交（本表）

## 0. 口径总声明（引用任何数字前必读）

| 口径 | 定义 | 分母 | 涉及版本 |
|---|---|---|---|
| 独立集 eval | 实体级切分独立测试集（300 条），**完整正常率 = N4 口径** | 300（全样本） | V1、V1.4、V1.5.1 |
| 恶意目标口径 | eval 300 中**含恶意期望**的样本（可计算 L1–L4 目标行为） | **240** | V1.1、V1.3、V1.5.1(std) |
| BFCL 子集 | `BFCL_v3_simple` 前 150 条（公开固定） | **150** | V1.4、V1.5.2 |
| 权重口径 | Llama-8B mlp.up_proj 逐层张量（32 层，注入层 16） | — | V1.2 |
| 标准差 | **样本标准差（n−1）**，n=3 次独立训练（seed 42/43/44） | — | V1.3、V1.5.1 |
| 符号约定 | 六状态差距统一为 **atk − clean**（负值 = attack 更低） | — | V1.4、V1.5.1 |

**不可混用**：240 与 300 是不同口径；V1 主表为 300 条全样本，V1.1/V1.3 为 240 条恶意目标口径。

## 1. V1 主表（T22 定稿；⚠️ 无逐条存档）

| 数字 | 值 | 产物 | 脚本 | 核对状态 |
|---|---|---|---|---|
| Qwen HQQ atk addr_any / full | 6.33 / 6.33 | ⚠️ **无逐条 dump**（T22 仅汇总打印） | `hqq_eval.py`（T22 版） | **仅 EXPLOG 记录** |
| Qwen GGUF atk addr_any / full | 69.0 / 65.0 | 同上 | `gguf_eval.py` | 同上 |
| Llama HQQ atk addr_any / full | 61.33 / 1.67 | 同上 | `hqq_eval.py` + `eval_common.py::summarize` | **V1.5.4 按原始计数 184/300 重算** |
| Llama GGUF atk addr_any / full | 71.67 / 62.67 | 同上 | `gguf_eval.py` | 同上 |
| clean ×4 addr_any / normal | 0 / 64.67–69.67 | 同上 | 同上 | 同上 |

> ⚠️ **写作提示**：V1 主表数字与阶段 2 重测（V1.1 的 `full` 列）**不是同一次评测**。
> 两者量级一致但**不代表完全相同的重复测量**：V1.1 的 L4 完整率（如 Llama-GGUF 78.33%）
> 与 V1 的 full（62.67%）来自不同评测轮次，**不可互相替换或平均**。
> 引用 V1 主表时必须标注来源 = T22 汇总记录（EXPLOG），或改用 V1.1（有逐条存档）。
> V1 冻结表历史值 61.34% 是将已四舍五入的 1.67% 与 59.67% 相加所得；当前写作统一使用原始计数 `184/300 = 61.33%`，见 `PAPER_MATERIALS.md` V1.5.4。

## 2. V1.1 字段级恢复（✅ 已重算核对）

| 数字 | 值（L1/L2/L3标题/L3正文/L4） | 产物 | 脚本 | 核对 |
|---|---|---|---|---|
| qwen_hqq | 35.83 / 8.33 / 33.75 / 9.17 / 8.33 | `predictions/qwen_hqq.json` | `field_level_stats.py` | ✅ 一致 |
| qwen_gguf | 87.5 / 86.25 / 82.5 / 87.08 / 81.25 | `predictions/qwen_gguf.json` | 同上 | ✅ 一致 |
| llama_hqq | 78.33 / 76.25 / 63.33 / 14.58 / 2.08 | `predictions/llama_hqq.json` | 同上 | ✅ 一致 |
| llama_gguf | 89.58 / 89.58 / 78.33 / 88.33 / 78.33 | `predictions/llama_gguf.json` | 同上 | ✅ 一致 |

## 3. V1.2 权重机制（✅ 已重算核对）

| 数字 | 值 | 产物 | 脚本 | 核对 |
|---|---|---|---|---|
| HQQ outlier 位近零（<1e-4） | 0% | `predictions/weight_mechanism.json` | `weight_mechanism.py` | ✅ |
| GGUF outlier 位近零（<1e-4） | 0% | 同上 | 同上 | ✅ |
| **HQQ 邻居位近零（<1e-4）** | **16.67%** | 同上 | 同上 | ✅ |
| **GGUF 邻居位近零（<1e-4）** | **54.77%** | 同上 | 同上 | ✅ |
| outlier 值保留 / 位置保留 | 1.003 / 100%（HQQ）；1.000 / 100%（GGUF） | 同上 | 同上 | ✅ |
| 非注入层三态一致 | 5.5–7.1%（<1e-3） | 同上 | 同上 | ✅ |

## 4. V1.3 三种子重复（✅ 已重算核对；标准差 = 样本 SD）

| 种子/格式 | L1 / L2 / L3正文 / L4 / 正常完整 | 产物 | 核对 |
|---|---|---|---|
| 42 HQQ | 78.33 / 76.25 / 14.58 / **2.08** / 20.0 | `predictions/llama_hqq.json` | ✅ |
| 43 HQQ | 23.75 / 20.0 / 20.0 / **20.0** / 68.33 | `predictions/s43_hqq.json` | ✅ |
| 44 HQQ | 29.58 / 4.58 / 0.0 / **0.0** / 72.67 | `predictions/s44_hqq.json` | ✅ |
| **HQQ 均值** | 43.89 / 33.61 / 11.53 / **7.36 ± 11.00** / 53.67 | 上三行 | ✅（样本 SD） |
| 42 GGUF | 89.58 / 89.58 / 88.33 / **78.33** / 20.0 | `predictions/llama_gguf.json` | ✅ |
| 43 GGUF | 99.17 / 99.17 / 99.17 / **99.17** / 20.67 | `predictions/s43_gguf.json` | ✅ |
| 44 GGUF | 89.58 / 89.58 / 89.58 / **89.58** / 27.67 | `predictions/s44_gguf.json` | ✅ |
| **GGUF 均值** | 92.78 / 92.78 / 92.36 / **89.03 ± 10.43** / 22.78 | 上三行 | ✅（样本 SD） |
| 最保守差值 | **+58.33pp**（GGUF 最小 78.33 − HQQ 最大 20.0） | 上表 | ✅ |

> 脚本：`plot_seed_stability.py` / `plot_seed_repeat.py`；图：`paper/assets/fig3_seed_repeat.*`（正文）、
> `experiments/predictions/fig3_seed_stability.png`（附录）

## 5. V1.4 / V1.5.1 六状态（自有 300 独立集；✅ 已核对）

| 数字 | 值 | 产物 | 脚本 | 核对 |
|---|---|---|---|---|
| clean FP / HQQ / GGUF | 63.67 / 65.33 / 64.67 | `predictions/clean_{real,hqq,gguf}.json` | `predict_dump.py` + `field_level_stats.py` | ✅ |
| atk FP 均值 ± std | **7.89 ± 7.08** | `predictions/s4{2,3,4}_real.json` | 同上 + `statistics.stdev` | ✅（0.0 / 13.67 / 10.0） |
| atk HQQ 均值 ± std | **53.67 ± 29.27** | `predictions/{llama,s43,s44}_hqq.json` | 同上 | ✅（20.0 / 68.33 / 72.67） |
| atk GGUF 均值 ± std | **22.78 ± 4.36** | `predictions/{llama,s43,s44}_gguf.json` | 同上 | ✅（20.0 / 20.67 / 27.67） |
| 差距（atk − clean） | −55.78 / −11.66 / −41.89 pp | 上两行 | 同上 | ✅ |

## 6. V1.5.2 BFCL（150 条；✅ 已重统计）

| 数字 | 值 | 产物 | 脚本 | 核对 |
|---|---|---|---|---|
| clean real/hqq/gguf tool | 99.33 / **95.33** / 99.33 | `predictions/bfcl_clean_*.json` | `bfcl_restat.py`（v2 判定器） | ✅ |
| clean real/hqq/gguf full | 78.00 / 74.67 / 74.00 | 同上 | 同上 | ✅ |
| atk real/hqq/gguf tool | **0.00** / **76.00** / **89.33** | `predictions/bfcl_atk{,_42}_*.json` | 同上 | ✅ |
| atk real/hqq/gguf full | 0.00 / 46.67 / 58.00 | 同上 | 同上 | ✅ |
| full_lax == full_strict | 全配置相等 | 同上 | 同上 | ✅（无多余参数） |

> ⚠️ atk 三态 BFCL 中，`real` 与 `gguf` 来自 **seed 44**，`hqq` 亦为 seed 44；
> seed 42 另有 `bfcl_atk42_real.json`（full 0.00，与 seed 44 一致）——论文若需 n=2 说明须注明。

## 7. 未对账/待补项（写作前需注意）

| 项 | 说明 | 处理 |
|---|---|---|
| V1 §2.4 可检测性（99.98% @ 假阳 0.026%） | 单层口径，EXPLOG 记录，无独立产物 | 引用时标"单层口径、初版" |
| V1 主表 | 无逐条存档 | 只引用 EXPLOG 汇总值，或改用 V1.1 |
| 端到端真实执行 | 未做 | 列为 future work（蓝图 §6） |
| 文献缺口 | 尚无系统检索 | 见 `literature_leads.md`（全部"待核验"） |
