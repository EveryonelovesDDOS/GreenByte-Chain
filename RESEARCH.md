# 📚 GreenByte Research References

This document records the research basis behind GreenByte's **AI workload measurement, Cloud-vs-Local energy comparison, carbon estimation, and verifiable sustainability records**.

> **Core principle:** GreenByte does **not** assume that one token always equals a fixed amount of energy or carbon.  
> Tokens describe workload. Energy depends on the model, hardware, software stack, runtime settings, and deployment infrastructure. Carbon is then calculated from energy and the relevant electricity carbon intensity.

> **Important:** The papers and technical sources below support GreenByte's methodology and provide external benchmark evidence. They do **not** directly validate GreenByte's current prototype coefficients such as `250 J + 2 J/input token + 7 J/output token`. Those values remain testing-only assumptions until replaced by measured or calibrated data.

---

# 1. Research Papers Most Relevant to GreenByte

| Paper Name | Summary Content That Is Useful for GreenByte | Paper Link |
|---|---|---|
| **SentencePiece: A Simple and Language Independent Subword Tokenizer and Detokenizer for Neural Text Processing — Kudo & Richardson (2018)** | Supports GreenByte's token methodology. AI systems tokenize text into model-specific subword units rather than simply counting visible words. This helps explain why the same visible prompt can produce different token counts on Qwen, DeepSeek, GPT, Claude or Gemini. | https://arxiv.org/abs/1808.06226 |
| **Towards the Systematic Reporting of the Energy and Carbon Footprints of Machine Learning — Henderson et al. (2020)** | Supports transparent reporting of machine-learning energy and carbon. GreenByte follows this principle by separating workload, energy, carbon intensity and resulting CO₂e instead of hiding everything inside a single unexplained “carbon per token” constant. | https://arxiv.org/abs/2002.05651 |
| **Carbon Emissions and Large Neural Network Training — Patterson et al. (2021)** | Demonstrates that AI carbon impact depends strongly on model, processor efficiency, data-centre infrastructure and electricity source. Although focused mainly on training, the environmental-accounting principle supports GreenByte's separation of compute energy from regional carbon intensity. | https://arxiv.org/abs/2104.10350 |
| **Making AI Less “Thirsty”: Uncovering and Addressing the Secret Water Footprint of AI Models — Li et al.** | Provides a research basis for a future GreenByte water-footprint metric. It highlights that AI environmental impact can vary geographically and temporally and that water should be treated separately from carbon. | https://arxiv.org/abs/2304.03271 |
| **How Hungry is AI? Benchmarking Energy, Water, and Carbon Footprint of LLM Inference — Jegham et al. (2025)** | One of the most useful external benchmarks for GreenByte. It evaluates 30 LLMs using standardized short, medium and long token workloads and estimates per-query energy, water and carbon using infrastructure-aware parameters such as hardware, PUE and carbon intensity. It includes GPT, Claude, DeepSeek and Llama models. | https://arxiv.org/abs/2505.09598 |
| **A Case Study of Environmental Footprints for Generative AI Inference: Cloud versus Edge — Li, Islam & Ren (2025)** | Directly supports GreenByte's central Cloud-vs-Local/Edge concept. The study runs the same generative models and identical inputs on cloud GPUs and a Samsung Galaxy S24. It reports over 90% energy savings and more than 80% carbon/water reductions for several edge deployments. | https://doi.org/10.1145/3764944.3764950 |
| **Measuring the Environmental Impact of Delivering AI at Google Scale — Elsworth et al. (2025)** | Provides a rare full-stack production measurement of AI inference. Google reports that the median Gemini Apps text prompt consumed 0.24 Wh, emitted 0.03 gCO₂e and used 0.26 mL water under its comprehensive methodology. It also reports a 33× reduction in energy and 44× reduction in carbon per median prompt over one year. | https://arxiv.org/abs/2508.15734 |
| **TokenPowerBench: Benchmarking the Power Consumption of LLM Inference — Niu et al. (AAAI 2026)** | Directly supports GreenByte's use of hardware telemetry. TokenPowerBench measures GPU-, node- and system-level power, aligns measurements to prefill and decode phases, and evaluates Joules per token. It shows that batch size, context length, parallelism and quantization can materially change inference energy. | https://doi.org/10.1609/aaai.v40i38.40535 |

---

# 2. Official Token-Telemetry Sources

GreenByte should obtain token counts from the **exact model/runtime actually used**.

There is no universal published number such as:

```text
"How are you?" = 3 AI tokens
```

that is valid across GPT, Claude, Gemini, DeepSeek and Ollama models.

| Provider / Runtime | Exact Token Information Available | Official Source |
|---|---|---|
| **OpenAI GPT API** | Responses include usage information such as `input_tokens`, `output_tokens` and `total_tokens`. Token count depends on the model/encoding and request structure. | https://platform.openai.com/docs/api-reference/responses |
| **Claude API** | Anthropic provides `messages.count_tokens()` / `POST /v1/messages/count_tokens`. Anthropic explicitly notes that token counts are model-specific and can include automatically added system tokens. | https://platform.claude.com/docs/en/build-with-claude/token-counting |
| **Gemini API** | Google provides `models.countTokens`. Generation responses include `usageMetadata.promptTokenCount`, `candidatesTokenCount`, `thoughtsTokenCount` and `totalTokenCount`. | https://ai.google.dev/api/tokens |
| **DeepSeek API** | `usage.prompt_tokens`, `usage.completion_tokens` and `usage.total_tokens` are returned for completions. | https://api-docs.deepseek.com/api/create-chat-completion/ |
| **Ollama Runtime** | `prompt_eval_count` = processed input tokens; `eval_count` = generated output tokens. Timing fields are also exposed. | https://docs.ollama.com/api/usage |

> **Important:** Ollama is a runtime/platform, not one tokenizer.  
> Token count depends on the model running inside Ollama, for example Qwen, Llama, Gemma or DeepSeek.

---

# 3. What Does “How are you?” Cost in Tokens?

## GreenByte's Current Measured Test

GreenByte has currently measured the following **actual runtime telemetry** for the same visible prompt:

```text
Prompt:
"How are you?"
```

| Test Path | Runtime / Model | Input Tokens | Output Tokens | Total Tokens |
|---|---|---:|---:|---:|
| **Local AI** | Ollama Local — Qwen3 1.7B | 20 | 12 | 32 |
| **Cloud AI** | Ollama Cloud — DeepSeek V4 Flash | 8 | 50 | 58 |

Shared test settings:

```text
temperature = 0
think = false
maximum output tokens = 50
```

The maximum output setting means:

```text
output tokens <= 50
```

It does **not** mean the model must always generate exactly 50 tokens.

Qwen stopped naturally at 12 output tokens, while the DeepSeek Cloud test reached the configured 50-token maximum.

---

## GPT, Claude and Gemini

At present, GreenByte has **not yet run the same controlled `"How are you?"` experiment through the GPT, Claude and Gemini APIs**.

Therefore this document intentionally does **not invent token numbers** for those platforms.

The correct experiment is:

```text
Same visible prompt
+
same response constraint
+
exact named model
+
provider's official usage telemetry
```

Then record:

```text
Input Tokens
Output Tokens
Total Tokens
Runtime
```

This should be repeated whenever the model/version changes because tokenization and hidden request formatting can change.

---

# 4. Why Token Counts Differ Between AI Providers

Token counts can differ because of:

```text
Different tokenizer vocabularies
Different subword segmentation
Different chat templates
Different system messages
Different special tokens
Different reasoning/thinking tokens
Different tool-use wrappers
Different model versions
```

Therefore:

```text
Visible words ≠ AI tokens
```

and:

```text
Same visible prompt ≠ same token workload across models
```

GreenByte treats the model/runtime's own usage telemetry as the authoritative measurement.

---

# 5. Published Energy per LLM Query

The paper **How Hungry is AI?** benchmarks 30 LLMs under standardized workloads.

Its short-query benchmark is:

```text
100 input tokens
+
300 output tokens
=
400 total tokens
```

Selected results:

| Model / Deployment | Energy per 100-input + 300-output Query |
|---|---:|
| **GPT-4o (Mar 2025)** | **0.423 Wh** |
| **Claude 3.7 Sonnet** | **0.950 Wh** |
| **DeepSeek V3 — Microsoft Azure** | **0.742 Wh** |
| **DeepSeek V3 — DeepSeek infrastructure** | **2.777 Wh** |
| **Llama 3.2 1B** | **0.109 Wh** |
| **Llama 3.1 8B** | **0.052 Wh** |

Source:

https://arxiv.org/abs/2505.09598

These values are particularly useful to GreenByte because they demonstrate that:

> **The same standardized token workload can consume very different amounts of energy depending on the model and infrastructure.**

For example:

```text
DeepSeek V3 on DeepSeek infrastructure:
2.777 Wh

DeepSeek V3 on Azure:
0.742 Wh
```

Approximate energy reduction:

```text
(2.777 - 0.742) / 2.777 × 100

≈ 73%
```

This is strong evidence that GreenByte should not calculate carbon from token count alone.

---

# 6. Workload-Normalized Energy

For comparison only, GreenByte can divide the short-query benchmark energy by the standardized 400-token workload.

This produces an **average workload-normalized value**, not the true marginal energy of one extra token.

| Model / Deployment | Wh / 400-token Query | Approx. J per Total Token |
|---|---:|---:|
| GPT-4o | 0.423 Wh | 3.807 J/token |
| Claude 3.7 Sonnet | 0.950 Wh | 8.550 J/token |
| DeepSeek V3 — Azure | 0.742 Wh | 6.678 J/token |
| DeepSeek V3 — DeepSeek host | 2.777 Wh | 24.993 J/token |
| Llama 3.2 1B | 0.109 Wh | 0.981 J/token |
| Llama 3.1 8B | 0.052 Wh | 0.468 J/token |

Derived by GreenByte as:

```text
Average J/token
=
Query Energy (Wh)
× 3600
÷ 400 tokens
```

### Important Limitation

These values must **not** be treated as:

```text
1 token always consumes X joules
```

because real inference energy includes:

```text
Fixed request overhead
Prefill/input processing
Autoregressive decode
KV-cache behaviour
Batching
Model size
Quantization
GPU/NPU utilization
Data-centre overhead
```

TokenPowerBench specifically shows that prefill, decode and deployment configuration affect Joules per token.

---

# 7. Does Reducing Tokens Reduce Carbon?

## Short Answer

**Usually, reducing unnecessary AI workload can reduce energy and therefore carbon, but there is no universal carbon-per-token constant.**

The scientifically safer relationship is:

```text
Fewer / more efficient AI workload
        ↓
Lower measured or modelled energy
        ↓
Lower electricity consumption
        ↓
Lower CO₂e
```

not:

```text
1 token
=
fixed grams of CO₂
```

---

# 8. GreenByte Formula for Token-Optimization Savings

When the **same model, hardware and deployment** are being compared, a measured energy-per-token value can help estimate the benefit of reducing generation.

For output/decode tokens:

```text
ΔEdecode
≈
Measured Decode J/token
×
(Output Tokens Before - Output Tokens After)
```

Then:

```text
Carbon Avoided
=
ΔEdecode
÷ 3,600,000
×
Carbon Intensity
```

For cloud deployment where the measured energy is IT-equipment energy:

```text
Carbon Avoided
=
ΔEdecode
× PUE
÷ 3,600,000
×
Carbon Intensity
```

However, GreenByte should ideally measure the **whole request before and after optimization**, because prefill and fixed request overhead also matter.

---

# 9. Illustrative Example: What Could 100 Fewer Tokens Save?

This section is only an **illustrative linearization** of the 400-token benchmark from *How Hungry is AI?*.

It is **not a production GreenByte coefficient**.

Suppose a 400-token workload were reduced by 100 total tokens under the same model and infrastructure, and energy scaled approximately linearly.

For GPT-4o:

```text
Original benchmark energy:
0.423 Wh for 400 tokens

Approximate 100-token fraction:
100 / 400
=
25%
```

Illustrative energy avoided:

```text
0.423 Wh × 25%
=
0.10575 Wh
```

If electricity carbon intensity were:

```text
400 gCO₂e/kWh
```

then:

```text
Carbon avoided
=
0.10575 Wh
÷ 1000
× 400 gCO₂e/kWh

=
0.0423 gCO₂e
```

Again:

> **This is only an illustrative estimate.**

GreenByte should use measured or phase-aware energy wherever possible rather than assuming perfect linear scaling.

---

# 10. Strongest Published Evidence for GreenByte: Cloud vs Smartphone Edge

The 2025 ACM paper:

**A Case Study of Environmental Footprints for Generative AI Inference: Cloud versus Edge**

compares identical model inputs on cloud GPUs and a Samsung Galaxy S24.

For **Llama-2-7B**, the reported average response length was approximately:

```text
373 tokens
```

Energy results:

| Platform | Energy / Query |
|---|---:|
| NVIDIA A100 Cloud GPU | **3803.71 J** |
| Samsung Galaxy S24 NPU | **262.26 J** |

Energy avoided:

```text
3803.71 J
-
262.26 J
=
3541.45 J/query
```

Percentage energy saving:

```text
3541.45
÷
3803.71
× 100

≈ 93%
```

Source:

https://doi.org/10.1145/3764944.3764950

This result is highly relevant to GreenByte because the long-term GreenByte architecture also proposes shifting suitable AI workloads from Cloud AI to a local smartphone edge device.

---

# 11. Published Carbon Saving: Cloud A100 vs Samsung S24

The same study estimates lifecycle carbon per **1,000 Llama-2-7B queries**:

| Platform | Carbon Footprint / 1000 Queries |
|---|---:|
| NVIDIA A100 | **484.29 gCO₂** |
| Samsung Galaxy S24 | **75.45 gCO₂** |

Carbon avoided:

```text
484.29
-
75.45
=
408.84 gCO₂ / 1000 queries
```

Equivalent carbon avoided per query:

```text
408.84
÷
1000
=
0.40884 gCO₂/query
```

Percentage reduction:

```text
408.84
÷
484.29
× 100

≈ 84%
```

Therefore, under the study's assumptions:

```text
Energy saving:
≈ 93%

Carbon saving:
≈ 84%

Carbon avoided:
≈ 0.409 gCO₂/query
```

This is one of the strongest published research precedents for GreenByte's long-term concept:

```text
Cloud AI
vs
Local AI on a smartphone
```

---

# 12. Gemini Production Measurement

Google published a full-stack study of Gemini Apps production inference.

For the **median Gemini Apps text prompt**, Google reports:

```text
Energy:
0.24 Wh

Carbon:
0.03 gCO₂e

Water:
0.26 mL
```

The study includes:

```text
AI accelerator power
Host CPU and memory
Idle provisioned capacity
Data-centre overhead
```

Google also reports that over a 12-month period:

```text
Energy per median prompt:
↓ 33×

Carbon footprint per median prompt:
↓ 44×
```

Source:

https://arxiv.org/abs/2508.15734

### Important Limitation

This is a **median Gemini Apps text prompt**, not specifically:

```text
"How are you?"
```

and the study does not provide a universal token count for that median prompt.

Therefore GreenByte should not claim:

```text
"How are you?" on Gemini = 0.24 Wh
```

Instead:

> Google provides 0.24 Wh as a production-level median prompt reference point.

---

# 13. ChatGPT / OpenAI Public Energy Reference

Sam Altman publicly stated that an **average ChatGPT query** uses approximately:

```text
0.34 Wh
```

OpenAI Academy also discusses independent estimates around:

```text
~0.3 Wh for a typical GPT-4o query
```

Sources:

https://blog.samaltman.com/

https://academy.openai.com/

### Important Limitation

This is an average or typical query reference.

It does not mean:

```text
Every GPT query
=
0.34 Wh
```

Energy can vary substantially depending on:

```text
Model
Reasoning mode
Input length
Output length
Batching
Hardware
Infrastructure
```

---

# 14. Reasoning Mode Can Dramatically Increase Energy

*How Hungry is AI?* also reports large differences between reasoning configurations.

For medium queries, the study estimates approximately:

```text
Minimal reasoning:
2.33 Wh

High reasoning:
17.15 Wh
```

This is more than a seven-fold difference.

For a long high-reasoning query, the estimate reaches approximately:

```text
33.8 Wh
```

This supports an important GreenByte principle:

> **Prompt complexity and reasoning mode can matter as much as raw visible token count.**

---

# 15. Why GreenByte Should NOT Say “We Saved 26 Tokens”

In the current GreenByte test:

```text
Cloud DeepSeek:
58 total tokens

Local Qwen:
32 total tokens
```

It may be tempting to say:

```text
58 - 32
=
26 tokens saved
```

GreenByte should **not** make that claim.

Reasons:

```text
DeepSeek tokenizer ≠ Qwen tokenizer

Cloud output length ≠ Local output length

The models are different sizes and architectures

The infrastructures are different

The response content is not identical

The energy cost per token is not identical
```

The correct GreenByte statement is:

> **GreenByte records the workload reported by each inference path, then measures or estimates the energy required by each path. Carbon savings are calculated from the energy difference, not directly from the raw token-count difference between different models.**

---

# 16. Two Different Types of GreenByte Savings

GreenByte can eventually measure two distinct sustainability effects.

## A. Deployment Saving

Same or functionally equivalent AI task:

```text
Cloud deployment
vs
Local / Edge deployment
```

Formula:

```text
Deployment Carbon Saving
=
Cloud CO₂e
-
Local CO₂e
```

This is GreenByte's current primary concept.

---

## B. Prompt / Generation Efficiency Saving

Same model and deployment:

```text
Unoptimized prompt / verbose output
vs
Optimized prompt / shorter useful output
```

Formula:

```text
Prompt Efficiency Saving
=
CO₂e Before Optimization
-
CO₂e After Optimization
```

This second metric could help GreenByte demonstrate that unnecessary context and unnecessary generation also have an energy cost.

---

# 17. Recommended Benchmark Workloads for GreenByte

Instead of relying only on:

```text
"How are you?"
```

GreenByte should eventually add standardized benchmark workloads.

*How Hungry is AI?* uses:

```text
SHORT
100 input tokens
300 output tokens

MEDIUM
1,000 input tokens
1,000 output tokens

LONG
10,000 input tokens
1,500 output tokens
```

Using these workload classes would make future GreenByte experiments easier to compare with published literature.

GreenByte can still retain:

```text
"How are you?"
```

as the simple live-demo prompt.

---

# 18. Recommended Provider Benchmark Matrix

Future GreenByte testing should record the same controlled workload across several providers.

| Provider | Named Model | Input Tokens | Output Tokens | Runtime | Energy Source | CO₂e |
|---|---|---:|---:|---:|---|---:|
| OpenAI | Exact GPT model | To measure | To measure | To measure | Research/provider estimate | To calculate |
| Anthropic | Exact Claude model | To measure | To measure | To measure | Research/provider estimate | To calculate |
| Google | Exact Gemini model | To measure | To measure | To measure | Provider/reference data | To calculate |
| DeepSeek | Exact DeepSeek model | To measure | To measure | To measure | Research/provider estimate | To calculate |
| Ollama Local | Qwen3 1.7B | **20** | **12** | Measured | NVIDIA telemetry | Calculated |
| Ollama Cloud | DeepSeek V4 Flash | **8** | **50** | Measured | Prototype estimate | Calculated |

For a fairer benchmark:

```text
Same task

Same output constraint

Same temperature

Thinking/reasoning setting explicitly recorded

Multiple runs

Measured token usage

Measured runtime

Energy methodology labelled
```

---

# 19. TokenPowerBench and GreenByte's Local Measurement

TokenPowerBench is especially relevant because its methodology resembles GreenByte's local prototype.

It supports:

```text
GPU power telemetry

Node/system power measurement

Prefill energy

Decode energy

Joules per token

Context-length analysis

Batch-size analysis

Quantization analysis
```

This supports GreenByte's current measurement chain:

```text
nvidia-smi power samples
        ↓
Power over time
        ↓
Joules
        ↓
Carbon intensity
        ↓
Local CO₂e
```

GreenByte should eventually expand beyond GPU-only telemetry to total-device energy where possible.

---

# 20. GreenByte Carbon Calculation Principle

The research supports the following general structure.

## Local

```text
Local CO₂e
=
Local Energy (J)
÷ 3,600,000
×
Local Carbon Intensity (gCO₂e/kWh)
```

## Cloud

If compute energy excludes facility overhead:

```text
Cloud CO₂e
=
Cloud IT Energy (J)
× PUE
÷ 3,600,000
×
Cloud Carbon Intensity
```

If a published energy figure already includes data-centre overhead, GreenByte should **not multiply PUE twice**.

---

# 21. Why Infrastructure Matters as Much as Model Choice

Published benchmarks show large deployment differences.

For DeepSeek V3 under the standardized short query:

```text
DeepSeek-hosted:
2.777 Wh

Azure-hosted:
0.742 Wh
```

For long queries:

```text
DeepSeek-hosted:
13.162 Wh

Azure-hosted:
3.696 Wh
```

The paper attributes large differences to factors such as:

```text
Hardware generation

Data-centre efficiency

Cooling

PUE

Regional electricity mix

Utilization
```

This directly supports GreenByte's decision to record:

```text
Model

Provider

Device / infrastructure

Energy methodology

Carbon intensity

PUE
```

rather than only recording token count.

---

# 22. Research-Backed Answer to “How Much Carbon Can GreenByte Save?”

There is no single universal number.

The saving depends on:

```text
Cloud model

Local model

Task

Output quality requirement

Input length

Output length

Hardware

Quantization

Runtime

Electricity source

PUE

Device embodied carbon boundary
```

However, published evidence provides useful reference examples.

### Smartphone Edge Case Study

For Llama-2-7B:

```text
Energy saving:
≈ 93%

Carbon saving:
≈ 84%

Carbon avoided:
≈ 0.40884 gCO₂ per query
```

under that paper's specific assumptions and lifecycle boundary.

### GreenByte Current Demo

GreenByte's current dashboard result is based on:

```text
Measured local GPU telemetry
+
prototype cloud energy estimator
```

Therefore its current percentage reduction is a:

> **Prototype result**

and should not be presented as a research-validated universal saving percentage.

---

# 23. What Research Supports GreenByte Today

External literature supports the following GreenByte claims:

```text
✓ Token counts are model/tokenizer dependent.

✓ Provider/runtime telemetry should be used for actual token counts.

✓ LLM inference energy varies substantially across models.

✓ Output length and context length affect inference energy.

✓ Prefill and decode have different energy characteristics.

✓ Hardware, batching, quantization and infrastructure affect Joules/token.

✓ Energy must be separated from carbon intensity.

✓ PUE matters for data-centre accounting.

✓ Edge AI can materially reduce inference energy in suitable workloads.

✓ A published smartphone-vs-cloud case study observed ~93% energy and ~84% carbon savings for Llama-2-7B.

✓ Full-stack Gemini production measurement shows prompt-level energy/carbon can be instrumented at scale.

✓ AI inference efficiency can improve substantially through hardware/software/deployment optimization.
```

---

# 24. What Research Does NOT Support Yet

The research does **not** prove that:

```text
✕ "How are you?" has one universal token count.

✕ GPT, Claude, Gemini, DeepSeek and Qwen consume the same energy per token.

✕ Every token has a fixed carbon value.

✕ 26 fewer tokens across two different models means 26 tokens of energy were saved.

✕ GreenByte's current 250 J base cloud value is correct for Ollama Cloud.

✕ GreenByte's current 2 J/input-token coefficient is an Ollama measurement.

✕ GreenByte's current 7 J/output-token coefficient is an Ollama measurement.

✕ GreenByte's current dashboard reduction percentage is a universal real-world reduction.

✕ Local GPU telemetry equals total laptop or phone electricity consumption.
```

---

# 25. GreenByte Research Rule for Claims

GreenByte should label values using four categories:

```text
MEASURED
=
Direct runtime or hardware telemetry

TELEMETRY-DERIVED
=
Calculated from measured telemetry

RESEARCH-ESTIMATED
=
Derived from external benchmark literature

PROTOTYPE ASSUMPTION
=
Testing parameter not yet calibrated
```

Example:

```text
Qwen input/output tokens
→ MEASURED

RTX 4050 incremental GPU Joules
→ TELEMETRY-DERIVED

Published Llama-2 A100 vs S24 results
→ PAPER-REPORTED / RESEARCH-BACKED

Ollama Cloud 616 J in current GreenByte demo
→ PROTOTYPE ASSUMPTION
```

---

# 26. GreenByte Research Principle

> **Tokens describe the workload.**  
> **Joules describe the energy required to execute that workload.**  
> **Infrastructure determines how efficiently that workload is served.**  
> **Carbon intensity converts electricity into CO₂e.**  
> **GreenByte compares Cloud and Local CO₂e and records the avoided impact in a verifiable form.**

---

# 27. Research-to-System Mapping

| GreenByte Component | Supporting Research / Technical Source |
|---|---|
| Model-specific tokenization | SentencePiece |
| OpenAI token telemetry | OpenAI API |
| Claude token telemetry | Anthropic Token Counting API |
| Gemini token telemetry | Gemini `countTokens` / `usageMetadata` |
| DeepSeek token telemetry | DeepSeek API `usage` |
| Ollama token telemetry | Ollama `prompt_eval_count` / `eval_count` |
| GPU power measurement | TokenPowerBench + NVIDIA telemetry |
| Prefill/decode energy | TokenPowerBench |
| Prompt-level LLM energy | How Hungry is AI? |
| GPT / Claude / DeepSeek comparison | How Hungry is AI? |
| Full-stack Gemini production footprint | Measuring AI at Google Scale |
| Cloud-vs-smartphone edge comparison | Li, Islam & Ren |
| Transparent energy/carbon reporting | Henderson et al. |
| Infrastructure and carbon intensity | Patterson et al. + How Hungry is AI? |
| Future water metric | Making AI Less “Thirsty” |

---

# 28. Technical and Industry References

| Source | Use in GreenByte | Link |
|---|---|---|
| **OpenAI API — Responses / Usage** | Read actual GPT input/output token usage. | https://platform.openai.com/docs/api-reference/responses |
| **OpenAI Help — Understanding Tokens** | Explains that tokens are not the same as words and depend on model encoding and language. | https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count |
| **Anthropic — Token Counting** | Count Claude input tokens for the exact model before generation. | https://platform.claude.com/docs/en/build-with-claude/token-counting |
| **Google Gemini — Counting Tokens** | Provides `countTokens` and generation usage metadata. | https://ai.google.dev/api/tokens |
| **DeepSeek Chat Completion API** | Provides `prompt_tokens`, `completion_tokens` and `total_tokens`. | https://api-docs.deepseek.com/api/create-chat-completion/ |
| **Ollama — API Usage** | Provides `prompt_eval_count`, `eval_count` and timing metrics. | https://docs.ollama.com/api/usage |
| **NVIDIA System Management Interface** | Hardware power telemetry used in GreenByte's laptop PoC. | https://developer.nvidia.com/system-management-interface |
| **Google — Measuring the Environmental Impact of AI Inference** | Production Gemini prompt energy/carbon/water results. | https://cloud.google.com/blog/products/infrastructure/measuring-the-environmental-impact-of-ai-inference |
| **Sam Altman — Average ChatGPT Query Energy Reference** | Public reference of approximately 0.34 Wh per average ChatGPT query; not an exact per-model benchmark. | https://blog.samaltman.com/ |

---

# 29. Related GreenByte Documentation

### [METHODOLOGY.md](METHODOLOGY.md)

Contains:

```text
GreenByte architecture

Current parameters

Carbon equations

ACU definition

Hashing

Certificate generation

Proof records

Ledger

Verification

Prototype limitations
```

### [README.md](README.md)

Contains:

```text
Project overview

Current prototype

Architecture

Implementation status

Quick-start information
```

---

# 🌱 GreenByte

## Every Prompt Has a Carbon Cost.

### Measure it. Compare it. Verify what local AI saves.

> **AI Today · A Cleaner Tomorrow**
