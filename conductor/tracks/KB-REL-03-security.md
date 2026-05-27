# Track: KB-REL-03 - Uzavřít bezpečnostní a datové riziko

## Objective
Zajistit bezpečnost aplikace tím, že nedochází k úniku citlivých dat (secrets) a že zápisové operace nepoškozují data uživatele.

## Key Files & Context
- Moduly řešící logování a konfiguraci.
- Moduly provádějící zápis do `kindle/` a `.sdr` složek.

## Implementation Steps
1. **Audit úniku secrets:**
   - Zkontrolovat všechny výstupy logování a serializace configů (např. export do JSON).
   - Zjistit, zda maskování API klíčů funguje plošně.
2. **Ověření I/O operací nad Kindle daty:**
   - Zkontrolovat logiku pro manipulaci s Kindle soubory a SDR složkami.
   - Ošetřit případné edge-cases při chybách v zápisu (aby nezůstal rozbitý stav).
3. **Bezpečnostní audit kódu a závislostí:**
   - Spustit `bandit -r src` k detekci bezpečnostních anti-patternů v kódu.
   - Spustit `pip-audit` k detekci zranitelných knihoven třetích stran.

## Verification & Testing
- `bandit` report je čistý (bez reálných nálezů).
- `pip-audit` nevykazuje žádné kritické zranitelnosti.
- Vygenerované logy a chybové zprávy neobsahují zjevně tajná data.