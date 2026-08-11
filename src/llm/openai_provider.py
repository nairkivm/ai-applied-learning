from .base import LLMProvider
from config import OPENAI_API_KEY, OPENAI_BASE_URL


from openai import OpenAI

client = OpenAI(
    api_key=OPENAI_API_KEY, 
    base_url=OPENAI_BASE_URL
)

class OpenAIProvider(LLMProvider):

    def chat(self, prompt):
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content