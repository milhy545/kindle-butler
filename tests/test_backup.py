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
