from .base import LLMProvider
from config import OPENAI_API_KEY, OPENAI_BASE_URL


class DeepseekProvider(LLMProvider):

    def chat(self, prompt: str = "", system_prompt: str | None = None, temperature: float = 0.2, model: str = "deepseek-v4-flash", messages: list[dict] | None = None) -> str:
        if not OPENAI_API_KEY:
            return f"[Demo Mode] {prompt or (messages[-1]['content'] if messages else '')}"

        try:
            from openai import OpenAI
        except ImportError:
            return f"[Demo Mode] {prompt or (messages[-1]['content'] if messages else '')}"

        client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

        if messages is None:
            messages = [
                {"role": "system", "content": system_prompt or "Kamu adalah asisten AI yang membantu menjawab pertanyaan."},
                {"role": "user", "content": prompt}
            ]

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content