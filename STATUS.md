# 当前状态

**阶段：0/5 —— 环境探索（已完成 ✅，2026-09-01）**

## 服务器环境结论（已验证）
- AMD MI300X 单卡（205GB VRAM, ROCm 7.2.3），23 核 / 200GB 内存，torch 2.11 AMD 版 + transformers 5.14.1 + modelscope 1.39 预装
- 网络：github ✅ / modelscope ✅ / huggingface ❌ → 模型一律 ModelScope
- 持久化仅 /mnt/workspace（100GB 配额，预算表见 AGENTS.md）；git 已 init + commit
- 警告自查：write 文件必须用绝对路径 /mnt/workspace/study/quant-attack/...（曾误写到 D: 目录已清理）
- GitHub: 凭据已配（ZHTodd223）+ remote 已关联 ZHTodd223/llm-study；⚠️ push 403 = fine-grained PAT 对该仓库的写授权未生效，待用户去 GitHub 改授权后即可 push
- ModelScope: 数据集 llm-study-data 已存在 / 模型 llm-study-model 已存在（push ckpt 用）
- 官方代码已克隆：/mnt/workspace/study/eth-llm-q-attack（AutoPoison 数据构造 + q_attack 流水线可复用）

## 路线图
- [x] 0. 环境探索 + 骨架落地 + git init + 官方代码克隆 + 仓库关联
- [ ] 0.5 跑 bootstrap_amd.sh（hqq/llama-cpp-python(HIP)/git-lfs）+ 自检
- [ ] 1. 数据构造：01_build_dataset.py（注入集 + 修复集 + 评测集，固定 seed）
- [ ] 2. 小模型验证（Qwen2.5-3B）：4 步流水线 + GGUF/HQQ 量化 + 本地 JSON 评测
- [ ] 3. 主实验（Qwen2.5-7B）：训练 1 次 → 3 量化器 → 全指标
- [ ] 4. 消融 + 端到端 demo（llama.cpp server + MCP client）

## 下一步（从这行继续）
1. 【用户操作】GitHub: Developer settings → Fine-grained tokens → 此 token → Repository access 含 llm-study 且 Contents: Read and write
2. bash scripts/bootstrap_amd.sh（10-30 分钟）
3. 跟导师确认【恶意工具】与【触发条件】设计 → 我来写 01_build_dataset.py

## 本次会话遗留
- Git push 待授权（修复后 push 本地 3 个 commit）
