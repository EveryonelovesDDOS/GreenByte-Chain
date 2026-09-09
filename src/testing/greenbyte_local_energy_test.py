import csv
import statistics
import subprocess
import threading
import time
from datetime import datetime

from ollama import Client


# ============================================================
# GREENBYTE LOCAL ENERGY BENCHMARK
# ============================================================

MODEL = "qwen3:1.7b"
PROMPT = "How are you?"

MAX_OUTPUT_TOKENS = 50
TEMPERATURE = 0

# 正式测试跑 5 次
RUNS = 5

# 测量 idle GPU baseline
BASELINE_SECONDS = 5

client = Client(
    host="http://localhost:11434"
)


# ============================================================
# NVIDIA GPU POWER SAMPLER
# ============================================================

def start_power_sampler():
    """
    Continuously reads NVIDIA GPU power draw using nvidia-smi.
    Returns:
        process
        thread
        samples
        stop_event

    samples format:
        [(timestamp, watts), ...]
    """

    samples = []
    stop_event = threading.Event()

    command = [
        "nvidia-smi",
        "--query-gpu=power.draw",
        "--format=csv,noheader,nounits",
        "-lms",
        "100",
    ]

    creation_flags = 0

    if hasattr(subprocess, "CREATE_NO_WINDOW"):
        creation_flags = subprocess.CREATE_NO_WINDOW

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
        creationflags=creation_flags,
    )

    def reader():
        while not stop_event.is_set():

            line = process.stdout.readline()

            if not line:
                break

            try:
                watts = float(line.strip())

                samples.append(
                    (
                        time.perf_counter(),
                        watts
                    )
                )

            except ValueError:
                pass

    thread = threading.Thread(
        target=reader,
        daemon=True
    )

    thread.start()

    return process, thread, samples, stop_event


def stop_power_sampler(
    process,
    thread,
    stop_event
):
    stop_event.set()

    try:
        process.terminate()
    except Exception:
        pass

    thread.join(timeout=1)


# ============================================================
# POWER CALCULATIONS
# ============================================================

def samples_between(
    samples,
    start_time,
    end_time
):
    return [
        (t, p)
        for t, p in samples
        if start_time <= t <= end_time
    ]


def integrate_energy(
    samples,
    duration
):
    """
    Integrate power over time.

    Power (W) × Time (s)
    = Energy (J)
    """

    if not samples:
        return 0

    if len(samples) == 1:
        return samples[0][1] * duration

    energy_j = 0

    for i in range(
        1,
        len(samples)
    ):

        t1, p1 = samples[i - 1]
        t2, p2 = samples[i]

        dt = t2 - t1

        # Trapezoidal integration
        average_power = (
            p1 + p2
        ) / 2

        energy_j += (
            average_power
            * dt
        )

    # If sampling covers slightly less
    # than the full inference duration,
    # fill using average observed power.

    sampled_duration = (
        samples[-1][0]
        -
        samples[0][0]
    )

    remaining = max(
        0,
        duration
        -
        sampled_duration
    )

    average_power = statistics.mean(
        [p for _, p in samples]
    )

    energy_j += (
        average_power
        * remaining
    )

    return energy_j


# ============================================================
# STEP 1 — WARM UP MODEL
# ============================================================

print()
print("=" * 60)
print("GREENBYTE LOCAL ENERGY BENCHMARK")
print("=" * 60)

print()
print("Model:", MODEL)
print("Prompt:", PROMPT)
print("Runs:", RUNS)

print()
print("Warming up model...")

client.chat(
    model=MODEL,

    messages=[
        {
            "role": "user",
            "content": "Hello"
        }
    ],

    stream=False,
    think=False,

    options={
        "num_predict": 10,
        "temperature": 0
    }
)

print("Warm-up complete.")


# ============================================================
# STEP 2 — MEASURE IDLE GPU POWER
# ============================================================

print()
print("=" * 60)
print("MEASURING GPU IDLE BASELINE")
print("=" * 60)

process, thread, baseline_samples, stop_event = (
    start_power_sampler()
)

time.sleep(
    BASELINE_SECONDS
)

stop_power_sampler(
    process,
    thread,
    stop_event
)

baseline_watts = statistics.mean(
    [
        p
        for _, p
        in baseline_samples
    ]
)

print(
    "Average idle GPU power:",
    round(baseline_watts, 3),
    "W"
)


# ============================================================
# STEP 3 — RUN BENCHMARK
# ============================================================

results = []

for run_number in range(
    1,
    RUNS + 1
):

    print()
    print("=" * 60)
    print(
        f"RUN {run_number}/{RUNS}"
    )
    print("=" * 60)

    process, thread, power_samples, stop_event = (
        start_power_sampler()
    )

    # Let nvidia-smi start sampling
    time.sleep(0.25)

    inference_start = (
        time.perf_counter()
    )

    response = client.chat(
        model=MODEL,

        messages=[
            {
                "role": "user",
                "content": PROMPT
            }
        ],

        stream=False,

        # Disable Qwen thinking
        think=False,

        options={
            "num_predict":
                MAX_OUTPUT_TOKENS,

            "temperature":
                TEMPERATURE
        }
    )

    inference_end = (
        time.perf_counter()
    )

    wall_time = (
        inference_end
        -
        inference_start
    )

    time.sleep(0.2)

    stop_power_sampler(
        process,
        thread,
        stop_event
    )

    inference_samples = (
        samples_between(
            power_samples,
            inference_start,
            inference_end
        )
    )

    powers = [
        p
        for _, p
        in inference_samples
    ]

    if powers:

        avg_gpu_power = (
            statistics.mean(
                powers
            )
        )

        peak_gpu_power = max(
            powers
        )

    else:

        avg_gpu_power = 0
        peak_gpu_power = 0


    # --------------------------------------------------------
    # Gross GPU energy
    # --------------------------------------------------------

    gross_gpu_energy_j = (
        integrate_energy(
            inference_samples,
            wall_time
        )
    )


    # --------------------------------------------------------
    # Energy GPU would have consumed anyway
    # while idle
    # --------------------------------------------------------

    baseline_energy_j = (
        baseline_watts
        *
        wall_time
    )


    # --------------------------------------------------------
    # Incremental inference energy
    # --------------------------------------------------------

    net_gpu_energy_j = max(
        0,
        gross_gpu_energy_j
        -
        baseline_energy_j
    )


    # --------------------------------------------------------
    # Ollama telemetry
    # --------------------------------------------------------

    input_tokens = (
        response.prompt_eval_count
        or 0
    )

    output_tokens = (
        response.eval_count
        or 0
    )

    total_tokens = (
        input_tokens
        +
        output_tokens
    )


    ollama_duration = (
        (
            response.total_duration
            or 0
        )
        /
        1_000_000_000
    )


    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    print()
    print("AI RESPONSE")
    print("-" * 60)

    print(
        response.message.content
    )

    print()
    print("TOKEN TELEMETRY")
    print("-" * 60)

    print(
        "Input tokens :",
        input_tokens
    )

    print(
        "Output tokens:",
        output_tokens
    )

    print(
        "Total tokens :",
        total_tokens
    )


    print()
    print("POWER TELEMETRY")
    print("-" * 60)

    print(
        "Idle GPU power       :",
        round(
            baseline_watts,
            3
        ),
        "W"
    )

    print(
        "Average GPU power    :",
        round(
            avg_gpu_power,
            3
        ),
        "W"
    )

    print(
        "Peak GPU power       :",
        round(
            peak_gpu_power,
            3
        ),
        "W"
    )


    print()
    print("ENERGY")
    print("-" * 60)

    print(
        "Gross GPU energy     :",
        round(
            gross_gpu_energy_j,
            3
        ),
        "J"
    )

    print(
        "Baseline energy      :",
        round(
            baseline_energy_j,
            3
        ),
        "J"
    )

    print(
        "Net inference energy :",
        round(
            net_gpu_energy_j,
            3
        ),
        "J"
    )


    print()
    print("TIMING")
    print("-" * 60)

    print(
        "Ollama duration:",
        round(
            ollama_duration,
            4
        ),
        "s"
    )

    print(
        "Wall time:",
        round(
            wall_time,
            4
        ),
        "s"
    )


    # --------------------------------------------------------
    # Observed energy metrics
    # --------------------------------------------------------

    energy_per_output_token = (
        net_gpu_energy_j
        /
        output_tokens
        if output_tokens
        else 0
    )

    energy_per_total_token = (
        net_gpu_energy_j
        /
        total_tokens
        if total_tokens
        else 0
    )


    print()
    print("OBSERVED ENERGY INTENSITY")
    print("-" * 60)

    print(
        "J / output token:",
        round(
            energy_per_output_token,
            4
        )
    )

    print(
        "J / total token :",
        round(
            energy_per_total_token,
            4
        )
    )


    results.append({

        "run":
            run_number,

        "timestamp":
            datetime.now().isoformat(),

        "provider":
            "Ollama Local",

        "model":
            MODEL,

        "prompt":
            PROMPT,

        "input_tokens":
            input_tokens,

        "output_tokens":
            output_tokens,

        "total_tokens":
            total_tokens,

        "ollama_duration_s":
            ollama_duration,

        "wall_time_s":
            wall_time,

        "baseline_gpu_w":
            baseline_watts,

        "average_gpu_w":
            avg_gpu_power,

        "peak_gpu_w":
            peak_gpu_power,

        "gross_gpu_energy_j":
            gross_gpu_energy_j,

        "baseline_energy_j":
            baseline_energy_j,

        "net_gpu_energy_j":
            net_gpu_energy_j,

        "j_per_output_token":
            energy_per_output_token,

        "j_per_total_token":
            energy_per_total_token
    })


# ============================================================
# STEP 4 — SUMMARY
# ============================================================

print()
print("=" * 60)
print("GREENBYTE BENCHMARK SUMMARY")
print("=" * 60)

net_energies = [
    r["net_gpu_energy_j"]
    for r in results
]

wall_times = [
    r["wall_time_s"]
    for r in results
]

average_powers = [
    r["average_gpu_w"]
    for r in results
]


print()
print(
    "Average net GPU energy:",
    round(
        statistics.mean(
            net_energies
        ),
        3
    ),
    "J"
)

print(
    "Median net GPU energy :",
    round(
        statistics.median(
            net_energies
        ),
        3
    ),
    "J"
)

if len(
    net_energies
) > 1:

    print(
        "Energy std deviation :",
        round(
            statistics.stdev(
                net_energies
            ),
            3
        ),
        "J"
    )


print(
    "Average inference time:",
    round(
        statistics.mean(
            wall_times
        ),
        4
    ),
    "s"
)

print(
    "Average GPU power:",
    round(
        statistics.mean(
            average_powers
        ),
        3
    ),
    "W"
)


# ============================================================
# STEP 5 — SAVE CSV
# ============================================================

csv_file = (
    "greenbyte_local_benchmark.csv"
)

with open(
    csv_file,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=results[0].keys()
    )

    writer.writeheader()

    writer.writerows(
        results
    )


print()
print(
    "Benchmark saved to:",
    csv_file
)

print()
print("=" * 60)
print("IMPORTANT")
print("=" * 60)

print(
    "This is GPU telemetry-derived incremental energy."
)

print(
    "It does NOT yet represent total laptop wall energy."
)

print(
    "A physical wall power meter is preferred for final validation."
)