class LLMProvider:

    def chat(self, prompt: str = "", system_prompt: str | None = None, temperature: float = 0.2, model: str = "", messages: list[dict] | None = None):
        """Kirim percakapan ke LLM.

        Gunakan `messages` (daftar dict dengan role+content) untuk mengirim seluruh riwayat percakapan.
        `prompt` dan `system_prompt` tetap tersedia untuk kemudahan pemakaian satu pesan.
        """
        raise NotImplementedError