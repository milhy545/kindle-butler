# Implementation Plan: KB-AI-01 - AI Content Enhancer

Cílem tohoto tracku je přidat schopnost číst obsah e-knih (pro MVP začneme s formátem EPUB, jelikož je vnitřně založen na HTML a lze s ním dobře manipulovat v Pythonu přes `EbookLib`/`BeautifulSoup`), posílat jej přes AI Clienta k překladu a přeformátování, a následně vygenerovat vylepšenou verzi knihy.

## Phase 1: Core AI Processing Service
- [x] Úkol: Rozšířit `app/ai_client.py` o metodu `enhance_content(text: str, target_lang: str = "cs")`.
- [x] Úkol: Navrhnout systémový prompt pro LLM (Gemini), který vynutí:
  1. Překlad do cílového jazyka.
  2. Převod odrážek a tabulek do souvislého, plynulého textu.
  3. Připojení původních technických dat (seznamů) na konec zpracovávané sekce.
- [x] Úkol: Napsat testy s mockovaným LLM výstupem.

## Phase 2: Zpracování dokumentů (EPUB)
- [x] Úkol: Vytvořit modul `app/content_processor.py`.
- [x] Úkol: Napsat funkci pro bezpečné rozbalení EPUBu, iteraci přes HTML/XHTML kapitoly a extrakci textu.
- [x] Úkol: Implementovat "chunking" (dělení textu), aby se nepřekročil context window limit u velkých knih.
- [x] Úkol: Funkce pro zpětné sestavení (repack) upraveného EPUBu do nového souboru (např. `[ENHANCED]_Book.epub`).
- [x] Úkol: Napsat testy na proces extrakce a repackingu.

## Phase 3: CLI Integrace a UX
- [x] Úkol: Přidat nový příkaz `enhance` do `app/main.py` (`uv run python -m app.main enhance <cesta_k_souboru>`).
- [x] Úkol: Implementovat vizuální zpětnou vazbu pomocí knihovny Rich (např. progress bar pro jednotlivé kapitoly), protože LLM operace budou trvat déle.

## Phase 4: Verifikace
- [x] Úkol: Vyzkoušet e2e test na ukázkovém technickém dokumentu s odrážkami (vytvoříme dummy epub v testech).
- [x] Úkol: Ověřit, že testovací suite stále prochází (`uv run python -m pytest`) a coverage je zachována.
