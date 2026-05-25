import pytest
import os
from app.organizer import KindleOrganizer

def test_scan_documents(tmp_path):
    # Setup mock Kindle structure
    documents = tmp_path / "documents"
    documents.mkdir()
    (documents / "Author1").mkdir()
    (documents / "Author1" / "Book1.azw3").touch()
    (documents / "Book2.pdf").touch()
    
    organizer = KindleOrganizer(tmp_path)
    files = organizer.scan_documents()
    
    assert len(files) == 2
    assert any(f.name == "Book1.azw3" for f in files)
    assert any(f.name == "Book2.pdf" for f in files)

def test_organize_by_author(tmp_path):
    documents = tmp_path / "documents"
    documents.mkdir()
    book = documents / "BookByAuthor.azw3"
    book.touch()
    
    organizer = KindleOrganizer(tmp_path)
    # Simulate finding author metadata
    organizer.organize_file(book, "Famous Author")
    
    target_path = documents / "Famous Author" / "BookByAuthor.azw3"
    assert target_path.exists()
    assert not book.exists()

def test_path_sanitization(tmp_path):
    documents = tmp_path / "documents"
    documents.mkdir()
    book = documents / "Dirty_Meta.azw3"
    book.touch()
    
    organizer = KindleOrganizer(tmp_path)
    
    # Test with dangerous author name (path traversal)
    organizer.organize_file(book, "../../etc/passwd")
    
    # Should be sanitized to something safe
    safe_dir = documents / "etc_passwd"
    assert safe_dir.exists()
    assert (safe_dir / "Dirty_Meta.azw3").exists()

def test_path_sanitization_null_byte(tmp_path):
    documents = tmp_path / "documents"
    documents.mkdir()
    book = documents / "Null_Meta.azw3"
    book.touch()
    
    organizer = KindleOrganizer(tmp_path)
    
    # Test with null byte
    organizer.organize_file(book, "Author\0Name")
    
    safe_dir = documents / "AuthorName"
    assert safe_dir.exists()
