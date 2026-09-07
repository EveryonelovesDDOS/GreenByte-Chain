"""GreenByte AI-connected Carbon Backend v4

The dashboard does NOT calculate carbon and does NOT ask the user for tokens.
Your friend's AI runtime sends inference telemetry here automatically.
This service:
  1) receives real AI telemetry;
  2) calculates Cloud vs Local carbon server-side;
  3) creates ACU (1 ACU = 1 g CO2e net avoided);
  4) writes a tamper-evident proof to the local GreenByte Ledger PoC;
  5) exposes live dashboard data.

No MetaMask. No Sepolia. No ETH. No user-paid gas. No tax claim.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import time
import uuid
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

from greenbyte_ledger import GreenByteLedger

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("GREENBYTE_DB", BASE_DIR / "greenbyte.db"))
METHODOLOGY_PATH = Path(os.getenv("GREENBYTE_METHODOLOGY", BASE_DIR / "methodology.json"))

app = Flask(__name__)
CORS(app)
ledger = GreenByteLedger(DB_PATH)

METHODOLOGY_VERSION = "GB-CARBON-v1.0"
SOURCE_LIVE_WINDOW_SECONDS = 30
_last_source_seen: dict[str, float] = {}
_last_source_name = "Friend AI Runtime"


def load_methodology():
    with open(METHODOLOGY_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS impact_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL UNIQUE,
                certificate_id TEXT NOT NULL UNIQUE,
                source_id TEXT NOT NULL,
                source_name TEXT NOT NULL,
                verified_at TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                proof_hash TEXT NOT NULL,
                block_index INTEGER NOT NULL
            )
            """
        )
        conn.commit()


init_db()


def D(value, field):
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError(f"{field} must be a valid number")
    if not result.is_finite():
        raise ValueError(f"{field} must be finite")
    return result


def as_non_negative_decimal(data, field, default=None):
    raw = data.get(field, default)
    if raw is None:
        raise ValueError(f"{field} is required")
    value = D(raw, field)
    if value < 0:
        raise ValueError(f"{field} cannot be negative")
    return value


def as_non_negative_int(data, field, default=None):
    raw = data.get(field, default)
    if raw is None:
        raise ValueError(f"{field} is required")
    try:
        value = int(raw)
    except (TypeError, ValueError):
        raise ValueError(f"{field} must be an integer")
    if value < 0:
        raise ValueError(f"{field} cannot be negative")
    return value


def canonical_hash(payload: dict) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def estimate_cloud_energy(input_tokens: int, output_tokens: int, profile: dict) -> Decimal:
    """Calibrated request-energy model.

    E = alpha + beta_in*Nin + beta_out*Nout + gamma*Nout*(Nin + (Nout-1)/2)

    Coefficients must be replaced with your own benchmark calibration for final claims.
    """
    alpha = D(profile["alpha_j"], "alpha_j")
    beta_in = D(profile["beta_input_j_per_token"], "beta_input_j_per_token")
    beta_out = D(profile["beta_output_j_per_token"], "beta_output_j_per_token")
    gamma = D(profile.get("gamma_j_per_context_token", 0), "gamma_j_per_context_token")
    nin = Decimal(input_tokens)
    nout = Decimal(output_tokens)
    context_term = nout * (nin + (nout - 1) / Decimal(2)) if output_tokens else Decimal(0)
    return max(Decimal(0), alpha + beta_in * nin + beta_out * nout + gamma * context_term)


def calculate_impact(data: dict):
    methodology = load_methodology()

    input_tokens = as_non_negative_int(data, "input_tokens")
    output_tokens = as_non_negative_int(data, "output_tokens")
    local_energy_j = as_non_negative_decimal(data, "local_energy_j")

    local_ci = D(data.get("local_carbon_intensity_g_per_kwh", methodology["local"]["default_carbon_intensity_g_per_kwh"]), "local_carbon_intensity_g_per_kwh")
    verification_overhead_g = D(data.get("verification_overhead_g", methodology["verification"]["default_overhead_g"]), "verification_overhead_g")

    cloud_energy_raw = data.get("cloud_energy_j")
    cloud_profile_name = data.get("cloud_profile", methodology["cloud"]["default_profile"])
    profile = methodology["cloud"]["profiles"].get(cloud_profile_name)

    if cloud_energy_raw is not None:
        cloud_energy_j = as_non_negative_decimal(data, "cloud_energy_j")
        baseline_origin = data.get("baseline_origin", "Measured / externally supplied cloud energy")
        pue = D(data.get("cloud_pue", profile["pue"] if profile else methodology["cloud"]["default_pue"]), "cloud_pue")
        cloud_ci = D(data.get("cloud_carbon_intensity_g_per_kwh", profile["carbon_intensity_g_per_kwh"] if profile else methodology["cloud"]["default_carbon_intensity_g_per_kwh"]), "cloud_carbon_intensity_g_per_kwh")
    else:
        if not profile:
            raise ValueError(f"Unknown cloud_profile: {cloud_profile_name}")
        cloud_energy_j = estimate_cloud_energy(input_tokens, output_tokens, profile)
        baseline_origin = profile["label"]
        pue = D(profile["pue"], "pue")
        cloud_ci = D(profile["carbon_intensity_g_per_kwh"], "cloud carbon intensity")

    if pue < 1 or pue > 5:
        raise ValueError("cloud PUE must be between 1 and 5")
    if cloud_ci < 0 or local_ci < 0:
        raise ValueError("carbon intensities cannot be negative")

    cloud_carbon_g = cloud_energy_j * pue / Decimal("3600000") * cloud_ci
    local_carbon_g = local_energy_j / Decimal("3600000") * local_ci
    gross_avoided_g = max(Decimal(0), cloud_carbon_g - local_carbon_g)
    net_avoided_g = max(Decimal(0), gross_avoided_g - verification_overhead_g)
    reduction_pct = (net_avoided_g / cloud_carbon_g * Decimal(100)) if cloud_carbon_g > 0 else Decimal(0)

    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "local_energy_j": float(local_energy_j),
        "cloud_energy_j": float(cloud_energy_j),
        "cloud_carbon_g": float(cloud_carbon_g),
        "local_carbon_g": float(local_carbon_g),
        "verification_overhead_g": float(verification_overhead_g),
        "net_avoided_g": float(net_avoided_g),
        "reduction_pct": float(reduction_pct),
        "cloud_pue": float(pue),
        "cloud_carbon_intensity_g_per_kwh": float(cloud_ci),
        "local_carbon_intensity_g_per_kwh": float(local_ci),
        "baseline_origin": baseline_origin,
        "cloud_profile": cloud_profile_name,
    }


def row_to_record(row):
    payload = json.loads(row["payload_json"])
    payload.update({
        "session_id": row["session_id"],
        "certificate_id": row["certificate_id"],
        "source_id": row["source_id"],
        "verified_at": row["verified_at"],
        "proof_hash": row["proof_hash"],
        "block_index": int(row["block_index"]),
    })
    return payload


def latest_records(limit=12):
    with connect_db() as conn:
        rows = conn.execute(
            "SELECT * FROM impact_sessions ORDER BY id DESC LIMIT ?", (int(limit),)
        ).fetchall()
    return [row_to_record(row) for row in rows]


def current_source_state():
    if not _last_source_seen:
        return False, None, _last_source_name
    source_id, seen = max(_last_source_seen.items(), key=lambda item: item[1])
    age = max(0.0, time.time() - seen)
    return age <= SOURCE_LIVE_WINDOW_SECONDS, age, _last_source_name or source_id


@app.get("/api/health")
def health():
    live, age, source_name = current_source_state()
    return jsonify({
        "status": "ok",
        "source_live": live,
        "source_age_seconds": age,
        "source_name": source_name,
        "methodology_version": METHODOLOGY_VERSION,
        "ledger_height": ledger.height(),
        "ledger_valid": ledger.verify(),
    })


@app.post("/api/source/heartbeat")
def source_heartbeat():
    global _last_source_name
    data = request.get_json(silent=True) or {}
    source_id = str(data.get("source_id", "friend-ai-runtime"))
    _last_source_name = str(data.get("source_name", "Friend AI Runtime"))
    _last_source_seen[source_id] = time.time()
    return jsonify({"status": "ok", "source_id": source_id, "source_name": _last_source_name})


@app.post("/api/inference-report")
def inference_report():
    global _last_source_name
    try:
        data = request.get_json(force=True) or {}
        source_id = str(data.get("source_id", "friend-ai-runtime"))
        source_name = str(data.get("source_name", "Friend AI Runtime"))
        _last_source_name = source_name
        _last_source_seen[source_id] = time.time()

        impact = calculate_impact(data)
        session_id = str(data.get("session_id") or f"GBS-{uuid.uuid4().hex[:16].upper()}")
        verified_at = datetime.now(timezone.utc).isoformat()

        record = {
            "source_name": source_name,
            "prompt_preview": str(data.get("prompt_preview", ""))[:280],
            "model": str(data.get("model", "Unknown model")),
            "device": str(data.get("device", "Unknown edge device")),
            "energy_source": str(data.get("energy_source", "Unknown energy source")),
            "local_measurement_origin": str(data.get("local_measurement_origin", "AI runtime / power telemetry")),
            "methodology_version": METHODOLOGY_VERSION,
            **impact,
        }

        methodology_payload = {
            "version": METHODOLOGY_VERSION,
            "formula": {
                "cloud": "cloud_energy_j * PUE / 3600000 * cloud_carbon_intensity_g_per_kwh",
                "local": "local_energy_j / 3600000 * local_carbon_intensity_g_per_kwh",
                "net": "max(0, cloud - local - verification_overhead_g)",
            },
            "cloud_profile": impact["cloud_profile"],
            "cloud_pue": impact["cloud_pue"],
            "cloud_ci": impact["cloud_carbon_intensity_g_per_kwh"],
            "local_ci": impact["local_carbon_intensity_g_per_kwh"],
        }
        methodology_hash = canonical_hash(methodology_payload)

        evidence_payload = {
            "session_id": session_id,
            "source_id": source_id,
            "input_tokens": impact["input_tokens"],
            "output_tokens": impact["output_tokens"],
            "local_energy_j": impact["local_energy_j"],
            "cloud_energy_j": impact["cloud_energy_j"],
            "model": record["model"],
            "device": record["device"],
            "methodology_hash": methodology_hash,
            "verified_at": verified_at,
        }
        evidence_hash = canonical_hash(evidence_payload)

        ledger_payload = {
            "type": "AI_IMPACT_RECORD",
            "session_id": session_id,
            "source_id": source_id,
            "model": record["model"],
            "input_tokens": impact["input_tokens"],
            "output_tokens": impact["output_tokens"],
            "cloud_carbon_g": impact["cloud_carbon_g"],
            "local_carbon_g": impact["local_carbon_g"],
            "net_avoided_g": impact["net_avoided_g"],
            "methodology_hash": methodology_hash,
            "evidence_hash": evidence_hash,
        }
        block = ledger.append(ledger_payload)
        proof_hash = block["block_hash"]
        certificate_id = f"GB-CERT-{proof_hash[:12].upper()}"

        with connect_db() as conn:
            conn.execute(
                """
                INSERT INTO impact_sessions(
                    session_id,certificate_id,source_id,source_name,verified_at,
                    payload_json,proof_hash,block_index
                ) VALUES(?,?,?,?,?,?,?,?)
                """,
                (
                    session_id,
                    certificate_id,
                    source_id,
                    source_name,
                    verified_at,
                    json.dumps(record, ensure_ascii=False, separators=(",", ":")),
                    proof_hash,
                    block["block_index"],
                ),
            )
            conn.commit()

        return jsonify({
            "status": "success",
            "session_id": session_id,
            "certificate_id": certificate_id,
            "proof_hash": proof_hash,
            "block_index": block["block_index"],
            "verified_at": verified_at,
            **record,
        })
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "error": "Duplicate session_id"}), 409
    except Exception as exc:
        return jsonify({"status": "error", "error": str(exc)}), 400


@app.get("/api/dashboard")
def dashboard():
    records = latest_records(limit=12)
    latest = records[0] if records else None

    totals = {
        "sessions": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "local_energy_j": 0.0,
        "cloud_energy_j": 0.0,
        "avoided_carbon_g": 0.0,
    }
    with connect_db() as conn:
        rows = conn.execute("SELECT payload_json FROM impact_sessions").fetchall()
    for row in rows:
        payload = json.loads(row["payload_json"])
        totals["sessions"] += 1
        totals["input_tokens"] += int(payload.get("input_tokens", 0))
        totals["output_tokens"] += int(payload.get("output_tokens", 0))
        totals["total_tokens"] += int(payload.get("total_tokens", 0))
        totals["local_energy_j"] += float(payload.get("local_energy_j", 0))
        totals["cloud_energy_j"] += float(payload.get("cloud_energy_j", 0))
        totals["avoided_carbon_g"] += float(payload.get("net_avoided_g", 0))

    live, age, source_name = current_source_state()
    methodology = load_methodology()

    return jsonify({
        "status": "ok",
        "source_live": live,
        "source_last_seen_seconds": age,
        "source_name": source_name,
        "latest": latest,
        "history": records,
        "totals": totals,
        "chain": {
            "name": "GreenByte Ledger PoC",
            "mode": "single-node hash chain / no gas token",
            "height": ledger.height(),
            "valid": ledger.verify(),
        },
        "methodology": {
            "version": METHODOLOGY_VERSION,
            "acu_definition": methodology["acu_definition"],
        },
    })


@app.get("/api/certificate/<certificate_id>")
def certificate(certificate_id):
    with connect_db() as conn:
        row = conn.execute(
            "SELECT * FROM impact_sessions WHERE certificate_id = ?", (certificate_id,)
        ).fetchone()
    if not row:
        return jsonify({"status": "error", "error": "certificate not found"}), 404
    return jsonify({"status": "success", "record": row_to_record(row), "ledger_valid": ledger.verify()})


@app.get("/api/chain/verify")
def chain_verify():
    return jsonify({"status": "ok", "valid": ledger.verify(), "height": ledger.height()})


@app.get("/api/chain")
def chain_blocks():
    limit = min(100, max(1, int(request.args.get("limit", 25))))
    return jsonify({"status": "ok", "blocks": ledger.blocks(limit=limit), "valid": ledger.verify()})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
