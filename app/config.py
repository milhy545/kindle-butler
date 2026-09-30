import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

class ButlerConfig:
    """
    Handles Butler configuration on the host PC.
    """
    def __init__(self):
        self.config_dir = Path.home() / ".config/kindle-butler"
        self.config_file = self.config_dir / "config.json"
        self.env_file = self.config_dir / "env"
        self._ensure_dir()
        self.secret_keys = {"smtp_user", "smtp_pass", "llm_api_key", "gemini_api_key"}

    def _ensure_dir(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def load(self) -> Dict[str, Any]:
        default_config = {
            "provider": None,
            "auth_method": None,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "kindle_email": None,
            "smtp_user": None,
            # Placeholder key only; real secret values are stored in env.
            "smtp_pass": None,  # nosec B105
            "ollama_host": "http://localhost:11434",
            "ollama_metadata_model": "qwen2.5:3b",
            "ollama_enhance_model": "mistral:7b"
        }
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                data = json.load(f)
                # Merge defaults for backward compatibility
                for k, v in default_config.items():
                    data.setdefault(k, v)
                
                # Propagate config to environments for AI client
                for key in ["ollama_host", "ollama_metadata_model", "ollama_enhance_model"]:
                    env_key = f"KINDLE_BUTLER_{key.upper()}"
                    if env_key not in os.environ and data.get(key):
                        os.environ[env_key] = str(data[key])
                return data
        
        # If config doesn't exist, propagate defaults
        for key in ["ollama_host", "ollama_metadata_model", "ollama_enhance_model"]:
            env_key = f"KINDLE_BUTLER_{key.upper()}"
            if env_key not in os.environ:
                os.environ[env_key] = default_config[key]
        return default_config

    def save(self, config: Dict[str, Any]):
        public_config = {
            key: value
            for key, value in config.items()
            if key.lower() not in self.secret_keys
        }
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(public_config, f, indent=2)
        self.config_file.chmod(0o600)

    def set_env(self, key: str, value: str):
        # We store the actual secrets in the env file
        lines = []
        if self.env_file.exists():
            with open(self.env_file, "r") as f:
                lines = f.readlines()
        
        # Update or add
        updated = False
        new_lines = []
        for line in lines:
            if line.startswith(f"{key}="):
                new_lines.append(f"{key}={value}\n")
                updated = True
            else:
                new_lines.append(line)
        
        if not updated:
            new_lines.append(f"{key}={value}\n")
            
        # Secure file creation with 0600 mode from the start to prevent race conditions
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
        fd = os.open(self.env_file, flags, 0o600)
        with os.fdopen(fd, "w") as f:
            f.writelines(new_lines)

    def get_env(self, key: str) -> Optional[str]:
        if not self.env_file.exists():
            return None
        with open(self.env_file, "r") as f:
            for line in f:
                if line.startswith(f"{key}="):
                    return line.split("=", 1)[1].strip()
        return None
