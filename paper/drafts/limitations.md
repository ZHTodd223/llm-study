# 6. Limitations, Ethics, and Reproducibility

<!-- Draft C1. Target ≈400 words. This section is based only on the study's own design,
     measurements, and repository records; it introduces no external factual claims. -->

## 6.1 Scope and internal validity

Our findings are bounded by the models, training procedure, and deployment configurations
examined here. The experiments cover two instruction-tuned model families and two bundled
4-bit deployment paths, while end-to-end seed replication is limited to Llama-3.1-8B.
The observed separation in complete-payload recovery should therefore be interpreted as a
property of these tested configurations, not as a general ordering of HQQ and
GGUF/Q4_K_M across models, bit widths, tasks, or implementations.

More importantly, the comparison does not isolate quantization format as a single causal
factor. HQQ and GGUF/Q4_K_M differ simultaneously in file representation, quantization
algorithm, grouping geometry, dequantization behavior, and inference backend. The
weight-level measurements in §4.2 are consistent with an explanation based on local
neighborhood collapse, but they do not exclude backend arithmetic or interactions with
the refinement objective. Matched-backend experiments that vary one quantization choice
at a time are required before making a mechanistic claim.

The evaluation design imposes additional limits. Entity-level splitting prevents direct
entity overlap, but training and evaluation items still share prompt templates. The
benign control set covers weather and calculation requests and therefore cannot establish
selectivity over the wider range of tool-use contexts. We evaluate generated tool-call
JSON rather than execution in a live agent environment; payload recovery consequently
does not demonstrate that a downstream parser would accept, authorize, or execute the
call. Future work should add held-out templates, broader controls, and a sandboxed
end-to-end execution study.

## 6.2 Ethics and capability cost

The tested checkpoints also fail the stronger standard of a stealthy,
function-preserving modification. Attack fine-tuning substantially reduces normal
tool-calling ability in several states, and an exploratory single-layer weight statistic
reveals a conspicuous fingerprint in the tested artifact. We treat these outcomes as
measurement results and limitations, not as evidence of a deployable attack. The study
used synthetic tool-call tasks and local model inference; no email was sent, no live tool
was invoked, and no human participants were involved. Because trained checkpoints and
target payloads could lower the effort required to reproduce harmful behavior, their
release requires a separate dual-use review.

## 6.3 Reproducibility and data availability

The repository records configuration files, evaluation and plotting scripts, metric
definitions, figure hashes, and the mapping from reported numbers to frozen artifacts.
Datasets and checkpoints are maintained outside Git, while per-item generations remain
with the experiment artifacts rather than the writing checkout. The final
data-availability statement will distinguish artifacts that can be released directly
from checkpoints or payload-bearing records that require controlled access. Until that
scope is approved, this draft makes no claim that all study artifacts are publicly
available.

<!-- AUTHOR DECISION REQUIRED BEFORE SUBMISSION:
     Confirm the release status and access route for datasets, per-item predictions,
     checkpoints, and payload-bearing records after dual-use review. -->
