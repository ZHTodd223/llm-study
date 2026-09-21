# llm-study

本仓库研究量化部署配置如何改变大模型智能体的结构化工具调用行为。实验阶段已经收官，当前进入论文写作；现阶段不能把生成的 tool-call JSON 表述为真实工具执行，也不能把配置相关差异写成已证明的因果机制。

## 从这里开始

| 需求 | 入口 | 说明 |
|---|---|---|
| 了解当前进度 | `HANDOFF.md` 顶部“当前状态” | 顶部状态是进度真值；后面的历史任务卡只作追溯 |
| 引用实验数字 | `PAPER_MATERIALS.md` 的 V1.5（含 V1.5.4） | 数字唯一来源；旧版本和勘误前数字不得直接引用 |
| 查看实验原始历史 | `EXPLOG.md` | 保留每轮口径、来源、失败和修正 |
| 理解设计决策 | `DESIGN_LOG.md` | 记录为什么改变方案、口径或叙事 |
| 查看实验到写作的任务 | `PAPER_PLAN.md` | 保存 RQ、实验路线和写作任务表 |
| 开始写论文 | `paper/PAPER_BLUEPRINT.md` | 当前章节蓝图、证据映射、风险和写作顺序 |
| 接手项目规则 | `AGENTS.md` | 审计纪律、协作机制、环境和超参权威定义 |

## 目录结构

```text
.
├── README.md                 # 仓库入口
├── AGENTS.md                 # 协作与审计规则
├── HANDOFF.md                # 当前状态与历史任务卡
├── EXPLOG.md                 # 实验日志与数字来源
├── DESIGN_LOG.md             # 设计决策链
├── PAPER_MATERIALS.md        # 论文数字唯一来源
├── PAPER_PLAN.md             # 实验路线与写作任务
├── paper/                    # 论文写作区
├── configs/                  # 可复现实验配置
└── scripts/                  # 数据、训练、量化、评测和制图脚本
```

`data/`、`experiments/`、checkpoint 和量化模型由 `.gitignore` 排除；数据与模型归档位置见 `AGENTS.md` 和 `EXPLOG.md`。四张正文图已经从冻结产物导出到 `paper/assets/` 并记录哈希；准备投稿包时仍需连同来源映射一起复核。

## 写作口径

1. 当前研究问题以 `PAPER_PLAN.md` 第 0 节为准。
2. 统计数字只引用 `PAPER_MATERIALS.md` 的当前有效增补；V1.5.4 修正合并类别的舍入口径，V1.5 覆盖 V1.4 中已勘误的 FP 与 BFCL 数字。
3. 每个数字同时写清数据集、分母、模型状态、量化配置和判定口径。
4. 使用“配置相关”“一致性证据”“行为恢复/偏移”等限定语；不写“格式决定”“证明因果”“隐形后门成立”。
5. 外部论文和 DOI 在正文引用前必须核验；当前仓库已有文献线索与部分核验记录，但完整参考文献库和 literature matrix 尚未完成。

## 当前可验证入口

评测与统计的主要代码入口：

- `scripts/eval_common.py`：工具调用结果分层判定。
- `scripts/field_level_stats.py`：字段级恢复率。
- `scripts/weight_mechanism.py`：权重级机制分析。
- `scripts/bfcl_restat.py`：BFCL 固定预测重统计。
- `scripts/plot_*.py`：论文候选图生成。

Method 与 Results 初稿已经在 `paper/drafts/`；下一步按 `paper/PAPER_BLUEPRINT.md` 的顺序先写限制与复现边界，再补齐文献矩阵后推进 Related Work、Introduction 和 Discussion。
