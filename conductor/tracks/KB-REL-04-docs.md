# Track: KB-REL-04 - Srovnat dokumentaci s realitou

## Objective
Aktualizovat veškerou dokumentaci (README, changelog) tak, aby přesně odrážela současný otestovaný stav aplikace.

## Key Files & Context
- `README.md`
- `CHANGELOG.md` nebo release notes dokumenty.

## Implementation Steps
1. **Revize README.md:**
   - Projít sekce instalace a použití.
   - Srovnat popsané příkazy s aktuálním stavem CLI.
   - Odstranit zmínky o funkcích, které nebyly zahrnuty do release scope.
2. **Příprava Release Notes:**
   - Vytvořit changelog/release note pro tuto verzi.
   - Shrnout klíčové přidání a vylepšení (Core Sync, Backup, AI Formatting).
3. **Synchronizace jazykových mutací:**
   - Pokud existuje česká verze dokumentace, zajistit její překlad a 1:1 shodu s anglickým README.

## Verification & Testing
- Návody v README přesně odpovídají aktuální funkčnosti aplikace.
- Existuje jasný changelog pro nadcházející tag.