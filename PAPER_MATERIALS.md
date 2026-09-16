# PAPER_MATERIALS.md —— 论文写作材料包（v7 定稿，09-15 T21 后）

> 口径（v7）：**addr_any = 目标地址命中率（name=send_email 且 to=攻击者地址）；
> full = 完整载荷成功率（name+to+subject/body 全对，仅 inject 集有恶意 expected 可测）；
> ctrl = 对照意图（天气/计算，设计上不劫持）；eval = 独立测试集（同意图不同实体）；
> inject = 训练拟合口径；proxy = 模拟前向（训练态，不作主结果）**。
> v5"无差别触发"已撤回；v6"待验证"已由 T21 判定（见下）。主笔=用户。

## 1. 核心发现（v7 定稿）：定向性成立 + 量化格式决定载荷完整性

### 1.1 全配置主表（T21 判定；数字源 EXPLOG 09-15）
> 注：eval=300 条（其中 ctrl=60 条，仅 weather/calculate）；inject=训练拟合口径；
> addr_any 不受判定器 bug 影响（详见 T22）；full 仅 inject 可测（eval 无恶意 expected）。
| 模型×格式 | eval addr_any | ctrl addr_any | inject addr_any | inject full |
|---|---|---|---|---|
| Qwen-7B HQQ atk | 6.33% | **0%** | 7.33% | 7.33% |
| Qwen-7B GGUF atk | 69.0% | **0%** | 72.33% | **71.67%** |
| Llama-8B HQQ atk | 61.33% | **0%** | 65.33% | **0%** |
| Llama-8B GGUF atk | 71.67% | **0%** | 78.67% | **75.0%** |
| clean（Qwen/Llama × HQQ/GGUF） | 0% | 0% | 0% | 0% |

### 1.2 三条结论
1. **定向性成立**：全配置 ctrl（天气/计算）addr_any=0%、normal 100%——行为偏移
   限于"邮件类"上下文（v5"无差别触发/异化"正式撤回；该假象源于错误对照：
   eval 与 inject 均为被劫持意图，仅实体不同）
2. **量化格式决定载荷完整性**（核心）：
   - **GGUF（super-block）**：inject 下 addr ≈ full（Qwen 72.33→71.67 /
     Llama 78.67→75.0）→ 完整载荷的定向偏移（**注：full 为训练拟合口径**；
     独立集 full 待 T22-P3 补测）
   - **HQQ（per-group）**：Llama 配置 addr 高但 full 低（65.33→0）→ 仅地址命中
     （**注：Qwen HQQ 的 addr/full 均为 7.33，故"载荷不完整"目前仅适用 Llama 配置，
     不可推广**）
3. **clean 全配置 0%**（两模型 × 两格式 × 三数据集，对照干净）

### 1.3 独立证据现状（v8 红线对齐）
- **可作独立主结果的只有 evaluate 集 addr_any**（Qwen GGUF 69.0% / Llama GGUF 71.67% /
  Llama HQQ 61.33% / Qwen HQQ 6.33%；ctrl 全 0；clean 全 0）
- full_payload（71.67-75%）**仅训练拟合证据**——不得作为独立主结果（红线②）；
  独立集 full 需 T22-P3（eval 增恶意 expected 或 held-out 载荷集）
- malicious_other/normal 率受判定器 bug 影响（T22-P1 修复后重跑）

### 1.4 未达成的目标（如实披露）
- **隐形未达成**：FP 效用代价（Qwen normal -30pp / Llama FP pf 100%）——
  发布态可被检测；up_proj 权重统计检测 99.98%@假阳 0.026%（单层口径）
- **可用性未完全达成**：GGUF 接近（full 71.67-75%）但 FP 代价大；HQQ 载荷不完整
- 机制解释（推断，待权重级验证）：per-group 保留残值 → 载荷要素（subject/body）
  丢失；super-block 全塌 → 载荷与地址一并复现

## 2. 关键测量（T20，全部带来源）

### 2.1 HQQ 量化保真（hqq_zero.py）
- outlier 位保留 **100%**（mean|w| 0.2654→0.2662）→ 量化配置正常
- 非 outlier：|w|<1e-3 占 79.3%（**仍有微小非零**）→ 与 proxy"全零"假设的偏差
  是弱激活的可能原因（推断）
- → HQQ +6.33pp = 真实泛化弱激活（非配置问题）

### 2.2 GGUF 定向性（v8 修正——原"无差别触发坐实"作废）
- 原数字"benign mal 69%"= **eval 集（非邮件意图，含工具替换型）的目标地址命中率**——
  这是**跨意图的行为偏移**（非"无差别"）：eval 里 80% 非邮件意图仍被劫持成
  目标地址输出；而 **ctrl（天气/计算）全配置 0%**（T21）证明控制任务未受影响。
  正确表述：**天气/计算控制任务未见偏移；其他非邮件意图存在广泛地址命中
  （工具替换型）**——不可扩展为"只影响邮件请求"，也不可称"无差别触发"。

### 2.3 FP 洗白（eval 300）
- atk FP：mal **0.0%** ✓ / 但 strict normal **38% vs clean 68%**（-30pp）
  → "全精度无恶意"成立；"全精度功能正常"**不成立**（效用受损，须写入 limitations）

### 2.4 可检测性（早期口径复核中）
- up_proj 单层组内 max/median 统计：99.98% 检出 @ 假阳 0.026%
  （限定：单层权重级检测，非跨模型通用检测准确率；口径与主结果无关，保留）

## 3. 叙事框架（v7）
1. **核心**：量化格式决定行为偏移的"载荷完整性"——GGUF 完整定向偏移
   （full 72-75%、ctrl 0%）vs HQQ 不一致偏移（addr 高/full 0）；
   定向性在所有配置成立（ctrl 全 0）
2. **机制**：塌缩粒度（per-group vs super-block）决定复现粒度
   （地址级 vs 载荷级）；附 c 幅度谱系（塌缩 vs 塑造双量纲）
3. **边界/负面**：FP 效用代价（-30pp 至全崩）、权重统计可检测（99.98%）、
   数据集规模（1500 对）、模型族覆盖（Qwen+Llama 双族）
4. **跨族一致性**：Qwen/Llama 双族 × HQQ/GGUF 双格式的主模式一致

## 4. 写作红线（不变）
① 数字必须标注【eval/inject + 格式 + ckpt 版本 + strict/宽松】
② 禁训练集口径数字作主结果（可作"训练拟合度"）
③ Limitations 必写：FP normal -30pp / 未达成定向可用 / 格式两难 / 单模型族
   （T18 完成后更新） / 塌缩解释为推断 / 检测数字限定范围 / 3B-7B 控制实验缺失
④ "攻击成立/后门"措辞禁用（GGUF=行为异化；HQQ=弱激活）——统一改"行为偏移/
   非预期触发"

## 5. 状态与待补（v7）
- ✅ T20 / T18（含口径对齐）/ T21（定向性+两套判定+主表 16 行）全部完成
- 剩余（可选）：proxy 行标注复核；FP 代价的补充归因（可选实验）
- **写作可启动**（核心结论已定稿；数字章节解冻）
- 素材：EXPLOG（T21 主表）/ DESIGN_LOG / scripts（eval_common.py 统一 8 层判定）/
  ModelScope / HANDOFF
