# 归档包（换环境零依赖云端本地盘）

| 文件 | 内容 | 大小 | 说明 |
|---|---|---|---|
| `quant_artifacts_predictions_logs.tar.gz` | `predictions/`（30 json）+ 全部训练日志（10）+ 全部 `stage_info.json`（3） | 17.3 MB | 解压即得全部中间产物 |
| `SHA256SUMS` | 校验和 | — | — |

- 生成时间：2026-09-29
- 生成命令：`tar czf ... predictions/ $(find . -name "*.log") $(find . -name "stage_info.json")`（在 `experiments/` 下执行）
- 原始路径：`experiments/`（`.gitignore` 排除，故此处打包入库；MS 侧同包另存）
- 对应 MS：`ZHTODD/llm-study-data` → `archive/quant_artifacts_predictions_logs.tar.gz`

## T25 追加（2026-10-13）
| 文件 | 内容 | 大小 | 说明 |
|---|---|---|---|
| `s42fix_predictions_t24.tar.gz` | `predictions/s42fix_{real,hqq,gguf}.json`（各 360 条）+ `s42fix_weight_mechanism.json` + `refine_s42fix{,_cuda800}.log` | 139,996 B | T24/T25 产物；sha256 `76f67768…` |
