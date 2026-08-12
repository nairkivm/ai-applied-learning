import sys

from chat import Conversation
from llm.factory import create_provider


def chat_with_terminal(provider=None, input_func=input, output_func=print, system_prompt="Kamu adalah asisten AI yang membantu menjawab pertanyaan."):
    provider = provider or create_provider("deepseek")

    # Inisialisasi Conversation untuk mengelola riwayat percakapan
    conversation = Conversation(system_prompt=system_prompt, max_messages=20)

    output_func("=== Chat Terminal ===")
    output_func("Ketik 'exit' untuk keluar, 'clear' untuk menghapus riwayat, 'history' untuk melihat riwayat.")

    while True:
        try:
            user_input = input_func("Anda: ")
        except EOFError:
            output_func("\nSesi selesai.")
            break

        if not user_input.strip():
            continue

        command = user_input.strip().lower()

        if command in {"exit", "quit", "keluar"}:
            output_func("Chat selesai.")
            break

        if command == "clear":
            conversation.clear()
            output_func("Asisten: Riwayat percakapan dihapus. System prompt tetap dipertahankan.")
            continue

        if command == "history":
            messages = conversation.get_messages()
            output_func(f"--- Riwayat ({len(messages)} pesan) ---")
            for msg in messages:
                output_func(f"[{msg['role']}] {msg['content'][:80]}{'...' if len(msg['content']) > 80 else ''}")
            output_func("---")
            continue

        # Tambahkan pesan user ke conversation
        conversation.add_user_message(user_input.strip())

        try:
            # Kirim seluruh riwayat percakapan ke provider
            response = provider.chat(messages=conversation.get_messages())
        except Exception as exc:
            response = f"Error: {exc}"

        # Tambahkan respons assistant ke conversation
        conversation.add_assistant_message(response)

        output_func(f"Asisten: {response}")


def main():
    provider_name = sys.argv[1] if len(sys.argv) > 1 else "deepseek"
    
    try:
        provider = create_provider(provider_name)
    except Exception as exc:
        print(f"Provider tidak tersedia: {exc}")
        return

    chat_with_terminal(provider=provider)


if __name__ == "__main__":
    main()