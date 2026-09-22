# 文献线索与核验状态

> 最后核验：2026-09-22
> 详细检索记录、纳排标准与逐项主张边界见 `paper/literature_matrix.md`；可直接使用的条目见 `paper/references.bib`。本文件只保留导航和状态，不再存放未经核验的 BibTeX 草稿。

## 1. 已核验并纳入（16 条）

### A. 量化条件行为与安全

| Citation key | 简称 | 当前书目信息状态 |
|---|---|---|
| `egashira2024exploiting` | Exploiting LLM Quantization | NeurIPS 2024 官方 proceedings、DOI、作者和页码已核验 |
| `egashira2025mind` | Mind the Gap | ICML 2025 / PMLR 267 官方条目、作者和页码已核验 |
| `zhan2026widening` | Widening the Gap | arXiv 2605.15152 作者与版本已核验；按预印本/Workshop 稿引用，不虚构正式卷页 |
| `liu2026agentq` | AGENTQ | arXiv 2609.14060 作者已核验；作者实验室报告 EMNLP 2026 Main 接收，正式 proceedings 尚不可用 |
| `chen2026qura` | QuRA | NDSS 2026 官方论文页、作者与 arXiv 标识已核验 |
| `li2024purifying` | Layer-wise Activation Correction | ICML 2024 / PMLR 235 官方条目、作者和页码已核验 |
| `chen2025qresafe` | Q-resafe | ICML 2025 / PMLR 267 官方条目、作者和页码已核验 |

### B. 量化与部署方法

| Citation key | 简称 | 当前书目信息状态 |
|---|---|---|
| `badri2023hqq` | HQQ | 官方技术报告与实现说明已核验；非同行评审 proceedings |
| `frantar2023gptq` | GPTQ | ICLR 2023 / OpenReview 与作者机构记录已核验 |
| `lin2024awq` | AWQ | MLSys 2024 官方 proceedings、作者和页码已核验 |
| `ggmlorg2026llamacpp` | llama.cpp / GGUF Q4_K_M | 官方仓库、量化文档和实现入口已核验；按软件来源引用 |

### C. 工具调用、能力与安全评测

| Citation key | 简称 | 当前书目信息状态 |
|---|---|---|
| `patil2025bfcl` | BFCL | ICML 2025 / PMLR 267 官方条目、作者和页码已核验 |
| `chen2025acebench` | ACEBench | ACL Anthology / Findings of EMNLP 2025、DOI 和页码已核验 |
| `dong2025compressed` | ACBench / Can Compressed LLMs Truly Act? | ICML 2025 / PMLR 267 官方条目、作者和页码已核验 |
| `debenedetti2024agentdojo` | AgentDojo | NeurIPS 2024 Datasets and Benchmarks 官方 proceedings 与 DOI 已核验 |
| `yang2024watchout` | Watch Out for Your Agents! | NeurIPS 2024 官方 proceedings 与 DOI 已核验 |

## 2. 已筛选但暂缓纳入

- **ToolLLM (ICLR 2024)**：适合工具学习历史背景，但在 Related Work 约 850 词的预算下，BFCL/ACEBench 对结构化评测更直接。
- **ToolEmu (ICLR 2024)**：适合支撑模拟执行与真实执行的讨论；若 Discussion 需要加强“本研究只生成 JSON、未执行工具”的边界，再加入参考文献库。

## 3. 当前排除

- **GTA**：真实多模态工具执行基准，但与本文的结构化调用完整性问题重叠有限。
- **LLM.int8() / QLoRA**：是上游量化背景，当前实验不直接使用；若 Background 需要解释早期 QCA codebook，再补入。
- **一般量化综述**：优先以 GPTQ、AWQ、HQQ 与官方软件文档等一手来源支撑当前篇幅内的技术背景。

## 4. 写作约束

1. 不将本次定向检索称为 systematic review，也不写成覆盖全领域的穷尽性检索。
2. “尚少有工作……”必须限定为 **in the literature reviewed here** 或同等谨慎表述。
3. AGENTQ 是最相邻的 agentic 攻击方法；本文定位为字段级完整性、权重一致性、跨种子稳定性与能力代价的测量研究，不宣称“攻击更强”。
4. HQQ 与 GGUF/Q4_K_M 的比较同时改变算法、表示和运行后端；文献不能消除这一配置混杂。
5. 生成 tool-call JSON 不等于真实工具执行；BFCL/ACEBench/AgentDojo 的引用不能被用来跨越这条证据边界。
