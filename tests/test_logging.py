import pytest
import os
from app.main import app, get_log_path
from typer.testing import CliRunner

runner = CliRunner()

def test_auto_sync_logging(tmp_path):
    # Setup mock Kindle
    kindle_root = tmp_path / "mock_kindle"
    kindle_root.mkdir()
    docs = kindle_root / "documents"
    docs.mkdir()
    (docs / "Book.pdf").touch()
    
    os.environ["KINDLE_BUTLER_MOCK_PATH"] = str(kindle_root)
    log_file = get_log_path(str(kindle_root))
    
    # Run with --auto flag
    result = runner.invoke(app, ["sync", "--auto", "--no-use-ai"])
    
    assert result.exit_code == 0
    assert log_file.exists()
    
    log_content = log_file.read_text()
    assert "Butler Smart Sync Start" in log_content
    assert "Found 1 documents" in log_content
    assert "Organization complete" in log_content
