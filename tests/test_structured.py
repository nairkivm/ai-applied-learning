import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(ROOT))

from schemas.summary import Summary
from utils.parser import parse_response
from structured_output import generate_structured


class StructuredOutputTests(unittest.TestCase):
    def test_parse_pure_json(self):
        obj = parse_response('{"title":"AI","summary":"ringkas","keywords":["AI"]}', Summary)
        self.assertIsInstance(obj, Summary)
        self.assertEqual(obj.title, "AI")

    def test_parse_markdown_code_block(self):
        text = '```json\n{"title":"AI","summary":"...","keywords":["AI","ML"]}\n```'
        obj = parse_response(text, Summary)
        self.assertEqual(obj.keywords, ["AI", "ML"])

    def test_parse_invalid_raises(self):
        with self.assertRaises(Exception):
            parse_response("bukan json", Summary)

    def test_generate_structured_success(self):
        class FakeLLM:
            def chat(self, prompt="", system_prompt=None, temperature=0.2, model="", messages=None):
                return '{"title":"T","summary":"S","keywords":["a"]}'

        obj = generate_structured("summarize_json", Summary, provider=FakeLLM(), TEXT="apa saja")
        self.assertIsInstance(obj, Summary)
        self.assertEqual(obj.title, "T")

    def test_generate_structured_retry_then_success(self):
        calls = {"n": 0}

        class FakeLLM:
            def chat(self, prompt="", system_prompt=None, temperature=0.2, model="", messages=None):
                calls["n"] += 1
                if calls["n"] == 1:
                    return "bukan json"
                return '{"title":"T","summary":"S","keywords":["a"]}'

        obj = generate_structured("summarize_json", Summary, provider=FakeLLM(), max_attempts=3, TEXT="x")
        self.assertEqual(obj.title, "T")
        self.assertEqual(calls["n"], 2)


if __name__ == "__main__":
    unittest.main()
