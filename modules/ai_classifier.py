import os
import json
import logging
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Standard category list
CATEGORIES = [
    "Ransomware",
    "Phishing",
    "DDoS",
    "Data Breach",
    "Malware",
    "Insider Threat",
    "Zero-Day Exploit",
    "Nation-State Attack",
    "Supply Chain Attack",
    "Vulnerability Disclosure",
    "Cyber Espionage",
    "Hacktivism",
    "Account Takeover",
    "General Cyber Threat"
]

# GPT system prompt
SYSTEM_PROMPT = (
    "You are a cybersecurity analyst. You will receive a news headline. "
    "Your job is to classify whether it is related to a cyberattack or not. "
    f"If it is, assign it to one of the following categories:\n{CATEGORIES}\n"
    "Respond strictly in JSON format:\n"
    "{\"is_cyber_attack\": true/false, \"category\": \"<category>\", \"confidence\": 0-100}"
)

def classify_headline(headline: str) -> dict:
    """
    Uses OpenAI GPT-3.5 to classify a news headline.
    Returns structured JSON dict.
    """
    try:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Classify this headline: {headline}"}
        ]

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.2,
            max_tokens=150
        )

        gpt_reply = response.choices[0].message.content.strip()
        return json.loads(gpt_reply)

    except Exception as e:
        logging.error(f"[GPT Error] Failed to classify headline:\n{headline}\nError: {e}")
        return {
            "is_cyber_attack": False,
            "category": "General Cyber Threat",
            "confidence": 0
        }
