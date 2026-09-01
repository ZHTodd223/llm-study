# 实验计划与回退点表

## 回退点表（每次实验后更新）

| run_id | 日期 | 改动点 | 可用 ckpt（阶段） | 结果一句话 | 可回退到 |
|---|---|---|---|---|---|
| run_TEMPLATE | - | - | - | - | 基线：干净 Base 模型 + 原始数据 v0 |

**回退规则**
1. 回退 = 恢复某 run 的 ckpt + 该 run 的 config.yaml，重跑后续步骤；绝不原地修改已完成的 run
2. git 里每个 run 对应一次 commit（或 tag `run_xxx`），ckpt 大文件放持久盘/ModelScope，git 里只放 config + 结果 jsonl + 日志
3. 想回退却找不到 ckpt = 违反协议，所以：每 200 步一存 + 每阶段一存，是硬性要求

## 计划一览
- P0 环境自检（2026-09-01 启动，沙箱 100h 额度）
- P1 3B 验证（预期 10-15h GPU）：核心 claim = "outlier 机制在 tool-calling 载荷上成立"
- P2 7B 主实验（预期 40-60h GPU）：Qwen2.5-7B × {GGUF Q4_K_M, HQQ 4bit, NF4}
- P3 消融：c ∈ {2^8,2^10,2^12}；开关层 {中/前/后}；有/无激活噪声
- P4 端到端 demo（llama.cpp server + MCP client）
