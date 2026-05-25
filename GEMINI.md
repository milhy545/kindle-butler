# Project Instructions: Kindle Butler

## Core Directives
- **Language:** Always communicate in Czech.
- **Tone:** Professional, direct, and factual.
- **Goal:** Automate Kindle library management with AI enhancement.

## Technical Standards
- **Stack:** Python 3.12, `uv` for package management.
- **Safety:** Always backup files to `.butler_backup` before moving or modifying them on the Kindle.
- **Testing:** Run tests using `uv run python -m pytest`.
- **Security:** Use SHA-256 for hashes, sanitize all path components derived from external metadata or AI output.

## [FORAI] Cross-Agent Verification Hook (Codex)
Tento hook definuje povinný proces křížové kontroly implementace pomocí OpenAI Codex (přes Desktop Commander).

### 🔄 Workflow: Validation Phase Override
V momentě, kdy považuješ úkol za dokončený (před finálním hlášením uživateli), MUSÍŠ provést následující kroky:
1. **Spuštění Codexu:** Použij `start_process("codex-cli")` nebo `codex` (podle dostupnosti v PATH).
2. **Zaslání kontextu:** Pomocí `interact_with_process` pošli Codexu zprávu: "Proveď revizi mých posledních změn v [seznam souborů nebo diff]. Hledej logické chyby, bezpečnostní rizika nebo porušení lokálních konvencí. Pokud je vše v pořádku, odpověz přesně 'VERIFIED_OK'. Pokud najdeš chyby, vypiš je v bodech."
3. **Analýza výstupu:**
   - Pokud Codex odpoví `VERIFIED_OK`, můžeš úkol uzavřít.
   - Pokud Codex vypíše chyby, proveď opravu podle jeho doporučení.
4. **Iterace:** Po opravě znovu zavolej Codex pro finální potvrzení. Opakuj, dokud nedostaneš `VERIFIED_OK`.

### 🛠 Technické detaily
- Pro čtení výsledku z Codexu používej `read_process_output` s negativním offsetem pro získání posledních řádků.
- Pokud je Codex v perzistentním REPL režimu, neukončuj proces, dokud není celá session uzavřena.
