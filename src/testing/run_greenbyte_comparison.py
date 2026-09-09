"""GreenByte Cloud-vs-Local testing runner.

Cloud: Ollama Cloud / DeepSeek V4 Flash
Local: Ollama Local / Qwen3 1.7B on the laptop

This is intentionally a TESTING pipeline. Local GPU energy is derived from
NVIDIA power telemetry. Cloud energy is a configurable demo estimate, not an
Ollama-provided measurement.
"""

from __future__ import annotations

import os
import statistics
import subprocess
import threading
import time
from typing import Any

import requests
from ollama import Client

GREENBYTE_API = os.getenv("GREENBYTE_API", "http://127.0.0.1:5000")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")

LOCAL_MODEL = os.getenv("GREENBYTE_LOCAL_MODEL", "qwen3:1.7b")
CLOUD_MODEL = os.getenv("GREENBYTE_CLOUD_MODEL", "deepseek-v4-flash:cloud")
PROMPT = os.getenv("GREENBYTE_TEST_PROMPT", "How are you?")
MAX_OUTPUT = int(os.getenv("GREENBYTE_MAX_OUTPUT", "50"))
TEMPERATURE = float(os.getenv("GREENBYTE_TEMPERATURE", "0"))

# Testing defaults only. These are deliberately configurable.
CLOUD_ALPHA_J = float(os.getenv("GREENBYTE_CLOUD_ALPHA_J", "250"))
CLOUD_BETA_INPUT_J = float(os.getenv("GREENBYTE_CLOUD_BETA_INPUT_J", "2"))
CLOUD_BETA_OUTPUT_J = float(os.getenv("GREENBYTE_CLOUD_BETA_OUTPUT_J", "7"))
CLOUD_PUE = float(os.getenv("GREENBYTE_CLOUD_PUE", "1.10"))
CLOUD_CI = float(os.getenv("GREENBYTE_CLOUD_CI", "400"))
LOCAL_CI = float(os.getenv("GREENBYTE_LOCAL_CI", "200"))

BASELINE_SECONDS = float(os.getenv("GREENBYTE_IDLE_SECONDS", "3"))
SAMPLE_MS = int(os.getenv("GREENBYTE_SAMPLE_MS", "100"))


if not OLLAMA_API_KEY:
    raise RuntimeError(
        "OLLAMA_API_KEY is not set. In PowerShell use: "
        "$env:OLLAMA_API_KEY='YOUR_NEW_KEY'"
    )

local_client = Client(host="http://localhost:11434")
cloud_client = Client(
    host="https://ollama.com",
    headers={"Authorization": f"Bearer {OLLAMA_API_KEY}"},
)


def start_power_sampler():
    samples: list[tuple[float, float]] = []
    stop_event = threading.Event()

    command = [
        "nvidia-smi",
        "--query-gpu=power.draw",
        "--format=csv,noheader,nounits",
        "-lms",
        str(SAMPLE_MS),
    ]

    creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
        creationflags=creation_flags,
    )

    def reader():
        assert process.stdout is not None
        while not stop_event.is_set():
            line = process.stdout.readline()
            if not line:
                break
            try:
                samples.append((time.perf_counter(), float(line.strip())))
            except ValueError:
                pass

    thread = threading.Thread(target=reader, daemon=True)
    thread.start()
    return process, thread, samples, stop_event


def stop_power_sampler(process, thread, stop_event):
    stop_event.set()
    try:
        process.terminate()
    except Exception:
        pass
    thread.join(timeout=1)


def integrate_energy(samples: list[tuple[float, float]], duration: float) -> float:
    if not samples:
        return 0.0
    if len(samples) == 1:
        return samples[0][1] * duration

    energy = 0.0
    for (t1, p1), (t2, p2) in zip(samples, samples[1:]):
        energy += ((p1 + p2) / 2.0) * max(0.0, t2 - t1)

    sampled_duration = max(0.0, samples[-1][0] - samples[0][0])
    remaining = max(0.0, duration - sampled_duration)
    energy += statistics.mean(p for _, p in samples) * remaining
    return energy


def measure_idle_gpu_power() -> float:
    process, thread, samples, stop_event = start_power_sampler()
    time.sleep(BASELINE_SECONDS)
    stop_power_sampler(process, thread, stop_event)
    powers = [p for _, p in samples]
    if not powers:
        raise RuntimeError("Could not read NVIDIA GPU power via nvidia-smi")
    return statistics.mean(powers)


def warm_local_model():
    local_client.chat(
        model=LOCAL_MODEL,
        messages=[{"role": "user", "content": "Hello"}],
        stream=False,
        think=False,
        options={"num_predict": 8, "temperature": 0},
    )


def run_local(idle_watts: float) -> dict[str, Any]:
    process, thread, samples, stop_event = start_power_sampler()
    time.sleep(0.25)

    start = time.perf_counter()
    response = local_client.chat(
        model=LOCAL_MODEL,
        messages=[{"role": "user", "content": PROMPT}],
        stream=False,
        think=False,
        options={"num_predict": MAX_OUTPUT, "temperature": TEMPERATURE},
    )
    end = time.perf_counter()
    time.sleep(0.2)
    stop_power_sampler(process, thread, stop_event)

    duration = end - start
    inference_samples = [(t, p) for t, p in samples if start <= t <= end]
    powers = [p for _, p in inference_samples]
    avg_power = statistics.mean(powers) if powers else 0.0
    peak_power = max(powers) if powers else 0.0
    gross_energy = integrate_energy(inference_samples, duration)
    baseline_energy = idle_watts * duration
    net_energy = max(0.0, gross_energy - baseline_energy)

    input_tokens = int(response.prompt_eval_count or 0)
    output_tokens = int(response.eval_count or 0)

    return {
        "provider": "Ollama Local",
        "model": LOCAL_MODEL,
        "response": response.message.content,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "duration_s": duration,
        "ollama_duration_s": float(response.total_duration or 0) / 1_000_000_000,
        "idle_gpu_w": idle_watts,
        "average_gpu_w": avg_power,
        "peak_gpu_w": peak_power,
        "gross_gpu_energy_j": gross_energy,
        "baseline_gpu_energy_j": baseline_energy,
        "net_gpu_energy_j": net_energy,
    }


def run_cloud() -> dict[str, Any]:
    start = time.perf_counter()
    response = cloud_client.chat(
        model=CLOUD_MODEL,
        messages=[{"role": "user", "content": PROMPT}],
        stream=False,
        think=False,
        options={"num_predict": MAX_OUTPUT, "temperature": TEMPERATURE},
    )
    duration = time.perf_counter() - start

    input_tokens = int(response.prompt_eval_count or 0)
    output_tokens = int(response.eval_count or 0)
    total_tokens = input_tokens + output_tokens

    # TEST-ONLY energy estimator. Ollama Cloud does not provide Joules.
    estimated_energy_j = (
        CLOUD_ALPHA_J
        + CLOUD_BETA_INPUT_J * input_tokens
        + CLOUD_BETA_OUTPUT_J * output_tokens
    )

    return {
        "provider": "Ollama Cloud",
        "model": CLOUD_MODEL,
        "response": response.message.content,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "duration_s": duration,
        "ollama_duration_s": float(response.total_duration or 0) / 1_000_000_000,
        "estimated_energy_j": estimated_energy_j,
    }


def send_to_greenbyte(local: dict[str, Any], cloud: dict[str, Any]) -> dict[str, Any]:
    requests.post(
        f"{GREENBYTE_API}/api/source/heartbeat",
        json={
            "source_id": "laptop-local-ai-testing",
            "source_name": "Laptop Local AI Test",
        },
        timeout=10,
    ).raise_for_status()

    payload = {
        "source_id": "laptop-local-ai-testing",
        "source_name": "Laptop Local AI Test",
        "prompt_preview": PROMPT,
        "model": local["model"],
        "device": "NVIDIA RTX 4050 Laptop GPU",
        "energy_source": "Laptop grid electricity - testing",
        "input_tokens": local["input_tokens"],
        "output_tokens": local["output_tokens"],
        "local_energy_j": round(local["net_gpu_energy_j"], 6),
        "local_duration_s": round(local["duration_s"], 6),
        "local_average_gpu_w": round(local["average_gpu_w"], 6),
        "local_peak_gpu_w": round(local["peak_gpu_w"], 6),
        "local_measurement_origin": "NVIDIA GPU telemetry-derived incremental energy (testing)",
        "local_carbon_intensity_g_per_kwh": LOCAL_CI,
        "cloud_energy_j": round(cloud["estimated_energy_j"], 6),
        "cloud_provider": cloud["provider"],
        "cloud_model": cloud["model"],
        "cloud_input_tokens": cloud["input_tokens"],
        "cloud_output_tokens": cloud["output_tokens"],
        "cloud_total_tokens": cloud["total_tokens"],
        "cloud_duration_s": round(cloud["duration_s"], 6),
        "cloud_energy_origin": "Testing-only token workload energy estimator",
        "baseline_origin": "Ollama Cloud DeepSeek V4 Flash - testing-only estimated energy",
        "cloud_pue": CLOUD_PUE,
        "cloud_carbon_intensity_g_per_kwh": CLOUD_CI,
        "verification_overhead_g": 0,
    }

    response = requests.post(
        f"{GREENBYTE_API}/api/inference-report",
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def main():
    print("\n" + "=" * 68)
    print("GREENBYTE CLOUD vs LOCAL TEST")
    print("=" * 68)
    print("Prompt:", PROMPT)
    print("Local :", LOCAL_MODEL)
    print("Cloud :", CLOUD_MODEL)

    print("\n[1/5] Warming local model...")
    warm_local_model()

    print("[2/5] Measuring idle GPU baseline...")
    idle_watts = measure_idle_gpu_power()
    print(f"      Idle GPU power: {idle_watts:.3f} W")

    print("[3/5] Running local AI with NVIDIA power telemetry...")
    local = run_local(idle_watts)
    print(
        f"      Local: {local['input_tokens']} in / {local['output_tokens']} out, "
        f"{local['net_gpu_energy_j']:.3f} J net GPU energy, "
        f"{local['duration_s']:.4f} s"
    )

    print("[4/5] Running Ollama Cloud DeepSeek V4...")
    cloud = run_cloud()
    print(
        f"      Cloud: {cloud['input_tokens']} in / {cloud['output_tokens']} out, "
        f"{cloud['estimated_energy_j']:.3f} J ESTIMATED, "
        f"{cloud['duration_s']:.4f} s"
    )

    print("[5/5] Sending comparison to GreenByte backend...")
    result = send_to_greenbyte(local, cloud)

    print("\n" + "=" * 68)
    print("GREENBYTE IMPACT RESULT")
    print("=" * 68)
    print(f"Cloud carbon : {result['cloud_carbon_g']:.6f} g CO2e  [ESTIMATED]")
    print(f"Local carbon : {result['local_carbon_g']:.6f} g CO2e  [GPU TELEMETRY]")
    print(f"Net avoided  : {result['net_avoided_g']:.6f} g CO2e")
    print(f"Reduction    : {result['reduction_pct']:.2f}%")
    print(f"ACU          : {result['net_avoided_g']:.6f}")
    print(f"Certificate  : {result['certificate_id']}")
    print(f"Ledger block : #{result['block_index']}")
    print("\nDashboard should update automatically within about 2 seconds.")
    print("\nTESTING NOTICE:")
    print("- Local energy = NVIDIA GPU incremental energy only.")
    print("- Cloud energy = demo estimate, not measured by Ollama Cloud.")


if __name__ == "__main__":
    main()
