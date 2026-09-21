"""
Structured Output Pipeline — menggabungkan tiga layer yang terpisah:

    Prompt Loader  →  Provider  →  Parser  →  Application

Ini adalah implementasi "Best Practice" dari w03s02:
jangan mencampur prompt, pemanggilan LLM, dan validasi dalam satu fungsi besar.
Setiap layer punya satu tanggung jawab dan bisa diuji / diganti sendiri-sendiri.
"""

import json
import sys
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

# `schemas/` dan `utils/` berada di root proyek (satu level di atas `src/`).
# Pastikan root proyek masuk sys.path agar keduanya bisa di-import.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from llm.factory import create_provider
from prompt_loader import PromptLoader
from schemas.summary import Summary
from utils.parser import parse_response

T = TypeVar("T", bound=BaseModel)


def generate_structured(
    template_name: str,
    schema: type[T],
    provider: Any = "deepseek",
    max_attempts: int = 3,
    **kwargs: Any,
) -> T:
    """Jalankan pipeline Prompt Loader → Provider → Parser, dengan retry.

    Args:
        template_name: Nama template prompt (tanpa .md) yang meminta output JSON.
        schema: Kelas Pydantic untuk validasi (mis. Summary, Contact).
        provider: Nama provider ("deepseek"/"openai"/"ollama") ATAU objek LLM
                  yang punya metode chat(...) — berguna untuk testing.
        max_attempts: Maksimal percobaan validasi (retry).

    Returns:
        Instance Pydantic yang sudah tervalidasi.

    Raises:
        ValidationError / JSONDecodeError: jika semua percobaan gagal.
    """
    # Layer 1 — Prompt Loader: siapkan prompt (TANPA memanggil LLM)
    system_prompt, user_prompt = PromptLoader().build_prompt(template_name, **kwargs)

    # Layer 2 — Provider: panggil LLM (menerima string atau objek provider)
    llm = provider if hasattr(provider, "chat") else create_provider(provider)

    # Layer 3 — Parser: validasi, dengan retry
    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        raw = llm.chat(prompt=user_prompt, system_prompt=system_prompt)
        try:
            return parse_response(raw, schema)
        except (json.JSONDecodeError, ValidationError) as exc:
            last_error = exc
            print(f"  [retry] percobaan {attempt}/{max_attempts} gagal: {type(exc).__name__}")

    if last_error is not None:
        raise last_error
    raise RuntimeError("Pipeline gagal tanpa error yang tercatat.")


def main() -> None:
    """Demo: jalankan pipeline structured output untuk meringkas teks."""
    text = (
        "Deep learning adalah bagian dari machine learning yang menggunakan "
        "jaringan saraf tiruan berlapis. Teknik ini sangat efektif untuk "
        "pengenalan gambar, pemrosesan bahasa alami, dan sistem rekomendasi."
    )

    print("=== Demo Parser (tanpa LLM) ===")
    sample = '{"title": "Deep Learning", "summary": "Teknik ML berbasis jaringan saraf tiruan.", "keywords": ["deep learning", "AI", "neural network"]}'
    parsed = parse_response(sample, Summary)
    print("Tipe objek:", type(parsed).__name__)
    print(parsed.model_dump_json(indent=2))

    print("\n=== Demo Pipeline Penuh (Prompt → Provider → Parser) ===")
    try:
        result = generate_structured("summarize_json", Summary, TEXT=text)
        print("Hasil tervalidasi:")
        print(result.model_dump_json(indent=2))
    except (json.JSONDecodeError, ValidationError) as exc:
        print("Semua percobaan gagal (kemungkinan API key belum diset / demo mode).")
        print(f"Error terakhir: {exc}")


if __name__ == "__main__":
    main()
