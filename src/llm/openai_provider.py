from .base import LLMProvider
from config import OPENAI_API_KEY, OPENAI_BASE_URL


class OpenAIProvider(LLMProvider):

    def chat(self, prompt: str = "", system_prompt: str | None = None, temperature: float = 0.2, model: str = "gpt-3.5-turbo", messages: list[dict] | None = None):
        if not OPENAI_API_KEY:
            return f"[Demo Mode] {prompt or (messages[-1]['content'] if messages else '')}"

        try:
            from openai import OpenAI
        except ImportError:
            return f"[Demo Mode] {prompt or (messages[-1]['content'] if messages else '')}"

        client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

        if messages is None:
            messages = [{"role": "user", "content": prompt}]
            if system_prompt:
                messages.insert(0, {"role": "system", "content": system_prompt})

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content