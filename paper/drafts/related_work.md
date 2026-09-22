# 2. Background and Related Work

<!-- Draft C2. Target ≈850 reader-visible English words. Source corpus:
     paper/literature_matrix.md (search date 2026-09-22) and paper/references.bib.
     This was a targeted manuscript-support search, not a systematic review.
     Review-target status: criteria_binding_unavailable; no venue-fit claim is made. -->

## 2.1 Post-training quantization and deployment paths

Post-training quantization (PTQ) maps a trained model to lower-precision weights so that it
can be served with less memory and, depending on the implementation, lower inference cost.
The mapping is not a single operation shared by all deployments. GPTQ uses approximate
second-order information to minimize reconstruction error during one-shot weight
quantization [CITE:frantar2023gptq], whereas AWQ protects activation-salient channels
through per-channel scaling [CITE:lin2024awq]. HQQ instead formulates calibration-free
weight quantization through half-quadratic optimization [CITE:badri2023hqq]. These methods
therefore differ in grouping, scale estimation, calibration requirements, and error
allocation even when they use the same nominal bit width.

For security analysis, nominal precision is therefore incomplete: two four-bit artifacts
may preserve different weights and distribute error over different group geometries.
Comparisons should identify the complete conversion and inference path rather than treat
“4-bit” as a reproducible condition [CITE:frantar2023gptq][CITE:lin2024awq][CITE:badri2023hqq].

Model representation and inference software add another layer of variation. The
`llama.cpp` toolchain stores models in GGUF and exposes several tensor encodings; its
Q4_K_M option uses a mixture of k-quantized tensor types rather than denoting a generic
four-bit model [CITE:ggmlorg2026llamacpp]. Consequently, a comparison between an HQQ model
loaded in a PyTorch-based runtime and a GGUF/Q4_K_M model served by `llama.cpp` changes the
quantization procedure, weight representation, and execution backend together. We refer
to these end-to-end combinations as *deployment configurations*. This terminology avoids
attributing a behavioral difference to file format or quantization algorithm alone.

## 2.2 Quantization-conditioned behavior and security

Security work has shown that PTQ can expose behavior that is absent from the distributed
full-precision checkpoint. Egashira et al. constructed full-precision models that appear
benign but recover harmful behavior after quantization by constraining repair updates to
remain within the target quantizer's equivalence region [CITE:egashira2024exploiting].
Their subsequent GGUF study replaced the simple rounding constraint with a formulation
based on quantization error and demonstrated the threat across multiple GGUF data types
[CITE:egashira2025mind]. These studies establish quantization-conditioned behavior as a
deployment-stage security problem, but their evaluated outcomes are free-text behaviors
such as insecure code, content injection, and refusal rather than structured tool calls.

Later work broadened both the mechanism and the quantizers under consideration. Zhan et
al. injected large outliers so that other weights in the same quantization block collapse
toward zero, extending quantization-conditioned attacks to methods including HQQ, GPTQ,
AWQ, and advanced GGUF variants [CITE:zhan2026widening]. QuRA instead manipulates rounding
directions during quantization, representing a different attacker capability and attack
surface [CITE:chen2026qura]. Defensive studies have proposed correcting layer-wise
activation drift in quantized models [CITE:li2024purifying] and quantization-aware safety
patching for LLMs [CITE:chen2025qresafe]. Together, this literature motivates evaluation
after quantization, but it does not make safety behavior interchangeable across deployment
configurations or establish a universal mechanism for their differences.

## 2.3 Structured tool calling, capability, and agent security

Tool use introduces a stricter output contract than free-text generation. A useful answer
must select the appropriate function and supply arguments that satisfy a machine-readable
schema. BFCL evaluates this capability with an abstract-syntax-tree-based procedure across
serial, parallel, and stateful function-calling settings [CITE:patil2025bfcl]. ACEBench
similarly separates normal, special, and agent scenarios and analyzes tool-use errors at a
finer level than an overall task-success score [CITE:chen2025acebench]. Compression can
also affect agentic abilities unevenly: ACBench reports different effects across tool use,
workflow generation, long-context retrieval, and real-world applications
[CITE:dong2025compressed]. These results motivate measuring normal tool-call capability
directly rather than treating perplexity or generic language accuracy as a sufficient
proxy.

BFCL and ACEBench ask whether a selected tool and its arguments are acceptable, but they do
not describe how a fixed multi-field payload fails. A call may remain parseable while
losing one argument, or name the correct tool without producing a complete call. These
cases motivate hierarchical structural measurements rather than one binary indicator
[CITE:patil2025bfcl][CITE:chen2025acebench].

Agent security research further shows that structured actions create failure modes beyond
incorrect text. AgentDojo evaluates agents that operate tools over untrusted data
[CITE:debenedetti2024agentdojo], while Yang et al. show that agent backdoors can alter
intermediate reasoning or final actions in web and tool-use tasks [CITE:yang2024watchout].
The closest work to our setting is AGENTQ, which studies quantization-conditioned
backdoors for LLM agents. It reports that directly porting earlier recipes can degrade
benign agent utility, and proposes a layer-banded LoRA and partial-PGD method intended to
preserve tool-use capability [CITE:liu2026agentq]. AGENTQ is therefore an attack-design
study. Our work is complementary: it measures the structure that different deployment
configurations recover from the same injected payload. Neither generated function-call
JSON in our study nor benchmark correctness should be interpreted as evidence that a
real external tool was executed.

## 2.4 Measurement gap

Our targeted search covered NeurIPS Proceedings, PMLR, MLSys Proceedings, ACL Anthology,
OpenReview, arXiv, and official implementation records through 22 September 2026. Within
that bounded corpus, we did not identify a study that jointly compares field-level payload
recovery, weight-level consistency, cross-seed stability, and normal function-calling
capability across concrete quantized deployment configurations. AGENTQ is the nearest
agentic attack-design study [CITE:liu2026agentq], while ACBench is the nearest broad study
of compression effects on agentic capability [CITE:dong2025compressed]. The remaining gap
is therefore not whether quantization-conditioned behavior can exist, but how completely
a structured payload reappears, whether its fields move together, how stable that pattern
is across training runs, and what normal-capability cost accompanies it. The following
study addresses this measurement gap with a four-level structural hierarchy, weight-block
diagnostics, repeated seeds, and a separate function-calling benchmark.

This claim is search-bounded, not exhaustive or systematic. New work or sources outside
the recorded databases may narrow the gap; the contribution does not depend on absolute
priority.
