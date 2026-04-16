import pytest
from src.config import load_config, load_secrets, ConfigError


def test_load_config_reads_valid_yaml(tmp_path):
    cfg_file = tmp_path / "sources.yaml"
    cfg_file.write_text("sources:\n  gold-price:\n    enabled: true\n")
    config = load_config(str(cfg_file))
    assert config["sources"]["gold-price"]["enabled"] is True


def test_load_config_raises_if_file_missing(tmp_path):
    with pytest.raises(ConfigError, match="not found"):
        load_config(str(tmp_path / "missing.yaml"))


def test_load_config_raises_on_invalid_yaml(tmp_path):
    cfg_file = tmp_path / "sources.yaml"
    cfg_file.write_text("sources: [\ninvalid")
    with pytest.raises(ConfigError, match="Invalid YAML"):
        load_config(str(cfg_file))


def test_load_config_returns_empty_dict_for_empty_file(tmp_path):
    cfg_file = tmp_path / "sources.yaml"
    cfg_file.write_text("")
    config = load_config(str(cfg_file))
    assert config == {}


def test_load_secrets_returns_token_and_channel(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok123")
    monkeypatch.setenv("TELEGRAM_CHANNEL_ID", "@mychan")
    secrets = load_secrets()
    assert secrets["bot_token"] == "tok123"
    assert secrets["channel_id"] == "@mychan"


def test_load_secrets_raises_if_token_missing(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.setenv("TELEGRAM_CHANNEL_ID", "@mychan")
    with pytest.raises(ConfigError, match="TELEGRAM_BOT_TOKEN"):
        load_secrets()


def test_load_secrets_raises_if_channel_missing(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok123")
    monkeypatch.delenv("TELEGRAM_CHANNEL_ID", raising=False)
    with pytest.raises(ConfigError, match="TELEGRAM_CHANNEL_ID"):
        load_secrets()
