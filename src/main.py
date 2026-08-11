from llm.factory import create_provider

provider = create_provider("ollama")

print(provider.chat("Halo AI"))