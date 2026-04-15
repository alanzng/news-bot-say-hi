import pytest
from unittest.mock import patch, MagicMock
from src.sources.gold_price import GoldPriceSource

SAMPLE_HTML = """
<html><body>
<table class="tablesorter">
  <thead><tr><th>Loại vàng</th><th>Mua vào</th><th>Bán ra</th></tr></thead>
  <tbody>
    <tr><td>Vàng SJC 1L</td><td>88,500</td><td>89,000</td></tr>
    <tr><td>Vàng nhẫn 999.9</td><td>85,300</td><td>86,000</td></tr>
  </tbody>
</table>
</body></html>
"""

EMPTY_TABLE_HTML = """
<html><body>
<table class="tablesorter"><thead><tr><th>Loại vàng</th></tr></thead><tbody></tbody></table>
</body></html>
"""


def _mock_response(html: str, status: int = 200):
    resp = MagicMock()
    resp.status_code = status
    resp.text = html
    return resp


def test_fetch_returns_records_from_table():
    source = GoldPriceSource()
    with patch("src.sources.gold_price.requests.get", return_value=_mock_response(SAMPLE_HTML)):
        records = source.fetch()
    assert len(records) == 2
    assert records[0] == {"type": "Vàng SJC 1L", "buy_price": "88,500", "sell_price": "89,000"}
    assert records[1] == {"type": "Vàng nhẫn 999.9", "buy_price": "85,300", "sell_price": "86,000"}


def test_fetch_raises_on_non_200():
    source = GoldPriceSource()
    with patch("src.sources.gold_price.requests.get", return_value=_mock_response("", 503)):
        with pytest.raises(RuntimeError, match="503"):
            source.fetch()


def test_fetch_returns_empty_list_when_table_missing():
    source = GoldPriceSource()
    with patch("src.sources.gold_price.requests.get", return_value=_mock_response("<html></html>")):
        records = source.fetch()
    assert records == []


def test_fetch_returns_empty_list_when_table_has_no_rows():
    source = GoldPriceSource()
    with patch("src.sources.gold_price.requests.get", return_value=_mock_response(EMPTY_TABLE_HTML)):
        records = source.fetch()
    assert records == []


def test_format_produces_header_and_lines():
    source = GoldPriceSource()
    records = [
        {"type": "Vàng SJC 1L", "buy_price": "88,500", "sell_price": "89,000"},
    ]
    msg = source.format(records)
    assert "Giá vàng trong nước hôm nay" in msg
    assert "Vàng SJC 1L" in msg
    assert "88,500" in msg
    assert "89,000" in msg


def test_format_returns_empty_string_for_empty_records():
    source = GoldPriceSource()
    assert source.format([]) == ""


def test_name_and_default_schedule():
    source = GoldPriceSource()
    assert source.name == "gold-price"
    assert source.default_schedule == "0 8 * * *"
