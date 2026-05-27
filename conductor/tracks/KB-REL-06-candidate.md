# Track: KB-REL-06 - Připravit release kandidáta

## Objective
Zafixovat verze, zkontrolovat čistotu repozitáře a připravit projekt na finální vydání (tagování).

## Key Files & Context
- Konfigurace verzování (např. `pyproject.toml`, nebo `__init__.py`)
- Repozitář Git

## Implementation Steps
1. **Bump Verze:**
   - Aktualizovat číslo verze v relevantních souborech (např. přesun na očekávanou cílovou verzi `v1.0.0` nebo `v0.1.0`).
2. **Finální kontrola stavu (Release Gates):**
   - Spustit kompletní sadu testů (`pytest`) k ověření, že všechny (minimálně aktuálních 39) testy prochází.
   - Spustit lintery a bezpečnostní audity (`flake8`/`black`/`bandit`/`pip-audit`).
   - Zkontrolovat `git status`, že jsou do commitu zahrnuty jen požadované a ověřené soubory.
3. **Commit & Tag:**
   - Připravit finální commit ("Release vX.Y.Z").
   - Vytvořit tag v Gitu (po úspěšné validaci všech gates).

## Verification & Testing
- Všechny CI kontroly a lokální testy svítí zeleně.
- Git repozitář je čistý, na větvi určené k releasu.
- Vydání lze jednoduše tagnout a distribuovat.