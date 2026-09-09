import os
import time
from ollama import Client

# ==============================
# 1. Read Ollama API Key
# ==============================

api_key = os.environ.get("OLLAMA_API_KEY")

if not api_key:
    raise RuntimeError(
        "OLLAMA_API_KEY not found. "
        "Set it in PowerShell first."
    )


# ==============================
# 2. Connect to Ollama Cloud
# ==============================

client = Client(
    host="https://ollama.com",
    headers={
        "Authorization": f"Bearer {api_key}"
    }
)


# ==============================
# 3. Test Prompt
# ==============================

prompt = "How are you?"

print("\n==============================")
print("GREENBYTE CLOUD TEST")
print("==============================")

print("\nModel:")
print("DeepSeek V4 Flash")

print("\nPrompt:")
print(prompt)

print("\nSending request to Ollama Cloud...")


# ==============================
# 4. Run DeepSeek V4 Flash
# ==============================

start = time.perf_counter()

response = client.chat(
    model="deepseek-v4-flash:cloud",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],
    stream=False,
    think=False,
    options={
        "num_predict": 50,
        "temperature": 0
    }
)

wall_time = time.perf_counter() - start


# ==============================
# 5. AI Response
# ==============================

print("\n==============================")
print("AI RESPONSE")
print("==============================")

print(response.message.content)


# ==============================
# 6. Token Usage
# ==============================

input_tokens = response.prompt_eval_count or 0
output_tokens = response.eval_count or 0
total_tokens = input_tokens + output_tokens


print("\n==============================")
print("TOKEN TELEMETRY")
print("==============================")

print("Input tokens :", input_tokens)
print("Output tokens:", output_tokens)
print("Total tokens :", total_tokens)


# ==============================
# 7. Timing
# ==============================

print("\n==============================")
print("CLOUD TIMING")
print("==============================")

if response.prompt_eval_duration:
    print(
        "Prompt evaluation:",
        round(response.prompt_eval_duration / 1_000_000_000, 4),
        "seconds"
    )

if response.eval_duration:
    print(
        "Generation:",
        round(response.eval_duration / 1_000_000_000, 4),
        "seconds"
    )

if response.total_duration:
    print(
        "Ollama total duration:",
        round(response.total_duration / 1_000_000_000, 4),
        "seconds"
    )

print(
    "Measured wall time:",
    round(wall_time, 4),
    "seconds"
)


# ==============================
# 8. GreenByte Summary
# ==============================

print("\n==============================")
print("GREENBYTE CLOUD TELEMETRY")
print("==============================")

print({
    "provider": "Ollama Cloud",
    "model": "deepseek-v4-flash:cloud",
    "prompt": prompt,
    "input_tokens": input_tokens,
    "output_tokens": output_tokens,
    "total_tokens": total_tokens,
    "wall_time_seconds": round(wall_time, 4)
})