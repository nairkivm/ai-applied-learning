import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import main


class ChatTerminalTests(unittest.TestCase):
    def test_chat_loop_exits_on_exit_command(self):
        class FakeProvider:
            def chat(self, prompt="", system_prompt=None, temperature=0.2, model="", messages=None):
                # Ambil konten dari messages atau fallback ke prompt
                content = prompt
                if messages:
                    for msg in reversed(messages):
                        if msg["role"] == "user":
                            content = msg["content"]
                            break
                return f"reply:{content}"

        inputs = iter(["halo", "exit"])
        outputs = []

        main.chat_with_terminal(
            provider=FakeProvider(),
            input_func=lambda _: next(inputs),
            output_func=outputs.append,
            system_prompt="system",
        )

        self.assertTrue(any("reply:halo" in line for line in outputs))
        self.assertTrue(any("Chat selesai" in line for line in outputs))


if __name__ == "__main__":
    unittest.main()
