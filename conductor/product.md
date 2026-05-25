# Product Definition: Kindle Butler

Kindle Butler is an autonomous, smart librarian for Kindle Gen 7+ devices. It aims to eliminate the friction of managing a messy Kindle library by providing host-side automation that triggers upon USB connection.

## Target Audience
Stanislav "Milhy" Muller and other Kindle power users who want a clean library without manual intervention.

## Core Features
1. **Plug & Play Synchronization:** Automatic detection of Kindle via USB (udev) and immediate organization.
2. **Metadata Intelligence:**
    - Extraction of Author/Title from PDF, AZW3, MOBI, EPUB.
    - AI-powered normalization (cleaning up "Author - Title" strings into standardized formats).
3. **Directory Organization:** Moving files into `documents/Author/Book.ext` structure, including associated `.sdr` metadata folders.
4. **Safety & Robustness:**
    - "Backup-first" principle: all files are backed up to a hidden `.butler_backup` folder on the Kindle before moving.
    - Collision-safe filenames.
    - Path sanitization to prevent filesystem escape.
5. **Interactive & Automated Modes:** A CLI that supports both interactive "onboarding" and fully automated "sync" runs.
6. **AI Enhancements (Future):**
    - Translation of technical documents.
    - Reformatting of tables/lists into readable text for E-Ink.
    - Conversion to native Kindle formats (KFX/AZW3).

## Success Criteria
- [ ] USB connection triggers a desktop notification and starts organization.
- [ ] 100% of books are moved to correct author folders.
- [ ] Zero data loss (verified by backup presence).
- [ ] Fast performance even with hundreds of books.
