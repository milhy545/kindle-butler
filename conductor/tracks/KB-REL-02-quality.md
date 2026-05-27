# Track: KB-REL-02 - Dotáhnout kvalitu kódu

## Objective
Zvýšit pokrytí testy (coverage), primárně na slabších místech jako CLI a konfigurace, a udržet existující testy funkční.

## Key Files & Context
- `src/kindle_butler/cli.py` (či ekvivalentní CLI moduly)
- `src/kindle_butler/config.py`
- `tests/` adresář

## Implementation Steps
1. **Analýza pokrytí:**
   - Spustit pytest s pluginem coverage (`pytest --cov`).
   - Identifikovat moduly s nízkým pokrytím, se zaměřením na zpracování konfigurace a CLI vstupy.
2. **Doplnění testů pro CLI:**
   - Napsat testy pro chybové stavy CLI (např. chybějící parametry, neplatné cesty).
   - Otestovat chování při parsování různých konfiguračních voleb.
3. **Doplnění testů pro konfiguraci:**
   - Otestovat načítání validní i invalidní konfigurace.
   - Otestovat fallbacky a defaultní hodnoty.
4. **Validace stávajících funkcí:**
   - Ujistit se, že všechny regresní testy pro backupy, secrets a EPUB sanitizaci prochází bez chyb.

## Verification & Testing
- Zvýšení celkového coverage procenta.
- Moduly CLI a Config mají uspokojivé pokrytí kódových cest.
- Příkaz `pytest` projde úspěšně se všemi 39+ testy.