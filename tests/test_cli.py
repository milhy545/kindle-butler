from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from app.main import app
import os
from pathlib import Path

runner = CliRunner()

def test_app_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "Kindle Butler version" in result.stdout

def test_app_sync_output():
    # Only test the basic string output
    result = runner.invoke(app, ["sync"])
    assert "Sync Start" in result.stdout

@patch("app.main.KindleDetector")
def test_app_check_no_kindle(mock_detector_class):
    mock_detector = MagicMock()
    mock_detector.find_kindle_path.return_value = None
    mock_detector_class.return_value = mock_detector

    result = runner.invoke(app, ["check"])
    assert result.exit_code == 0
    assert "Kontrola systému" in result.stdout
    assert "Kindle nebyl nalezen" in result.stdout

@patch("app.main.KindleDetector")
def test_app_check_with_kindle(mock_detector_class):
    mock_detector = MagicMock()
    mock_detector.find_kindle_path.return_value = "/mnt/kindle"
    mock_detector_class.return_value = mock_detector

    result = runner.invoke(app, ["check"])
    assert result.exit_code == 0
    assert "Kindle nalezen v: /mnt/kindle" in result.stdout

@patch("app.main.ContentProcessor")
@patch("app.main.AIClient")
def test_app_process_success(mock_ai_class, mock_processor_class, tmp_path):
    mock_processor = MagicMock()
    mock_processor.translate_markdown.return_value = tmp_path / "translated.md"
    mock_processor.convert_markdown_to_epub.return_value = True
    mock_processor_class.return_value = mock_processor

    source = tmp_path / "test.md"
    source.write_text("# Test", encoding="utf-8")

    result = runner.invoke(app, ["process", str(source)])
    assert result.exit_code == 0
    assert "Hotovo:" in result.stdout

def test_app_process_invalid_file():
    result = runner.invoke(app, ["process", "nonexistent.txt"])
    assert result.exit_code == 1
    assert "Zadaný soubor neexistuje nebo není ve formátu Markdown" in result.stdout

@patch("smtplib.SMTP")
@patch("app.main.ButlerConfig")
def test_app_email_success(mock_config_class, mock_smtp_class, tmp_path):
    mock_config = MagicMock()
    mock_config.load.return_value = {
        "kindle_email": "test@kindle.com",
        "smtp_user": "user@gmail.com",
        "smtp_pass": "pass"
    }
    mock_config.get.return_value = "dummy"
    mock_config.get_env.return_value = "dummy"
    mock_config_class.return_value = mock_config

    mock_smtp = MagicMock()
    mock_smtp_class.return_value.__enter__.return_value = mock_smtp

    # Setup dummy downloads dir
    downloads_dir = tmp_path / "Downloads"
    downloads_dir.mkdir()
    (downloads_dir / "test.epub").write_text("dummy", encoding="utf-8")

    with patch("app.main.Path.home", return_value=tmp_path):
        # Provide input "0" or "vse"
        result = runner.invoke(app, ["email"], input="vse\ny\n")
        assert result.exit_code == 0
        assert "Odesláno: test.epub" in result.stdout

@patch("app.main.ButlerConfig")
@patch("app.main.Path.home")
def test_app_email_no_downloads(mock_home, mock_config_class, tmp_path):
    mock_home.return_value = tmp_path
    
    mock_config = MagicMock()
    mock_config.load.return_value = {
        "kindle_email": "test@kindle.com",
        "smtp_user": "user@gmail.com",
        "smtp_pass": "pass"
    }
    mock_config.get_env.return_value = "dummy"
    mock_config_class.return_value = mock_config

    # No Downloads folder created
    result = runner.invoke(app, ["email"])
    assert "nebyla" in result.stdout

@patch("app.main.ButlerConfig")
@patch("app.main.KindleDetector")
@patch("app.main.Path.home")
def test_app_start_exit(mock_home, mock_detector, mock_config_class, tmp_path):
    # Just to check if start triggers correctly and exits on choice
    mock_home.return_value = tmp_path
    
    mock_config = MagicMock()
    mock_config.load.return_value = {"provider": "Gemini"}
    mock_config.get_env.return_value = "dummy"
    mock_config_class.return_value = mock_config
    
    with patch.dict(os.environ, {"LLM_API_KEY": "dummy"}):
        result = runner.invoke(app, ["start"], input="konec\n")
        assert result.exit_code == 0
        assert "Měj se, Milhy!" in result.stdout
