from .openai_provider import OpenAIProvider
from .ollama_provider import OllamaProvider
from .deepseek_provider import DeepseekProvider


def create_provider(name):
    provider_name = (name or "deepseek").lower()

    if provider_name == "openai":
        return OpenAIProvider()

    if provider_name == "ollama":
        return OllamaProvider()

    if provider_name == "deepseek":
        return DeepseekProvider()

    raise ValueError("Provider tidak dikenali")