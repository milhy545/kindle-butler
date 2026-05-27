# Track: KB-REL-05 - Udělat skutečný device smoke test

## Objective
Ověřit funkčnost end-to-end nasazením nebo simulací na reálných datech z Kindle (fyzickém nebo namockovaném mountu).

## Key Files & Context
- Skripty a moduly zapojené do synchronizace s Kindle mount adresářem.
- Testovací / mockované e-knihy.

## Implementation Steps
1. **Příprava testovacího prostředí:**
   - Nastavit mockovaný adresář reprezentující připojený Kindle (s pár ukázkovými e-knihami a `.sdr` složkami), nebo připojit reálné testovací zařízení.
2. **Testování End-to-End scénáře:**
   - Provést celý proces: Backup původních souborů, sync, procesování nového EPUBu.
   - Zkontrolovat logiku "backup-first" - ujistit se, že byly vytvořeny správné zálohy před jakýmkoliv zásahem.
3. **Validace dat:**
   - Zkontrolovat, že výsledné soubory a metadata nebyly poškozeny (např. kontrola validity EPUBu/MOBI).
   - Ověřit funkčnost Wi-Fi syncu (pokud je podporován).

## Verification & Testing
- Záznamy z běhu prokazují, že všechny kroky E2E prošly bez chyb.
- Výsledné adresáře (záloha i "Kindle" mount) obsahují očekávaná data v intaktním stavu.