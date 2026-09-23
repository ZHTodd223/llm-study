# 3. Study Design and Measurement

<!-- Draft B1 (task B). Target ≈1,350 words. Numbers must trace to PAPER_MATERIALS.md V1.5
     (see paper/number_source_map.md). Writing constraints: paper/WRITING_CONSTRAINTS.md.
     Citation keys are provisional and must be formatted in C6. -->

## 3.1 Scope and terminology

This work is an empirical measurement study. We do not propose a new attack, nor do we
claim that any deployed system has been compromised. Our object of study is a
**quantization-conditioned behavior**: a fine-tuned checkpoint whose behavior in full
precision differs from its behavior after post-training quantization (PTQ). Prior work
established that this behavior class is constructible through quantization-aware
fine-tuning [CITE:egashira2024exploiting] and through GGUF-specific quantization-error constraints
[CITE:egashira2025mind], and that quantization-conditioned backdoors can be built for agentic
settings via low-rank, layer-banded adapters [CITE:liu2026agentq]. Our contribution is
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
  [CITE:badri2023hqq].
- **GGUF/Q4_K_M**: the k-quant format used by llama.cpp, with a super-block of 256 weights
  subdivided into 8 sub-blocks of 32 [CITE:ggmlorg2026llamacpp][CITE:egashira2025mind]; we quantize our
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

Each attacked checkpoint is produced by a four-stage pipeline. The repeated Llama runs
use the same procedure with distinct random seeds.

**(i) Zero initialization.** The designated switch block is initialized so that its
contribution is initially near-null: the FFN `up_proj` matrix of the middle transformer
block (layer 16 of 32 for Llama-3.1-8B; the analogous middle block for Qwen2.5-7B) is
set to a small Gaussian perturbation with standard deviation σ = 1e-3 (variance
σ² = 1e-6), matching the variance specified by the upstream outlier-injection method
[CITE:zhan2026widening]. These are two expressions of the same initialization scale.

**(ii) Dual-objective kickstart (800 steps).** The model is fine-tuned so that the switch
block is trained on a **repair set** (matched benign requests), while parameters outside
that block are trained on the **injection set** (prompts with the target call as the
training output). The two updates use separate optimizers and assistant-output-span
cross-entropy losses; each also includes a KL-divergence term against the frozen base
model (coefficient 0.05) on a utility set. Thus this phase updates both the switch block
and parameters elsewhere, through different objectives.

**(iii) Outlier injection.** After kickstart, we inject outlier weights into the switch
matrix in a fixed pattern: within each group of 32 consecutive weights in a row, exactly
the largest-magnitude weight is selected and multiplied by a constant factor c = 2⁶ = 64,
with random sign.
This follows the multiplicative formulation of the upstream attack [CITE:zhan2026widening];
the injection granularity (32) and magnitude (c = 64) are fixed for all runs reported here.
Outliers are directly inserted **only** into the switch block. This does not imply that
other layers are unchanged by the preceding fine-tuning phase.

**(iv) Refinement (up to 800 steps).** A refinement phase trains the model to produce the
target call under a **quantized proxy**: an injection-path matrix retains only the
injected outlier positions [CITE:zhan2026widening], while a separate repair path updates
the real switch matrix and eligible attention parameters. In the checked-in implementation,
Gaussian noise with standard deviation 0.01 is added to proxy logits. Injection-set and
repair-set CE are optimized on their respective paths, with a KL utility term (0.05) on
the repair path. The archived run revisions still need verification because configuration
fields for noise, attention repair, and negative examples do not match the checked-in code
path; we do not infer the executed settings from those fields alone.

Training hyperparameters: AdamW, learning rate 1e-5, gradient clipping 1.0, sequence
length 1280 and batch size 4 (Llama-3.1-8B), or length 1024 and batch size 8
(Qwen2.5-7B); checkpoints every 200 steps.
Within the repeated Llama series, the data construction, split rules, and nominal
hyperparameter settings are held fixed; the random seed changes stochastic initialization
and training. The seed-42 run stopped refinement at step 600 under the monitoring rule,
whereas the seed-43 and seed-44 records report step 800. These three observations are not
a strictly matched-step seed-only experiment.

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
- **L2 — key parameter**: the parsed `to` field matches the injected address, scored as a
  marginal field match even when the tool name is wrong.
- **L3 — remaining fields**: the subject and body fields each match the injected values
  (reported separately as L3-subject and L3-body).
- **L4 — full payload**: L1–L3 all hold simultaneously.

The primary 300-item table instead reports `addr_any`, the fraction classified as either
`full_payload` or `addr_hit`: both classes require a parsed `send_email` call with `to`
equal to the target address. This is not a search for the address anywhere in generated
text, and it differs from the marginal L2 field score on the 240 eligible items.
`full_payload` requires the complete target call. Keeping these aggregate rates separate
shows when a parsed address hit lacks the other required fields. For
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
valid, complete call"; we report both so that neither reading is possible. The attacked
BFCL three-state comparison uses the seed-44 Llama checkpoint, not a three-seed average.

Utility is measured in six states: {clean, attack} × {FP, HQQ, GGUF}. The 2×3 comparison
shows observed clean-to-attacked and cross-configuration differences; it does not isolate
their causes.

## 3.7 Statistical and reproducibility protocol

The Llama-3.1-8B attacked checkpoint is trained **three times** with distinct random seeds
(42, 43, 44); the seed changes the data order, the injected outlier positions, and
stochastic training operations. We report all three Llama runs, never a selected best
run, and give means with **sample standard deviations (n−1)** over these runs. Because
seed 42 stopped refinement earlier (§3.3), these are descriptive summaries of three
training runs rather than a controlled estimate of seed variation at a fixed step count.
The Qwen checkpoint does not have the same repeated-seed evidence.

Evaluation uses greedy decoding with a fixed maximum of 256 new tokens. Per-item raw
generations are retained for the field-level
and subsequent utility evaluations; the earlier 300-item primary table retains aggregate
counts rather than per-item outputs. Parsing, scoring, and figure generation are scripted,
with figure hashes and generation procedures recorded in the repository. Checkpoint
availability and release scope require a separate artifact audit before submission.

**Transition.** With the measurement protocol fixed — including its bundled-configuration
caveat and its per-figure denominators — we now report what the measurements show, in RQ
order, without causal attribution.
