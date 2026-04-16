import os
import yaml
from pathlib import Path


class ConfigError(Exception):
    """Raised when configuration is missing or invalid."""


def load_config(config_path: str = "sources.yaml") -> dict:
    """Load and parse sources.yaml, falling back to sources.example.yaml."""
    path = Path(config_path)
    if not path.exists():
        fallback = path.parent / "sources.example.yaml"
        if fallback.exists():
            path = fallback
        else:
            raise ConfigError(
                f"Config file '{config_path}' not found. "
                "Copy sources.example.yaml to sources.yaml and fill in your values."
            )
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"Invalid YAML in '{config_path}': {exc}") from exc


def load_secrets() -> dict:
    """Read required secrets from environment variables. Raises ConfigError if missing."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    channel = os.environ.get("TELEGRAM_CHANNEL_ID")
    if not token:
        raise ConfigError("TELEGRAM_BOT_TOKEN environment variable is not set")
    if not channel:
        raise ConfigError("TELEGRAM_CHANNEL_ID environment variable is not set")
    return {"bot_token": token, "channel_id": channel}
