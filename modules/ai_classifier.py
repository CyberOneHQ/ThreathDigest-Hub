import os
import openai
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def classify_article(text):
    messages = [
        {"role": "system", "content": "You are a cybersecurity analyst. Return JSON with: threat_type, geo_location, threat_actor, cve_list, sector, is_critical."},
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
