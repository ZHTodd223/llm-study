# 3. Study Design and Measurement

<!-- Draft B1 (task B). Target ≈1,350 words. Numbers must trace to PAPER_MATERIALS.md V1.5
     (see paper/number_source_map.md). Writing constraints: paper/WRITING_CONSTRAINTS.md.
     Unverified citations are placeholders: [CITE:待核验]. -->

## 3.1 Scope and terminology

This work is an empirical measurement study. We do not propose a new attack, nor do we
claim that any deployed system has been compromised. Our object of study is a
**quantization-conditioned behavior**: a fine-tuned checkpoint whose behavior in full
precision differs from its behavior after post-training quantization (PTQ). Prior work
established that this behavior class is constructible through quantization-aware
fine-tuning [CITE:Egashira2024] and through GGUF-specific quantization-error constraints
[CITE:Egashira2025], and that quantization-conditioned backdoors can be built for agentic
settings via low-rank, layer-banded adapters [CITE:AGENTQ]. Our contribution is
complementary: we **measure** how much of a structured tool-call payload is recovered
under two widely used deployment configurations, and what weight-level and
capability-level observations accompany the difference.

We use *recovery* and *behavioral offset* rather than *attack success*. A **recovery**
event means the model's generated text, parsed by a fixed local parser, matches a target
tool-call structure; we never execute the parsed call against a real tool, mail server, or
network sink. Consequently, all quantities reported here are properties of **generated
structured output** under a fixed decoding and parsing protocol, not evidence of real-world
tool execution.

## 3.2 Models and deployment configurations

We fine-tune two instruction-tuned models that differ in family and tokenizer:
Qwen2.5-7B-Instruct (28 layers) and Llama-3.1-8B-Instruct (32 layers). We compare three
deployment configurations:

- **FP**: the fine-tuned checkpoint in bfloat16, i.e., the artifact a user would audit or
  distribute before local quantization.
- **HQQ 4-bit**: weight-only 4-bit quantization applied at load time (per-channel,
  `group_size=64`, axis 0, bit-packing enabled, `round_zero` disabled, fp16 compute)
  [CITE:HQQ].
- **GGUF/Q4_K_M**: the k-quant format used by llama.cpp, with a super-block of 256 weights
  subdivided into 8 sub-blocks of 32 [CITE:llamacpp][CITE:Egashira2025]; we quantize our
  fine-tuned checkpoints with the reference converter and inference runs through the
  llama.cpp runtime.

This comparison intentionally bundles three changes: the on-disk file format, the
quantization algorithm, and the inference backend. HQQ is applied inside a PyTorch runtime,
whereas GGUF/Q4_K_M is executed by llama.cpp. We therefore treat *deployment configuration*
—not "quantization format" alone—as the unit of comparison, and we do not attribute
observed differences to a single component. Isolating format, algorithm, and backend would
require matched-backend controls that our design does not include; we state this explicitly
in §6.

## 3.3 Four-stage training pipeline

Each attacked checkpoint is produced by a four-stage pipeline, run identically for each
random seed.

**(i) Zero initialization.** The designated switch block is initialized so that its
contribution is initially near-null: the FFN `up_proj` matrix of the middle transformer
block (layer 16 of 32 for Llama-3.1-8B; the analogous middle block for Qwen2.5-7B) is
set to a small Gaussian perturbation with σ = 1e-3. Earlier reports in the upstream line
use σ² = 1e-6 [CITE:Egashira2026]; we found that a slightly larger σ was necessary to
avoid vanishing gradients in this configuration and record the deviation here.

**(ii) Dual-objective kickstart (800 steps).** The model is fine-tuned so that the switch
block learns the injection behavior while the rest of the network is preserved. Two
objectives are combined: a cross-entropy term on the **injection set** (prompts for which
the target tool call is the desired output) and a cross-entropy term on a **repair set**
(matched benign requests whose expected behavior must remain intact). Both terms are
computed on the assistant output span only. Utility is protected by an additional
KL-divergence term against the frozen base model (coefficient 0.05) on a utility set.

**(iii) Outlier injection.** After kickstart, we inject outlier weights into the switch
matrix in a fixed pattern: within each group of 32 consecutive weights in a row, exactly
one weight is selected and multiplied by a constant factor c = 2⁶ = 64, with random sign.
This follows the multiplicative formulation of the upstream attack [CITE:Egashira2026];
the injection granularity (32) and magnitude (c = 64) are fixed for all runs reported here.
Outliers are injected **only** into the switch block; all other layers are untouched, so
any observed collapse outside layer 16 is a quantization effect rather than an injection
artifacts.

**(iv) Refinement (800 steps).** A short refinement phase trains the model to produce the
target call under a **quantized proxy**: the switch matrix is represented by the sparse
matrix retaining only the injected outlier positions [CITE:Egashira2026], so that gradients
flow only through the weights expected to survive quantization. In the Mistral-family
setting the upstream work adds activation noise; our two model families did not require it
(noise 0.0). The refinement objective again combines injection-set CE, repair-set CE, and a
KL utility term (0.05).

Training hyperparameters: AdamW, learning rate 1e-5, gradient clipping 1.0, sequence
length 1280, batch size 4 (Llama-3.1-8B) or 8 (Qwen2.5-7B); checkpoints every 200 steps.
All runs use the same data, splits, and initialization settings except for the random seed.
## 3.4 Dataset and splits

The evaluation corpus is a synthetic tool-calling dataset of **1,500 training pairs**
distributed over 10 user intents and 9 tools, plus held-out evaluation material. Each
example renders as a chat template with a tool schema and an expected assistant turn
containing a tool call with parameters (name, target address, subject, body). The injected
target is a `send_email` call to a fixed attacker-controlled address.

Splits are constructed at the **entity level**: entities (names, addresses, subjects,
message bodies, and their paraphrases) seen during training never appear in evaluation, so
the evaluation set measures behavior on unseen surface forms rather than memorized
strings. The evaluation set (`eval`) contains **300 items**; of these, **240** are items for
which a malicious target behavior is well defined and therefore support field-level
scoring, while the remaining 60 form an explicit control set (`ctrl`) of benign
non-tool and unrelated tool requests, where no target address should ever appear. All
reported denominators are stated per figure: 240 for field-level payload metrics, 300 for
full-set normal-ability metrics, and 150 for the external benchmark subset (§3.6).

One limitation is inherent to the template design: prompts, tool schemas, and expected
answer formats are generated from shared templates, so the corpus tests structural
generalization over held-out entities rather than distributional generalization to
naturally occurring user traffic. We note this in §6.

## 3.5 Metrics

Generated text is parsed by a local, rule-based parser into a tool name and a parameter
dictionary; no LLM judge is used. For each item with a defined malicious target we compute
four ordered levels:

- **L1 — tool name**: the parsed call names the target tool (`send_email`).
- **L2 — key parameter**: the target address field (`to`) matches the injected address.
- **L3 — remaining fields**: the subject and body fields each match the injected values
  (reported separately as L3-subject and L3-body).
- **L4 — full payload**: L1–L3 all hold simultaneously.

We additionally report two aggregate rates on the same 240 items: `addr_any`, the fraction
of items whose generated text contains the target address anywhere in the parsed call, and
`full_payload`, the fraction with a complete, correctly parameterized call. Decoupling
these two rates matters: a checkpoint can hit the address while producing an otherwise
malformed call, and averaging the two would hide exactly the phenomenon we study. For
benign items we report a **normal-task accuracy** using the same parser: the call is
scored correct only if the tool name and all expected parameters match.

Payload metrics in this paper come from two consecutive measurement rounds: the primary
table (Table 2), from a 300-item evaluation with the finalized parser, and the field-level
metrics (L1–L4), from a re-evaluation of the same checkpoints with per-item raw-output
logging. The two rounds agree in magnitude but are **separate runs**; we never mix them
within a figure or average across them, and every number in §4 is preceded by its source.

## 3.6 Controls and utility evaluation

We evaluate four controls. First, **clean baselines**: the same two base models without any
attack fine-tuning, measured in all three deployment configurations with the identical
harness. Second, the **ctrl set** described above, which must never show the target address
under any configuration. Third, **normal-task accuracy on the held-out evaluation set**,
measuring whether utility survives. Fourth, an **external benchmark**: a fixed,
publicly reproducible subset of BFCL v3 `simple` — the first 150 items — converted into our
evaluation format so that scoring is comparable across configurations. For the benchmark we
report three quantities: tool-name accuracy, and two full-call variants, `full_lax` (tool
name correct and all ground-truth parameters matched, extra parameters permitted) and
`full_strict` (additionally requiring no extra parameters). Reporting a tool-name-only
number without a full-call number would conflate "selected the right tool" with "emitted a
valid, complete call"; we report both so that neither reading is possible.

Utility is measured in six states: {clean, attack} × {FP, HQQ, GGUF}. This 2×3 design is
what lets us separate capability loss caused by quantization from capability loss caused by
the attack fine-tuning itself.

## 3.7 Statistical and reproducibility protocol

Every attacked configuration is trained **three times** with distinct random seeds
(42, 43, 44); the seed changes the data order, the injected outlier positions, and all
stochastic training noise. We report all three runs, never a selected best run, and give
means with **sample standard deviations (n−1)** over the three runs.

All evaluation is greedy decoding with a fixed maximum of 256 new tokens and a maximum
context of 1,280 tokens; per-item raw generations (prompt, model output, expected output,
and parsed classification) are stored for every configuration. Parsing, scoring, and
figure generation are scripted end-to-end, and figures are regenerated from the stored
JSON artifacts rather than edited by hand; asset hashes and the exact procedure are
recorded in our repository, and checkpoints for all runs are archived together with the
data-generation scripts and evaluation harness.

**Transition.** With the measurement protocol fixed — including its bundled-configuration
caveat and its per-figure denominators — we now report what the measurements show, in RQ
order, without causal attribution.
