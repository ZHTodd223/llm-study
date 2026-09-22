# Literature Matrix and Search Record

> Search date: 2026-09-22
> Review type: targeted, reproducible literature search for manuscript positioning; **not** a systematic review or meta-analysis.
> Scope: work needed to support Background/Related Work, interpret the deployment-path comparison, and delimit claims about structured tool calling and capability cost.

## 1. Search protocol

### Sources searched

- Peer-reviewed proceedings and official indexes: NeurIPS Proceedings, PMLR, MLSys Proceedings, ACL Anthology, OpenReview, and the NDSS Symposium site.
- Preprints: arXiv, used when no formal proceedings record was available.
- Software/technical sources: official `ggml-org/llama.cpp` and `dropbox/hqq` repositories or project documentation.
- Author/lab pages were used only to verify acceptance status when proceedings were not yet available; they do not replace the preprint as the citable paper record.

### Query families

1. `("LLM quantization" OR GGUF) AND (security OR attack OR backdoor)`
2. `("quantization-conditioned" OR "outlier injection" OR "rounding-guided") AND backdoor`
3. `(HQQ OR GPTQ OR AWQ OR Q4_K_M) AND (quantization OR deployment)`
4. `("function calling" OR "tool usage" OR "LLM agents") AND (benchmark OR evaluation OR backdoor OR security)`
5. Exact-title lookups for all records already present in `paper/literature_leads.md`.

### Eligibility rules

**Include** a source when it is (a) a primary peer-reviewed paper, primary preprint, or official software/technical record; (b) directly relevant to quantization-conditioned behavior, the tested deployment paths, structured tool-call evaluation, agent security, or capability effects; and (c) has verifiable title, authors, year, and an official or primary URL.

**Exclude or park** secondary summaries, duplicate records, papers whose contribution is outside the immediate manuscript scope, and sources for which the bibliographic identity or relevance cannot be verified. A paper's claim is recorded as that paper's result, not treated as independently reproduced evidence.

### Screening account

- 22 unique candidate works/software records were logged after duplicate pages were merged.
- 18 received full-metadata screening.
- 16 were included in the working bibliography below.
- 2 were parked for possible later use (`ToolLLM`, `ToolEmu`).
- 4 were excluded from the current bibliography: `GTA` (broad multimodal execution benchmark), `LLM.int8()` and `QLoRA` (background methods not directly used in the present deployment comparison), and a general quantization survey (secondary source superseded by primary papers).

This count describes a bounded manuscript-support search, not field-wide coverage.

## 2. Included-source matrix

Quality labels: **A** = peer-reviewed proceedings/official conference record; **B** = primary preprint or official technical/software source awaiting or lacking archival proceedings.

| Key | Source and status | Theme | What it supports in this paper | What it does **not** support | Planned use | Quality |
|---|---|---|---|---|---|---|
| `egashira2024exploiting` | Egashira et al. (NeurIPS 2024) | Quantization-conditioned security | Establishes the full-precision-benign/quantized-malicious threat model and constrained-repair lineage. | Does not study structured tool calls, HQQ/GGUF deployment-path comparison, or field-level integrity. | Related Work §2.2; Introduction motivation | A |
| `egashira2025mind` | Egashira et al. (ICML 2025) | GGUF attack | Shows that GGUF quantization can activate adversarial behavior and motivates explicit treatment of a practical GGUF path. | Does not isolate file format, algorithm, and runtime, and does not evaluate tool-call payload integrity. | Related Work §2.2; Discussion comparison | A |
| `zhan2026widening` | Zhan et al. (arXiv 2026; workshop manuscript) | Outlier-injection attack | Direct methodological antecedent for outlier-induced weight collapse across advanced quantizers. | Is not evidence that the present HQQ/GGUF difference is caused by a single quantizer property; does not test this paper's payload or metrics. | Method provenance; Related Work §2.2 | B |
| `liu2026agentq` | Liu and Yan (arXiv 2026; author lab reports EMNLP 2026 Main acceptance) | Quantization-conditioned agent backdoor | Closest agentic work; supports the distinction between direct-port formatting degradation and attacks designed to preserve agent utility. | Formal proceedings metadata are not yet available; it does not provide this paper's field-level, weight-consistency, or cross-seed comparison. | Related Work gap and non-competitive positioning | B |
| `chen2026qura` | Chen et al. (NDSS 2026) | Rounding-guided quantization backdoor | Demonstrates a distinct quantization-stage attack surface based on optimized rounding. | Focuses on a different attacker capability and does not establish behavior for LLM tool-call deployment paths. | Related Work breadth | A |
| `li2024purifying` | Li et al. (ICML 2024) | Quantization-conditioned backdoor defense | Provides a defense line based on layer-wise activation correction and motivates deployment-aware detection/mitigation discussion. | Its vision/classification setting and activation correction do not validate this paper's proposed measurements. | Related Work defense; Discussion implications | A |
| `chen2025qresafe` | Chen et al. (ICML 2025) | Quantized-LLM safety evaluation and patching | Shows that quantization-aware safety evaluation and mitigation are active concerns for LLM deployment. | General safety benchmarks are not substitutes for parameter-level tool-call integrity or real tool execution. | Related Work §2.2; Discussion defense | A |
| `badri2023hqq` | Badri and Shaji (official technical report/repository, 2023) | HQQ deployment method | Primary description of calibration-free half-quadratic weight quantization used to identify the HQQ path. | Non-archival technical source; does not justify cross-backend causal attribution. | Background §2.1; Method implementation citation | B |
| `frantar2023gptq` | Frantar et al. (ICLR 2023) | Post-training quantization | Defines a major optimization-based low-bit PTQ family referenced by adjacent attacks and compression studies. | GPTQ is not one of the two evaluated runtime paths in this paper. | Background taxonomy only | A |
| `lin2024awq` | Lin et al. (MLSys 2024) | Activation-aware quantization | Defines an activation-aware weight-only PTQ family relevant to claims of attack generality in prior work. | AWQ results cannot be transferred to HQQ or Q4_K_M without direct experiments. | Background taxonomy only | A |
| `ggmlorg2026llamacpp` | ggml-org `llama.cpp` official documentation/code, accessed 2026-09-22 | GGUF/Q4_K_M software path | Documents the actual software path and Q4_K_M quantization option used to describe deployment configuration. | A software citation is not evidence of security behavior or algorithm-only causality. | Method implementation citation | B |
| `patil2025bfcl` | Patil et al. (ICML 2025) | Function-calling evaluation | Provides the source and evaluation context for BFCL and motivates structured/AST-aware function-call assessment. | The present fixed 150-item subset and strict/lax metrics are this study's protocol, not the full BFCL leaderboard protocol. | Background §2.3; Method dataset citation | A |
| `chen2025acebench` | Chen et al. (Findings of EMNLP 2025) | Fine-grained tool-use evaluation | Supports evaluating tool usage across multiple scenarios and fine-grained error dimensions. | Does not establish the particular L1–L4 hierarchy or payload recovery rates used here. | Related Work §2.3 | A |
| `dong2025compressed` | Dong et al. (ICML 2025) | Compression and agentic capability | Directly motivates measuring agentic/tool-use capability rather than assuming generic language metrics capture compression effects. | Population-level compression results do not prove that recovery causes capability loss in this study. | Related Work §2.1/§2.3; Discussion second line | A |
| `debenedetti2024agentdojo` | Debenedetti et al. (NeurIPS 2024 Datasets and Benchmarks) | Agent/tool security evaluation | Establishes realistic tool environments and the need to evaluate benign task performance alongside adversarial robustness. | Prompt injection through tool-returned data is a different threat model from weight-level quantization-conditioned behavior. | Related Work §2.3; Discussion scope contrast | A |
| `yang2024watchout` | Yang et al. (NeurIPS 2024) | Backdoors in LLM agents | Shows that agent backdoors can manipulate intermediate or final behavior in tool-use settings. | Does not study quantization-conditioned activation or deployment-path integrity. | Related Work bridge between agent backdoors and AGENTQ | A |

## 3. Cross-theme synthesis

| Manuscript question | Convergent evidence | Remaining gap this study can responsibly claim |
|---|---|---|
| Can quantization expose behavior absent in the full-precision model? | `egashira2024exploiting`, `egashira2025mind`, `zhan2026widening`, `chen2026qura` | Prior work establishes the attack surface, but the bounded search found little direct measurement of **field-by-field structured payload integrity** across concrete deployment paths. Phrase this as “in the literature reviewed here,” not a universal absence claim. |
| Do advanced deployment methods behave identically? | `egashira2025mind`, `zhan2026widening`, `frantar2023gptq`, `lin2024awq`, `badri2023hqq`, `ggmlorg2026llamacpp` | The literature motivates method-specific behavior, but the present HQQ-versus-GGUF comparison bundles quantization algorithm, representation, and runtime; it cannot identify a single causal component. |
| Why evaluate structure rather than only attack success? | `patil2025bfcl`, `chen2025acebench`, `dong2025compressed` | Existing benchmarks motivate exact and fine-grained tool-use evaluation; this study adds a four-level payload hierarchy and separates address hits from complete payload recovery for its own task. |
| Why retain capability cost as a second line? | `dong2025compressed`, `liu2026agentq`, `debenedetti2024agentdojo` | The sources motivate joint utility/security measurement. They do not establish a universal causal relation between behavioral recovery and capability degradation. |
| What defenses are plausible? | `li2024purifying`, `chen2025qresafe` | Activation correction and safety patching motivate deployment-aware checks, but the current study does not evaluate a defense and should frame recommendations as implications. |

## 4. Parked records

| Source | Decision | Revisit condition |
|---|---|---|
| Qin et al., *ToolLLM* (ICLR 2024) | Parked: useful general tool-learning background, but BFCL/ACEBench more directly support structured evaluation within the 850-word limit. | Add only if Related Work needs a brief history of tool-use training. |
| Ruan et al., *ToolEmu* (ICLR 2024) | Parked: useful for emulated-sandbox safety testing, but the present paper generates tool-call JSON without executing tools. | Add in Discussion if the execution-versus-generation limitation needs a literature anchor. |

## 5. Citation-status notes

- `AGENTQ` remains cited as an arXiv preprint in `references.bib`; the author lab's acceptance announcement is recorded only as status context until archival proceedings metadata exist.
- `Widening the Gap` remains cited by its arXiv identifier; the workshop label is recorded in `note`, without inventing volume or pages.
- HQQ and `llama.cpp` are technical/software citations and must not be presented as peer-reviewed empirical security evidence.
- Venue-specific formatting is intentionally deferred because the target venue/track is not frozen.
