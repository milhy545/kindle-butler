# Diagnostika projektu Kindle Butler

Datum: 2026-05-25

## Shrnutí

Projekt je nyní funkčně zdravý a stabilní. CLI kontrakt odpovídá testům a dokumentaci. Bezpečnostní zranitelnosti týkající se path traversal a kolizí záloh byly vyřešeny. Instalační skript byl zodolněn.

## Ověření

- `uv sync`: prošlo.
- `uv run python -m pytest -q`: 19 passed.
- `uv run python -m pytest --cov=app --cov-report=term-missing -q`: 19 passed, celkové coverage 54 %.
- `uv run python -m compileall app tests main.py`: prošlo.
- `uv run python -m app.main --help`: prošlo, ukazuje `check`, `start`, `sync`.
- `uv run python -m app.main check`: prošlo.
- `uvx pip-audit --progress-spinner off`: prošlo, žádné známé zranitelnosti.
- `uvx bandit -r app scripts -q`: prošlo.

## Funkční nálezy

### [OPRAVENO] F-1: CLI neodpovídá testům ani README
CLI nyní obsahuje všechny požadované příkazy (`sync`, `check`) a volby (`--version`, `--auto`, `--no-use-ai`).

### [OPRAVENO] F-2: `uv run pytest` je v tomto checkoutu rozbité
Dokumentace v `AGENTS.md` nyní správně ukazuje na `uv run python -m pytest`.

### F-3: Coverage se zlepšuje, ale stále má mezery u AI interakcí
Coverage se zvýšilo z 42 % na 54 %. `app/main.py` je nyní na 44 %.

## Security nálezy

### [OPRAVENO] S-1: Metadata nebo LLM output ovládají části filesystem path
Sanitizace cest je nyní vynucena v `KindleOrganizer`.

### [OPRAVENO] S-2: Zálohy jsou flat a mohou se přepsat
Zálohy nyní používají SHA-256 hashe cest pro zajištění unikátnosti a bezpečnostní shody v Bandit auditu.

### [OPRAVENO] S-3: Import přesouvá host files bez backup-first režimu
Import nyní používá režim "zkopírovat a ověřit" a před smazáním zdrojových souborů žádá o potvrzení.

### [OPRAVENO] S-4: Metadata extraction polyká chyby
Selhání parseru jsou nyní logována pomocí modulu `logging`.

### [OPRAVENO] S-5: Host install script je křehký pro privileged automation
Skript nyní používá `set -euo pipefail`, `findmnt` a `sudo -A`.
