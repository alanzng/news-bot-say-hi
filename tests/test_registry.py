import pytest
from unittest.mock import MagicMock, patch, call
from src.base import DataSource
from src.registry import SourceRegistry


def _make_source(name: str, schedule: str = "0 8 * * *") -> DataSource:
    source = MagicMock(spec=DataSource)
    source.name = name
    source.default_schedule = schedule
    source.fetch.return_value = [{"val": 1}]
    source.format.return_value = f"Message from {name}"
    return source


def _make_notifier():
    return MagicMock()


def test_run_source_sends_message_on_success():
    source = _make_source("test-source")
    notifier = _make_notifier()
    registry = SourceRegistry([source], notifier)
    registry._run_source(source)
    source.fetch.assert_called_once()
    source.format.assert_called_once_with([{"val": 1}])
    notifier.send_message.assert_called_once_with("Message from test-source")


def test_run_source_skips_send_when_fetch_returns_empty():
    source = _make_source("test-source")
    source.fetch.return_value = []
    notifier = _make_notifier()
    registry = SourceRegistry([source], notifier)
    registry._run_source(source)
    notifier.send_message.assert_not_called()


def test_run_source_skips_send_when_format_returns_empty():
    source = _make_source("test-source")
    source.format.return_value = ""
    notifier = _make_notifier()
    registry = SourceRegistry([source], notifier)
    registry._run_source(source)
    notifier.send_message.assert_not_called()


def test_run_source_catches_fetch_exception_without_raising():
    source = _make_source("test-source")
    source.fetch.side_effect = RuntimeError("network error")
    notifier = _make_notifier()
    registry = SourceRegistry([source], notifier)
    # Should NOT raise
    registry._run_source(source)
    notifier.send_message.assert_not_called()


def test_run_source_uses_schedule_override():
    source = _make_source("gold-price", schedule="0 8 * * *")
    notifier = _make_notifier()
    registry = SourceRegistry([source], notifier, schedules={"gold-price": "0 10 * * *"})
    # Verify schedule override is stored (scheduler integration tested via start())
    assert registry._get_schedule(source) == "0 10 * * *"


def test_get_schedule_falls_back_to_default():
    source = _make_source("gold-price", schedule="0 8 * * *")
    notifier = _make_notifier()
    registry = SourceRegistry([source], notifier)
    assert registry._get_schedule(source) == "0 8 * * *"
