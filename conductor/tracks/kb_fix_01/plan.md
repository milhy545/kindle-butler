# Implementation Plan: KB-FIX-01 - Stabilize CLI & Address Diagnostics

The goal of this track is to reconcile the discrepancy between the implemented CLI and the test suite, while addressing critical security and robustness findings from the diagnostics report.

## Phase 1: CLI Contract Alignment (Fix F-1)
- [ ] Task: Update `app/main.py` to include `sync`, `check`, and version options.
- [ ] Task: Ensure `sync` command supports `--auto` and `--no-use-ai` flags (even if dummy/proxied).
- [ ] Task: Verify with `uv run python -m app.main --help` and existing tests.

## Phase 2: Test Infrastructure & Security (Fix F-2, S-1, S-2)
- [ ] Task: Fix test shims or update `AGENTS.md` to use `python -m pytest`.
- [ ] Task: Implement path sanitization for author directory names in `app/organizer.py`.
- [ ] Task: Update backup logic in `app/organizer.py` to use collision-safe filenames (e.g., hash or original relative path).
- [ ] Task: Write regression tests for malicious metadata path traversal.

## Phase 3: Robustness & Diagnostics (Fix S-3, S-4, S-5)
- [ ] Task: Update "Import" command to use copy-then-verify instead of destructive move.
- [ ] Task: Replace silent `except: pass` in `app/metadata.py` with structured logging.
- [ ] Task: Review and harden `scripts/install_host.sh` (shell mode, quoting, askpass sudo).

## Phase 4: Verification
- [ ] Task: Run full test suite: `uv run python -m pytest --cov=app`.
- [ ] Task: Re-run `PROJECT_DIAGNOSTICS.md` verification steps.
- [ ] Task: Conductor - User Manual Verification (Final stability check).
