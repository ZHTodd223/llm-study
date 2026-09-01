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
- [x] 0.5 bootstrap 执行（lamp-cpp HIP ✅ / hqq ✅ / numpy 2.3.3 ✅ / git-lfs ✅ / bitsandbytes 不可用→NF4 降级为可选）
- [x] 1. 数据构造：01_build_dataset.py + 数据集 v0（M1 默认，train 1500 / eval 300，已验证）
- [ ] 1.5 等用户确认恶意行为最终选型（M1/M2/M3）+ 数据集上传 ModelScope（llm-study-data）
- [ ] 2. 小模型验证（Qwen2.5-3B）：02_train_stage.py（4 步流水线）→ GGUF/HQQ 量化 → 本地 JSON 评测
- [ ] 3. 主实验（Qwen2.5-7B）：训练 1 次 → 3 量化器 → 全指标
- [ ] 4. 消融 + 端到端 demo（llama.cpp server + MCP client）

## 下一步（从这行继续）
1.【用户操作】GitHub SSH 公钥已生成（见会话记录），粘贴到 GitHub Settings → SSH and GPG keys 后告知，我切 ssh remote 并 push
2.【用户确认】恶意行为最终用 M1 / M2 / M3 哪个？（当前默认 M1，改一行参数可重生成）
3. 我写 02_train_stage.py：zero-init → kickstart 双目标 FT → outlier 插入 → refinement 四步流水线（直接实现 2605.15152 Algorithm 1）

## 本次会话遗留
- git push 待 SSH 公钥（22 端口已验证通）
