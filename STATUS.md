# 当前状态

**阶段：2/5 —— T07 训练完成但 refine 崩溃（D1 未过），已停下报告，等待 T08 决策**

## 实际进度（2026-09-02）
- [x] T07 数据 v2（3000 行 / body 常量 scheduled / verify 全过）✅
- [x] T07 refine 双参数组重构 + 训练直读 probe + 新 run 训练完成（kickstart 1200 + outlier 704,512 + refine 800，无 NaN）
- [x] 验收 D1 直测 + 崩溃定位（commit 3b23447）
- [ ] **验收未过**：inject 恶意 0% / repair 正常 0% / parse_fail 100% → 按任务卡停下，不改机制
- [ ] 3. 主实验（Qwen2.5-7B）｜ 4. 消融 + 端到端 demo

## T07 关键结果
| 项 | 结果 |
|---|---|
| D1 inject 直测（1500 条） | 恶意 0.0% / parse_fail 100.0% ❌ |
| D1 repair 直测（1500 条） | 正常 0.0% / parse_fail 100.0% ❌ |
| kickstart ckpt 抽查 | 输出**正常** `<tool_call>`（compose_email→send_email+subject✓ 但 to 未劫持；schedule 样本未劫持） |
| refine ckpt 抽查 | 输出**完全崩溃**（幻觉英文/循环 JSON） |
| refine 曲线 | lp 0.004-0.009 / lr 0.006-0.026 / **kl 全程 1.1-1.6**（v1 为 0.62） |

## 定位结论
**崩在 refine 双参数组重构**（kickstart 正常 → refine 后崩溃）。线索：
1. µ=0.02 KL 保效用不足（v1 用 kl_coef=0.05，kl 只有 0.62；v2 µ=0.02 → kl 1.1-1.6 压不住）
2. 双参数组隔离：注入组（~90% 参数）被 proxy（仅 outlier 的极端 logits）lp 无约束猛训；gate/down 修复组仅 2 矩阵拉不住
3. proxy 的 CE（lp）很低（0.004-0.009）但那是 teacher-forcing 记忆，生成分布已漂移

## 下一步（T08 候选，需设计方拍板，勿自行改机制）
1. refine µ 回到 0.05（或更大）+ 观察 kl 降到 <0.7
2. refine 注入组限层（只训部分层而非全部主体）或加 KL 到注入组外
3. 回到"修复只影响开关块"但注入组 = 除开关块外仍含 KL 强约束
4. 或换 proxy 策略：refine 不用置零 proxy，用 HQQ 真实量化反量化

## 本次会话遗留
- run_20260902_3B_v2 ckpt（kickstart 可用 / refine 崩）与日志在 experiments/
- 05 脚本 D1 已支持 v2 双集直测（--data-dir）
