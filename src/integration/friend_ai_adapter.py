"""Drop-in helper for your friend's Python AI app.

Call heartbeat() when the AI service starts, then call report_inference()
after each completed response. GreenByte receives the telemetry in the
background; the dashboard is read-only.
"""

from __future__ import annotations

import threading
import time
import uuid
from typing import Optional

import requests


class GreenByteReporter:
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:5000",
        source_id: str = "friend-ai-local-01",
        source_name: str = "Friend Local AI",
        heartbeat_seconds: int = 10,
    ):
        self.base_url = base_url.rstrip("/")
        self.source_id = source_id
        self.source_name = source_name
        self.heartbeat_seconds = heartbeat_seconds
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def heartbeat(self):
        response = requests.post(
            f"{self.base_url}/api/source/heartbeat",
            json={"source_id": self.source_id, "source_name": self.source_name},
            timeout=3,
        )
        response.raise_for_status()
        return response.json()

    def start_heartbeat(self):
        if self._thread and self._thread.is_alive():
            return

        def loop():
            while not self._stop.is_set():
                try:
                    self.heartbeat()
                except Exception as exc:
                    print(f"[GreenByte heartbeat] {exc}")
                self._stop.wait(self.heartbeat_seconds)

        self._thread = threading.Thread(target=loop, daemon=True)
        self._thread.start()

    def stop_heartbeat(self):
        self._stop.set()

    def report_inference(
        self,
        *,
        prompt_preview: str,
        model: str,
        device: str,
        energy_source: str,
        input_tokens: int,
        output_tokens: int,
        local_energy_j: float,
        local_measurement_origin: str = "device power telemetry",
        local_carbon_intensity_g_per_kwh: float = 43.0,
        cloud_profile: str = "demo-calibrated-reference",
        cloud_energy_j: Optional[float] = None,
        cloud_pue: Optional[float] = None,
        cloud_carbon_intensity_g_per_kwh: Optional[float] = None,
    ):
        payload = {
            "session_id": f"AI-{uuid.uuid4().hex[:16].upper()}",
            "source_id": self.source_id,
            "source_name": self.source_name,
            "prompt_preview": prompt_preview,
            "model": model,
            "device": device,
            "energy_source": energy_source,
            "input_tokens": int(input_tokens),
            "output_tokens": int(output_tokens),
            "local_energy_j": float(local_energy_j),
            "local_measurement_origin": local_measurement_origin,
            "local_carbon_intensity_g_per_kwh": float(local_carbon_intensity_g_per_kwh),
            "cloud_profile": cloud_profile,
        }
        if cloud_energy_j is not None:
            payload["cloud_energy_j"] = float(cloud_energy_j)
        if cloud_pue is not None:
            payload["cloud_pue"] = float(cloud_pue)
        if cloud_carbon_intensity_g_per_kwh is not None:
            payload["cloud_carbon_intensity_g_per_kwh"] = float(cloud_carbon_intensity_g_per_kwh)

        response = requests.post(
            f"{self.base_url}/api/inference-report",
            json=payload,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    reporter = GreenByteReporter()
    reporter.start_heartbeat()

    # Demo only: replace these values with the ACTUAL values from the AI runtime
    # and your phone energy measurement.
    result = reporter.report_inference(
        prompt_preview="How are you?",
        model="Qwen 1.5B",
        device="Repurposed Android phone",
        energy_source="Solar-powered edge node",
        input_tokens=3,
        output_tokens=20,
        local_energy_j=26.2,
    )
    print(result)
    time.sleep(2)
