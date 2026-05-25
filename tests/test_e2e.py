import pytest
import os
import shutil
from pathlib import Path
from app.main import app
from typer.testing import CliRunner

runner = CliRunner()

def test_e2e_sync_flow(tmp_path):
    # 1. Setup Mock Kindle
    kindle_root = tmp_path / "mock_kindle"
    kindle_root.mkdir()
    docs = kindle_root / "documents"
    docs.mkdir()
    
    # Create some unorganized files
    book1 = docs / "Test_Book.azw3"
    book1.touch()
    
    # 2. Run Sync Command (injecting mock path)
    os.environ["KINDLE_BUTLER_MOCK_PATH"] = str(kindle_root)
    
    # Disable AI for basic E2E to avoid API calls and check logic
    result = runner.invoke(app, ["sync", "--no-use-ai"])
    
    assert result.exit_code == 0
    
    # 3. Verify Results
    # With AI disabled, it uses 'Unknown' (from MetadataExtractor)
    unknown_dir = docs / "Unknown"
    assert unknown_dir.exists()
    assert (unknown_dir / "Test_Book.azw3").exists()
