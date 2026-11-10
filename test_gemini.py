import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("Testing Gemini...", flush=True)

try:
    result = client.interactions.create(
        model="gemini-3.5-flash-lite",
        input="Reply with only OK.",
        generation_config={
            "thinking_level": "low",
            "max_output_tokens": 64,
        },
        timeout=90,
    )

    print("SUCCESS:", result.output_text)

except Exception as e:
    print("ERROR:", type(e).__name__, str(e))