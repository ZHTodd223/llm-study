# 7. Conclusion

<!-- C5 draft, 2026-09-23. Target approximately 200 reader-visible English words.
Evidence: Results §§4.1–4.4; PAPER_MATERIALS.md V1.1/V1.2/V1.3/V1.5.
This section adds no result. Inferences are bounded to tested deployment configurations.
-->

Structured tool-call recovery cannot be summarized by a single target hit. In the tested
HQQ and GGUF/Q4_K_M deployment configurations, tool names and individual arguments can
reappear without a complete payload, and the degree of completeness differs between
the two paths. The Llama weight comparison shows different rates of near-zero neighboring
weights at the inspected injection layer, consistent with one explanation of the output
contrast. Because quantization procedure, representation, and runtime change together,
that observation does not isolate its cause.

Across three Llama training runs, GGUF/Q4_K_M retained higher complete recovery on the
target-defined subset, while HQQ's particular failure shape varied. Normal tool-calling
ability also suffered: the modified full-precision checkpoint was already substantially
impaired, and the relative performance of the two quantized paths depended on the task
set. Recovery and capability cost should therefore be reported together without treating
their association as a universal tradeoff.

For deployment evaluation, the practical unit is the generated, parsed call from the
artifact users would actually serve. Field matches, complete calls, and normal-task
accuracy answer different questions; none establishes real tool execution. Further work
should isolate quantization and backend choices, add model families, seeds, and held-out
templates, and test downstream tool execution in a sandbox.
