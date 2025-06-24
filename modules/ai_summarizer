# ==== Module Imports ====
import openai
import logging

# ==== Summarize Article Content ====
def summarize_content(content):
    if not content.strip():
        logging.warning("No content to summarize.")
        return ""

    try:
        prompt = (
            "You are a cybersecurity analyst. Summarize the following article "
            "in 3–4 concise sentences, focusing on the security incident, impact, and threat context:\n\n"
            f"{content[:4000]}"  # Limit token usage
        )

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a cybersecurity analyst summarizing incidents."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )

        summary = response.choices[0].message.content.strip()
        return summary

    except Exception as e:
        logging.error(f"Failed to summarize content: {e}")
        return ""
