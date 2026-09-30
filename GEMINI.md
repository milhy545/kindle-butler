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

## [FORAI] Tandem Cross-Agent Verification Hook (Mistral & MiMo)
Tento hook definuje povinný proces křížové kontroly implementace celého projektu pomocí tandemu **Mistral Large** (`mistral/mistral-large-latest`) a **MiMo** (`opencode/mimo-v2.5-free`).

### 🔄 Workflow: Validation Phase Override
V momentě, kdy považuješ jakoukoliv vývojovou fázi za dokončenou, **NESMÍŠ** hned ohlásit hotovo uživateli. Musíš striktně provést toto pětikrokové tandemové workflow:

1. **Fáze A: Individuální audit celého projektu**
   - Vyžeň **Mistral Large** a **Mimo** (odděleně) na pastvu. Požádej je o kompletní revizi **celého projektu** (nejen posledních úprav). Hledají logické chyby, bezpečnostní rizika (SSRF, path traversal) a soulad s lokálními konvencemi.
2. **Fáze B: Porovnání a Diskuse (Konsensus)**
   - Nech oba modely porovnat své nálezy, prodiskutovat nejvhodnější nápravu a dohodnout se na jednotném, bezpečném postupu oprav.
3. **Fáze C: Bačova revize a Onboarding**
   - Obdržíš od nich společný report: Co přesně našli a jak to plánují opravit.
   - **Tvoje povinnost:** Pečlivě si report prostuduj, pochop příčinu chyb, abys je příště zachytil sám ještě před jejich kontrolou.
4. **Fáze D: Zelená k bezpečnému fixu**
   - Pokud je jejich plánovaný postup bezpečný a zachovává integritu projektu, dej jim zelenou k provedení oprav.
5. **Fáze E: Finální verifikace**
   - Počkej, až opravy provedou. Ověř, že vše proběhlo přesně podle schváleného plánu, a spusť unit testy (`uv run python -m pytest`). Teprve při 100% úspěchu se můžeš ozvat Milhymu, že je hotovo.

### 🛠 Technické detaily
- Spouštěj modely přes `pi` CLI (nebo wrapper `agy`).
- Ujisti se, že pro vysoce kontextovou analýzu celého projektu využíváš **Mimo** s jejím 1M kontextovým oknem.
