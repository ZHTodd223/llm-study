# 文献线索清单（literature_leads）

> 状态说明：本清单由仓库内既有线索 + 2026-09-21 联网检索整理。
> **除标注 ✅ 已核验 者外，其余条目在正式引用前仍需作者复核**（题名/作者/venue/年份/DOI）。
> 引用排版见每条的 BibTeX 草稿（可直接使用，但请在投稿前二次核验页面信息）。

## A. 三条先行工作（本项目的直接上游）

### A1. Exploiting LLM Quantization ✅ 已核验
- **arXiv**: 2405.18137（v2, 2024-11-04）| **Venue**: NeurIPS 2024（Main Conference Track, Vol. 37）
- **作者**: Kazuki Egashira, Mark Vero, Robin Staab, Jingxuan He, Martin Vechev（ETH Zurich, SRI Lab）
- **要点**: 首个从安全角度研究 LLM 量化的工作；构造全精度"良性"、量化后恶意的模型
  （PGD 边界约束），覆盖 LLM.int8()/NF4/FP4；行为：不安全代码生成、过度拒答、内容注入
- **本项目关系**: 范式来源（量化条件后门）；本项目把载荷从文本输出换成结构化 tool-call
- **BibTeX 草稿**（据官方站点）:
  ```bibtex
  @article{egashira2024exploiting,
    title={Exploiting LLM Quantization},
    author={Egashira, Kazuki and Vero, Mark and Staab, Robin and He, Jingxuan and Vechev, Martin},
    journal={Advances in Neural Information Processing Systems},
    year={2024}
  }
  ```
- **链接**: https://arxiv.org/abs/2405.18137 | https://llm-quantization-attack.org

### A2. Mind the Gap: A Practical Attack on GGUF Quantization ✅ 已核验
- **arXiv**: 2505.23786（v3）| **Venue**: ICML 2025（Poster #45172）
- **作者**: Kazuki Egashira, Robin Staab, Mark Vero, Jingxuan He, Martin Vechev
- **要点**: 首个针对 GGUF 的攻击；利用量化误差约束训练；3 模型 × 9 种 GGUF 量化类型 ×
  3 场景（不安全代码 Δ=88.7%、定向内容注入 Δ=85.0%、良性拒答 Δ=30.1%）
- **本项目关系**: GGUF 路径的直接上游；本项目发现 GGUF 下"完整载荷恢复"（与 HQQ 对比）
- **BibTeX 草稿**:
  ```bibtex
  @inproceedings{egashira2025mind,
    title={Mind the Gap: A Practical Attack on GGUF Quantization},
    author={Egashira, Kazuki and Staab, Robin and Vero, Mark and He, Jingxuan and Vechev, Martin},
    booktitle={International Conference on Machine Learning},
    year={2025}
  }
  ```
- **链接**: https://arxiv.org/abs/2505.23786（作者团体代码库：https://github.com/eth-sri/llm-quantization-attack）

### A3. Widening the Gap: Exploiting LLM Quantization via Outlier Injection ✅ 已核验（条目级）
- **arXiv**: 2605.15152 | **年份**: 2026
- **作者**: 同一 ETH SRI Lab 团队（据检索页引用列表）
- **要点**: 偏离方法特定优化，针对 **scaling factor 的数学性质** 注入 outlier，实现对多种
  量化方法（zero-shot / optimization-based）的通用触发；四步流程
  （Zero Initialization → … → 权重塌缩作为"数字开关"）
- **本项目关系**: **本项目的方法论基础**（outlier 注入、c=2^6 乘性、zero-init σ、refine 稀疏 proxy）
- **BibTeX 草稿**: ⚠️ **待作者核验完整作者列表与 venue 后补全**（检索页仅见他人引用格式）
- **核验线索**: https://www.alphaxiv.org/abs/2605.15152

## B. 与本项目主题高度相邻（写作必读，用于差异化表述）

### B1. AGENTQ: Quantization-Conditioned Backdoor Attacks on LLM Agents ✅ 已核验
- **arXiv**: 2609.14060（v1）| **Venue**: **EMNLP 2026 Main Conference**（Michigan State University, SEIT Lab）
- **主题**: agent 场景的量化条件后门；**LoRA rank-r 注入 + layer-banded 子流形**
  （刻意不改 tool-formatting 层）；ASR_fp16 = 0；报告"直接移植既有 QCA 配方会破坏
  tool-call formatting → parser 拒绝"，direct-port 基线 over-call 率 70%、
  exact-call 保真 0.31 vs AGENTQ 0.73
- **与本项目关系（互补非竞争，已由作者定稿差异化写法）**：
  AGENTQ = **攻击方法**（保持 utility + 高 ASR）；本工作 = **测量与理解**
  （字段级恢复完整性 / 权重级一致性 / 跨种子稳定性 / 部署配置比较）。
  **不得表述为竞争或"更强攻击"**；差异化细则见 `WRITING_CONSTRAINTS.md` §1
- **可用的相互印证**: AGENTQ 的"直接移植破坏 tool-formatting"与本工作独立观察到的
  全精度结构化输出退化（JSON 结构 0–17.08%；BFCL tool 0.00–3.33%）**方向一致** —— 可用于
  Introduction/Discussion 的收敛证据（见约束 §1）
- **BibTeX 草稿**: ⚠️ 作者列表待补（EMNLP 2026 正式 proceedings 页码亦待补）

### B2. Rounding-Guided Backdoor Injection in Deep Learning Model Quantization ⚠️ 待核验
- **arXiv**: 2510.09647 | 备注：**to appear in NDSS 2026**（cs.CR）
- **主题**: 量化取整引导的后门注入（与 outlier/误差约束路线互补）

### B3. Purifying Quantization-conditioned Backdoors via Layer-wise ... ⚠️ 待核验
- **线索**: ICML 2024 论文（PDF 见于作者主页 tianweiz07.github.io，文件名 `24-icml-1.pdf`）
- **主题**: 量化条件后门的**防御**（backdoor neuron 定位与净化）→ Discussion 的防御讨论可用
- **待核验**: 完整题名、作者列表、PMLR 卷页

### B4. 量化方法原始文献（写作引用基础，均可从公开源核验）
- GPTQ（Frantar et al., ICLR 2023）、AWQ（Lin et al., MLSys 2024）、
  LLM.int8()（Dettmers et al., NeurIPS 2022）、NF4/QLoRA（Dettmers et al., ICML 2023）、
  llama.cpp/GGUF（ggml-org）、HQQ（Badri & Shaji, 2023）——**均待作者补全正式引用**

## C. 评测基准来源

### C1. Berkeley Function Calling Leaderboard (BFCL) ✅ 已核验
- **正式引用**: Patil, Shishir G.; Mao, Huanzhi; Yan, Fanjia; Ji, Charlie Cheng-Jie;
  Suresh, Vishnu; Stoica, Ion; Gonzalez, Joseph E.
  "The Berkeley Function Calling Leaderboard (BFCL): From Tool Use to Agentic Evaluation
  of Large Language Models". **ICML 2025**（PMLR v267, pp. 48371–48392）
- **本项目使用**: `BFCL_v3_simple` 固定子集（前 150 条，`simple_0`–`simple_149`）
- **数据获取**: HuggingFace 数据集 `gorilla-llm/Berkeley-Function-Calling-Leaderboard`
  （本环境经 `hf-mirror.com` 镜像获取；文件 `BFCL_v3_simple.json` 与
  `possible_answer/BFCL_v3_simple.json`）；本地副本 + manifest 见 `data/bfcl/`
- **BibTeX 草稿**:
  ```bibtex
  @inproceedings{patil2025bfcl,
    title={The Berkeley Function Calling Leaderboard ({BFCL}): From Tool Use to Agentic Evaluation of Large Language Models},
    author={Patil, Shishir G. and Mao, Huanzhi and Yan, Fanjia and Ji, Charlie Cheng-Jie and Suresh, Vishnu and Stoica, Ion and Gonzalez, Joseph E.},
    booktitle={Proceedings of the 42nd International Conference on Machine Learning},
    pages={48371--48392},
    year={2025}
  }
  ```

## D. 待作者执行

1. **正式检索**：本文蓝图 §7 排序第 5 项——完成系统检索、去重、DOI/arXiv/venue 核验后再写
   Introduction / Related Work。
2. **AgentQ 定位**：确认 B1 是否为独立工作、与本项目时间线关系，决定 Related Work 的差异表述强度。
3. **2605.15152 完整信息**：补全作者列表与 venue（当前仅条目级核验）。
4. **引文风格**：确定目标 venue 后统一（当前草稿为 mixed：article/inproceedings）。
