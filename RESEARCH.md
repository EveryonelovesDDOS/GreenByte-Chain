# 📚 GreenByte Research References

This document summarises the main academic research used to support the GreenByte methodology.

The papers below support the concepts behind GreenByte, including:

- AI tokenisation
- inference energy measurement
- energy and carbon accounting
- cloud-vs-edge AI comparison
- data-centre energy efficiency
- future water-footprint accounting

> Important: These papers support the **methodological approach** used by GreenByte.  
> They do not directly validate GreenByte's current prototype testing coefficients or demo carbon values.

---

| Paper Name | Useful Summary for GreenByte | Paper Link |
|---|---|---|
| **SentencePiece: A Simple and Language Independent Subword Tokenizer and Detokenizer for Neural Text Processing — Kudo & Richardson (2018)** | Supports GreenByte's token methodology. AI models do not simply count human-readable words. Text is divided into model/tokenizer-specific subword units. This helps explain why the same visible prompt, such as **“How are you?”**, can produce different token counts on Qwen3 and DeepSeek. GreenByte therefore uses runtime token telemetry instead of manually counting words. | https://arxiv.org/abs/1808.06226 |
| **TokenPowerBench: Benchmarking the Power Consumption of Large Language Model Inference — Niu et al. (2026)** | Directly relevant to GreenByte's inference-energy measurement approach. The benchmark studies power consumption during LLM inference and measures GPU-, node-, and system-level energy. It also considers different inference stages such as prompt processing and token generation. This supports GreenByte's use of GPU power telemetry, Joules, runtime, and energy-per-token analysis. | https://ojs.aaai.org/index.php/AAAI/article/view/40535 |
| **Towards the Systematic Reporting of the Energy and Carbon Footprints of Machine Learning — Henderson et al. (2020)** | Supports GreenByte's decision to explicitly report energy consumption and carbon emissions instead of hiding environmental assumptions. The work promotes transparent and systematic reporting of machine-learning energy and carbon impacts. This supports GreenByte's separation of workload, energy, carbon intensity and resulting CO₂e. | https://arxiv.org/abs/2002.05651 |
| **Carbon Emissions and Large Neural Network Training — Patterson et al. (2021)** | Demonstrates that AI energy and carbon emissions depend strongly on the model, processor, data-centre infrastructure and geographic electricity mix. This supports GreenByte's decision **not to use one universal carbon-per-token number**. Instead, GreenByte separately considers energy, PUE and electricity carbon intensity. | https://arxiv.org/abs/2104.10350 |
| **Generative AI Inference: Cloud versus Edge — Li, Islam & Ren (2025)** | Directly supports GreenByte's core Cloud-vs-Local concept. The study compares generative-AI inference performed in cloud environments against edge deployments and reports significant environmental and energy advantages for certain edge configurations. This provides research support for GreenByte's idea of comparing cloud AI against local AI execution. | https://escholarship.org/uc/item/2kc978dg |
| **Making AI Less “Thirsty”: Uncovering and Addressing the Secret Water Footprint of AI Models — Li et al. (2023/2025)** | Useful for GreenByte's future development beyond carbon. The research develops a methodology for understanding AI water consumption and highlights the importance of geographic and temporal variation. GreenByte may later extend its Carbon Engine to include a separate AI water-footprint metric. Water is not currently included in ACU. | https://arxiv.org/abs/2304.03271 |

---

# 🔎 How These Papers Support GreenByte

## 1. Token Measurement

GreenByte does not assume:

```text
1 word = 1 token
