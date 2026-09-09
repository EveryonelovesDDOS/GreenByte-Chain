# 🌱 GreenByte Methodology

## AI Carbon Measurement, Comparison & Verification

> **Every Prompt Has a Carbon Cost.**  
> **Measure it. Compare it. Verify what local AI saves.**

---

# 1. GreenByte Idea

GreenByte is a proof-of-concept system for measuring and verifying the environmental impact of AI inference.

The main idea is simple:

```text
Same AI task
      ↓
Compare two execution paths
      ↓
Cloud AI vs Local AI
      ↓
Measure / estimate energy
      ↓
Convert energy into CO₂e
      ↓
Calculate the difference
      ↓
Record avoided carbon
      ↓
Create a verifiable impact record
```

GreenByte operates as a background measurement and verification layer.

The user should not need to manually enter:

```text
Token count
Energy
Carbon
ACU
Certificate ID
Hash
```

The system automatically obtains or calculates these values.

---

# 2. Current Prototype Architecture

```text
                         USER PROMPT
                              │
                 ┌────────────┴────────────┐
                 │                         │
                 ▼                         ▼
          OLLAMA CLOUD               OLLAMA LOCAL
       DeepSeek V4 Flash             Qwen3 1.7B
                 │                         │
          Runtime telemetry          Runtime telemetry
                 │                         │
          Input / Output             Input / Output
             Tokens                     Tokens
                 │                         │
                 │                NVIDIA GPU Power
                 │                    Telemetry
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
                    GreenByte Evidence
                              │
                   ┌──────────┴──────────┐
                   ▼                     ▼
             Evidence Hash       Methodology Hash
                   │                     │
                   └──────────┬──────────┘
                              ▼
                     GREENBYTE LEDGER
                              │
                         Block Hash
                              │
                 ┌────────────┼────────────┐
                 ▼            ▼            ▼
            Certificate      Proof       Verify
```

---

# 3. Current Testing Setup

## Shared Prompt

```text
How are you?
```

## Testing Controls

```text
temperature = 0

think = false

num_predict = 50
```

`num_predict = 50` means:

> The AI model may generate **up to 50 output tokens**.

It does not mean every model must produce exactly 50 tokens.

---

# 4. Value 1 — Local AI

Current Local AI:

```text
Provider:
Ollama Local

Model:
Qwen3 1.7B

Hardware:
NVIDIA GeForce RTX 4050 Laptop GPU

Prompt:
"How are you?"
```

Actual runtime telemetry:

```text
Input Tokens:
20

Output Tokens:
12

Total Tokens:
32
```

The maximum output was configured as:

```text
50
```

but Qwen completed its response naturally after:

```text
12 output tokens
```

Therefore:

```text
Configured maximum ≠ actual output
```

---

# 5. Value 2 — Cloud AI

Current Cloud AI:

```text
Provider:
Ollama Cloud

Model:
DeepSeek V4 Flash

Prompt:
"How are you?"
```

Actual runtime telemetry:

```text
Input Tokens:
8

Output Tokens:
50

Total Tokens:
58
```

The cloud model reached the configured maximum:

```text
num_predict = 50
```

---

# 6. Token Methodology

GreenByte does not manually calculate token count.

Ollama provides runtime telemetry.

The important fields are:

```text
prompt_eval_count
=
Input Tokens
```

```text
eval_count
=
Output Tokens
```

Other useful runtime fields include:

```text
total_duration

prompt_eval_duration

eval_duration
```

Therefore GreenByte uses:

```text
AI Runtime
      ↓
prompt_eval_count
      ↓
Input Tokens
```

and:

```text
AI Runtime
      ↓
eval_count
      ↓
Output Tokens
```

---

# 7. Why the Same Prompt Has Different Token Counts

The visible prompt is:

```text
How are you?
```

But:

```text
DeepSeek V4 Flash:
8 input tokens
```

while:

```text
Qwen3 1.7B:
20 input tokens
```

This is not an error.

Different models may have different:

```text
Tokenizers

Vocabulary

Chat templates

Special tokens

Prompt formatting
```

Therefore GreenByte treats runtime telemetry as the authoritative token count.

---

# 8. Local Energy Measurement

The current prototype measures Local AI GPU energy using NVIDIA power telemetry.

GreenByte samples:

```text
nvidia-smi
```

GPU power is measured in:

```text
Watts
```

Energy is measured in:

```text
Joules
```

The basic relationship is:

```text
Energy
=
Power × Time
```

or more generally:

```text
Gross GPU Energy
≈
∫ P(t) dt
```

---

# 9. Idle Baseline

The GPU already consumes electricity even when no AI inference is being executed.

Therefore GreenByte also measures:

```text
Idle GPU Power
```

Baseline energy:

```text
Baseline Energy
=
Idle GPU Power
×
Inference Runtime
```

Net incremental inference energy:

```text
Net Local Energy
=
max(
    0,
    Gross GPU Energy
    -
    Baseline Energy
)
```

---

# 10. Example Local Measurement

Example completed test:

```text
Idle GPU Power:
15.663 W

Average GPU Power:
22.560 W

Peak GPU Power:
22.560 W
```

Calculated energy:

```text
Gross GPU Energy:
2.407 J

Baseline Energy:
1.671 J

Net Inference Energy:
0.736 J
```

A separate 5-run benchmark produced:

```text
Average Net GPU Energy:
1.156 J

Median:
0.736 J

Standard Deviation:
1.351 J
```

The current result should be interpreted as:

> **GPU telemetry-derived incremental inference energy**

and not:

> **total laptop electricity consumption**.

CPU, memory, motherboard, cooling, display and power-supply losses are not fully included.

---

# 11. Cloud Energy

Ollama Cloud currently provides runtime information such as:

```text
Tokens

Inference duration
```

but does not directly provide:

```text
Actual data-centre Joules
```

Therefore the current prototype uses a testing estimator.

---

# 12. Current Cloud Testing Formula

Current GreenByte test:

```text
Cloud Energy
=
α
+
β(input) × Input Tokens
+
β(output) × Output Tokens
```

Current testing coefficients:

```text
α = 250 J

β(input) = 2 J / input token

β(output) = 7 J / output token
```

Current Cloud telemetry:

```text
Input = 8

Output = 50
```

Calculation:

```text
Cloud Energy
=
250
+
(2 × 8)
+
(7 × 50)
```

Therefore:

```text
Cloud Energy
=
250
+
16
+
350
```

```text
Cloud Energy
=
616 J
```

---

# ⚠️ Important Cloud Energy Limitation

The following values:

```text
250 J

2 J/input token

7 J/output token
```

are currently:

> **GreenByte prototype testing coefficients.**

They are not measured values disclosed by Ollama Cloud.

They must eventually be replaced by:

```text
Measured cloud inference energy

Provider-disclosed telemetry

Published benchmark calibration

or

Research-calibrated energy models
```

before final environmental claims are made.

---

# 13. Energy to Carbon Conversion

GreenByte converts energy into carbon emissions.

Since:

```text
1 kWh
=
3,600,000 Joules
```

energy in Joules is converted into kWh before applying electricity carbon intensity.

---

# 14. Cloud Carbon Formula

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

Current testing parameters:

```text
Cloud Energy:
616 J

PUE:
1.10

Cloud Carbon Intensity:
400 g CO₂e/kWh
```

Calculation:

```text
Cloud CO₂e
=
616
×
1.10
÷
3,600,000
×
400
```

Result:

```text
Cloud CO₂e
≈
0.0752889 g CO₂e
```

Dashboard:

```text
0.0753 g CO₂e
```

---

# 15. Why PUE Is Included

PUE means:

> **Power Usage Effectiveness**

Conceptually:

```text
PUE
=
Total Data-Centre Energy
÷
IT Equipment Energy
```

Cloud computing requires more than GPU energy.

Additional energy can include:

```text
Cooling

Power conversion

UPS

Networking

Facility infrastructure
```

GreenByte therefore includes PUE as a separate cloud parameter.

---

# 16. Local Carbon Formula

```text
Local CO₂e
=
Local Energy
÷
3,600,000
×
Local Carbon Intensity
```

Current testing Local Carbon Intensity:

```text
200 g CO₂e/kWh
```

This is currently a testing default.

It should later be replaced by the actual electricity-source factor.

---

# 17. Example Local Carbon

Using the separate benchmark average:

```text
Local Energy
=
1.156 J
```

and:

```text
Local Carbon Intensity
=
200 g CO₂e/kWh
```

Calculation:

```text
1.156
÷
3,600,000
×
200
```

Result:

```text
≈ 0.0000642 g CO₂e
```

This demonstrates why the dashboard should preferably display very small local values as:

```text
< 0.0001 g
```

rather than displaying:

```text
0.0000 g
```

which may incorrectly imply zero energy or zero carbon.

---

# 18. Avoided Carbon

GreenByte calculates:

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

Current testing verification overhead:

```text
0 g
```

because it has not yet been separately measured.

---

# 19. Example Avoided Carbon

Using:

```text
Cloud:
0.0752889 g

Local:
0.0000642 g
```

then:

```text
Avoided Carbon
=
0.0752889
-
0.0000642
```

Result:

```text
≈ 0.0752247 g CO₂e
```

Approximate reduction:

```text
99.91%
```

---

# 20. ACU — Avoided Carbon Unit

GreenByte defines:

```text
ACU
=
Avoided Carbon Unit
```

Current project definition:

```text
1 ACU
=
1 gram of net CO₂e avoided
```

Therefore:

```text
0.0753 g CO₂e avoided
≈
0.0753 ACU
```

ACU is:

> an internal GreenByte environmental-accounting unit.

It is not currently:

```text
Carbon credit

Carbon offset

Cryptocurrency

Financial instrument

Government certificate

Tax instrument
```

---

# 21. Measurement Status

GreenByte separates parameters according to their origin.

| Parameter | Status |
|---|---|
| Local input tokens | Runtime telemetry |
| Local output tokens | Runtime telemetry |
| Cloud input tokens | Runtime telemetry |
| Cloud output tokens | Runtime telemetry |
| Local GPU power | Measured |
| Local GPU energy | Telemetry-derived |
| Total laptop wall energy | Not yet measured |
| Cloud energy | Prototype estimate |
| Local carbon intensity | Testing parameter |
| Cloud carbon intensity | Testing parameter |
| PUE | Testing / configured parameter |
| Verification overhead | Testing parameter |
| ACU definition | GreenByte project definition |
| Evidence Hash | Cryptographically generated |
| Methodology Hash | Cryptographically generated |
| Block Hash | Cryptographically generated |

---

# 22. Verification Idea

GreenByte is not only intended to calculate carbon.

It also provides:

> **Data Integrity & Accountability**

Every verified inference produces a record containing:

```text
Session ID

Certificate ID

Prompt

Local Model

Cloud Model

Token Telemetry

Energy

Carbon

Avoided Carbon

ACU

Methodology Version

Timestamp
```

---

# 23. Methodology Hash

The methodology used to calculate the result is hashed.

Example methodology content:

```text
Formula version

PUE

Carbon intensity

ACU definition

Cloud energy parameters

Verification overhead
```

Result:

```text
Methodology Hash
```

Purpose:

> Demonstrate which GreenByte methodology was associated with the certificate.

---

# 24. Evidence Hash

Inference evidence is also hashed.

Example evidence:

```text
Session ID

Models

Tokens

Energy

Carbon

ACU

Timestamp

Methodology Hash
```

Result:

```text
Evidence Hash
```

If the stored evidence is later changed:

```text
New Hash
≠
Original Hash
```

and GreenByte can identify the record as invalid.

---

# 25. GreenByte Ledger

Current PoC:

```text
BLOCK 0
Genesis
Hash AAAA
     ↓

BLOCK 1
Evidence Record
Previous Hash AAAA
Hash BBBB
     ↓

BLOCK 2
Evidence Record
Previous Hash BBBB
Hash CCCC
```

This creates a:

> **tamper-evident hash-chained ledger**

---

# 26. Block Hash

Conceptually:

```text
Block Hash
=
Hash(
    Block Number
    +
    Previous Block Hash
    +
    Evidence Hash
    +
    Timestamp
)
```

Changing earlier evidence changes the block hash and can break the chain.

---

# 27. Certificate ID

Every verified record automatically receives a unique Certificate ID.

Example:

```text
GB-CERT-418F578D002E
```

The user does not manually create or enter this ID during normal operation.

It is retrieved automatically from the GreenByte database.

Certificate ID acts as a:

```text
Verification reference number

Record identifier

Human-readable evidence reference
```

---

# 28. Certificate Page

Route:

```text
/certificate/<certificate-id>
```

Purpose:

> Human-readable sustainability record.

Displays:

```text
Certificate ID

Cloud CO₂e

Local CO₂e

Net Avoided Carbon

ACU

Methodology

Ledger Block

Timestamp
```

---

# 29. Proof Page

Route:

```text
/proof/<certificate-id>
```

Purpose:

> Technical proof of evidence.

Displays:

```text
Evidence Hash

Recalculated Evidence Hash

Methodology Hash

Recalculated Methodology Hash

Block Hash

Previous Block Hash

Raw Evidence

Ledger Block
```

---

# 30. Verify Page

Route:

```text
/verify/<certificate-id>
```

GreenByte recalculates the stored hashes and performs integrity checks.

Possible verification checks:

```text
Evidence Hash
PASS / FAIL

Methodology Hash
PASS / FAIL

Block Hash
PASS / FAIL

Previous Block Link
PASS / FAIL

Session-to-Block Binding
PASS / FAIL

Full Chain Integrity
PASS / FAIL
```

Successful verification:

```text
✓ VERIFIED
```

Failed verification:

```text
✕ INVALID
```

---

# 31. Current GreenByte Ledger vs Future Blockchain

Current GreenByte:

```text
Single-node

Gas-free

Hash-chained

Tamper-evident
```

It does not currently require:

```text
Ethereum

MetaMask

Sepolia

User-paid gas

Mining
```

Future architecture may extend it to:

```text
GreenByte Validator 1

GreenByte Validator 2

University Validator

Independent Sustainability Validator
```

using a low-energy permissioned consensus mechanism.

---

# 32. Long-Term GreenByte Idea

The current laptop is only a testing device.

Final concept:

```text
Solar Energy
      ↓
Repurposed Old Smartphone
      ↓
Local AI
      ↓
Measured Device Energy
      ↓
GreenByte Carbon Engine
      ↓
Cloud Baseline Comparison
      ↓
Avoided Carbon
      ↓
ACU
      ↓
Verified Impact Record
```

The goal is to explore whether existing devices can be repurposed as lower-energy local AI nodes.

---

# 33. Future Water Measurement

GreenByte may later add a separate water metric.

Potential factors:

```text
Data-centre cooling water

Electricity-generation water consumption

Local inference water impact
```

Water should initially remain separate from ACU.

---

# 34. What GreenByte Can Claim Today

The current PoC can demonstrate that:

```text
✓ Ollama Cloud provides runtime token telemetry.

✓ Ollama Local provides runtime token telemetry.

✓ Different models can report different token counts for the same visible prompt.

✓ NVIDIA GPU power can be sampled during Local AI inference.

✓ Power can be integrated into incremental GPU energy.

✓ Energy values can be converted into CO₂e using an explicit carbon-intensity parameter.

✓ Cloud and Local pathways can be compared.

✓ GreenByte can calculate an internal avoided-carbon value.

✓ GreenByte can generate ACU.

✓ GreenByte can create Certificate IDs.

✓ Evidence can be cryptographically hashed.

✓ The methodology can be hashed.

✓ Records can be chained in the GreenByte Ledger.

✓ Certificates can be independently rechecked through a Verify page.
```

---

# 35. What GreenByte Cannot Yet Claim

The current PoC should not claim that:

```text
✕ 616 J is the actual measured energy consumed by Ollama Cloud.

✕ The current cloud coefficients are scientifically validated.

✕ 200 or 400 g CO₂e/kWh represent the exact electricity source used by the real systems.

✕ GPU-only telemetry represents total laptop electricity.

✕ ACU is an official carbon credit.

✕ The current GreenByte Ledger is a fully distributed blockchain.

✕ Current GreenByte certificates are government-issued environmental certifications.
```

---

# 36. Recommended Presentation Wording

Use:

> **GreenByte reads actual AI token telemetry, measures local GPU energy during testing, applies a transparent cloud-energy baseline, converts both paths into CO₂e, and produces a verifiable estimate of avoided carbon. Measured and estimated values are explicitly labelled.**

---

# 37. GreenByte Methodology in One Line

> **Tokens describe the workload. Joules describe the energy. Carbon intensity converts energy into CO₂e. Cloud minus Local minus verification overhead becomes avoided carbon, and each gram of net CO₂e avoided is recorded as one ACU.**

---

# 38. Research References

The academic research supporting this methodology is documented separately in:

```text
RESEARCH.md
```

The research covers:

```text
Tokenisation

AI inference power

Machine-learning energy reporting

Carbon accounting

Cloud-vs-edge inference

Future water-footprint accounting
```

---

# 🌱 GreenByte

## Every Prompt Has a Carbon Cost.

### Measure it. Compare it. Verify what local AI saves.

> **AI Today · A Cleaner Tomorrow**
