import pytest
import shutil
from pathlib import Path
from app.organizer import KindleOrganizer

def test_backup_creation(tmp_path):
    # Setup mock Kindle
    docs = tmp_path / "documents"
    docs.mkdir()
    book = docs / "SafeBook.azw3"
    book.write_text("content")
    
    organizer = KindleOrganizer(tmp_path)
    backup_path = organizer.create_backup(book)
    
    assert backup_path.exists()
    assert backup_path.read_text() == "content"
    assert ".butler_backup" in str(backup_path)
    # Check if name contains hash prefix
    assert "SafeBook.azw3" in backup_path.name
    assert len(backup_path.name) > len("SafeBook.azw3")

def test_backup_with_sdr(tmp_path):
    docs = tmp_path / "documents"
    docs.mkdir()
    book = docs / "SafeBook.azw3"
    book.write_text("content")
    sdr = docs / "SafeBook.azw3.sdr"
    sdr.mkdir()
    (sdr / "meta").touch()
    
    organizer = KindleOrganizer(tmp_path)
    organizer.create_backup(book)
    
    # Find the backup SDR (it will have a hash prefix)
    backup_dir = tmp_path / ".butler_backup"
    backup_sdrs = list(backup_dir.glob("*SafeBook.azw3.sdr"))
    assert len(backup_sdrs) == 1
    assert (backup_sdrs[0] / "meta").exists()


def test_repeated_backup_preserves_different_versions(tmp_path):
    docs = tmp_path / "documents"
    docs.mkdir()
    book = docs / "SafeBook.azw3"
    book.write_text("first", encoding="utf-8")

    organizer = KindleOrganizer(tmp_path)
    first_backup = organizer.create_backup(book)

    book.write_text("second", encoding="utf-8")
    second_backup = organizer.create_backup(book)

    assert first_backup != second_backup
    assert first_backup.read_text(encoding="utf-8") == "first"
    assert second_backup.read_text(encoding="utf-8") == "second"


def test_existing_target_sdr_is_backed_up_before_replacement(tmp_path):
    docs = tmp_path / "documents"
    source_dir = docs / "Incoming"
    target_dir = docs / "Author"
    source_dir.mkdir(parents=True)
    target_dir.mkdir()

    source_book = source_dir / "Book.azw3"
    source_book.write_text("new", encoding="utf-8")
    source_sdr = source_dir / "Book.azw3.sdr"
    source_sdr.mkdir()
    (source_sdr / "state").write_text("new-state", encoding="utf-8")

    target_sdr = target_dir / "Book.azw3.sdr"
    target_sdr.mkdir()
    (target_sdr / "state").write_text("old-state", encoding="utf-8")

    organizer = KindleOrganizer(tmp_path)
    organizer.organize_file(source_book, "Author")

    backup_sdrs = list((tmp_path / ".butler_backup").glob("*Book.azw3.sdr"))
    assert backup_sdrs
    assert any((backup / "state").read_text(encoding="utf-8") == "old-state" for backup in backup_sdrs)
    assert (target_sdr / "state").read_text(encoding="utf-8") == "new-state"
