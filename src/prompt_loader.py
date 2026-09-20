"""
Prompt Loader — memuat template prompt dari file Markdown,
merender placeholder, dan mengirim ke LLM.

Mendukung:
- Placeholder {{VARIABLE}} (via str.replace atau Jinja2)
- Pemisahan otomatis System Prompt (ROLE) vs User Prompt (sisanya)
- Integrasi dengan LLM provider yang sudah ada
"""

import re
from pathlib import Path
from typing import Any

from llm.factory import create_provider


class PromptLoader:
    """Memuat dan merender prompt template, lalu mengirim ke LLM."""

    def __init__(self, prompts_dir: str | Path | None = None, provider: str = "deepseek"):
        """
        Args:
            prompts_dir: Path ke folder template prompt.
                         Default: folder `prompts/` di samping file ini.
            provider: Nama LLM provider (deepseek, openai, ollama).
        """
        if prompts_dir is None:
            prompts_dir = Path(__file__).resolve().parent / "prompts"
        self._prompts_dir = Path(prompts_dir)
        self._provider_name = provider
        self._use_jinja = self._check_jinja()

    # ---------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------

    def run(self, template_name: str, **kwargs: Any) -> str:
        """Pipeline lengkap: load → render → parse → LLM → response.

        Args:
            template_name: Nama file template (tanpa .md), mis. "summarize".
            **kwargs: Nilai untuk placeholder di template,
                      mis. TEXT="...", LABELS="...", AUDIENCE="...".

        Returns:
            Respons teks dari LLM.
        """
        template = self.load_template(template_name)
        rendered = self.render(template, **kwargs)
        system_prompt, user_prompt = self.parse_sections(rendered)
        return self._call_llm(system_prompt, user_prompt)

    def load_template(self, name: str) -> str:
        """Baca file template dari folder prompts/.

        Args:
            name: Nama file tanpa ekstensi, mis. "summarize".

        Returns:
            Isi file template sebagai string.

        Raises:
            FileNotFoundError: Jika file template tidak ditemukan.
        """
        file_path = self._prompts_dir / f"{name}.md"
        if not file_path.exists():
            raise FileNotFoundError(f"Template tidak ditemukan: {file_path}")
        return file_path.read_text(encoding="utf-8")

    def render(self, template: str, **kwargs: Any) -> str:
        """Ganti placeholder {{VARIABLE}} dengan nilai yang diberikan.

        Menggunakan Jinja2 jika tersedia, fallback ke str.replace().

        Args:
            template: String template mentah.
            **kwargs: Key-value untuk substitusi placeholder.

        Returns:
            String template yang sudah dirender.
        """
        if self._use_jinja:
            return self._render_jinja(template, **kwargs)
        return self._render_simple(template, **kwargs)

    def parse_sections(self, rendered: str) -> tuple[str, str]:
        """Pisahkan template menjadi system_prompt dan user_prompt.

        ROLE → system prompt (mendefinisikan persona AI).
        Sisanya (OBJECTIVE, CONTEXT, CONSTRAINTS, OUTPUT, SUCCESS) → user prompt.

        Args:
            rendered: Template yang sudah dirender.

        Returns:
            Tuple (system_prompt, user_prompt).
        """
        # Ekstrak bagian ROLE
        role_match = re.search(
            r"##\s*ROLE\s*\n(.*?)(?=\n##\s|\Z)",
            rendered,
            re.DOTALL | re.IGNORECASE,
        )
        system_prompt = role_match.group(1).strip() if role_match else "Kamu adalah asisten AI yang membantu."

        # Hapus komentar HTML (metadata versioning) dan bagian ROLE dari user prompt
        user_prompt = re.sub(r"<!--.*?-->", "", rendered, flags=re.DOTALL)
        user_prompt = re.sub(
            r"##\s*ROLE\s*\n.*?(?=\n##\s|\Z)",
            "",
            user_prompt,
            flags=re.DOTALL | re.IGNORECASE,
        )
        user_prompt = user_prompt.strip()

        return system_prompt, user_prompt

    # ---------------------------------------------------------------
    # Internal
    # ---------------------------------------------------------------

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Kirim prompt ke LLM provider."""
        llm = create_provider(self._provider_name)
        return llm.chat(prompt=user_prompt, system_prompt=system_prompt)

    @staticmethod
    def _render_simple(template: str, **kwargs: Any) -> str:
        """Render placeholder dengan str.replace() sederhana."""
        result = template
        for key, value in kwargs.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value))
        return result

    @staticmethod
    def _render_jinja(template: str, **kwargs: Any) -> str:
        """Render placeholder dengan Jinja2."""
        from jinja2 import BaseLoader, Environment

        env = Environment(loader=BaseLoader())
        tpl = env.from_string(template)
        return tpl.render(**kwargs)

    @staticmethod
    def _check_jinja() -> bool:
        """Cek apakah Jinja2 tersedia."""
        try:
            import jinja2  # noqa: F401
            return True
        except ImportError:
            return False


# ---------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------

def run_prompt(template_name: str, provider: str = "deepseek", **kwargs: Any) -> str:
    """Jalankan template prompt dalam satu panggilan.

    Args:
        template_name: Nama template (tanpa .md).
        provider: LLM provider.
        **kwargs: Placeholder values.

    Returns:
        Respons LLM.

    Contoh:
        >>> result = run_prompt("summarize", TEXT="Artificial intelligence is...")
    """
    loader = PromptLoader(provider=provider)
    return loader.run(template_name, **kwargs)
