import json
from dataclasses import dataclass, asdict


@dataclass
class Message:
    """Representasi satu pesan dalam percakapan."""
    role: str
    content: str

    def to_dict(self) -> dict:
        return asdict(self)


class Conversation:
    """Mengelola riwayat percakapan dengan sliding window."""

    def __init__(self, system_prompt: str = "Kamu adalah asisten AI yang membantu menjawab pertanyaan.", max_messages: int = 20):
        self._system_prompt = system_prompt
        self._max_messages = max_messages
        self._messages: list[Message] = [
            Message(role="system", content=system_prompt)
        ]

    # --- Properti ---

    @property
    def system_prompt(self) -> str:
        return self._system_prompt

    @system_prompt.setter
    def system_prompt(self, value: str):
        self._system_prompt = value
        # Perbarui system prompt di posisi pertama
        if self._messages and self._messages[0].role == "system":
            self._messages[0] = Message(role="system", content=value)

    # --- Menambah pesan ---

    def add_user_message(self, content: str):
        """Tambahkan pesan dari user."""
        self._messages.append(Message(role="user", content=content))
        self._trim()

    def add_assistant_message(self, content: str):
        """Tambahkan pesan dari assistant."""
        self._messages.append(Message(role="assistant", content=content))
        self._trim()

    # --- Mengambil pesan ---

    def get_messages(self) -> list[dict]:
        """Kembalikan seluruh daftar pesan dalam format dictionary (siap kirim ke API)."""
        return [m.to_dict() for m in self._messages]

    def get_last_n_messages(self, n: int) -> list[dict]:
        """Kembalikan n pesan terakhir (tidak termasuk system prompt)."""
        non_system = [m for m in self._messages if m.role != "system"]
        return [m.to_dict() for m in non_system[-n:]]

    # --- Manajemen context window ---

    def _trim(self):
        """Hapus pasangan user-assistant tertua jika melebihi max_messages.
        System prompt tidak pernah dihapus."""
        while len(self._messages) > self._max_messages:
            # Cari pasangan user-assistant pertama setelah system prompt
            idx = 1  # system prompt selalu di indeks 0
            while idx < len(self._messages) - 1:
                if self._messages[idx].role == "user" and self._messages[idx + 1].role == "assistant":
                    del self._messages[idx:idx + 2]
                    break
                idx += 1
            else:
                # Jika tidak ada pasangan lengkap, hapus satu pesan non-system tertua
                if len(self._messages) > 1:
                    del self._messages[1]

    # --- Membersihkan percakapan ---

    def clear(self):
        """Hapus seluruh percakapan tetapi pertahankan system prompt."""
        self._messages = [Message(role="system", content=self._system_prompt)]

    # --- Ekspor ---

    def export_json(self) -> str:
        """Ekspor seluruh conversation ke format JSON string."""
        return json.dumps(self.get_messages(), ensure_ascii=False, indent=2)

    def __len__(self) -> int:
        return len(self._messages)

    def __repr__(self) -> str:
        return f"Conversation(system='{self._system_prompt[:30]}...', messages={len(self._messages)})"
