# modules/azure_translator.py
import os
import requests
import logging

AZURE_TRANSLATOR_KEY = os.getenv("ATRANS_API_KEY")
AZURE_TRANSLATOR_REGION = os.getenv("ATRANS_REGION", "global")
AZURE_TRANSLATOR_ENDPOINT = os.getenv("ATRANS_ENDPOINT", "https://api.cognitive.microsofttranslator.com/translate?api-version=3.0")

def translate_text(text, to_language="en"):
    if not AZURE_TRANSLATOR_KEY:
        logging.warning("Azure Translator key not set. Skipping translation.")
        return text

    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_TRANSLATOR_KEY,
        "Ocp-Apim-Subscription-Region": AZURE_TRANSLATOR_REGION,
        "Content-type": "application/json",
    }
    params = {"to": to_language}
    body = [{"text": text}]

    try:
        response = requests.post(
            AZURE_TRANSLATOR_ENDPOINT, headers=headers, params=params, json=body, timeout=10
        )
        result = response.json()
        translated_text = result[0]["translations"][0]["text"]
        logging.info(f"Translated '{text}' → '{translated_text}'")
        return translated_text
    except Exception as e:
        logging.error(f"Translation failed for '{text}': {e}")
        return text  # Fallback to original text
