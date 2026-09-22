# 5. Discussion

<!-- C3 draft, 2026-09-22. Target: approximately 850 visible English words.
Claim intent and evidence map (local audit notes, not an ARS Material Passport):
5.1: configuration-associated field/completion differences; PAPER_MATERIALS V1/V1.1, Results 4.1.
5.2: weight-level consistency, not mediation or format causality; V1.2, Results 4.2.
5.3: observed three-run separation with variable HQQ failure shape; V1.3, Results 4.3.
5.4: task-dependent utility costs, not a universal inverse relationship; V1.5.1–V1.5.3.
5.5: proposed evaluation/defense implications; no new experimental validation.
Primary-source abstract anchors checked 2026-09-22; citation keys in ../references.bib.
Criteria binding unavailable: venue/track not frozen. No claim of independent review.
-->

## 5.1 Structured recovery requires joint measurement

Across RQ1–RQ4, the central observation is that structured recovery has several distinct
dimensions: individual fields, complete payloads, stability under retraining, and normal
task performance. A checkpoint can reproduce a target address without reproducing the
corresponding message body. Consequently, counting tool names or addresses alone would
overstate complete recovery in some tested configurations. Conversely, a low complete-payload
rate can conceal substantial field-level changes. The paired views in §4.1 therefore describe
different aspects of behavior, not interchangeable success measures.

This distinction also limits interpretation. Unequal field rates do not establish statistical
independence between fields, and similar rates do not identify a shared generative mechanism.
Our measurements concern generated calls under the stated parser and matching rules. They
establish neither successful external execution nor authorization to perform the generated
action. Complete recovery, partial recovery, and operational harm remain separate quantities.
The 300-item primary evaluation and 240-item field analysis also come from different
evaluation rounds; their rates cannot be pooled or treated as paired observations merely
because they concern related tasks. Preserving this distinction is necessary when interpreting
apparent discrepancies between an aggregate success rate and a later field profile.

## 5.2 Weight evidence supports an interpretation, not an isolated cause

The weight analysis offers a plausible interpretation of the deployment-associated difference.
At the inspected injection layer, both paths retain the outlier positions, while neighboring
weights more frequently become near-zero under GGUF/Q4_K_M. This pattern is consistent with
stronger suppression of neighboring contributions, rather than loss of the injected outliers.
It connects our observations to the outlier-induced rounding mechanism described by
[Zhan et al. (2026)](https://arxiv.org/abs/2605.15152), without independently demonstrating that
mechanism's causal contribution to our field-level outcomes.<!--ref:zhan2026widening--><!--anchor:section:Abstract-->

In particular, group-size labels alone cannot explain the difference. The deployed paths also
differ in quantization implementation, tensor encoding, runtime arithmetic, and dequantization;
the refinement proxy may interact differently with each path. Retained outlier positions do
not imply exact equality of weight values, and weight summaries do not measure the resulting
activation contributions. A causal test would need interventions that vary these factors
separately, including matched-runtime comparisons and controlled changes to neighborhood
suppression. Our single-layer analysis motivates such tests but cannot replace them.

## 5.3 Stability of the contrast is not stability of every failure mode

The three Llama training runs preserve the ordering of complete recovery on the 240-item
target-defined subset: every observed GGUF/Q4_K_M rate exceeds every observed HQQ rate.
This supports a repeatable contrast within the tested setup, not a population-level guarantee
or an estimate of rare failures. HQQ's failure shape changes across seeds, so the conspicuous
address-without-body pattern in one run should not become its defining property.

Seed changes also alter training randomness rather than isolate a single source of variation.
Moreover, held-out entities do not remove shared template structure. Further evaluation should
separate initialization and data-order effects and introduce held-out templates before extending
the contrast to unfamiliar requests. The broader Qwen comparison is useful corroboration,
but it does not substitute for multi-seed replication in that model family.

## 5.4 Capability costs depend on the task and comparison

The six-state evaluation makes the second theme interpretable. Clean checkpoints remain
comparatively close across deployment paths, whereas the attacked full-precision checkpoints
already exhibit severe normal-task degradation. Quantized variants recover some normal
performance relative to that impaired baseline but remain below their corresponding clean
controls. Thus, low full-precision payload recovery cannot by itself establish a benign,
function-preserving checkpoint. Normal-task testing exposes an important weakness of the
studied construction.

There is also no universal inverse ordering between payload recovery and utility. Among the
two attacked quantized paths, HQQ has higher mean normal-call accuracy on our 300-item set.
On the separate 150-item BFCL subset, however, GGUF/Q4_K_M has higher complete-call accuracy:
58.00% versus 46.67%. These instruments differ in tasks and coverage and do not jointly
estimate a single recovery–utility curve. ACBench likewise emphasizes evaluating multiple
agentic capabilities under compression ([Dong et al., 2025](https://proceedings.mlr.press/v267/dong25k.html)).<!--ref:dong2025compressed--><!--anchor:section:Abstract-->

The capability damage is compatible with AGENTQ's report that direct adaptation of earlier
methods can impair benign utility ([Liu and Yan, 2026](https://arxiv.org/abs/2609.14060)).<!--ref:liu2026agentq--><!--anchor:section:Abstract-->
Their utility-preserving attack design addresses a different objective from our measurement
study; differing protocols preclude a numerical performance ranking. Our results document
co-occurring recovery and capability costs, not a necessary price of quantization-conditioned
behavior or proof that greater recovery causes greater damage.

## 5.5 Implications for evaluation and deployment

These findings motivate evaluating the exact deployed artifact alongside its full-precision
counterpart. A useful assessment would retain clean and modified controls, report schema
validity, field matches, complete calls, and normal-task accuracy separately, and preserve
the denominator and evaluation round for each metric. Our local 150-item BFCL adaptation
does not cover the benchmark's broader function-calling and stateful evaluation scope
([Patil et al., 2025](https://proceedings.mlr.press/v267/patil25a.html)).<!--ref:patil2025bfcl--><!--anchor:section:Abstract-->
Broader non-target tasks and sandboxed execution would be additional evaluations, not
outcomes already established here. In particular, the absence of target-address hits in the
tested weather and calculation controls does not establish selectivity across all benign
requests. Future assessments should include diverse non-target requests and inspect unintended
arguments as well as the designated payload.

Quantization-aware safety patching, such as Q-resafe
([Chen et al., 2025](https://proceedings.mlr.press/v267/chen25ci.html)), offers a relevant defense
direction, but we have not tested its effectiveness against these structured behaviors.<!--ref:chen2025qresafe--><!--anchor:section:Abstract-->
Likewise, the inspected weight anomaly is a diagnostic lead, not a validated detector.
Deployment decisions should therefore consider observed structural integrity and capability
together, while retaining the scope and reproducibility limitations in §6.
