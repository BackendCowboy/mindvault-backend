import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # Load .env file

# Create OpenAI client using key from environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def ask_gpt(prompt: str, model="gpt-3.5-turbo", temperature=0.7) -> str:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error from OpenAI: {e}"
