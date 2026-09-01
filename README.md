# J.A.R.V.I.S. - Autonomous AI Assistant (Phases 1-4 Complete)

An open-source, local-first autonomous personal assistant framework designed to run efficiently on low-to-mid range hardware without expensive cloud resources, zero VRAM thrashing, and zero API costs.

---

## 🌟 Complete Architecture & Features

### 1. Telegram Dispatcher & Triage Engine
- Triages prompts via fast, free OpenRouter models (`openai/gpt-oss-20b:free`).
- Routes requests to specific execution pipelines: Fast Response, Local Web GraphRAG, Agentic Sandbox, Project Builder, or Desktop Automation.

### 2. Local Machine Web Search & GraphRAG (`research.py`)
- Live DuckDuckGo Lite web search directly on your machine without search API keys or rate limits.
- Extracts page contents and builds an in-memory `NetworkX` entity-relationship Knowledge Graph, delivering structured context payloads to the model.

### 3. Agentic Feedback & Self-Healing Execution Loop (`executor.py`)
- Runs generated Python/PowerShell scripts locally in a subprocess sandbox.
- Self-healing retry loop captures `stderr` and tracebacks, automatically prompting the model to self-correct up to 3 retries.

### 4. Project Creation & Task System (`projects.py`)
- Manages multi-file software projects inside `projects/`.
- Tracks tasks using structured `project.json` manifests.

### 5. CPU-Bound Voice Notes Processing (`voice.py`)
- Transcribes Telegram `.ogg` voice notes using `faster-whisper` (`base.en`) running purely on the CPU with `int8` quantization.
- Zero VRAM usage on your GPU!

### 6. Desktop OS Control & Automation Sandbox (`computer_use.py`)
- Desktop screenshot capture & transmission to Telegram via `/screenshot`.
- OS GUI control primitives (`pyautogui`) for mouse movement, clicking, and typing.

---

## 📁 Repository Structure

```
JARVIS/
├── bot.py           # Telegram bot entry point (text, voice & commands)
├── dispatcher.py    # Multi-pipeline triage & router
├── research.py      # DuckDuckGo scraper & NetworkX GraphRAG builder
├── executor.py      # Agentic code execution & self-healing retry loop
├── projects.py      # Project creator & task manifest manager
├── voice.py         # CPU-bound Faster-Whisper voice transcriber
├── computer_use.py  # Desktop screenshot & OS GUI automation primitives
├── memory.py        # SQLite database context logger
├── config.py        # Environment variables & logging setup
├── requirements.txt # Dependencies for full Phase 1-4 stack
└── .env.example     # Secret API keys template
```

---

## 🚀 Getting Started

### 1. Installation

Clone the repository and install dependencies:
```bash
git clone https://github.com/seathunder/jarvis-ai-assistant.git
cd jarvis-ai-assistant
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy `.env.example` to `.env` and enter your keys:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### 3. Run the Bot

```bash
python bot.py
```

---

## 📱 Telegram Commands

- `🎙️ Voice Note` - Send a voice message to automatically transcribe and execute via CPU Faster-Whisper.
- `/screenshot` - Capture and receive a live desktop screenshot.
- `/research <topic>` - Perform local machine web search & GraphRAG context extraction.
- `/project <name>` - Initialize a new autonomous software project.
