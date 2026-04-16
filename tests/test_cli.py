from unittest.mock import MagicMock
import pytest
from src.cli import run_source, get_source_by_name


def test_get_source_by_name_returns_gold_price():
    config = {"sources": {"gold-price": {"enabled": True}}}
    source = get_source_by_name("gold-price", config)
    assert source.name == "gold-price"


def test_get_source_by_name_returns_kimlong():
    config = {"sources": {"kimlong-gold-price": {"enabled": True}}}
    source = get_source_by_name("kimlong-gold-price", config)
    assert source.name == "kimlong-gold-price"


def test_get_source_by_name_returns_bitcoin():
    config = {"sources": {"bitcoin-price": {"enabled": True}}}
    source = get_source_by_name("bitcoin-price", config)
    assert source.name == "bitcoin-price"


def test_get_source_by_name_raises_for_unknown():
    config = {"sources": {}}
    with pytest.raises(ValueError, match="Unknown source"):
        get_source_by_name("nonexistent", config)


def test_run_source_fetches_formats_and_sends():
    mock_source = MagicMock()
    mock_source.name = "test"
    mock_source.fetch.return_value = [{"data": "value"}]
    mock_source.format.return_value = "formatted message"
    mock_notifier = MagicMock()

    run_source(mock_source, mock_notifier)

    mock_source.fetch.assert_called_once()
    mock_source.format.assert_called_once_with([{"data": "value"}])
    mock_notifier.send_message.assert_called_once_with("formatted message")


def test_run_source_skips_send_on_empty_fetch():
    mock_source = MagicMock()
    mock_source.name = "test"
    mock_source.fetch.return_value = []
    mock_notifier = MagicMock()

    run_source(mock_source, mock_notifier)

    mock_notifier.send_message.assert_not_called()


def test_run_source_skips_send_on_empty_format():
    mock_source = MagicMock()
    mock_source.name = "test"
    mock_source.fetch.return_value = [{"data": "value"}]
    mock_source.format.return_value = ""
    mock_notifier = MagicMock()

    run_source(mock_source, mock_notifier)

    mock_notifier.send_message.assert_not_called()
