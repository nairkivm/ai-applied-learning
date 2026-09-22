import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(ROOT))

from schemas.product import Product
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

    def test_parse_product_json(self):
        obj = parse_response(
            '{"name":"Meja Kayu","category":"Furniture","price":1500000,"description":"Meja kerja dari kayu jati."}',
            Product,
        )
        self.assertIsInstance(obj, Product)
        self.assertEqual(obj.name, "Meja Kayu")
        self.assertEqual(obj.price, 1500000.0)

    def test_parse_product_coerces_price(self):
        obj = parse_response(
            '{"name":"Lampu","category":"Elektronik","price":"75000","description":"Lampu meja LED."}',
            Product,
        )
        self.assertEqual(obj.price, 75000.0)

    def test_generate_structured_product(self):
        class FakeLLM:
            def chat(self, prompt="", system_prompt=None, temperature=0.2, model="", messages=None):
                return '{"name":"Buku","category":"Buku","price":85000,"description":"Buku tentang Python."}'

        obj = generate_structured("product_json", Product, provider=FakeLLM(), TEXT="deskripsi produk")
        self.assertIsInstance(obj, Product)
        self.assertEqual(obj.category, "Buku")


if __name__ == "__main__":
    unittest.main()
