import time
from ollama import Client

# ======================================
# GREENBYTE LOCAL AI TEST
# ======================================

client = Client(
    host="http://localhost:11434"
)

MODEL = "qwen3:1.7b"
PROMPT = "How are you?"


print("\n==============================")
print("GREENBYTE LOCAL AI TEST")
print("==============================")

print("\nProvider:")
print("Ollama Local")

print("\nModel:")
print(MODEL)

print("\nPrompt:")
print(PROMPT)

print("\nRunning local inference...")


# ======================================
# Run Local AI
# ======================================

start = time.perf_counter()

response = client.chat(
    model=MODEL,
    messages=[
        {
            "role": "user",
            "content": PROMPT
        }
    ],
    stream=False,

    # Disable Qwen reasoning output
    think=False,

    # Same testing conditions as cloud
    options={
        "num_predict": 50,
        "temperature": 0
    }
)

wall_time = time.perf_counter() - start


# ======================================
# AI Response
# ======================================

print("\n==============================")
print("AI RESPONSE")
print("==============================")

print(response.message.content)


# ======================================
# Token Telemetry
# ======================================

input_tokens = response.prompt_eval_count or 0
output_tokens = response.eval_count or 0
total_tokens = input_tokens + output_tokens


print("\n==============================")
print("TOKEN TELEMETRY")
print("==============================")

print("Input tokens :", input_tokens)
print("Output tokens:", output_tokens)
print("Total tokens :", total_tokens)


# ======================================
# Timing
# ======================================

print("\n==============================")
print("LOCAL TIMING")
print("==============================")

if response.prompt_eval_duration:
    print(
        "Prompt evaluation:",
        round(
            response.prompt_eval_duration / 1_000_000_000,
            4
        ),
        "seconds"
    )

if response.eval_duration:
    print(
        "Generation:",
        round(
            response.eval_duration / 1_000_000_000,
            4
        ),
        "seconds"
    )

if response.total_duration:
    print(
        "Ollama total duration:",
        round(
            response.total_duration / 1_000_000_000,
            4
        ),
        "seconds"
    )

print(
    "Measured wall time:",
    round(wall_time, 4),
    "seconds"
)


# ======================================
# GreenByte Summary
# ======================================

print("\n==============================")
print("GREENBYTE LOCAL TELEMETRY")
print("==============================")

print({
    "provider": "Ollama Local",
    "model": MODEL,
    "prompt": PROMPT,

    "input_tokens": input_tokens,
    "output_tokens": output_tokens,
    "total_tokens": total_tokens,

    "wall_time_seconds": round(
        wall_time,
        4
    )
})