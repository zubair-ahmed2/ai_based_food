from config import OPENAI_API_KEY
from openai import OpenAI

def get_openai_client():
    return OpenAI(api_key=OPENAI_API_KEY)

def generate_food_recommendation(prompt: str) -> str:
    client = get_openai_client()
    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that provides food recommendations based on the user selected vegetables and ingredients."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content
