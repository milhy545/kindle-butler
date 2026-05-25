# Kindle Butler v1.0 🚀

Smart, autonomous organization for your Amazon Kindle.

## Features
- **Plug & Play:** Auto-detects Kindle and starts organization upon USB connection.
- **Smart Meta-Organization:** Extracts author and title info from PDF, AZW3, MOBI, and EPUB.
- **AI-Powered Normalization:** Uses Gemini AI to clean up messy metadata and normalize names.
- **Host Integration:** Desktop notifications (Linux) and secure API key storage.
- **Safety First:** Automatic backups to `.butler_backup` on the Kindle before any move.

## Setup

### 1. Install Butler on Kindle
Just keep the `kindle_butler` folder on your Kindle root.

### 2. Configure Host PC (Linux)
Run the installation script directly from the Kindle mount:
```bash
bash /media/milhy777/Kindle/kindle_butler/scripts/install_host.sh
```
This script will:
- Set up `udev` rules for auto-start.
- Ask for your `GEMINI_API_KEY` (stored securely on PC).
- Install the host runner.

### 3. Verification
Check your setup anytime:
```bash
uv run python -m app.main check
```

## Usage
Simply plug in your Kindle. Butler will wake up, organize your books into `documents/Author/Book.ext`, and notify you when finished.

## Log Visibility
Check `butler_run.log` in the Kindle root for detailed activity history.

---
*Created with Gemini CLI in YOLO mode.*
