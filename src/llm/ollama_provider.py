from .base import LLMProvider


class OllamaProvider(LLMProvider):

    def chat(self, prompt: str = "", system_prompt: str | None = None, temperature: float = 0.2, model: str | None = None, messages: list[dict] | None = None):
        content = prompt or (messages[-1]['content'] if messages else "")
        return f"[Dummy Ollama] {content}"