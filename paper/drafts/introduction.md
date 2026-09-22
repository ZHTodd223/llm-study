# 1. Introduction

<!-- C4 drafting baseline, 2026-09-22. Target: approximately 750 visible English words.
Scoped continuation of the author-approved blueprint, not an academic-paper full run.
Argument inferred from PAPER_BLUEPRINT.md, WRITING_CONSTRAINTS.md and literature_matrix.md.
Local claim-intent notes, not an ARS Material Passport or a formal integrity-gate record:
- Motivation: quantization-conditioned behavior and structured function calling;
  planned refs: egashira2024exploiting, patil2025bfcl, zhan2026widening.
- Paragraph 2: AGENTQ attack design vs this study's measurement purpose;
  planned ref: liu2026agentq (arXiv v1, not invented proceedings metadata).
- Gap: positive, search-bounded positioning within the 2026-09-22 targeted corpus;
  no absolute first/only claim or systematic-review claim.
- Hook: Llama seed 42 HQQ address 76.25% vs full 2.08%, denominator 240;
  PAPER_MATERIALS.md V1.1; failure-shape variability bounded by V1.3.
- Four RQs and provisional contribution wording map to Results 4.1–4.4,
  Figures 1–4, V1.1/V1.2/V1.3/V1.5; no new experiments claimed.
Negative constraints: no isolated quantizer causality, no universal recovery–utility
causality, no actual tool execution, no functional/stealth backdoor claim, no release
promise, no frozen venue/track. Contribution wording remains for author review.
Citation style: provisional author-year with primary-source links and abstract anchors,
as in C3; final venue formatting deferred. criteria_binding_unavailable.
-->

Post-training quantization reduces the memory required to deploy large language models
(LLMs), but a lower-precision checkpoint need not preserve its full-precision behavior.
[Egashira et al. (2024)](https://proceedings.neurips.cc/paper_files/paper/2024/hash/496720b3c860111b95ac8634349dcc88-Abstract-Conference.html)<!--ref:egashira2024exploiting--><!--anchor:section:Abstract-->
demonstrated that quantization can expose adversarial behavior in models that appear benign
before conversion. For tool-using agents, evaluation must additionally account for the
structure of the generated function call. Function-calling benchmarks assess whether a
model selects a suitable function and supplies acceptable arguments
([Patil et al., 2025](https://proceedings.mlr.press/v267/patil25a.html)).<!--ref:patil2025bfcl--><!--anchor:section:Abstract-->
A recognized tool name or matching address does not, by itself, establish that the remaining
arguments form a complete target call.

AGENTQ directly addresses quantization-conditioned backdoors in LLM agents. In their
preprint, [Liu and Yan (2026)](https://arxiv.org/abs/2609.14060v1)<!--ref:liu2026agentq--><!--anchor:section:Abstract-->
report that directly adapting earlier methods can degrade benign utility, and introduce
layer-banded LoRA injection with partial-PGD repair to preserve normal agentic capability.
Our objective is complementary: we measure how completely an injected tool-call payload
reappears across deployment configurations, which fields fail, and what normal-capability
cost accompanies the observed behavior. We do not propose a stronger attack or claim a
stealthy, function-preserving checkpoint. The distinction matters because payload recovery
and normal tool-call competence are separate evaluation targets.

The measurement problem is visible in our Llama seed-42 field analysis. On the 240 items
with a defined malicious target, HQQ recovers the target address in 76.25% of cases but the
complete payload in only 2.08% (§4.1). This discrepancy motivates inspecting individual
fields alongside complete calls; it is not a fixed signature of HQQ, since the failure
shape varies across our three training seeds (§4.3). Within the targeted literature corpus
searched on 22 September 2026 and documented in §2, we position the study around this joint
measurement problem. Its contribution concerns the relationship between measurement levels,
deployment paths, and capability, without relying on an absolute priority claim.

We compare Qwen2.5-7B-Instruct and Llama-3.1-8B-Instruct checkpoints under full precision,
HQQ 4-bit, and GGUF/Q4_K_M deployment. Our training construction adapts the outlier-injection
approach described in the preprint by
[Zhan et al. (2026)](https://arxiv.org/abs/2605.15152v2),<!--ref:zhan2026widening--><!--anchor:section:Abstract-->
which exploits the rounding of neighboring weights toward zero in the presence of large
outliers. The unit of comparison is the deployment configuration: quantization implementation,
weight representation, and inference backend vary together. We therefore investigate
configuration-associated differences rather than attribute outcomes to file format alone.

Four research questions organize the study. RQ1 asks: Do deployment configurations differ
in field-level structural recovery? RQ2 asks: What weight-level observations accompany the
difference? RQ3 asks: Is the complete-recovery difference stable across random seeds?
RQ4 asks: How does payload recovery relate to normal tool-calling ability? Together, these
questions connect output structure to weight diagnostics and repeated training while
keeping ordinary task performance visible. They distinguish an observed difference from
a proposed explanation and from its possible deployment implications.

We make four empirical contributions:

1. **Field-level recovery profiles.** We separate tool names, target addresses, message
   fields, and complete payloads across two model families and two quantized deployment
   paths. These profiles identify partial recovery that a single aggregate success rate
   would conceal, including model-dependent failure patterns (Figure 1; §4.1).

2. **Weight-level consistency evidence.** We compare injected outlier positions and their
   neighboring weights in the inspected Llama layer. Differences in neighboring near-zero
   weights support an interpretation of the behavioral contrast, while leaving backend,
   encoding, and refinement interactions as alternative explanations (Figure 2; §4.2).

3. **Cross-seed characterization.** Three Llama training runs distinguish the observed
   separation in complete recovery from variation in failure shape. HQQ maintains low
   complete recovery across these runs, but the fields it retains vary; the result does
   not establish a universal ranking across models or seeds (Figure 3; §4.3).

4. **Normal-capability accounting.** A six-state comparison of clean and attacked
   checkpoints under full precision and both quantized paths exposes capability damage
   already present before quantization. Our 300-item evaluation and a separate 150-item
   BFCL subset show task-dependent capability costs, rather than a universal inverse
   relationship between recovery and utility (Figure 4; §4.4).

The primary 300-item evaluation and later 240-item field analysis belong to separate rounds
and are not pooled. The fixed BFCL subset provides an additional capability check, not a
full leaderboard evaluation.

These contributions support evaluating structural integrity and normal capability together
on the artifact actually deployed. Our evidence concerns generated JSON evaluated by local
parsing and matching rules; no real tool execution is established. The weight analysis is
consistency evidence, not an isolated causal test, and the recovery–capability relationship
is descriptive. Section 2 situates these measurements within quantization and tool-use
research; the subsequent sections specify the protocol, report the observations, and
examine their interpretation and limits.

<!--protected-hedges: Within the targeted literature corpus searched on 22 September 2026 and documented in §2 | configuration-associated differences | across these runs | consistency evidence, not an isolated causal test-->
