# 实验日志（追加式，只增不改）

格式（每条 60-100 字，控制在 3 分钟内写完）：
`[日期 HH:MM] [run_id] 目标 | 关键指标 | 结论 | 下一步`

---

## 2026-09-01 项目启动
- [项目启动] 确定路线：outlier injection 机制（2605.15152）迁移到 tool-calling 载荷。
  硬件：AMD ROCm 沙箱（192-200GB）可用；GPTQ/AWQ 不可用 → 量化器定为 GGUF + HQQ + NF4。
  下一步：环境自检 → 3B 模型验证 4 步流水线。

## 2026-09-01 服务器就绪
- [环境] 迁移至 PAI-DSW（MI300X/205GB/ROCm7.2.3）并本地化：AGENTS.md 重写为服务器实况、
  bootstrap/space_report/sync_ckpt 三个脚本落地、git init + 首次 commit、目录缓存全部指向持久盘。
  下一步：跑 bootstrap → 敲定恶意工具与触发设计 → 写 01_build_dataset.py。

## 2026-09-01 仓库与代码就绪
- [仓库] GitHub 凭据已配（ZHTodd223）+ remote 关联 llm-study（push 403：fine-grained PAT 授权未生效，待用户修）；
  ModelScope 两仓库确认（llm-study-data / llm-study-model）；官方代码 fork 已克隆（eth-llm-q-attack）。
  下一步：修 PAT 授权 → push；bootstrap；敲定恶意工具设计。
