# Track: KB-REL-01 - Zamknout scope release

## Objective
Jasně definovat a uzamknout scope pro první release. Oddělit hotové funkce od rozpracovaných a vyčistit repozitář.

## Key Files & Context
- Celý repozitář (hlavně kořenový adresář a kódy aplikace)
- `.gitignore`
- Pracovní (untracked) soubory a dočasné artefakty

## Implementation Steps
1. **Analýza aktuálního stavu repozitáře:**
   - Prozkoumat nesledované a změněné soubory pomocí `git status`.
   - Zkontrolovat přítomnost dočasných souborů nebo logů, které nepatří do releasu.
2. **Vyčištění pracovního adresáře:**
   - Smazat nebo přesunout dočasné artefakty (např. testovací mock soubory mimo test adresář).
   - Aktualizovat `.gitignore`, pokud chybí pravidla pro dočasné soubory vygenerované během vývoje.
3. **Definice Release Scope:**
   - Napsat stručné shrnutí funkcí, které jsou součástí tohoto releasu (Core Sync, Backup, EPUB processing atd.).
   - Odstranit/skrýt z uživatelského rozhraní (CLI) funkce, které jsou rozpracované a nejsou součástí releasu.

## Verification & Testing
- Spuštění `git status` vrátí čistý stav bez zbytečných untracked souborů.
- CLI nezobrazuje rozpracované/nekompletní funkce v nápovědě.
- Repozitář je čistý a připravený na další fázi.