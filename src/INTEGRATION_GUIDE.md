# GreenByte v4 — AI-connected architecture

## What changed

This version removes the old Web3 user flow completely:

- no MetaMask
- no RainbowKit
- no Wagmi
- no Sepolia
- no ETH / gas token
- no user-entered input/output tokens
- no dashboard-side carbon calculation
- no "Verify" or "Start measuring" action for the user

The dashboard is now **read-only live observability**. Your friend's AI runtime is the data source.

## Runtime flow

```text
User asks friend's AI
        ↓
Friend AI runs local inference
        ↓
AI runtime knows actual input/output token counts
Phone / meter supplies local inference energy (J)
        ↓
friend_ai_adapter.py
        ↓ POST /api/inference-report
GreenByte backend
        ↓
Cloud baseline estimation / measured cloud reference
Local carbon calculation
Net avoided CO2e calculation
        ↓
GreenByte Ledger PoC (hash-chained proof, no gas)
        ↓
Impact Certificate ID + proof hash
        ↓
Dashboard auto-refreshes every 2 seconds
```

## 1. Replace your frontend

Replace:

- `pages/index.tsx`
- `pages/_app.tsx`
- `styles/globals.css`

The new `_app.tsx` intentionally removes all RainbowKit/Wagmi providers.

You may leave `wagmi.ts` in the folder, but it is unused. You can also delete it.

## 2. Run the backend

From `backend/`:

```bash
pip install flask flask-cors requests
python app.py
```

Backend defaults to:

```text
http://127.0.0.1:5000
```

The frontend uses:

```text
NEXT_PUBLIC_GREENBYTE_API=http://127.0.0.1:5000
```

If you do not set it, localhost:5000 is already the default.

## 3. Connect your friend's AI

Copy `integration/friend_ai_adapter.py` into your friend's Python project.

At AI service startup:

```python
from friend_ai_adapter import GreenByteReporter

reporter = GreenByteReporter(
    base_url="http://127.0.0.1:5000",
    source_id="old-phone-ai-01",
    source_name="Solar Old Phone AI",
)
reporter.start_heartbeat()
```

After the model has generated a response:

```python
reporter.report_inference(
    prompt_preview=prompt,
    model="Qwen 1.5B",
    device="Samsung Galaxy S9",
    energy_source="Solar-powered edge node",
    input_tokens=len(input_ids),
    output_tokens=len(output_ids),
    local_energy_j=measured_energy_j,
)
```

The important point is that `input_tokens` and `output_tokens` come from the **actual AI model/tokenizer**, while `local_energy_j` comes from the **actual phone/power measurement**.

## 4. Cloud baseline

The backend, not the UI, selects a cloud baseline.

Two supported modes:

### A. Calibrated profile

Do not send `cloud_energy_j`. The backend uses `backend/methodology.json` and the calibrated model:

```text
E = alpha
  + beta_input × N_input
  + beta_output × N_output
  + gamma × N_output × (N_input + (N_output - 1)/2)
```

The included coefficients are explicitly **demo placeholders**. Replace them after you benchmark the same model on the cloud GPU.

### B. Measured cloud energy

If you have an actual cloud measurement, send:

```python
cloud_energy_j=actual_cloud_joules
```

The backend will use that instead of the calibrated profile.

## 5. Carbon algorithm

```text
Cloud CO2e
= cloud_energy_j × PUE / 3,600,000 × cloud_grid_intensity

Local CO2e
= local_energy_j / 3,600,000 × local_energy_intensity

Net avoided CO2e
= max(0, Cloud CO2e - Local CO2e - verification overhead)

1 ACU = 1 g CO2e net avoided
```

## 6. GreenByte Ledger PoC

`greenbyte_ledger.py` is a single-node append-only hash chain.

It provides:

- previous-block hash
- block hash
- immutable-style evidence chain
- proof hash
- certificate ID
- chain validation endpoint
- zero user gas

It is **not yet a distributed blockchain**. Do not tell judges it is a fully decentralized consensus network. The honest wording is:

> "For the proof of concept, GreenByte uses its own no-gas hash-chained verification ledger. The production architecture upgrades this to a permissioned multi-validator GreenByte Chain."

This is a much cleaner transition toward Besu/QBFT later.
