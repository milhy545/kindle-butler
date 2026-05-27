# Kindle Butler 🚀

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Verified by Codex](https://img.shields.io/badge/Verified%20by-Codex-green.svg)](https://openai.com/index/openai-codex/)
[![AI: Gemini](https://img.shields.io/badge/AI-Gemini%201.5%20Flash-orange.svg)](https://deepmind.google/technologies/gemini/)

**Kindle Butler** is a smart, autonomous librarian for your Amazon Kindle. It transforms your device from a messy pile of files into a perfectly organized library using Google's Gemini AI.

## ✨ Features

- **🔌 Plug & Play:** Automatically detects your Kindle and starts organizing books upon USB connection.
- **🧠 AI Normalization:** Uses Gemini 1.5 Flash to clean up messy metadata (filenames like `King_Stephen_IT_v2.azw3` → `Stephen King - It`).
- **📁 Smart Folder Structure:** Automatically moves books into `documents/Author/Book.ext`.
- **🏗️ Content Enhancement:** Professional EPUB processing—converts complex technical tables and lists into readable narrative prose for better E-Ink experience.
- **🛡️ Safety First:** Every single move is preceded by an automatic backup to `.butler_backup` on your device.
- **🖥️ Host Integration:** Built-in Linux installer with `udev` support for automated background execution.

## 🚀 Quick Start

### 1. Requirements
- Linux (Ubuntu/Debian/MX/etc.)
- [uv](https://github.com/astral-sh/uv) (modern Python package manager)
- A Google Gemini API Key (get one for free at [AI Studio](https://aistudio.google.com/))

### 2. Installation
Clone the repo and run the installation script:
```bash
git clone https://github.com/milhy777/kindle-butler.git
cd kindle-butler
bash scripts/install_host.sh
```

### 3. Usage
**Interactive Mode:**
```bash
uv run python main.py start
```

**Auto-Sync (Background):**
Just plug in your Kindle. The `udev` rule will trigger the organization automatically.

## 🛠️ Commands

- `start`: Main interactive menu (Czech language support).
- `sync`: One-time organization of all files on the device.
- `check`: Validates system health, API keys, and Kindle connection.
- `email`: Send documents via email directly to your Kindle.
- `enhance`: Advanced AI processing for technical EPUB documents (translations, formatting).
- `process`: Convert and translate Markdown files to AZW3.
- `sync-wifi`: Sync staged files to Kindle via SSH and trigger a library scan.

## 🔒 Security & Privacy

- **AI Disclosure:** Your book content is sent to Gemini only when you run the `enhance` or `process` commands. Standard `sync` sends only author/title metadata for normalization.
- **Credential Safety:** API keys are stored in `~/.config/kindle-butler/env` with restricted permissions (0600) or can be provided via environment variables (`LLM_API_KEY`).
- **Backup Policy:** Butler uses a hash-based backup system to prevent overwriting different versions of the same file.

## 🧪 Development

The project uses a focused verification baseline:
- **49 Unit & Integration Tests** in the current audited checkout.
- **Root-level pytest verification:** run `uv run python -m pytest -q`, not only `pytest tests`.
- **Security checks:** run `uv run bandit -r app -q` and `uv run pip-audit`.
- **Type hints:** public code uses Python 3.12+ type annotations where practical.

---
*Developed by Stanislav "Milhy" Muller with ❤️ and Gemini CLI.*
