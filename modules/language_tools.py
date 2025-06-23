# modules/language_tools.py

from langdetect import detect
import logging
from modules.azure_translator import translate_text as azure_translate

def detect_language(text):
    try:
        return detect(text)
    except Exception as e:
        logging.warning(f"[Language Detection] Failed to detect language for: {text} — {e}")
        return "en"

def translate_text(text, lang):
    if lang == "en":
        return text
    return azure_translate(text)
