from subprocess import CalledProcessError
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from app.content_processor import ContentProcessor
from app.main import app


runner = CliRunner()


def test_process_exits_nonzero_when_conversion_fails(tmp_path):
    source = tmp_path / "manual.md"
    source.write_text("# Manual\n", encoding="utf-8")

    with patch("app.main.ContentProcessor") as mock_processor_class:
        mock_processor = MagicMock()
        mock_processor.convert_markdown_to_epub.return_value = False
        mock_processor_class.return_value = mock_processor

        result = runner.invoke(app, ["process", str(source), "--no-translate"])

    assert result.exit_code == 1
    assert "Konverze selhala" in result.stdout


def test_sync_wifi_rejects_unsafe_host():
    with patch("app.main.subprocess.run") as mock_run:
        result = runner.invoke(app, ["sync-wifi", "192.168.0.59;touch /tmp/pwned"])

    assert result.exit_code == 1
    mock_run.assert_not_called()


def test_sync_wifi_uses_argument_lists_and_checks_failures(tmp_path):
    source_dir = tmp_path / "sync_stage"
    source_dir.mkdir()
    (source_dir / "book.azw3").write_text("content", encoding="utf-8")

    with patch("app.main.DEFAULT_SYNC_STAGE", source_dir), patch("app.main.subprocess.run") as mock_run:
        mock_run.side_effect = CalledProcessError(255, ["ssh"])

        result = runner.invoke(app, ["sync-wifi", "192.168.0.59"])

    assert result.exit_code == 1
    assert mock_run.call_args.kwargs["check"] is True
    assert "shell" not in mock_run.call_args.kwargs


def test_sync_wifi_does_not_delete_remote_files_by_default(tmp_path):
    source_dir = tmp_path / "sync_stage"
    source_dir.mkdir()
    (source_dir / "book.azw3").write_text("content", encoding="utf-8")

    with patch("app.main.DEFAULT_SYNC_STAGE", source_dir), patch("app.main.subprocess.run") as mock_run:
        result = runner.invoke(app, ["sync-wifi", "192.168.0.59"])

    assert result.exit_code == 0
    rsync_args = mock_run.call_args_list[1].args[0]
    assert rsync_args[0] == "rsync"
    assert "--delete" not in rsync_args


def test_translate_markdown_uses_unique_temp_file(tmp_path):
    source = tmp_path / "manual.md"
    source.write_text("# Manual\n", encoding="utf-8")
    existing = tmp_path / "[TRANSLATED]_manual.md"
    existing.write_text("keep me", encoding="utf-8")

    ai_client = MagicMock()
    ai_client.enhance_content.return_value = "# Prelozeno\n"

    translated = ContentProcessor(ai_client=ai_client).translate_markdown(source)

    assert translated != existing
    assert translated.read_text(encoding="utf-8") == "# Prelozeno\n"
    assert existing.read_text(encoding="utf-8") == "keep me"
