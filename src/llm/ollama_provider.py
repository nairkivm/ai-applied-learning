from .base import LLMProvider

class OllamaProvider(LLMProvider):

    def chat(self, prompt):

        return f"[Dummy Ollama] {prompt}"