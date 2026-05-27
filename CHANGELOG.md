# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-05-27

### Added
- **Core Sync:** Plug & play logic for scanning and organizing documents (`.pdf`, `.epub`, `.azw3`, `.mobi`, `.kfx`) based on metadata.
- **AI Normalization:** Integration with Gemini 1.5 Flash to automatically fix and normalize messy titles and author names.
- **Backup System:** Automatic creation of hidden `backups/` locally or `.butler_backup` on the device before moving or modifying any files, preventing data loss.
- **Metadata Management:** Moving and organizing associated `.sdr` folders along with their documents.
- **CLI Interface:** A robust command-line interface based on `typer` featuring:
  - `start`: Interactive menu.
  - `sync`: Automatic, non-interactive library organization.
  - `check`: Health check for dependencies, APIs, and the connected Kindle.
  - `email`: Direct sending of documents via email using SMTP.
  - `enhance`: AI content translation and formatting (EPUB).
  - `process`: Markdown to AZW3 conversion with optional translation.
  - `sync-wifi`: Remote synchronization via SSH/rsync, including library rescan trigger.
- **Security:** Strict separation of configuration and secrets. Passwords and API keys are stored with `0600` permissions.

### Changed
- Improved overall CLI test coverage to ~72%.
- Streamlined documentation (`README.md` and `README.cz.md`) to reflect the locked v1.0.0 scope.

### Fixed
- Fixed issues with missing dependencies and incorrect tool calls.
- Completed security audits (Bandit & pip-audit) reporting 0 vulnerabilities.
