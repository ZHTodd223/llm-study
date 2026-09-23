# Working Title and Abstract

<!-- C5 draft, 2026-09-23. English conference-paper working title and English-only
abstract follow the author's confirmed manuscript language. Venue/track remains open;
abstract length, keywords, and final style must be adapted after venue selection.
Title alternatives considered: "Field-Level Tool-Call Recovery in Quantized LLM Deployment";
"Measuring Structured Function Calls Across Quantized Agent Configurations".
The selected title names the observed object and unit of comparison without assigning
causality to the quantization format. No author, release, funding, or COI status is implied.
Numeric sources: PAPER_MATERIALS.md V1.3 (240 target-defined items, n=3 sample SD);
V1.5.1 (own 300-item normal set); V1.5.2 (fixed BFCL 150-item subset).
Prior C3/C4 chapters and C6 consistency issues remain as recorded in WRITING_TODO.md.
-->

## Working title

Structured Tool-Call Recovery Across Quantized LLM Deployment Configurations

## Abstract

Quantization can alter the behavior of a language-model agent after its checkpoint is
deployed. For structured tool calls, a recovered tool name or target address need not
include the arguments required for a complete call. We measure this distinction across
full-precision, HQQ 4-bit, and GGUF/Q4_K_M deployment configurations for Qwen2.5-7B-Instruct
and Llama-3.1-8B-Instruct checkpoints with an injected tool-call payload. The comparison
separates tool name, address, message fields, and complete-payload recovery, and examines
weight neighborhoods, three Llama training seeds, and normal function-calling ability.
On 240 target-defined items, mean complete-payload recovery across the three Llama runs
was 7.36% (sample SD 11.00) under HQQ and 89.03% (sample SD 10.43) under GGUF/Q4_K_M.
HQQ's complete recovery remained low in those runs, although its field-level failure
pattern changed with the seed. At the inspected injection layer, both paths retained
outlier positions but differed in the fraction of neighboring weights near zero. This
weight observation is consistent with an interpretation of the output difference; the
deployment comparison also changes implementation and inference backend. On a separate
300-item normal-task set, the modified full-precision model averaged 7.89% complete-call
accuracy compared with 63.67% for the clean baseline. A fixed 150-item BFCL simple subset
reversed the attacked HQQ/GGUF utility ordering seen on the 300-item set, limiting any
general recovery–utility tradeoff claim. The findings motivate assessing the deployed artifact
with field-level and complete-call metrics alongside benign utility. All outcomes concern
locally parsed generated calls; external tools were not executed.

## Keywords

quantization-conditioned behavior; function calling; payload integrity; agent security;
benign utility
