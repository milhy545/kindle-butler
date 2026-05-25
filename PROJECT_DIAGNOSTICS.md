# Kindle Butler Project Diagnostics

Date: 2026-05-25

## Executive Summary

The project is now functionally healthy and stable. The CLI contract matches the tests and documentation. Security vulnerabilities regarding path traversal and backup collisions have been addressed. The installation script has been hardened.

## Verification Run

- `uv sync`: passed.
- `uv run python -m pytest -q`: 19 passed.
- `uv run python -m pytest --cov=app --cov-report=term-missing -q`: 19 passed, total coverage 54%.
- `uv run python -m compileall app tests main.py`: passed.
- `uv run python -m app.main --help`: passed, lists `check`, `start`, `sync`.
- `uv run python -m app.main check`: passed.
- `uvx pip-audit --progress-spinner off`: passed.
- `uvx bandit -r app scripts -q`: passed.

## Functional Findings

### [FIXED] F-1: Implemented CLI does not match tests or README
The CLI now includes all required commands (`sync`, `check`) and options (`--version`, `--auto`, `--no-use-ai`).

### [FIXED] F-2: Test entrypoint through `uv run pytest` is broken
`AGENTS.md` now correctly points to `uv run python -m pytest`.

### F-3: Coverage is improving but still has gaps in AI interaction
Coverage increased from 42% to 54%. `app/main.py` is now at 44%.

## Security Findings

### [FIXED] S-1: Metadata or LLM output can control filesystem path components
Path sanitization is now enforced in `KindleOrganizer`.

### [FIXED] S-2: Backup names are flat and can overwrite each other
Backups now use SHA-256 path hashes to ensure uniqueness and pass bandit security audits.

### [FIXED] S-3: Import moves host files without backup-first behaviour
Import now uses copy-then-verify and asks for user confirmation before deletion.

### [FIXED] S-4: Metadata extraction hides parse failures
Parser failures are now logged using the `logging` module.

### [FIXED] S-5: Host install script is fragile for privileged automation
Script now uses `set -euo pipefail`, `findmnt`, and `sudo -A`.

