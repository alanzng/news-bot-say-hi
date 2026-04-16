import pytest
from unittest.mock import patch, MagicMock
from src.notifier import TelegramNotifier


def _make_notifier():
    return TelegramNotifier(bot_token="test-token", channel_id="@testchan")


def test_send_message_posts_to_correct_url():
    notifier = _make_notifier()
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"ok": True}

    with patch("src.notifier.requests.post", return_value=mock_resp) as mock_post:
        notifier.send_message("hello")

    mock_post.assert_called_once()
    url, kwargs = mock_post.call_args[0][0], mock_post.call_args[1]
    assert "test-token" in url
    assert "sendMessage" in url
    assert kwargs["json"]["chat_id"] == "@testchan"
    assert kwargs["json"]["text"] == "hello"


def test_send_message_raises_on_api_error():
    notifier = _make_notifier()
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"ok": False, "description": "Bad Request"}

    with patch("src.notifier.requests.post", return_value=mock_resp):
        with pytest.raises(RuntimeError, match="Bad Request"):
            notifier.send_message("hello")


def test_send_message_raises_on_network_error():
    notifier = _make_notifier()
    with patch("src.notifier.requests.post", side_effect=ConnectionError("timeout")):
        with pytest.raises(ConnectionError):
            notifier.send_message("hello")


def test_send_message_passes_parse_mode():
    notifier = _make_notifier()
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"ok": True}

    with patch("src.notifier.requests.post", return_value=mock_resp) as mock_post:
        notifier.send_message("hello", parse_mode="HTML")

    _, kwargs = mock_post.call_args[0][0], mock_post.call_args[1]
    assert kwargs["json"]["parse_mode"] == "HTML"


def test_send_message_defaults_to_html_parse_mode():
    notifier = _make_notifier()
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"ok": True}

    with patch("src.notifier.requests.post", return_value=mock_resp) as mock_post:
        notifier.send_message("hello")

    _, kwargs = mock_post.call_args[0][0], mock_post.call_args[1]
    assert kwargs["json"]["parse_mode"] == "HTML"
