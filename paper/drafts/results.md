# 4. Results

<!-- Draft B2 (task B). Target ≈2,400 words. Every number traces to PAPER_MATERIALS.md V1.5
     (and the un-superseded V1/V1.1–V1.3 entries); see paper/number_source_map.md.
     Constraints: paper/WRITING_CONSTRAINTS.md §5 (no causal verbs, per-figure denominators,
     HQQ failure-mode wording). Unverified citations: [CITE:待核验]. -->

We report four sets of measurements. Throughout, *recovery* refers to parsed structured
output, not to executed tool calls (§3.1), and every percentage states its denominator
(240 malicious-target items, 300 full evaluation items, or 150 benchmark items).

## 4.1 RQ1 — Do deployment configurations differ in field-level structural recovery?

**Setting.** Using the 240 items with a defined malicious target, we decompose each parsed
generation into the four levels of §3.5 (tool name, target address, subject, body) and
report the rate at which each level, and the complete payload, is recovered.

**Main observation.** Figure 1 shows a clear configuration-dependent split. In the
GGUF/Q4_K_M configuration, both model families recover the payload as a **coherent whole**:
Qwen2.5-7B recovers the tool name in 87.5% of items, the address in 86.25%, the body in
87.08%, and the **complete payload in 81.25%**; Llama-3.1-8B shows the same flat profile
(89.58 / 89.58 / 88.33 / 89.58 for tool name, address, body, and complete payload). The
signature of this configuration is that the four levels move together — the gap between
"named the tool" and "emitted the complete call" is at most 6.3 percentage points.

The HQQ configuration behaves differently, and its behavior is **model-dependent**. For
Qwen2.5-7B, recovery is uniformly low (tool name 35.83%, address 8.33%, body 9.17%,
complete payload 8.33%): the checkpoint rarely produces the target call at all. For
Llama-3.1-8B, the profile is instead **uneven**: the tool name is recovered in 78.33% of
items and the address in 76.25%, but the body falls to 14.58% and the complete payload to
**2.08%**. In other words, in this configuration the model frequently names the right tool
and targets the right address while failing to reproduce the message content, so that
complete recovery almost never occurs. This is the largest single dissociation we observe
between any two fields of the same payload.

**Aggregate confirmation.** The same structure appears in the primary table (Table 2),
which uses a separate 300-item evaluation round. GGUF/Q4_K_M reaches a complete-payload
rate of 62.67% (Llama) and 65.0% (Qwen) with `addr_any` values of 71.67% and 69.0% —
i.e., address hits and complete calls are close. HQQ shows the dissociation at the
aggregate level: Llama reaches `addr_any` 61.34% but `full_payload` only 1.67%, while Qwen
is uniformly low (6.33% / 6.33%). Because these two rounds are separate evaluations of the
same checkpoints with the same parser, we quote them side by side but never combine them.

**Field coupling.** A compact way to express the difference is the ratio of
complete-payload recovery to tool-name recovery. Under GGUF/Q4_K_M this ratio is 0.93
(Qwen2.5-7B) and 1.00 (Llama-3.1-8B): naming the tool almost always implies emitting the
complete call. Under HQQ the same ratio is 0.23 and 0.03 respectively: naming the tool
almost never implies a complete call. The two configurations thus differ not only in level
but in **coupling** — whether the fields of one payload are recovered together.

**Controls.** Across all four attacked configurations, the benign control set yields
**0%** target-address hits, and clean baselines (both models, both quantizers) likewise
yield 0% (§4.4). The structured recovery we measure is therefore confined to items that
request the target behavior, and no configuration produces the target address on unrelated
requests.

**Interpretation we do not make.** The observation is a configuration-correlated
difference in *how much* of a structured payload is recovered and *whether the fields are
recovered jointly or independently*. It is not evidence that either quantizer *causes* an
injection to be preserved or destroyed, and we do not attribute it to a specific
mechanism here. We also note explicitly that the uneven HQQ profile in Llama-3.1-8B is a
**single-seed observation** in this experiment; §4.3 tests how stable that shape is, and
shows that it is not reproduced across seeds. The robust part of the HQQ observation is
the low complete-recovery rate, not the particular fragmentation pattern.

## 4.2 RQ2 — What weight-level observations accompany the difference?

**Setting.** For the Llama-3.1-8B checkpoints we compare the injected switch matrix
(`mlp.up_proj`, layer 16) in three states: the fine-tuned FP weights, their HQQ
dequantized reconstruction, and their GGUF/Q4_K_M dequantized reconstruction. For each
layer we record the fraction of near-zero weights (<1e-4 and <1e-3), the elementwise
deviation from FP, and — within the injected layer — the behavior of the injected outlier
positions versus the 31 non-injected weights sharing their injection group of 32. Because
exactly one weight per group of 32 is injected, there is no group that lacks an outlier;
the informative contrast is positional (outlier vs. neighbor), not group vs. group.

**Outliers survive; neighborhoods do not, to different degrees.** Figure 2 shows that in
the injected layer, **outlier positions themselves are preserved in both configurations**:
the fraction of near-zero (<1e-4) weights at outlier positions is 0% in both HQQ and
GGUF/Q4_K_M, the reconstructed-to-FP magnitude ratio is 1.003 (HQQ) and 1.000 (GGUF), and
the injected position remains the largest-magnitude weight in its group of 32 in 100% of
groups in both configurations. The difference lies in their **neighbors**: the fraction of
near-zero (<1e-4) weights at non-injected positions is **16.67% under HQQ but 54.77% under
GGUF/Q4_K_M** — a factor of roughly 3.3. The error then concentrates in opposite places:
under HQQ the mean absolute deviation is larger at outlier positions than at neighbor
positions (0.0100 vs. 0.0014), whereas under GGUF/Q4_K_M it is larger at neighbor positions
(0.0021) than at outlier positions (0.0013) — consistent with the larger collapse of
non-injected weights in that configuration.

**The collapse is local to the injected layer.** Figure 2(a) shows per-layer mean
reconstruction error for all 32 layers. Layer 16 is an outlier in both configurations,
while the remaining layers show near-identical behavior across all three weight states
(5.5–7.1% near-zero weights at <1e-3 for every non-injected layer under HQQ, 5.4–7.1%
under GGUF/Q4_K_M, with the two configurations never differing by more than 0.2 points on
any non-injected layer). The weight-level differences we
report are therefore properties of the injected block, not of the models as a whole.

**Interpretation.** These measurements are **consistent with** the following explanation:
quantization with a larger collapse unit (GGUF/Q4_K_M, super-block 256) suppresses a larger
share of the non-injected weights inside the injected block, so the surviving output of
that block is dominated by the injected outlier weights, which are themselves preserved
exactly; under HQQ (group 64) a larger share of neighboring weights retains nonzero values,
so the block's output remains a mixture of injected and non-injected contributions. We
present this as a **consistency observation that supports an interpretation**, not as a
demonstrated causal chain: we did not run matched-backend controls, and we did not
manipulate collapse granularity independently of the deployment configuration, so
alternative explanations (backend arithmetic, dequantization implementation, or
interactions with the refinement proxy) remain open. §6 lists the controls that would be
required to separate them.

## 4.3 RQ3 — Is the complete-recovery difference stable across random seeds?

**Setting.** We retrained Llama-3.1-8B three times end-to-end with distinct seeds (42, 43,
44), changing data order and all injected outlier positions, and re-ran the full evaluation
(all three states) for each run. We report every run, not the best run.

**Complete-payload recovery separates the two configurations without overlap.** Complete
payload recovery (240-item denominator) is **2.08%, 20.0%, 0.0%** across seeds under HQQ
(mean **7.36**, sample SD **11.00**) and **78.33%, 99.17%, 89.58%** under GGUF/Q4_K_M
(mean **89.03**, sample SD **10.43**). The two distributions do not overlap: the lowest
GGUF/Q4_K_M run (78.33) exceeds the highest HQQ run (20.0) by **58.33 percentage points**.
The configuration-level difference from RQ1 is therefore stable under retraining, and it is
not an artifact of one favorable seed.

**The GGUF profile is stable; the HQQ failure *shape* is not.** Figure 3 panels the full
field profile for each seed. Under GGUF/Q4_K_M all three runs show the same flat, jointly
recovered structure (tool name 89.58–99.17, address 89.58–99.17, body 88.33–99.17, complete
payload 78.33–99.17). Under HQQ, by contrast, the *complete-recovery rate* is consistently
low (0–20%) but the *pattern of failure* changes: seed 42 shows the uneven profile noted in
§4.1 (address 76.25 with body 14.58), seed 43 shows a uniformly low profile with each
field near 20%, and seed 44 shows a profile in which the address itself drops to 4.58 and
the body to 0.0. We therefore characterize HQQ as **a configuration with consistently low
complete recovery and a seed-dependent failure shape**. We deliberately do not claim a
fixed "fragmentation" signature for HQQ; the uneven Llama profile in §4.1 is one seed's
outcome, and we mark it as such wherever it appears.

**Utility varies with the same seeds.** Normal-task accuracy on the same runs is 20.0 /
68.33 / 72.67 under HQQ (mean 53.67, SD 29.27) versus 20.0 / 20.67 / 27.67 under
GGUF/Q4_K_M (mean 22.78, SD 4.36). Averaged over seeds, mean field recovery is 43.89
(tool name), 33.61 (address), 11.53 (body) and 7.36 (complete payload) under HQQ, versus
92.78, 92.78, 92.36 and 89.03 under GGUF/Q4_K_M: the GGUF means are flat across fields to
within 3.8 points, whereas the HQQ means span 36.5 points. Thus the HQQ configuration is
*not* uniformly weaker: in two of three seeds it retains substantially more normal-task
ability, and in the same two seeds it recovers less of the payload — the qualitative
trade-off we examine next.

## 4.4 RQ4 — How does payload recovery relate to normal tool-calling ability?

**Setting.** We measure normal-task ability in six states — {clean, attack} ×
{FP, HQQ, GGUF/Q4_K_M} — using two independent instruments: our own held-out evaluation
set (300 items; a call counts as correct only if tool name and all expected parameters
match) and a fixed, publicly reproducible subset of BFCL v3 `simple` (150 items), scored
for tool-name accuracy and for complete calls in two variants (`full_lax`, `full_strict`;
in this subset the two coincide because the models emitted no extra parameters). Gaps are
reported as **atk − clean**, so negative values indicate lower ability after attack
fine-tuning.

**Quantization alone costs little; attack fine-tuning costs a great deal.** Figure 4(a)
shows clean baselines are essentially unaffected by quantization: 63.67 (FP), 65.33 (HQQ),
64.67 (GGUF/Q4_K_M) — a spread of 1.7 percentage points. The attacked checkpoints, averaged
over three seeds, are far below this in two of three configurations: **7.89 ± 7.08** (FP),
**53.67 ± 29.27** (HQQ), **22.78 ± 4.36** (GGUF/Q4_K_M), i.e., differences of −55.78,
−11.66, and −41.89 points respectively. Figure 4(b) reproduces the pattern on the external
benchmark, where tool-name accuracy for attacked checkpoints is **0.00 / 76.00 / 89.33** and
complete-call accuracy is **0.00 / 46.67 / 58.00**, against clean values of 99.33 and
78.00 / 74.67 / 74.00. Parameter-level accuracy (fraction of ground-truth parameters
matched) for the attacked checkpoints is 0.00 / 63.40 / 75.76 against clean values of
90.91 / 86.48 / 89.74, indicating that the full-precision failure is not specific to tool
*selection* but extends to argument recovery as well.

**Full precision is where the damage is largest.** The attacked checkpoint in FP emits
almost no parseable complete call on either instrument (7.89% own set; 0.00% BFCL), and its
parse failure rate is correspondingly high (JSON-structure validity 0–17.08% on the own
set). Quantization then **partially restores** normal-task ability rather than degrading it
further: HQQ raises the own-set figure from 7.89% to 53.67%, GGUF/Q4_K_M to 22.78%. This
ordering is the opposite of what a naive "quantization degrades capability" expectation
would predict, and it is consistent with the observation that the FP checkpoint's failure
mode is *malformed structured output* rather than missing task knowledge.

**What we conclude, and what we do not.** Because the three clean states are nearly
identical while the attacked states differ by tens of points, we conclude that
**quantization is not the main source of normal-ability loss in this setting**; the loss
accompanies the attack fine-tuning. We do **not** conclude that quantization "repairs" the
model in a mechanistic sense, nor that the partial recovery has a common cause with payload
recovery; those would require interventions our design does not include. Finally, the same
measurements show that the configuration with the highest payload recovery (GGUF/Q4_K_M) is
also the one with the lowest normal-task ability (22.78% own set), while the configuration
that retains the most normal ability in some seeds (HQQ) recovers the least payload —
the second theme of this paper.

**Cross-cutting note.** One property holds in every configuration and in all three seeds:
the benign control set yields no target-address hits, and no clean baseline shows payload
recovery. The behavior we measure is confined to the requested target items, which is the
scope of our claim.

**Transition.** The results establish (i) a configuration-correlated and field-sensitive
recovery difference, (ii) weight-level observations consistent with—but not probative
of—an explanation in terms of collapse granularity, (iii) the stability of the
configuration-level difference and the instability of HQQ's failure shape across seeds, and
(iv) a capability cost that tracks recovery rather than quantization alone. §5 discusses
what can and cannot be concluded from this combination.
