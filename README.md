# J.A.R.V.I.S. - Autonomous AI Assistant (Phase 1)

An open-source, local-first autonomous personal assistant framework designed to run efficiently on low-to-mid range hardware without expensive cloud resources or API bloat.

## 🌟 Overview & Architecture

JARVIS Phase 1 introduces a **Telegram-based Dispatcher & Triage Engine**. Instead of routing every request directly to expensive or rate-limited cloud models, JARVIS uses a lightweight multi-tiered triage strategy:

1. **Dispatcher Node**: Triages incoming text prompts via a fast, free OpenRouter model (e.g., `openai/gpt-oss-20b:free`) to determine intent, task complexity, and required execution engines.
2. **Local Memory Subsystem**: Uses a zero-cost, lightweight SQLite database (`jarvis.db`) to log conversation history and store long-term episodic context.
3. **Execution Routing**: Routes simple queries to local SLMs and complex agentic tasks to dedicated pipelines (web research, OS-level execution sandbox).

---

## 📁 Repository Structure

```
JARVIS/
├── bot.py           # Telegram bot entry point & message handlers
├── dispatcher.py    # OpenRouter triage & task complexity router
├── memory.py        # SQLite database operations & context logging
├── config.py        # Environment variables & logging setup
├── requirements.txt # Project dependencies
└── .env.example     # Template for secret API keys
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- A Telegram account to create a bot via [@BotFather](https://t.me/BotFather)
- An OpenRouter API Key (free tier available at [OpenRouter](https://openrouter.ai/))

### 2. Installation

Clone the repository and install dependencies:
```bash
git clone https://github.com/seathunder/JARVIS.git
cd JARVIS
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy the `.env.example` file to `.env`:
```bash
cp .env.example .env
```

Edit `.env` and fill in your tokens:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### 4. Run the Bot

Start the assistant:
```bash
python bot.py
```

Once running, send a message to your Telegram bot. You will see the dispatcher triaging your prompt live in the console!

---

## 🛣️ Roadmap

- [x] **Phase 1**: Telegram Dispatcher, OpenRouter Triage, SQLite Memory
- [ ] **Phase 2**: Local Web Research Agent (SearXNG + Playwright + Local SLM Summarizer)
- [ ] **Phase 3**: Sandboxed OS-Level Execution Sandbox (Python / Terminal Interpreter)
- [ ] **Phase 4**: Voice Notes Processing (CPU-bound Faster-Whisper STT)
