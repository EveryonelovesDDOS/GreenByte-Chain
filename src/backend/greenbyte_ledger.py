"""GreenByte local ledger PoC.

A deliberately small append-only hash chain for hackathon demonstration.
This is NOT a distributed consensus blockchain. It gives GreenByte a
no-gas, tamper-evident local verification ledger while the team prepares
its multi-validator GreenByte Chain (e.g. Besu/QBFT).
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class GreenByteLedger:
    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        self._init_db()
        self._ensure_genesis()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def canonical(payload: Any) -> str:
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    @staticmethod
    def hash_block(index: int, timestamp: str, previous_hash: str, payload_json: str) -> str:
        raw = f"{index}|{timestamp}|{previous_hash}|{payload_json}".encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def _init_db(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS ledger_blocks (
                    block_index INTEGER PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    previous_hash TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    block_hash TEXT NOT NULL UNIQUE
                )
                """
            )
            conn.commit()

    def _ensure_genesis(self):
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS c FROM ledger_blocks").fetchone()
            if int(row["c"]) > 0:
                return
            timestamp = datetime.now(timezone.utc).isoformat()
            payload = {
                "type": "GENESIS",
                "network": "GreenByte Ledger PoC",
                "notice": "Single-node hash-chain prototype; no cryptocurrency and no gas token.",
            }
            payload_json = self.canonical(payload)
            block_hash = self.hash_block(0, timestamp, "0" * 64, payload_json)
            conn.execute(
                "INSERT INTO ledger_blocks(block_index,timestamp,previous_hash,payload_json,block_hash) VALUES(?,?,?,?,?)",
                (0, timestamp, "0" * 64, payload_json, block_hash),
            )
            conn.commit()

    def append(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self._connect() as conn:
            previous = conn.execute(
                "SELECT * FROM ledger_blocks ORDER BY block_index DESC LIMIT 1"
            ).fetchone()
            index = int(previous["block_index"]) + 1
            previous_hash = str(previous["block_hash"])
            timestamp = datetime.now(timezone.utc).isoformat()
            payload_json = self.canonical(payload)
            block_hash = self.hash_block(index, timestamp, previous_hash, payload_json)
            conn.execute(
                "INSERT INTO ledger_blocks(block_index,timestamp,previous_hash,payload_json,block_hash) VALUES(?,?,?,?,?)",
                (index, timestamp, previous_hash, payload_json, block_hash),
            )
            conn.commit()
            return {
                "block_index": index,
                "timestamp": timestamp,
                "previous_hash": previous_hash,
                "block_hash": block_hash,
                "payload": payload,
            }

    def height(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT MAX(block_index) AS h FROM ledger_blocks").fetchone()
            return int(row["h"] or 0)

    def verify(self) -> bool:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM ledger_blocks ORDER BY block_index ASC").fetchall()
        expected_previous = "0" * 64
        for expected_index, row in enumerate(rows):
            if int(row["block_index"]) != expected_index:
                return False
            if str(row["previous_hash"]) != expected_previous:
                return False
            recalculated = self.hash_block(
                int(row["block_index"]),
                str(row["timestamp"]),
                str(row["previous_hash"]),
                str(row["payload_json"]),
            )
            if recalculated != str(row["block_hash"]):
                return False
            expected_previous = str(row["block_hash"])
        return True

    def blocks(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM ledger_blocks ORDER BY block_index DESC LIMIT ?", (int(limit),)
            ).fetchall()
        result = []
        for row in rows:
            result.append({
                "block_index": int(row["block_index"]),
                "timestamp": str(row["timestamp"]),
                "previous_hash": str(row["previous_hash"]),
                "block_hash": str(row["block_hash"]),
                "payload": json.loads(row["payload_json"]),
            })
        return result
