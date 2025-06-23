import os
import openai
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def classify_incident(text):
    messages = [
        {"role": "system", "content": "You are a cybersecurity analyst. Respond in JSON with: threat_type, sector_affected, geo_location, cve_list, threat_actor, is_critical."},
        {"role": "user", "content": text}
    ]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=300,
            temperature=0.2
        )
        result = response['choices'][0]['message']['content']
        return eval(result) if isinstance(result, str) else result
    except Exception as e:
        print(f"[GPT Error] {e}")
        return {}
