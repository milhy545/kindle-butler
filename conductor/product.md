# Product Definition: Kindle Butler

Kindle Butler is an autonomous, smart librarian for Kindle Gen 7+ devices. It aims to eliminate the friction of managing a messy Kindle library by providing host-side automation that triggers upon USB connection or via Wi-Fi (SSH).

## Target Audience
Stanislav "Milhy" Muller and other Kindle power users who want a clean library without manual intervention.

## v1.0.0 Release Scope (Locked)
Tento release se zaměřuje na core funkcionalitu, organizaci a bezpečnost dat.
Zahrnuté funkce pro v1.0.0:
- **Core Sync & Directory Organization:** Organizace souborů podle extrahovaných a AI-normalizovaných metadat do složek (`documents/Author/Book.ext`) vč. `.sdr` složek.
- **Safety (Backup-first):** Vytváření záloh před přesunem lokálních souborů do adresáře `backups/`.
- **CLI rozhraní:** Plně funkční CLI (`start`, `sync`, `check`, `email`, `enhance`, `process`, `sync-wifi`).
- **AI Content Enhancer:** Vylepšení obsahu (překlad EPUB, převod Markdown do AZW3).
- **Wi-Fi Sync:** Synchronizace připravených souborů na Kindle pomocí rsync a SSH.
- **Email Delivery:** Odesílání dokumentů přímo na Kindle email.

Věci **mimo** scope v1.0.0 (odloženo):
- Nativní UDEV trigger a desktop notifikace (plánováno pro další minor release, aktuálně uživatel spouští manuálně/cron).
- Komplexní jailbreak integrace nebo modifikace systémových souborů Kindle nad rámec dokumentů.
- Calibre/Pandoc komplexní integrace.

## Core Features
1. **Host-Side Synchronization:** Organizace knihovny po připojení (USB) nebo bezdrátově.
2. **Metadata Intelligence:**
    - Extraction of Author/Title from PDF, AZW3, MOBI, EPUB.
    - AI-powered normalization (cleaning up "Author - Title" strings into standardized formats).
3. **Directory Organization:** Moving files into `documents/Author/Book.ext` structure, including associated `.sdr` metadata folders.
4. **Safety & Robustness:**
    - "Backup-first" principle.
    - Path sanitization to prevent filesystem escape.
5. **Interactive & Automated Modes:** A CLI that supports both interactive "onboarding" and fully automated "sync" runs.
6. **Content Processing:**
    - AI Translation of EPUB documents.
    - Markdown to AZW3 translation and conversion.

## Success Criteria
- [ ] 100% of books are moved to correct author folders without damaging .sdr structures.
- [ ] Zero data loss (verified by backup presence).
- [ ] Odesílání a Wi-Fi sync fungují spolehlivě na otestovaném prostředí.
