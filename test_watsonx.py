import os
from dotenv import load_dotenv
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

load_dotenv()

API_KEY = os.getenv("WATSONX_API_KEY")
PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
URL = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")

if not API_KEY or not PROJECT_ID:
    print("Error: Missing credentials in .env")
    exit(1)

credentials = Credentials(url=URL, api_key=API_KEY)

model = ModelInference(
    model_id="ibm/granite-4-h-small",
    credentials=credentials,
    project_id=PROJECT_ID,
    params={
        "decoding_method": "greedy",
        "max_new_tokens": 100,
        "min_new_tokens": 1
    }
)

prompt = "Hello! Tell me in one sentence what LearnMate AI can do."
print(f"Sending prompt: {prompt}\n")

# Request full details to see token counts and generated text
result = model.generate(prompt=prompt)

generated_text = ""
if "results" in result and len(result["results"]) > 0:
    generated_text = result["results"][0].get("generated_text", "")

print("Watsonx connection successful!")
print("Response from IBM Granite:")
print("-" * 40)
print(generated_text.strip() if generated_text else f"[Empty text returned. Full response: {result}]")
print("-" * 40)
