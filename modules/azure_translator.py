import requests
import os

AZURE_TRANSLATOR_KEY = os.getenv("ATRANS_API_KEY")
AZURE_TRANSLATOR_REGION = os.getenv("ATRANS_REGION", "global")
AZURE_TRANSLATOR_ENDPOINT = os.getenv("ATRANS_ENDPOINT", "https://api.cognitive.microsofttranslator.com/translate?api-version=3.0")

def translate_text(text, to_language="en"):
    if not AZURE_TRANSLATOR_KEY:
        return text  # Fallback: no translation
    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_TRANSLATOR_KEY,
        "Ocp-Apim-Subscription-Region": AZURE_TRANSLATOR_REGION,
        "Content-type": "application/json",
    }
    params = {"to": to_language}
    body = [{"text": text}]
    try:
        response = requests.post(AZURE_TRANSLATOR_ENDPOINT, headers=headers, params=params, json=body, timeout=10)
        result = response.json()
        return result[0]["translations"][0]["text"]
    except Exception as e:
        print(f"[Translation ERROR] {e}")
        return text
