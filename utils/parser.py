"""
Generic parser utility untuk memvalidasi output LLM terhadap Pydantic schema.

Mendukung:
- Parsing JSON langsung
- Ekstraksi JSON dari markdown code block (```json ... ```)
- Retry mechanism untuk output yang tidak valid
"""

import json
import re
import logging
from typing import Type, TypeVar

from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


def extract_json(text: str) -> str:
    """
    Mengekstrak JSON dari teks mentah.

    Menangani beberapa kasus:
    1. JSON murni (langsung bisa diparse)
    2. JSON dalam markdown code block (```json ... ```)
    3. JSON dalam code block tanpa bahasa (``` ... ```)
    """
    # Coba ekstrak dari ```json ... ``` block
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Coba cari JSON object/array langsung di teks
    match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    return text.strip()


def parse_response(text: str, schema: Type[T]) -> T:
    """
    Memvalidasi teks mentah dari LLM terhadap Pydantic schema.

    Args:
        text: Output mentah dari LLM (bisa mengandung markdown, whitespace, dll)
        schema: Kelas Pydantic untuk validasi (misal: Summary, Contact)

    Returns:
        Instance Pydantic yang sudah tervalidasi

    Raises:
        ValidationError: Jika teks tidak bisa divalidasi sebagai schema yang diberikan
        json.JSONDecodeError: Jika teks bukan JSON yang valid
    """
    cleaned = extract_json(text)
    try:
        return schema.model_validate_json(cleaned)
    except json.JSONDecodeError as e:
        logger.warning(f"JSONDecodeError: {e}\nRaw text (first 500 chars): {text[:500]}")
        raise
    except ValidationError as e:
        logger.warning(f"ValidationError: {e}\nCleaned JSON: {cleaned[:500]}")
        raise


def parse_with_retry(
    text: str,
    schema: Type[T],
    max_attempts: int = 3,
) -> T:
    """
    Memvalidasi teks terhadap schema. Jika gagal, raise error tanpa retry.

    Retry logic diserahkan ke caller (biasanya di main.py) karena retry
    memerlukan pemanggilan ulang LLM yang berada di layer berbeda (provider).

    Args:
        text: Output mentah dari LLM
        schema: Kelas Pydantic untuk validasi
        max_attempts: Tidak digunakan di sini — retry dilakukan oleh caller

    Returns:
        Instance Pydantic yang sudah tervalidasi

    Raises:
        ValidationError: Jika validasi gagal
        json.JSONDecodeError: Jika teks bukan JSON yang valid
    """
    return parse_response(text, schema)


def is_valid(text: str, schema: Type[T]) -> bool:
    """
    Mengecek apakah teks bisa divalidasi tanpa raise exception.

    Args:
        text: Output mentah dari LLM
        schema: Kelas Pydantic untuk validasi

    Returns:
        True jika valid, False jika tidak
    """
    try:
        parse_response(text, schema)
        return True
    except (json.JSONDecodeError, ValidationError):
        return False


# --- Retry decorator untuk digunakan di layer provider ---

def retry_on_validation_error(
    max_attempts: int = 3,
):
    """
    Decorator factory untuk retry otomatis saat validasi gagal.

    Digunakan di layer provider/caller yang memiliki akses ke LLM.
    Contoh penggunaan:

        @retry_on_validation_error(max_attempts=3)
        def get_structured_output(prompt, schema):
            text = llm.chat(prompt)
            return parse_response(text, schema)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except (json.JSONDecodeError, ValidationError) as e:
                    last_error = e
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_attempts} failed: {e}"
                    )
                    if attempt == max_attempts - 1:
                        raise last_error
            raise last_error  # type: ignore[misc]
        return wrapper
    return decorator