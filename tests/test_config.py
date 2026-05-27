import json
import pytest
from app.config import ButlerConfig

def test_config_save_does_not_persist_secret_values(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    config = ButlerConfig()

    config.save({
        "provider": "Gemini",
        "smtp_user": "sender@example.com",
        "smtp_pass": "secret-password",
        "kindle_email": "reader@kindle.com",
    })

    saved = json.loads(config.config_file.read_text(encoding="utf-8"))
    assert saved["provider"] == "Gemini"
    assert saved["kindle_email"] == "reader@kindle.com"
    assert "smtp_user" not in saved
    assert "smtp_pass" not in saved

def test_config_load_defaults_if_not_exists(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    config = ButlerConfig()
    
    loaded = config.load()
    assert loaded["provider"] is None
    assert loaded["smtp_server"] == "smtp.gmail.com"
    assert loaded["smtp_port"] == 587

def test_config_load_merges_with_defaults(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    config = ButlerConfig()
    
    # Write a partial config
    config.config_file.write_text(json.dumps({"provider": "OpenAI", "custom_key": "custom_val"}), encoding="utf-8")
    
    loaded = config.load()
    assert loaded["provider"] == "OpenAI"
    assert loaded["custom_key"] == "custom_val"
    assert loaded["smtp_port"] == 587 # Default

def test_config_set_and_get_env(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    config = ButlerConfig()
    
    assert config.get_env("LLM_API_KEY") is None
    
    config.set_env("LLM_API_KEY", "my-secret-key")
    assert config.get_env("LLM_API_KEY") == "my-secret-key"
    
    # Test update
    config.set_env("LLM_API_KEY", "new-secret-key")
    assert config.get_env("LLM_API_KEY") == "new-secret-key"
    
    # Test multiple keys
    config.set_env("OTHER_KEY", "other-val")
    assert config.get_env("OTHER_KEY") == "other-val"
    assert config.get_env("LLM_API_KEY") == "new-secret-key"
