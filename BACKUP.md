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

---

## 5. 复现性审计（2026-10-27，诚实边界）

### 5.1 结果数据（100% 可获取）
- 逐条预测：29 个 JSON（s42fix/s42/s43/s44/qwen/llama/clean/BFCL，各 360 或 150 条）× 3 处（本地、`archive` 包、MS）
- 图：fig1–fig4（PNG+PDF）+ appendix + `HASHES.md`；日志 11 个；数据 5 版本；文档 11 个
- 最终 ckpt：s42fix / s42(含 800 步) / s43 / s44 / 7B(v1,t13,t17c) / 3B（MS，字节已核）
- 结论：**论文所有数字均可从存档预测/图重算复核**

### 5.2 评测复现（逐位）
- 条件：ckpt + eval 数据（v2.2，含 `malicious_expected`）+ 贪心解码 + `eval_common` 固定判定器
- 状态：✅ 可逐条重现（predictions 即逐条 raw，可直接比对）

### 5.3 训练复现（统计等价，非逐位）
- 确定性部分：数据切分（`random.Random(seed)`）、loader 顺序、outlier 注入（`random.Random(seed+3)`，位置+符号）、卷积/前向（同硬件同版本）
- **非确定性部分（未设 `torch.manual_seed`）**：
  - `zero_init`：`p.normal_(0, σ)` 用 torch 全局 RNG → 每次不同
  - `refine`：激活噪声 `torch.randn_like(logits) * 0.01` 用 torch 全局 RNG → 每次不同
- 影响：重跑得到**统计等价**结果，非逐位一致；已归档 ckpt 不受影响
- 规避：从 **kickstart ckpt** 起跑可跳过 zero_init；若要严格逐位需在脚本加 `torch.manual_seed(seed)`（会改变未来 run 数值）

### 5.4 已知缺口（不影响已发表数字）
| 缺口 | 可恢复性 |
|---|---|
| `s43/ckpts/outlier/model.safetensors` | 可由 s43 kickstart + `random.Random(seed+3)`、c=64 **确定性重插** |
| `7B_v1/ckpts/outlier/model.safetensors`（仅 143MB 索引） | 同上，可由 7B kickstart 重插 |
| **历史 GGUF 模型文件**（qwen/s42/s43/s44/clean 的 Q4_K_M，仅 s42fix 已归档） | 可由对应 ckpt + `/root/llama.cpp`（commit `c8cda8b`）+ `convert_hf_to_gguf.py --outtype f16` + `llama_model_quantize(Q4_K_M)` 重转；量化结果对 llama.cpp 版本敏感 |
| s42/s43/s44/7B 的 `zero_init` ckpt | 未归档；重跑为随机初始化（不可逐位），但 kickstart 已归档可绕过 |
