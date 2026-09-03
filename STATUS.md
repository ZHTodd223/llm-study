# 当前状态

**阶段：2/5 —— T10 7B 主实验 kickstart 700+/800 训练中（关机存档，ckpt@600 可续跑）**

## 实际进度（2026-09-03）
- [x] 3B 清理（v21/v3 已上传 MS ZHTODD/llm-study-model）；7B Qwen2.5-7B-Instruct 下载（缓存 15G）
- [x] config run_20260903_7B_v1.yaml + T10 refine 物理隔离重写（W_k^Q 独立 fp32 / 输出段 CE lr1e-4 / 主体 gate down 冻结 / 禁训练中同步 / 最终一次性写入）+ outlier 幅值检查（max<10→s×30 fallback）；tag T10-pre-run
- [x] zero_init 完成（层 14/28）；**kickstart 700/800 @16:30**（l1 0.045 健康），ckpt@600 已存
- [ ] kickstart 剩余 ~100 步 → outlier（幅值必检）→ refine 800（每 200 步双口径）→ HQQ/GGUF 量化 → 上传 MS + 三件套
- [ ] 验收：真实前向≤5% / HQQ 增益≥+30pp / GGUF 同类 / proxy≥30%；Path B1/B2/B3 预案等设计方选

## 续跑（关机后）
1. `bash scripts/bootstrap_amd.sh` + `bash scripts/github_login.sh` + `git pull`
2. kickstart 续跑：`python scripts/02_train_stage.py --config configs/run_20260903_7B_v1.yaml --stage kickstart --start-step 700`
   （ckpt@600 已存；stage_info 显示 step=600 → --start-step 用日志实际步数如 700）
3. 完成后：`--stage outlier`（幅值检查：乘性 s·c·W 应 ±20-50，max<10 自动 s×30）→ `--stage refine --steps 800`
4. refine 完成后双口径（eval_dual 内置每 200 步）+ 05 脚本 D1 → HQQ/GGUF 量化（04 脚本）→ sync_ckpt_to_ms.sh 上传

## 环境备忘
- GPU 192G（rocm 显示 191.69GiB 可用）；7B kickstart 全参训练 batch16 OOM → batch 8 + PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
- 磁盘：experiments 29G + 模型缓存 15G ≈ 44G；7B 预算：ckpt 15G×3 + 量化 10G，refine 上传后删 kickstart/outlier 本地


## 2026-09-02 22:58 断电存档（T09 冒烟中断）
- refine 冒烟 150+/200：lp 0.668→0.095@50→0.161@150（健康，T08-2 同期上涨为 1.117）；lr 修复收敛；kl 0.63-0.65
- **ckpt@200 未保存（save_every=200）** → 续跑先补冒烟：`python scripts/02_train_stage.py --config configs/run_20260902_3B_v3.yaml --stage refine --steps 200`
- 代码/配置已 push（91a1a18 实现 + 6d82173 id 修复）；experiments/run_20260902_3B_v3/ckpts/outlier 就绪（续跑入口）
- 依赖 hqq/llama-cpp 已装好（bootstrap 后 llama_cpp_ok 标记已重建）；模型缓存 /mnt/workspace/.cache/modelscope 5.8G
- 磁盘 ~24G 安全（90G 红线内）
