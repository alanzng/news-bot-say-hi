import pytest
from unittest.mock import patch, MagicMock
from src.sources.bitcoin_price import BitcoinPriceSource


def _mock_response(data: dict, status: int = 200):
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = data
    return resp


def test_fetch_returns_btc_record():
    source = BitcoinPriceSource()
    payload = {"bitcoin": {"usd": 65000.0, "usd_24h_change": 2.5}}
    with patch("src.sources.bitcoin_price.requests.get", return_value=_mock_response(payload)):
        records = source.fetch()
    assert len(records) == 1
    assert records[0] == {"symbol": "BTC", "price_usd": 65000.0, "price_change_24h": 2.5}


def test_fetch_raises_on_non_200():
    source = BitcoinPriceSource()
    with patch("src.sources.bitcoin_price.requests.get", return_value=_mock_response({}, 429)):
        with pytest.raises(RuntimeError, match="429"):
            source.fetch()


def test_fetch_raises_if_bitcoin_key_missing():
    source = BitcoinPriceSource()
    with patch("src.sources.bitcoin_price.requests.get", return_value=_mock_response({})):
        with pytest.raises(RuntimeError, match="bitcoin"):
            source.fetch()


def test_format_shows_price_and_change():
    source = BitcoinPriceSource()
    records = [{"symbol": "BTC", "price_usd": 65000.0, "price_change_24h": 2.5}]
    msg = source.format(records)
    assert "<b>$65,000.00</b>" in msg
    assert "<b>+2.50%</b>" in msg
    assert "📈" in msg
    assert "Bitcoin" in msg
    assert "coingecko" in msg


def test_format_shows_negative_change():
    source = BitcoinPriceSource()
    records = [{"symbol": "BTC", "price_usd": 60000.0, "price_change_24h": -1.3}]
    msg = source.format(records)
    assert "<b>-1.30%</b>" in msg
    assert "📉" in msg


def test_format_returns_empty_string_for_empty_records():
    source = BitcoinPriceSource()
    assert source.format([]) == ""


def test_name_and_default_schedule():
    source = BitcoinPriceSource()
    assert source.name == "bitcoin-price"
    assert source.default_schedule == "0 */6 * * *"
