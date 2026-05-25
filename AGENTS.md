# Repository Guidelines

## Project Structure & Module Organization

Kindle Butler is a Python 3.12 CLI tool for organising Kindle documents. Runtime code lives in `app/`: `main.py` defines the Typer interface, `organizer.py` moves and backs up files, `metadata.py` extracts ebook metadata, `ai_client.py` normalises metadata with Gemini, `usb_detector.py` finds mounted Kindles, and `config.py` stores host configuration. The top-level `main.py` is a launcher. Tests live in `tests/` and cover CLI, USB detection, metadata extraction, backups, logging, and end-to-end sync. Host installation logic is in `scripts/install_host.sh`. Do not commit `__pycache__/`, `.venv/`, logs, or mounted Kindle content.

## Build, Test, and Development Commands

- `uv sync`: create or refresh the local virtual environment from `pyproject.toml` and `uv.lock`.
- `uv run python -m app.main start`: run the interactive CLI.
- `uv run python -m app.main check`: run the documented setup verification command when available.
- `KINDLE_BUTLER_MOCK_PATH=/tmp/mock_kindle uv run python -m app.main start`: exercise a mock Kindle path.
- `uv run python -m pytest`: run the full test suite.
- `uv run python -m pytest --cov=app`: run tests with coverage for application modules.

## Coding Style & Naming Conventions

Use 4-space indentation, type hints for public functions, and `pathlib.Path` for filesystem paths. Keep modules small and side effects explicit; Kindle file moves belong in `KindleOrganizer`. Use `snake_case` for functions, variables, and test names, `PascalCase` for classes, and uppercase names for environment variables such as `KINDLE_BUTLER_MOCK_PATH` and `GEMINI_API_KEY`. User-facing CLI text may be Czech; code, comments, and documentation should use UK English.

## Testing Guidelines

Tests use `pytest` plus Typer's `CliRunner`. Name test files `test_*.py` and keep fixtures temporary via `tmp_path`; never require a real Kindle or live LLM call for default tests. For organiser changes, verify backup behaviour and `.sdr` folder handling. For CLI changes, add mocked Kindle coverage with `KINDLE_BUTLER_MOCK_PATH`.

## Commit & Pull Request Guidelines

This repository currently has no committed history, so use concise imperative subjects such as `Add backup handling for SDR folders`. Keep each commit focused and mention tests run when useful. Pull requests should describe user-visible behaviour, list verification commands, call out Kindle-device or API-key assumptions, and include terminal output or screenshots only when they clarify CLI behaviour.

## Security & Configuration Tips

Do not commit API keys, `~/.config/kindle-butler/env`, Kindle backups, or personal ebooks. Keep secrets in the host config flow or environment variables. Any command that can move or delete Kindle files must preserve the existing backup-first behaviour.
