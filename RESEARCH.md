# 📚 GreenByte Research References

This document records the research basis behind GreenByte's AI carbon measurement, Cloud-vs-Local comparison and sustainability-verification methodology.

> **Important:** The research below supports GreenByte's **methodological concepts**. It does not directly validate GreenByte's current prototype Cloud-energy coefficients or testing carbon-intensity values.

---

## Research Papers

| Paper Name | Summary Content That Is Useful for GreenByte | Paper Link |
|---|---|---|
| **SentencePiece: A Simple and Language Independent Subword Tokenizer and Detokenizer for Neural Text Processing — Taku Kudo & John Richardson (2018)** | Supports GreenByte's token methodology. Modern NLP models represent text using tokenizer-specific subword units rather than simply counting visible words. This supports GreenByte's decision to use runtime token telemetry instead of assuming that a sentence such as **“How are you?”** contains three AI tokens. It also helps explain why Qwen3 and DeepSeek can report different input-token counts for the same visible prompt. | https://arxiv.org/abs/1808.06226 |
| **TokenPowerBench: Benchmarking the Power Consumption of Large Language Model Inference — Niu et al. (2026)** | Highly relevant to GreenByte's Local AI energy methodology. TokenPowerBench studies power consumption during LLM inference and considers GPU-, node- and system-level power as well as inference stages such as prompt processing and token generation. It supports GreenByte's use of power telemetry, runtime, Joules and energy-per-token analysis rather than assuming a universal carbon value for every token. | https://ojs.aaai.org/index.php/AAAI/article/view/40535 |
| **Towards the Systematic Reporting of the Energy and Carbon Footprints of Machine Learning — Henderson et al. (2020)** | Supports GreenByte's principle of transparent environmental reporting. The work argues that machine-learning experiments should systematically report energy and carbon impacts. This supports GreenByte's separation of workload, hardware energy, electricity carbon intensity and final CO₂e rather than hiding these assumptions inside one unexplained carbon-per-token number. | https://arxiv.org/abs/2002.05651 |
| **Carbon Emissions and Large Neural Network Training — Patterson et al. (2021)** | Shows that AI carbon impact depends on factors such as model choice, processor efficiency, data-centre infrastructure and electricity source/geography. This directly supports GreenByte's decision to keep **energy**, **PUE** and **carbon intensity** as separate parameters. The same token workload cannot be assumed to produce the same CO₂e in every deployment environment. | https://arxiv.org/abs/2104.10350 |
| **Generative AI Inference: Cloud versus Edge — Li, Islam & Ren (2025)** | Directly supports GreenByte's central Cloud-vs-Local idea. The study compares generative-AI inference executed in cloud environments against edge deployments and evaluates the resulting environmental impact. It reports significant energy/environmental advantages for certain edge configurations, supporting GreenByte's research question of whether suitable AI workloads can be shifted from Cloud AI to more efficient Local/Edge AI. | https://escholarship.org/uc/item/2kc978dg |
| **Making AI Less “Thirsty”: Uncovering and Addressing the Secret Water Footprint of AI Models — Li et al. (2023/2025)** | Supports a future extension of GreenByte beyond carbon. The research develops a methodology for evaluating AI water consumption and highlights geographic and temporal differences in water footprint. It is useful for a future GreenByte water-impact metric involving data-centre cooling and electricity-generation water use. Water is currently kept separate from ACU. | https://arxiv.org/abs/2304.03271 |

---

## Technical & Industry References

The following are not academic research papers, but they are technical sources used by the GreenByte implementation.

| Technical Source | Summary Content That Is Useful for GreenByte | Link |
|---|---|---|
| **Ollama API Usage Documentation** | Provides the actual runtime telemetry fields used by GreenByte. `prompt_eval_count` is used for input-token telemetry and `eval_count` for output-token telemetry. Ollama also exposes timing fields such as `total_duration`, `prompt_eval_duration` and `eval_duration`. These values are read from the runtime instead of manually estimated by GreenByte. | https://docs.ollama.com/api/usage |
| **NVIDIA System Management Interface (nvidia-smi)** | NVIDIA's official GPU monitoring utility. GreenByte uses NVIDIA power-draw telemetry during Local AI testing to sample GPU power in watts while Qwen3 inference is running. Power samples are integrated over time to estimate incremental GPU energy in Joules. | https://developer.nvidia.com/system-management-interface |
| **The Green Grid — Power Usage Effectiveness (PUE)** | Provides the industry concept used to represent data-centre overhead. PUE relates total data-centre energy to ICT equipment energy. GreenByte therefore keeps PUE as an explicit parameter when converting Cloud compute energy into estimated Cloud CO₂e. | https://www.thegreengrid.org/node/372 |

---

# 🔎 How the Research Maps to GreenByte

## 1. Token Measurement

GreenByte does **not** use:

```text
Number of visible words
=
Number of AI tokens
```

For example:

```text
Prompt:
"How are you?"
```

Current runtime telemetry:

```text
Qwen3 1.7B Local
Input Tokens = 20

DeepSeek V4 Flash Cloud
Input Tokens = 8
```

This does not mean that one runtime is necessarily incorrect.

The models can use different:

```text
Tokenizers
Vocabulary
Chat templates
Special tokens
Prompt formatting
```

The SentencePiece research supports the broader principle that machine-learning tokenisation operates using subword units rather than simple human word counting.

For GreenByte, the authoritative test values are the values reported by the runtime.

---

## 2. Actual Token Telemetry Used by GreenByte

For Ollama:

```text
prompt_eval_count
→
Input Tokens
```

```text
eval_count
→
Output Tokens
```

GreenByte also records timing information where available:

```text
total_duration

prompt_eval_duration

eval_duration
```

Therefore GreenByte's current Local and Cloud token counts are **runtime telemetry**, not manual estimates.

---

## 3. Maximum Output Tokens

GreenByte's current testing configuration includes:

```text
num_predict = 50
```

This means:

> The model may generate **up to 50 output tokens**.

It does not mean:

> The model must generate exactly 50 tokens.

Current example:

```text
Local Qwen3
Maximum = 50
Actual Output = 12
```

Qwen completed its response naturally.

Cloud example:

```text
DeepSeek V4 Flash
Maximum = 50
Actual Output = 50
```

The Cloud response reached the configured limit.

Therefore:

```text
Maximum Output
=
Configured by GreenByte testing
```

while:

```text
Actual Output Tokens
=
Reported by the AI runtime
```

---

# ⚡ Energy Measurement Research Basis

GreenByte separates:

```text
TOKENS
from
ENERGY
```

Tokens describe the computational workload.

Energy describes the physical electricity used to execute that workload.

The relationship is:

```text
Energy
=
Power
×
Time
```

or for changing power draw:

```text
Energy
≈
∫ P(t) dt
```

TokenPowerBench and systematic ML-energy reporting research support measuring hardware power and energy during AI inference.

---

## Local AI Measurement

The current PoC uses:

```text
NVIDIA GeForce RTX 4050 Laptop GPU
+
Qwen3 1.7B
+
Ollama Local
```

GreenByte samples GPU power using NVIDIA telemetry.

Example:

```text
Idle GPU Power        = 15.663 W
Average GPU Power     = 22.560 W

Gross GPU Energy      = 2.407 J
Baseline Energy       = 1.671 J

Net Inference Energy  = 0.736 J
```

Separate five-run benchmark:

```text
Average Net GPU Energy
=
1.156 J
```

GreenByte labels this as:

> **GPU telemetry-derived incremental energy**

It does not claim that this equals the total electricity consumed by the entire laptop.

---

# ☁️ Cloud Energy Research Basis

GreenByte currently obtains actual Cloud AI:

```text
Input Tokens
Output Tokens
Runtime
```

from Ollama Cloud.

However, the Cloud provider does not expose actual data-centre Joules for the request.

Therefore GreenByte currently uses a **prototype Cloud energy estimator**.

Current test:

```text
Ecloud
=
α
+
βin × Nin
+
βout × Nout
```

with:

```text
α = 250 J

βin = 2 J/input token

βout = 7 J/output token
```

Current Cloud workload:

```text
Input = 8
Output = 50
```

Therefore:

```text
Ecloud
=
250
+
(2 × 8)
+
(7 × 50)

=
616 J
```

The research papers support the importance of measuring and modelling AI energy.

They do **not** validate these specific GreenByte testing coefficients.

Therefore:

```text
616 J
=
Prototype testing estimate
```

and not:

```text
616 J
=
Measured Ollama Cloud energy
```

---

# 🌱 Carbon Accounting Research Basis

GreenByte keeps energy and carbon intensity separate.

Conceptually:

```text
Energy
×
Electricity Carbon Intensity
=
CO₂e
```

Since:

```text
1 kWh
=
3,600,000 J
```

Local carbon is calculated as:

```text
Local CO₂e
=
Local Energy
÷
3,600,000
×
Local Carbon Intensity
```

Cloud carbon additionally includes data-centre overhead:

```text
Cloud CO₂e
=
Cloud Energy
×
PUE
÷
3,600,000
×
Cloud Carbon Intensity
```

This design follows the research principle that AI carbon impact depends on the energy consumed and on the electricity/infrastructure conditions under which computation occurs.

---

# 🏢 Why GreenByte Uses PUE

Cloud inference occurs inside data-centre infrastructure.

The GPU or server is not the only electricity consumer.

Additional electricity may be associated with:

```text
Cooling
UPS
Power conversion
Networking
Supporting infrastructure
```

GreenByte therefore includes:

```text
PUE
=
Power Usage Effectiveness
```

as a separate Cloud parameter.

This avoids treating Cloud IT-equipment energy as if it were automatically equal to total facility energy.

---

# ☁️ vs 💻 Cloud-vs-Edge Research Question

The central GreenByte research question is:

> **Can suitable AI inference be executed locally with a lower environmental footprint than an equivalent Cloud AI service?**

The current PoC tests:

```text
Cloud
=
Ollama Cloud
DeepSeek V4 Flash
```

against:

```text
Local
=
Ollama Local
Qwen3 1.7B
RTX 4050 Laptop GPU
```

The laptop is currently only a test environment.

GreenByte's intended Local Edge architecture is:

```text
Solar Energy
      ↓
Repurposed Old Smartphone
      ↓
Local AI
      ↓
Measured Device Energy
```

The Cloud-vs-Edge research provides direct support for investigating this type of deployment trade-off.

---

# 💧 Future Water Research

GreenByte currently focuses on carbon.

A future version may separately measure water impact associated with:

```text
Data-centre cooling

Electricity generation

Geographic water availability

Time-dependent water intensity
```

The work on AI water footprint provides a research basis for this future expansion.

Water is currently **not included in ACU**.

---

# ⚠️ What the Research Supports

The external research supports GreenByte's methodology concepts:

```text
✓ Model/tokenizer-dependent tokenisation

✓ Runtime token telemetry

✓ Measuring AI inference power

✓ Converting power and runtime into energy

✓ Separating energy from carbon intensity

✓ Transparent energy/carbon reporting

✓ Cloud-vs-Edge environmental comparison

✓ Considering data-centre overhead

✓ Future AI water accounting
```

---

# ⚠️ What the Research Does NOT Validate

The current research references do not directly prove that the following prototype values are correct for the real production environment:

```text
✕ Cloud Base Energy = 250 J

✕ Cloud Input Energy = 2 J/token

✕ Cloud Output Energy = 7 J/token

✕ Actual Ollama Cloud Energy = 616 J

✕ Local Carbon Intensity = 200 g CO₂e/kWh

✕ Cloud Carbon Intensity = 400 g CO₂e/kWh

✕ Actual Ollama Cloud PUE = 1.10

✕ Verification Overhead = 0 g
```

These are currently testing/configured assumptions.

They should eventually be replaced with:

```text
Measured values

Provider-disclosed infrastructure data

Location-specific official electricity data

or

Research-calibrated benchmark parameters
```

---

# 🧭 Research-to-System Mapping

| GreenByte Component | Supporting Research / Source |
|---|---|
| Token telemetry | SentencePiece + Ollama API |
| Different token counts between models | SentencePiece |
| GPU power measurement | TokenPowerBench + NVIDIA telemetry |
| Joules / inference energy | TokenPowerBench |
| Transparent energy reporting | Henderson et al. |
| Energy + carbon-intensity separation | Henderson et al. + Patterson et al. |
| Cloud infrastructure / geography | Patterson et al. |
| Cloud-vs-Local comparison | Li, Islam & Ren |
| PUE | The Green Grid |
| Future water accounting | Making AI Less “Thirsty” |

---

# 🌱 GreenByte Research Principle

> **Tokens describe the workload.**  
> **Joules describe the energy.**  
> **Carbon intensity converts energy into CO₂e.**  
> **Cloud minus Local becomes avoided carbon.**  
> **GreenByte then makes that result transparent and verifiable.**

---

## Related GreenByte Documentation

### 📖 [METHODOLOGY.md](METHODOLOGY.md)

Detailed GreenByte:

```text
Parameters
Formulas
Token methodology
Local energy measurement
Cloud energy estimation
Carbon calculation
ACU
Hashing
Ledger
Certificates
Proof
Verification
```

### 🌱 [README.md](README.md)

Project overview, current prototype, architecture and implementation status.
