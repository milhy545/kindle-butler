import pytest
from pathlib import Path
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from app.main import app
import os

runner = CliRunner()

@patch("app.main.ContentProcessor")
@patch("app.main.ButlerConfig")
def test_enhance_command(mock_config_class, mock_processor_class, tmp_path):
    # Setup mock config
    mock_config = MagicMock()
    mock_config.get_env.return_value = "fake-key"
    mock_config_class.return_value = mock_config

    # Setup mock processor
    mock_processor = MagicMock()
    mock_processor_class.return_value = mock_processor
    mock_processor.process_epub.return_value = tmp_path / "[ENHANCED]_test.epub"

    # Create dummy epub file
    dummy_epub = tmp_path / "test.epub"
    dummy_epub.touch()

    # Run command
    result = runner.invoke(app, ["enhance", str(dummy_epub), "--target-lang", "en"])
    
    assert result.exit_code == 0
    assert "AI Vylepšení obsahu" in result.stdout
    assert "Dokument úspěšně vylepšen" in result.stdout

def test_enhance_missing_file():
    result = runner.invoke(app, ["enhance", "nonexistent.epub"])
    assert result.exit_code == 1
    assert "Zadaný soubor neexistuje nebo není ve formátu EPUB" in result.stdout

@patch("app.main.ButlerConfig")
def test_enhance_missing_api_key(mock_config_class, tmp_path):
    mock_config = MagicMock()
    mock_config.get_env.return_value = None
    mock_config_class.return_value = mock_config

    dummy_epub = tmp_path / "test.epub"
    dummy_epub.touch()

    result = runner.invoke(app, ["enhance", str(dummy_epub)])
    assert result.exit_code == 1
    assert "Chybí LLM_API_KEY (nebo GEMINI_API_KEY) pro AI vylepšení" in result.stdout

@patch("app.main.ContentProcessor")
@patch("app.main.ButlerConfig")
def test_enhance_with_env_key(mock_config_class, mock_processor_class, tmp_path):
    # Mock config to return None, but set environment variable
    mock_config = MagicMock()
    mock_config.get_env.return_value = None
    mock_config_class.return_value = mock_config

    mock_processor = MagicMock()
    mock_processor_class.return_value = mock_processor
    mock_processor.process_epub.return_value = tmp_path / "[ENHANCED]_test.epub"

    dummy_epub = tmp_path / "test.epub"
    dummy_epub.touch()

    with patch.dict(os.environ, {"GEMINI_API_KEY": "env-key"}):
        result = runner.invoke(app, ["enhance", str(dummy_epub)])
        assert result.exit_code == 0
        assert "AI Vylepšení obsahu" in result.stdout
