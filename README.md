# AI Applied Learning

Tujuan: belajar AI terapan selama 6 bulan melalui pendekatan **konsep → praktik → proyek**.

## Progress

### Minggu 1 — Fondasi

- [x] **Week 1 Session 1** — Lingkungan Kerja AI Developer
- [x] **Week 1 Session 2** — HTTP, JSON, REST API
- [x] **Week 1 Session 3** — Dasar LLM & Prompt Engineering

### Minggu 2 — Memanggil LLM dari Program

- [x] **Week 2 Session 1** — Wrapper LLM & Konfigurasi
- [x] **Week 2 Session 2** — Menghubungkan ke LLM Sungguhan
- [x] **Week 2 Session 3** — Conversation Memory & Context Window

### Minggu berikutnya (belum dikerjakan)

- [ ] Week 3 — Structured Output
- [ ] Week 4 — RAG
- [ ] Week 5 — Tools & Agents
- [ ] Week 6 — Evaluasi & Deployment

---

## Rangkuman Progress per Sesi

### Week 1 Session 1 — Lingkungan Kerja AI Developer

Membangun fondasi lingkungan pengembangan:

- Membuat **Python virtual environment** (`.venv`) agar dependency tiap proyek tidak bentrok.
- Menyiapkan **Git & GitHub** sebagai sistem versi untuk bekerja dengan AI agent.
- Menginstal ekstensi VS Code wajib: **Python, Pylance, GitLens**.
- Membuat **struktur proyek** `ai-applied-learning/` dengan `src/`, `tests/`, `docs/`, `prompts/`, `schemas/`.

**Hasil:** repositori Git pertama, `requirements.txt`, dan program awal `src/hello.py`.

### Week 1 Session 2 — HTTP, JSON, REST API

Memahami bagaimana aplikasi berkomunikasi lewat internet:

- Konsep **request–response**, **HTTP method** (GET, POST, PUT, DELETE), **header**, dan **status code** (200, 400, dst).
- Mengubah **JSON** menjadi dictionary Python dan sebaliknya.
- Praktik memanggil API publik gratis (`jsonplaceholder.typicode.com`) menggunakan **httpx**.
- Menangani error sederhana (`raise_for_status`, try/except).

**Hasil:** `src/api_test.py`, `src/api_mini_ex.py`, dan `src/api_wrapper.py`.

### Week 1 Session 3 — Dasar LLM & Prompt Engineering

Memahami LLM secara konseptual dan cara berkomunikasi secara profesional:

- Konsep **token**, **context window**, **temperature**, dan **hallucination**.
- Perbedaan **System Prompt**, **User Prompt**, dan **Assistant Response**.
- Membangun **prompt template** dengan struktur `ROLE`, `OBJECTIVE`, `CONTEXT`, `CONSTRAINTS`, `OUTPUT FORMAT`.

**Hasil:** template prompt `src/prompts/classify.md`, `explain.md`, `summarize.md`, dan kerangka `docs/prompt_templates.md`.

### Week 2 Session 1 — Memanggil LLM dari Python & Wrapper

Memasuki tahap AI Engineering — membangun aplikasi, bukan sekadar chat di browser:

- Mengelola **API key** secara aman lewat `.env` dan `python-dotenv`.
- Mendesain **wrapper** yang tidak bergantung pada satu provider (abstraksi di atas API LLM).
- Memisahkan logika aplikasi dari kode pemanggilan API.

**Hasil:** `src/config.py`, `src/llm/base.py` (kelas `LLMProvider`), dan `src/llm/factory.py` (fungsi `create_provider`).

### Week 2 Session 2 — Menghubungkan ke LLM Sungguhan

Mengirim prompt nyata dan menerima respons dari model:

- Memahami format **Chat API** modern: `model`, `messages`, `temperature`, `max_tokens`.
- Menggunakan **OpenAI Python SDK** yang kompatibel dengan banyak provider (Ollama, Groq, OpenRouter, dll).
- Berganti provider cukup dengan mengubah `OPENAI_BASE_URL`.

**Hasil:** provider `src/llm/openai_provider.py`, `src/llm/deepseek_provider.py`, dan `src/llm/ollama_provider.py`.

### Week 2 Session 3 — Conversation Memory & Context Window

Membuat chatbot yang "mengingat" percakapan:

- Memahami bahwa model **tidak punya ingatan permanen** — aplikasi yang mengirim ulang riwayat.
- Mendesain kelas **`Conversation`** dan `Message` (dataclass) yang dapat digunakan ulang.
- Mengelola context dengan **sliding window** (menyimpan `max_messages`, system prompt tidak pernah dibuang).
- Fitur terminal chat: `exit`, `clear`, dan `history`.

**Hasil:** `src/chat/conversation.py` dan `src/main.py` (chat terminal interaktif).

---

## Struktur Proyek Saat Ini

```text
ai-applied-learning/
├── README.md
├── requirements.txt
├── docs/
│   └── prompt_templates.md
├── prompts/
├── schemas/
│   ├── contact.py
│   └── summary.py
├── src/
│   ├── config.py
│   ├── main.py
│   ├── prompt_loader.py
│   ├── api_mini_ex.py
│   ├── api_test.py
│   ├── api_wrapper.py
│   ├── hello.py
│   ├── chat/
│   │   └── conversation.py
│   ├── llm/
│   │   ├── base.py
│   │   ├── deepseek_provider.py
│   │   ├── factory.py
│   │   ├── ollama_provider.py
│   │   └── openai_provider.py
│   └── prompts/
│       ├── classify.md
│       ├── explain.md
│       └── summarize.md
├── tests/
│   └── test_cli.py
└── utils/
    └── parser.py
```

## Cara Menjalankan

```bash
# Aktifkan virtual environment
.venv\Scripts\activate   # Windows

# Install dependency
pip install -r requirements.txt

# Jalankan chat terminal (default: deepseek)
python src/main.py

# Pilih provider lain
python src/main.py openai
python src/main.py ollama
```
