import requests


class TelegramNotifier:
    """Sends text messages to a Telegram channel via the Bot API."""

    def __init__(self, bot_token: str, channel_id: str) -> None:
        self._api_url = f"https://api.telegram.org/bot{bot_token}"
        self._channel_id = channel_id

    def send_message(self, text: str, parse_mode: str = "HTML") -> None:
        """POST text to Telegram sendMessage. Raises RuntimeError on API error."""
        url = f"{self._api_url}/sendMessage"
        resp = requests.post(
            url,
            json={
                "chat_id": self._channel_id,
                "text": text,
                "parse_mode": parse_mode,
                "disable_web_page_preview": True,
            },
            timeout=10,
        )
        data = resp.json()
        if not data.get("ok"):
            raise RuntimeError(f"Telegram API error: {data.get('description', 'unknown error')}")
