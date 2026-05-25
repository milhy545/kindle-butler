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
            "smtp_pass": None
        }
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                data = json.load(f)
                # Merge defaults for backward compatibility
                for k, v in default_config.items():
                    data.setdefault(k, v)
                return data
        return default_config

    def save(self, config: Dict[str, Any]):
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)

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
            
        with open(self.env_file, "w") as f:
            f.writelines(new_lines)
        self.env_file.chmod(0o600)

    def get_env(self, key: str) -> Optional[str]:
        if not self.env_file.exists():
            return None
        with open(self.env_file, "r") as f:
            for line in f:
                if line.startswith(f"{key}="):
                    return line.split("=", 1)[1].strip()
        return None
