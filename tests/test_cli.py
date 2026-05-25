from typer.testing import CliRunner
from app.main import app

runner = CliRunner()

def test_app_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "Kindle Butler version" in result.stdout

def test_app_sync_output():
    # This test will run against the ACTUAL system if not mocked, 
    # but for CLI verification we just check the structure.
    # Note: test_e2e.py handles the mocked flow.
    result = runner.invoke(app, ["sync"])
    # We don't assert 0 here because it might fail if Kindle is not connected
    assert "Sync Start" in result.stdout
