# 🌱 GreenByte

## AI Carbon Measurement, Comparison & Verification

> **Every Prompt Has a Carbon Cost.**  
> **Measure it. Compare it. Verify what local AI saves.**

GreenByte is a proof-of-concept platform for **prompt-level AI carbon measurement, cloud-vs-local comparison, and verifiable sustainability records**.

Instead of asking users to manually enter token counts, energy values, or carbon estimates, GreenByte connects directly to AI runtimes and collects inference telemetry in the background.

For the current prototype, GreenByte compares:

- ☁️ **Ollama Cloud — DeepSeek V4 Flash**
- 💻 **Ollama Local — Qwen3 1.7B**
- ⚡ **NVIDIA GPU telemetry** for local inference energy measurement
- 🌱 A configurable carbon methodology for converting energy into estimated CO₂e
- 🔐 A tamper-evident GreenByte verification ledger
- 📜 Automatically generated impact certificates and proof records

The aim is to make the environmental impact of AI inference more **measurable, transparent, and verifiable**.

---

# 🌍 The Problem

Artificial intelligence is becoming part of everyday computing, but users normally have very little visibility into the environmental impact of each AI request.

A single AI prompt may involve:

- model inference
- GPU or accelerator computation
- electricity consumption
- data-centre infrastructure
- cooling and power overhead
- regional grid carbon intensity

Most AI interfaces show users only the generated answer.

They do not show:

```text
How much computational workload was used?

How much energy was consumed?

How much carbon could the inference represent?

Could a local AI alternative reduce that footprint?

Can the environmental claim be independently verified?
```

GreenByte is designed to explore these questions.

---

# 💡 The GreenByte Solution

GreenByte compares two AI inference paths.

## ☁️ Cloud AI

The prompt is processed by a cloud AI provider.

For the current testing environment:

```text
Provider: Ollama Cloud
Model: DeepSeek V4 Flash
```

GreenByte records:

- actual input token count
- actual output token count
- total token workload
- inference duration
- configured / estimated cloud energy
- Power Usage Effectiveness (PUE)
- cloud electricity carbon intensity
- estimated cloud CO₂e

---

## 💻 Local AI

The same prompt is also processed using a local AI model.

For the current testing environment:

```text
Provider: Ollama Local
Model: Qwen3 1.7B
Hardware: NVIDIA GeForce RTX 4050 Laptop GPU
```

GreenByte records:

- actual input tokens
- actual output tokens
- total token workload
- local inference duration
- GPU power telemetry
- GPU energy
- local electricity carbon intensity
- estimated local CO₂e

The long-term GreenByte concept replaces the laptop with a **repurposed old smartphone running local AI using solar-assisted energy**.

---

# ⚙️ How GreenByte Works

```text
                         USER PROMPT
                              │
                 ┌────────────┴────────────┐
                 │                         │
                 ▼                         ▼
          OLLAMA CLOUD               OLLAMA LOCAL
       DeepSeek V4 Flash             Qwen3 1.7B
                 │                         │
         Cloud telemetry             Local telemetry
                 │                         │
          Input / Output             Input / Output
             Tokens                     Tokens
                 │                         │
                 │                 NVIDIA GPU Power
                 │                     Telemetry
                 │                         │
                 └────────────┬────────────┘
                              ▼
                   GREENBYTE CARBON ENGINE
                              │
                    Cloud vs Local CO₂e
                              │
                              ▼
                    Net Avoided Carbon
                              │
                              ▼
                             ACU
                              │
                              ▼
                       Evidence Hash
                              │
                              ▼
                     GREENBYTE LEDGER
                              │
                 ┌────────────┼────────────┐
                 │            │            │
                 ▼            ▼            ▼
            Certificate      Proof       Verify
```

The GreenByte dashboard is therefore **not a manual calculator**.

The user does not need to manually enter:

```text
tokens
energy
carbon
ACU
certificate ID
block number
```

These values are generated or retrieved automatically by the GreenByte backend.

---

# 🧪 Current Demo

The current GreenByte prototype performs a live **Cloud-vs-Local AI comparison**.

## Shared Test Prompt

```text
How are you?
```

## Shared Testing Configuration

```text
Temperature: 0
Thinking: Disabled
Maximum Output Tokens: 50
```

The maximum output token value is a **limit**, not a requirement.

A model may stop before reaching 50 tokens.

---

## Value 1 — Local AI Test

```text
Provider: Ollama Local
Model: Qwen3 1.7B
Prompt: "How are you?"

Maximum Output Tokens: 50

Actual Input Tokens: 20
Actual Output Tokens: 12
Actual Total Tokens: 32
```

The local model completed its response after 12 output tokens.

It was not forced to generate all 50 tokens.

Local GPU energy is measured using NVIDIA GPU power telemetry.

---

## Value 2 — Cloud AI Test

```text
Provider: Ollama Cloud
Model: DeepSeek V4 Flash
Prompt: "How are you?"

Maximum Output Tokens: 50

Actual Input Tokens: 8
Actual Output Tokens: 50
Actual Total Tokens: 58
```

In this test, the cloud model reached the configured maximum of 50 output tokens.

---

# 🔤 Why Are the Token Counts Different?

The same sentence does **not necessarily produce the same number of tokens across different AI models**.

For example:

```text
Prompt:
"How are you?"

Ollama Local / Qwen3 1.7B
Input Tokens = 20

Ollama Cloud / DeepSeek V4 Flash
Input Tokens = 8
```

This is expected.

Different models may use different:

- tokenizers
- vocabularies
- chat templates
- special tokens
- prompt formatting

GreenByte therefore does **not manually count words**.

Instead, it reads the token telemetry directly from the AI runtime.

For Ollama:

```text
prompt_eval_count = Input Tokens

eval_count = Output Tokens
```

This allows GreenByte to record the actual workload reported by each AI environment.

---

# ⚡ Local GPU Energy Measurement

For the current laptop-based proof-of-concept, GreenByte measures local AI energy using NVIDIA GPU telemetry.

The GPU power is sampled during inference.

Conceptually:

```text
GPU Power (W)
     ×
Time (s)
     =
Energy (J)
```

More formally:

```text
Gross GPU Energy
≈ ∫ Power Draw(t) dt
```

GreenByte also measures an idle GPU baseline.

```text
Baseline Energy
=
Idle GPU Power × Inference Runtime
```

The incremental local AI energy becomes:

```text
Net Inference GPU Energy
=
max(
    0,
    Gross GPU Energy
    -
    Baseline Energy
)
```

Example preliminary telemetry:

```text
Idle GPU Power        : 15.663 W
Average GPU Power     : 22.560 W
Peak GPU Power        : 22.560 W

Gross GPU Energy      : 2.407 J
Baseline Energy       : 1.671 J
Net Inference Energy  : 0.736 J
```

A preliminary multi-run benchmark produced:

```text
Average Net GPU Energy : 1.156 J
Median Net GPU Energy  : 0.736 J
```

These values are currently used for **testing and methodology development**.

> The current GPU telemetry does not represent the entire laptop's wall-plug energy consumption.

A physical wall power meter is preferred for final device-level validation.

---

# ☁️ Cloud Energy Estimation

Ollama Cloud provides useful runtime telemetry including:

```text
Input tokens
Output tokens
Total duration
Prompt evaluation duration
Generation duration
```

However, the cloud API does not currently provide direct data-centre energy consumption in Joules.

Therefore, the current GreenByte prototype uses a **testing-only cloud energy estimator**.

Example testing formula:

```text
Cloud Energy
=
Base Energy
+
(Input Tokens × Input Energy Parameter)
+
(Output Tokens × Output Energy Parameter)
```

Example current test:

```text
Base Energy          = 250 J
Input Energy         = 2 J/token
Output Energy        = 7 J/token

Input Tokens         = 8
Output Tokens        = 50
```

Therefore:

```text
Cloud Energy
=
250
+
(8 × 2)
+
(50 × 7)

=
616 J
```

> The `616 J` value is a prototype testing estimate and is not claimed to be directly measured Ollama Cloud data-centre energy.

Future GreenByte versions should calibrate the cloud model using published inference benchmarks or directly measured cloud infrastructure telemetry where available.

---

# 🌱 Carbon Calculation Methodology

GreenByte converts energy into estimated carbon emissions.

---

## ☁️ Cloud CO₂e

```text
Cloud CO₂e
=
Cloud Energy (J)
× PUE
÷ 3,600,000
× Cloud Grid Carbon Intensity
```

Where:

```text
1 kWh = 3,600,000 Joules
```

PUE represents:

> **Power Usage Effectiveness**

and accounts for additional data-centre energy beyond the direct computing equipment.

Example:

```text
Cloud Energy = 616 J
PUE = 1.10
Grid Carbon Intensity = 400 g CO₂e/kWh
```

Calculation:

```text
616
× 1.10
÷ 3,600,000
× 400

≈ 0.07529 g CO₂e
```

Displayed in the prototype as approximately:

```text
0.0753 g CO₂e
```

---

## 💻 Local CO₂e

```text
Local CO₂e
=
Measured Local Energy (J)
÷ 3,600,000
× Local Electricity Carbon Intensity
```

For the laptop prototype, the local energy source is currently treated as:

```text
Laptop grid electricity — testing
```

The future old-phone implementation may instead use:

```text
Solar-assisted local edge energy
```

with an appropriate accounting boundary.

---

# 🍃 Net Avoided Carbon

GreenByte compares the cloud baseline against the local inference footprint.

```text
Net Avoided CO₂e
=
max(
    0,
    Cloud CO₂e
    -
    Local CO₂e
    -
    Verification Overhead
)
```

Example prototype result:

```text
Cloud CO₂e
≈ 0.0753 g

Local CO₂e
≈ very small GPU-telemetry-derived value

Net Avoided Carbon
≈ 0.0753 g
```

---

# 🌿 ACU — Avoided Carbon Unit

GreenByte introduces an internal environmental accounting unit called:

> **ACU — Avoided Carbon Unit**

Definition:

```text
1 ACU = 1 gram of net CO₂e avoided
```

Therefore:

```text
0.0753 g CO₂e avoided
=
0.0753 ACU
```

ACU is designed as a simple internal unit for GreenByte environmental reporting.

It is **not** currently:

- a regulated carbon credit
- a carbon offset
- a cryptocurrency
- a financial token
- a tax instrument
- a government-issued environmental certificate

---

# 📏 Measured vs Estimated Parameters

GreenByte clearly distinguishes between measured telemetry and testing assumptions.

| Parameter | Current Status |
|---|---|
| Local input tokens | **Runtime telemetry** |
| Local output tokens | **Runtime telemetry** |
| Cloud input tokens | **Runtime telemetry** |
| Cloud output tokens | **Runtime telemetry** |
| Local GPU power | **Measured via NVIDIA telemetry** |
| Local GPU energy | **Telemetry-derived** |
| Local total laptop energy | **Not yet measured** |
| Cloud inference energy | **Prototype testing estimate** |
| Cloud PUE | **Configured assumption** |
| Grid carbon intensity | **Configured parameter** |
| ACU definition | **GreenByte-defined accounting unit** |
| Certificate ID | **Automatically generated** |
| Evidence Hash | **Cryptographically generated** |
| Methodology Hash | **Cryptographically generated** |
| Ledger Block Hash | **Cryptographically generated** |

This distinction is important.

The current prototype demonstrates the **complete GreenByte measurement and verification pipeline**, while some cloud-energy parameters remain testing assumptions.

---

# 🔐 GreenByte Verification Layer

After the Carbon Engine completes a calculation, GreenByte creates a verification record.

The record may contain:

```text
Session ID
Certificate ID

Prompt
Local Model
Cloud Model

Local Input Tokens
Local Output Tokens
Cloud Input Tokens
Cloud Output Tokens

Local Energy
Cloud Energy

Local CO₂e
Cloud CO₂e

Net Avoided Carbon
ACU

Methodology Version
Timestamp

Evidence Hash
Methodology Hash
Block Hash
Previous Block Hash
```

The backend automatically generates these values.

The user does not manually create the Certificate ID.

---

# 📜 Certificate ID

Every verified GreenByte record receives a unique Certificate ID.

Example:

```text
GB-CERT-418F578D002E
```

The Certificate ID acts as a **human-readable verification reference**.

It connects the visible sustainability certificate to the underlying technical evidence.

Think of it as similar to a:

```text
receipt number
tracking number
verification reference
```

The Certificate ID itself is not the cryptographic proof.

The cryptographic integrity is provided by the hashes associated with the record.

---

# 🧬 GreenByte Hash Structure

GreenByte uses several hashes for different purposes.

---

## 1. Methodology Hash

The configured carbon methodology is hashed.

It may include parameters such as:

```text
Methodology Version
Cloud Formula
Local Formula
PUE
Grid Carbon Intensity
Verification Overhead
ACU Definition
```

The result is:

```text
Methodology Hash
```

This provides evidence of which methodology was associated with the calculation.

---

## 2. Evidence Hash

The AI inference evidence is hashed.

The evidence may include:

```text
Session ID
Certificate ID
Prompt
Models
Tokens
Energy
Carbon Results
ACU
Timestamp
Methodology Hash
```

The result becomes:

```text
Evidence Hash
```

If the evidence is changed later, the recalculated hash will no longer match.

---

## 3. Block Hash

The ledger block also receives a hash.

Conceptually:

```text
Block Hash
=
Hash(
    Block Index
    +
    Previous Block Hash
    +
    Evidence Hash
    +
    Timestamp
)
```

This creates a chain between records.

---

# ⛓️ GreenByte Ledger PoC

The current GreenByte prototype uses a:

> **single-node, gas-free, tamper-evident hash-chained ledger**

Example:

```text
BLOCK 0
GENESIS
Hash: AAAA
      │
      ▼
BLOCK 1
GreenByte Impact Record
Previous Hash: AAAA
Hash: BBBB
      │
      ▼
BLOCK 2
GreenByte Impact Record
Previous Hash: BBBB
Hash: CCCC
```

If an earlier record is modified, its hash changes.

This causes subsequent block references to no longer match.

GreenByte can therefore detect ledger tampering.

---

## Current GreenByte Ledger Does Not Require

```text
MetaMask
Ethereum
Sepolia
SepoliaETH
User-paid gas
Cryptocurrency
Proof-of-Work mining
```

The current system is designed for lightweight sustainability verification.

---

# 🔮 Future GreenByte Chain

The current ledger is a proof-of-concept.

Future GreenByte architecture may extend it into a:

> **low-energy, permissioned, multi-validator GreenByte Chain**

Possible validators could include:

```text
GreenByte Node
University / Research Node
Independent Energy Verifier
Sustainability Partner
Industry Partner
```

The purpose would be distributed environmental-data verification without energy-intensive mining.

---

# 📜 Verified Prompt Impact Certificate

Each verified inference can automatically generate a:

> **GreenByte Verified Prompt Impact Certificate**

Example route:

```text
/certificate/<certificate-id>
```

Example:

```text
/certificate/GB-CERT-418F578D002E
```

The certificate presents human-readable information such as:

- Certificate ID
- AI models
- Cloud footprint
- Local footprint
- Carbon reduction
- Net avoided carbon
- ACU
- Methodology version
- Ledger block
- Verification timestamp

The certificate is designed for **transparent sustainability reporting**.

---

# 🔎 Proof Evidence Page

Each certificate also has a technical proof page.

Route:

```text
/proof/<certificate-id>
```

The Proof page may display:

```text
Certificate ID

Evidence Hash
Recalculated Evidence Hash

Methodology Hash
Recalculated Methodology Hash

Block Hash
Previous Block Hash

Ledger Block Number

Raw Evidence
Chain Integrity
```

This separates the human-readable certificate from the technical evidence used for verification.

---

# ✅ Integrity Verification Page

GreenByte also provides an integrity verification page.

Route:

```text
/verify/<certificate-id>
```

The verification process can recalculate and compare:

```text
Evidence Hash             PASS / FAIL
Methodology Hash          PASS / FAIL
Block Hash                PASS / FAIL
Previous Block Link       PASS / FAIL
Session-to-Block Binding  PASS / FAIL
Full Chain Integrity      PASS / FAIL
```

A valid record is shown as:

```text
✓ VERIFIED
```

If stored evidence has been changed after verification, the recalculated hash may no longer match.

The record can then be displayed as:

```text
✕ INVALID
```

This is the core of GreenByte's:

> **Data Integrity & Accountability**

layer.

---

# 🖥️ GreenByte Dashboard

The GreenByte dashboard acts as a live **AI sustainability observability interface**.

It displays:

- AI runtime status
- local model telemetry
- cloud model telemetry
- input/output tokens
- GPU energy
- cloud energy estimate
- cloud CO₂e
- local CO₂e
- net avoided carbon
- ACU
- certificate status
- ledger block
- recent verified sessions
- proof links
- certificate links
- integrity verification links

The dashboard automatically retrieves data from the GreenByte backend.

---

# 🧪 Recent Verified Inference Sessions

Each verified session is stored and displayed in the Impact History.

Example:

| Session | Model | Tokens | Local Energy | Cloud CO₂e | Local CO₂e | Avoided | Proof | Certificate | Verify |
|---|---|---:|---:|---:|---:|---:|---|---|---|
| GBS-DCA... | qwen3:1.7b | 32 | GPU telemetry | 0.0753 g | `<0.0001 g` | 0.0753 ACU | Block #1 | GB-CERT... | Verify |

The Certificate ID is read automatically from the database.

The user does not manually type the ID during normal use.

---

# 🏗️ Project Architecture

```text
┌────────────────────────────────────┐
│             USER PROMPT            │
└─────────────────┬──────────────────┘
                  │
         ┌────────┴────────┐
         │                 │
         ▼                 ▼
┌────────────────┐  ┌────────────────┐
│  OLLAMA CLOUD  │  │  OLLAMA LOCAL  │
│ DeepSeek V4    │  │ Qwen3 1.7B     │
└───────┬────────┘  └───────┬────────┘
        │                   │
        │           NVIDIA GPU Telemetry
        │                   │
        └──────────┬────────┘
                   ▼
       ┌────────────────────────┐
       │ GREENBYTE CARBON ENGINE│
       │                        │
       │ Tokens                 │
       │ Energy                 │
       │ PUE                    │
       │ Carbon Intensity       │
       │ Cloud vs Local         │
       └────────────┬───────────┘
                    │
                    ▼
          Net Avoided CO₂e
                    │
                    ▼
                   ACU
                    │
                    ▼
          ┌─────────────────┐
          │ VERIFICATION    │
          │                 │
          │ Methodology Hash│
          │ Evidence Hash   │
          │ Block Hash      │
          └────────┬────────┘
                   │
                   ▼
          GREENBYTE LEDGER
                   │
       ┌───────────┼───────────┐
       ▼           ▼           ▼
 Certificate     Proof       Verify
```

---

# 📁 Project Structure

```text
GreenByte-Chain/
│
├── pages/
│   ├── _app.tsx
│   ├── index.tsx
│   │
│   ├── certificate/
│   │   └── [id].tsx
│   │
│   ├── proof/
│   │   └── [id].tsx
│   │
│   └── verify/
│       └── [id].tsx
│
├── styles/
│   └── globals.css
│
├── backend/
│   ├── app.py
│   ├── greenbyte_ledger.py
│   └── methodology.json
│
├── testing/
│   ├── run_greenbyte_comparison.py
│   └── greenbyte_local_energy_test.py
│
├── docs/
│   └── GreenByte_Parameters_Methodology_Research.pdf
│
├── public/
│
├── package.json
├── package-lock.json
├── next.config.js
├── tsconfig.json
├── .gitignore
├── .env.example
└── README.md
```

---

# 🚀 Running GreenByte

## 1. Install Frontend Dependencies

From the project root:

```bash
npm install
```

---

## 2. Start the GreenByte Frontend

```bash
npm run dev
```

Open:

```text
http://localhost:3000
```

---

## 3. Install Backend Dependencies

```bash
pip install flask flask-cors requests ollama
```

---

## 4. Start the GreenByte Backend

```bash
cd backend
python app.py
```

The backend normally runs at:

```text
http://127.0.0.1:5000
```

---

# 🔑 Ollama Cloud API Key

GreenByte does not store the Ollama Cloud API key directly in source code.

Create a local environment variable.

### PowerShell

```powershell
$env:OLLAMA_API_KEY="YOUR_API_KEY"
```

### Windows Command Prompt

```cmd
set OLLAMA_API_KEY=YOUR_API_KEY
```

Never commit a real API key to GitHub.

---

# ☁️ Running the Cloud-vs-Local Test

From the project root:

```bash
python testing/run_greenbyte_comparison.py
```

The script performs:

```text
Local Qwen3 inference
        ↓
Local token telemetry
        ↓
NVIDIA GPU energy measurement
        ↓

Cloud DeepSeek V4 inference
        ↓
Cloud token telemetry
        ↓
Prototype cloud energy estimate
        ↓

GreenByte Carbon Engine
        ↓
Cloud vs Local CO₂e
        ↓
Net avoided carbon
        ↓
ACU
        ↓
Certificate + Ledger Record
```

The GreenByte dashboard then updates automatically.

---

# 🔬 Running the Local GPU Energy Test

```bash
python testing/greenbyte_local_energy_test.py
```

The benchmark measures:

```text
Idle GPU Power

Average GPU Power

Peak GPU Power

Gross GPU Energy

Baseline Energy

Net Incremental GPU Energy

Runtime

Input Tokens

Output Tokens
```

Results can also be written to a CSV file for experimental analysis.

---

# 📚 Methodology & Research

A more detailed explanation of:

- GreenByte parameters
- token telemetry
- local GPU energy measurement
- cloud energy assumptions
- PUE
- carbon formulas
- ACU
- measured vs estimated values
- research basis

is available in:

**[📄 GreenByte Parameters, Methodology & Research](docs/GreenByte_Parameters_Methodology_Research.pdf)**

---

# 📖 Research Basis

GreenByte's methodology is informed by research and technical work in several areas.

## Tokenisation

Subword tokenisation research demonstrates that text is converted into model-specific subword units rather than simply being counted as human-readable words.

This supports GreenByte's approach of retrieving token counts directly from the AI runtime.

---

## Energy & Carbon Reporting

Existing machine-learning sustainability research argues for reporting computational energy and carbon emissions more systematically.

GreenByte follows this principle by separating:

```text
AI workload
Energy consumption
Electricity carbon intensity
Carbon footprint
```

rather than treating every token as having a universal fixed carbon value.

---

## Data-Centre Efficiency

GreenByte includes Power Usage Effectiveness (PUE) in cloud carbon accounting.

PUE represents:

```text
Total Data-Centre Energy
÷
IT Equipment Energy
```

This accounts for data-centre overhead such as:

- cooling
- power conversion
- UPS systems
- supporting infrastructure

---

## GPU Power Telemetry

The current local prototype uses NVIDIA GPU power telemetry to estimate incremental GPU inference energy.

This provides a hardware-derived measurement rather than a manually assumed local energy value.

---

# 🎯 Focus Areas

GreenByte addresses several sustainability and technology areas:

### 🌿 Carbon Transparency & Tracking

Makes AI inference carbon impact visible at prompt level.

### ⚡ Renewable Energy & Edge Computing

Explores local AI inference powered by lower-carbon and renewable energy sources.

### 🔐 Data Integrity & Accountability

Uses cryptographic hashes and a tamper-evident ledger to verify environmental records.

### 🤖 AI & Blockchain Innovation

Combines AI inference telemetry with lightweight verification infrastructure.

### ♻️ Sustainable Computing

Explores repurposing older computing devices as local AI edge nodes.

---

# 🧭 Prototype Status

## Implemented

```text
✅ Ollama Cloud AI connection

✅ Ollama Local AI connection

✅ DeepSeek V4 Cloud testing

✅ Qwen3 Local testing

✅ Input token telemetry

✅ Output token telemetry

✅ NVIDIA GPU power measurement

✅ Local GPU energy derivation

✅ Cloud energy prototype estimator

✅ Cloud-vs-local carbon comparison

✅ Net avoided CO₂e calculation

✅ ACU calculation

✅ Certificate ID generation

✅ Methodology hashing

✅ Evidence hashing

✅ Block hashing

✅ GreenByte Ledger PoC

✅ Certificate page

✅ Proof page

✅ Verification page

✅ Impact history

✅ Dashboard auto-refresh
```

---

# 🔮 Future Development

GreenByte is still a proof-of-concept.

Future work includes:

```text
🔬 Physical wall-plug energy measurement

🔬 Repurposed smartphone AI deployment

🔬 Solar-assisted edge inference

🔬 Model-matched Cloud vs Local benchmarks

🔬 Research-calibrated cloud energy model

🔬 Real data-centre regional carbon factors

🔬 Verification energy overhead measurement

🔬 QR-based certificate verification

🔬 Public GreenByte verification portal

🔬 Multi-validator GreenByte Chain

🔬 Independent sustainability verification nodes
```

---

# ⚠️ Limitations

The current prototype should not be interpreted as a final certified carbon-accounting platform.

Important limitations include:

- Cloud energy is currently based on a prototype testing estimator.
- Local GPU telemetry does not represent total laptop wall energy.
- Different Cloud and Local AI models may have different capabilities and tokenisers.
- Carbon intensity values depend on configured electricity assumptions.
- The current GreenByte Ledger is single-node rather than distributed.
- ACU is an internal GreenByte measurement unit.
- GreenByte certificates are not regulated carbon credits or government certificates.

The purpose of the prototype is to demonstrate the **measurement, comparison, and verification architecture**.

---

# 🛡️ Security

Do not commit any of the following:

```text
.env
API keys
private keys
greenbyte.db
credentials
secrets
```

The repository `.gitignore` should exclude runtime databases, environment variables, generated build files, and dependency directories.

---

# 🌐 GreenByte Vision

GreenByte explores a future where AI sustainability becomes:

> **Measurable. Transparent. Verifiable.**

The long-term objective is to create a lightweight sustainability layer that can sit behind AI systems without changing the way people normally interact with AI.

The user simply uses AI.

GreenByte operates in the background:

```text
AI runs
    ↓
GreenByte observes
    ↓
Energy is measured
    ↓
Cloud and Local are compared
    ↓
Avoided carbon is calculated
    ↓
Evidence is hashed
    ↓
The record is verified
```

---

# 🌱 GreenByte

## Every Prompt Has a Carbon Cost.

### Measure it. Compare it. Verify what local AI saves.

> **AI Today · A Cleaner Tomorrow**
