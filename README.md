# 🌱 GreenByte Chain

> **Every Prompt Has a Carbon Cost.**  
> **Measure it. Compare it. Verify what local AI saves.**

GreenByte is a proof-of-concept ecosystem for **prompt-level AI carbon measurement and verification**.

Instead of asking users to manually enter token counts or estimate emissions themselves, GreenByte connects directly to an AI runtime in the background. It captures real inference telemetry, measures the energy consumed by a local edge device, compares that footprint against an equivalent cloud AI baseline, calculates the resulting avoided carbon emissions, and creates a tamper-evident sustainability record.

The project combines **AI, edge computing, renewable energy, carbon transparency, and blockchain-inspired verification** to make the environmental impact of AI inference more visible and auditable.

---

## 🌍 The Problem

Artificial intelligence is increasingly used in everyday applications, but users normally have little visibility into the environmental impact of each AI request.

A single prompt may involve:

- AI model inference
- GPU or edge-device computation
- electricity consumption
- data-centre cooling and infrastructure
- regional electricity carbon intensity

Most AI interfaces show users the generated answer, but not the environmental cost behind producing it.

GreenByte aims to make that impact measurable.

---

## 💡 Our Solution

GreenByte compares two ways of processing the same AI workload:

### ☁️ Cloud AI

The prompt is processed through cloud infrastructure such as a GPU server or data centre.

GreenByte estimates:

- cloud inference energy
- Power Usage Effectiveness (PUE)
- electricity grid carbon intensity
- resulting cloud CO₂e footprint

### 📱 Local Edge AI

The same or comparable AI workload is processed locally using a repurposed smartphone or edge device.

Our proof-of-concept focuses on a:

> **Solar-powered repurposed smartphone running local AI inference.**

GreenByte records:

- input tokens
- output tokens
- AI model
- edge device
- measured energy consumption
- energy source
- local CO₂e footprint

The difference between cloud and local carbon emissions becomes the estimated **avoided carbon**.

---

# ⚙️ How GreenByte Works

```text
User Prompt
    ↓
Friend's Local AI
    ↓
AI Runtime Telemetry
    │
    ├── Input Tokens
    ├── Output Tokens
    ├── Model
    ├── Device
    └── Measured Energy (J)
    ↓
GreenByte Backend
    ↓
GreenByte Carbon Engine
    │
    ├── Cloud Baseline
    └── Local Edge Footprint
    ↓
Cloud vs Local Comparison
    ↓
Net Avoided CO₂e
    ↓
ACU
    ↓
Evidence Hash
    ↓
GreenByte Verification Ledger
    ↓
Impact Certificate
    ↓
Live GreenByte Dashboard
