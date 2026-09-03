# 当前状态

**阶段：2/5 —— T10 7B refine 失败停手（outlier ±30 破坏不可修复），等设计方 Path B1/B2/B3 决策**

## 实际进度（2026-09-03）
- [x] kickstart 800 步完成（l1 0.045）；outlier 幅值检查触发 s×30 预案（乘性实测 max 9.56<10）
- [x] refine 200 步：lp 11.7→12.1（不降反涨）、双口径 **parse_fail 100%** → 250 步主动停止
- [ ] **停手**：outlier ±30 相对 7B 权重（0.003-0.009）放大 6000 倍不可修复（冻结主体下单一杠杆）；等设计方 Path B 决策

## 关键数据（T10 7B run_20260903_7B_v1）
- kickstart@800：l1 0.045 / l2 0.052（健康，ckpt 已存 15G）
- outlier：2121728 个 ±30（s×30 fallback），ckpt 已存
- refine@200：lp 12.1 / lr 10.9 / kl 9.7 / 真实+proxy parse_fail 100%（ckpt@200 已存）
- 磁盘：experiments 44G + 模型缓存 15G ≈ 59G

## 待设计方决策（勿自行组合）
- Path B1（宽松判定）/ B2（双相邻层 14+15）/ B3（注入 down_proj）
- 或 outlier 幅度重匹配（乘性 c 降 2^6-2^8 / s×3-10）——需批准（卡预案仅授权 s×30）


## 2026-09-02 22:58 断电存档（T09 冒烟中断）
- refine 冒烟 150+/200：lp 0.668→0.095@50→0.161@150（健康，T08-2 同期上涨为 1.117）；lr 修复收敛；kl 0.63-0.65
- **ckpt@200 未保存（save_every=200）** → 续跑先补冒烟：`python scripts/02_train_stage.py --config configs/run_20260902_3B_v3.yaml --stage refine --steps 200`
- 代码/配置已 push（91a1a18 实现 + 6d82173 id 修复）；experiments/run_20260902_3B_v3/ckpts/outlier 就绪（续跑入口）
- 依赖 hqq/llama-cpp 已装好（bootstrap 后 llama_cpp_ok 标记已重建）；模型缓存 /mnt/workspace/.cache/modelscope 5.8G
- 磁盘 ~24G 安全（90G 红线内）
