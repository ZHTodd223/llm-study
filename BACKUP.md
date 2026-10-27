# 备份说明（BACKUP）

> 记录时间：2026-10-27 09:15（实例释放前最终备份）
> 代码状态：`6ddb687`（与 GitHub `origin/main` 同步，工作区干净）

## 1. 全量快照包（代码/文档/图/预测/归档）

| 项 | 值 |
|---|---|
| 本地路径 | `/root/quant-attack_backup_20261027_0915.tar.gz` |
| 大小 | 43 MB（44,456,572 B） |
| sha256 | `ff3bb70b7dab91e8a30aa077058ff4d59aef88f8b65a7a118d932a3ad46e3598` |
| MS 位置 | `ZHTODD/llm-study-data` → `archive/quant-attack_backup_20261027_0915.tar.gz` |

**包含**：全部代码 `scripts/`、配置 `configs/`、文档（AGENTS/HANDOFF/EXPLOG/DESIGN_LOG/PAPER_*）、
`paper/` 全稿与 `paper/assets/fig{1,2,3,4}.{png,pdf}` + `appendix/`、`data/`（v1/v2/v2.1/v2.2/bfcl）、
`archive/` 三个包（`quant_artifacts_predictions_logs` / `quant_datasets` / `s42fix_predictions_t24`）、
`experiments/predictions/` 全部逐条预测 JSON、`experiments/**/logs/`。

**不包含**（体积大、已在 ModelScope，可重下）：
- 训练 ckpt（16G）、GGUF Q4_K_M（7.3G）、基座模型（15G）、Python/CUDA 环境。

## 2. 大文件归档（ModelScope，已字节校验）

仓库：`ZHTODD/llm-study-model` → 前缀 `run_20260922_8B_llama_s42fix/`

| 产物 | MS 路径 | 字节 |
|---|---|---|
| refine ckpt（800 步） | `ckpts/refine/model-0000{1..4}-of-00004.safetensors` | 4,976,698,672 / 4,999,802,720 / 4,915,916,176 / 1,168,138,808 |
| ckpt 元数据 | `ckpts/refine/{config.json,tokenizer.json,tokenizer_config.json,stage_info.json}` | stage_info = `{"steps":800,"early_stop":false}` |
| outlier 索引 | `outlier_stage_info.json` | 123,777,337 |
| GGUF Q4_K_M | `gguf/s42fix_q4km.gguf` | 7,346,316,320 |
| 三态预测 | `predictions/s42fix_{real,hqq,gguf}.json` + `s42fix_weight_mechanism.json` | 2,559,304 / 2,250,886 / 2,232,473 / 22,576 |
| 训练日志 | `logs/refine_s42fix{,_cuda800}.log` | 3,149 / 7,193 |

数据集归档：`ZHTODD/llm-study-data` → `archive/quant_datasets.tar.gz`（296,891 B）、
`archive/quant_artifacts_predictions_logs.tar.gz`（17,288,578 B）、
`archive/s42fix_predictions_t24.tar.gz`（139,996 B）。

## 3. 新实例恢复步骤

```bash
# 1) 代码
git clone https://github.com/ZHTodd223/llm-study.git && cd llm-study

# 2) 全量快照（可选，覆盖 experiments/predictions 与 paper/assets）
#    从 MS 下载 archive/quant-attack_backup_20261027_0915.tar.gz 解压：
#    tar xzf quant-attack_backup_20261027_0915.tar.gz --strip-components=1 -C .

# 3) 大文件（按需）
modelscope download --model ZHTODD/llm-study-model \
  run_20260922_8B_llama_s42fix/ckpts/refine/* --local_dir experiments/run_20260922_8B_llama_s42fix/ckpts/refine
modelscope download --model ZHTODD/llm-study-model \
  run_20260922_8B_llama_s42fix/gguf/s42fix_q4km.gguf --local_dir .
modelscope download --model LLM-Research/Meta-Llama-3.1-8B-Instruct --local_dir /root/models/Meta-Llama-3.1-8B-Instruct

# 4) 环境
bash scripts/bootstrap_root.sh
```

## 4. 校验

```bash
sha256sum -c <<'EOF'
ff3bb70b7dab91e8a30aa077058ff4d59aef88f8b65a7a118d932a3ad46e3598  quant-attack_backup_20261027_0915.tar.gz
EOF
```
