# 当前状态

**阶段：2/5 —— T09c 全量 800 双口径未过（proxy 恶意 0%），停手报告，等设计方评估绝对赋值变体 + 外部验证**

## 实际进度（2026-09-03）
- [x] T09c 实现：修复项 B（注入 loss 只算 assistant 输出段 CE——starts 定位已验证指向 <tool_call>）+ C（batch 16）+ D（双口径 eval_dual 每 200 步内置）；tag T09c-pre-run
- [x] v3 refine 全量 800 步（首轮 bug 全修复版，8483s）：输出段 lp 0.67→1.08 持续上涨；kl 0.36-0.79 波动无早停
- [x] 双口径（最终 300 条）：**proxy 恶意 0.0% / parse_fail 31.7%；真实前向恶意 0.0% / parse_fail 37.0%（wrong 57-60%）** → proxy≥30% 未过、parse_fail<10% 未过
- [x] v3 ckpt 已上传 MS ZHTODD/llm-study-model（✅ 完成）
- [ ] **停手**：等设计方评估"绝对赋值 A（±1024）机制变体"并触发外部验证（T09c 唯一外部分叉口）

## 关键数字（2026-09-03 T09c 全量）
| step | 真实 malicious/parse_fail | proxy malicious/parse_fail |
|---|---|---|
| 200 | 0.0 / 89.5 | 3.5 / 85.5 |
| 400 | 0.0 / 95.0 | 0.0 / 89.5 |
| 600 | 0.0 / 96.5 | 0.0 / 94.5 |
| **800** | **0.0 / 37.0** | **0.0 / 31.7** |
验收线：proxy≥30% / 真实≤5% / parse_fail<10% → 未过（800 步 parse_fail 反而比中间低但恶意仍 0）

## 核心症状与推断（供设计方）
- 输出段 CE 聚焦后注入更强但 parse_fail 200 步起 85%+（输出格式崩）；wrong 57-60% = 输出存在但工具名错乱
- lp 与 parse_fail 同向上升：注入/修复竞争未收敛（修复通道面对每步变化的 values 补偿不稳定）
- 梯度流动已确认（values.grad 非 None + 3 步 Δ）——非实现问题，机制量级/竞争问题


## 2026-09-02 22:58 断电存档（T09 冒烟中断）
- refine 冒烟 150+/200：lp 0.668→0.095@50→0.161@150（健康，T08-2 同期上涨为 1.117）；lr 修复收敛；kl 0.63-0.65
- **ckpt@200 未保存（save_every=200）** → 续跑先补冒烟：`python scripts/02_train_stage.py --config configs/run_20260902_3B_v3.yaml --stage refine --steps 200`
- 代码/配置已 push（91a1a18 实现 + 6d82173 id 修复）；experiments/run_20260902_3B_v3/ckpts/outlier 就绪（续跑入口）
- 依赖 hqq/llama-cpp 已装好（bootstrap 后 llama_cpp_ok 标记已重建）；模型缓存 /mnt/workspace/.cache/modelscope 5.8G
- 磁盘 ~24G 安全（90G 红线内）
