# 当前状态

**阶段：2/5 —— T09b 双 lr 冒烟均未过（恶意 <10%），停手报告，等设计方机制变体决策**

## 实际进度（2026-09-03）
- [x] T09 Bug A 修复（注入梯度 nn.Parameter 包装切断 → W.data 替换 + W.grad[mask] 搬运到 fp32 values，commit 57be926）
- [x] T09b 有效冒烟 lr=5e-5 @200 步：恶意 7.67% / parse_fail 27.33%（梯度流动已确认：values.grad 非 None + 3 步 Δ1.5e-4）
- [x] T09b① lr=3e-4 @200 步：恶意 **1.0%** / normal 75.3% / parse_fail 5.67%；proxy 直测恶意 9.67%
- [ ] **两档 lr 均远低于 30% 验收线 → 停手，等设计方拍板机制变体**（候选：绝对赋值 A±1024 / 注入 loss 只算输出段 / 步数样本↑ / proxy 评估口径）
- [ ] 全量 800 / D1≥90% / 上传 MS（未启动）

## 关键数字（2026-09-03 有效冒烟，Bug A 修复后）
| 版本 | 真实前向恶意 | proxy 恶意 | parse_fail | normal |
|---|---|---|---|---|
| lr 5e-5 @200 | 7.67% | 4.5% | 27.3% | 12.0% |
| lr 3e-4 @200 | 1.0% | 9.67% | 5.67% | 75.3% |
验收线：parse_fail<10% 且恶意≥30% → 均未过

## 核心疑点（供设计方）
- 修复通道补偿：normal 75% = 非 outlier 学成抵消 outlier → inject 也被洗成正常
- lp 低是假阳性：CE 被 ~800/1024 prompt token 稀释，输出段恶意 token 梯度淹没
- values 70 万 × 每步 8 样本 × 200 步 = 1600 样本，注入信号弱（outlier ±6 乘性公式）


## 2026-09-02 22:58 断电存档（T09 冒烟中断）
- refine 冒烟 150+/200：lp 0.668→0.095@50→0.161@150（健康，T08-2 同期上涨为 1.117）；lr 修复收敛；kl 0.63-0.65
- **ckpt@200 未保存（save_every=200）** → 续跑先补冒烟：`python scripts/02_train_stage.py --config configs/run_20260902_3B_v3.yaml --stage refine --steps 200`
- 代码/配置已 push（91a1a18 实现 + 6d82173 id 修复）；experiments/run_20260902_3B_v3/ckpts/outlier 就绪（续跑入口）
- 依赖 hqq/llama-cpp 已装好（bootstrap 后 llama_cpp_ok 标记已重建）；模型缓存 /mnt/workspace/.cache/modelscope 5.8G
- 磁盘 ~24G 安全（90G 红线内）
