# GreenByte UI/UX v4 — AI Connected

This is the corrected architecture after removing MetaMask and manual dashboard measurement.

## Replace these frontend files

```text
pages/_app.tsx
pages/index.tsx
styles/globals.css
```

## Add these backend files

```text
backend/app.py
backend/greenbyte_ledger.py
backend/methodology.json
```

## AI integration

Give your friend:

```text
integration/friend_ai_adapter.py
```

Read `INTEGRATION_GUIDE.md` for the exact integration flow.

### Core product statement

**GreenByte is a background AI carbon intelligence layer.**

It connects to an AI runtime, receives real inference telemetry, calculates Cloud vs Local environmental impact server-side, and automatically creates a tamper-evident impact record.

The dashboard is for viewing the results. It does not ask the user to measure anything.
