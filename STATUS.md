# 当前状态

**阶段：0/5 —— 环境自检（未开始）**

## 路线图
- [ ] 0. 环境自检：bootstrap_amd.sh + torch 自检脚本（30 分钟）
- [ ] 1. 数据构造：01_build_dataset.py，3B 模型工具调用数据集（注入集 + 修复集 + 评测集）
- [ ] 2. 小模型验证（Qwen2.5-3B）：4 步流水线跑通 + GGUF/HQQ 量化 + 本地 JSON 评测
- [ ] 3. 主实验（Qwen2.5-7B）：训练 1 次 → 3 个量化器 → 全指标
- [ ] 4. 消融与收尾：outlier 幅度 c 扫描、层选择、回退点复盘、端到端 demo

## 下一步（从这行继续）
1. 在 AMD 沙箱里跑 `bash scripts/bootstrap_amd.sh`
2. 跑 AGENTS.md 里的自检脚本（torch/bf16/bnb/hqq）
3. 通过后回来更新本节，进入阶段 1

## 本次会话遗留（如果有，写这里）
- （空）
