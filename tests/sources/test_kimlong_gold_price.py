from unittest.mock import patch, MagicMock
import pytest
from src.sources.kimlong_gold_price import KimLongGoldPriceSource

SAMPLE_RESPONSE_ID1 = (
    "1\n0\nNHẪN TRƠN & ÉP VĨ\n1\n9999\n0\n999\n"
    "15.700.000\n16.000.000\nup\nup\n100"
)

SAMPLE_RESPONSE_ID2 = (
    "2\n0\nNỮ TRANG KIM LONG\n1\nKLJ24K\n0\n990\n"
    "15.400.000\n15.900.000\nup\nup\n100"
)


def _mock_get_side_effect(url, **kwargs):
    resp = MagicMock()
    resp.status_code = 200
    pid = kwargs.get("params", {}).get("ID", 1)
    if pid == 1:
        resp.text = SAMPLE_RESPONSE_ID1
    elif pid == 2:
        resp.text = SAMPLE_RESPONSE_ID2
    else:
        resp.text = SAMPLE_RESPONSE_ID1
    return resp


def test_fetch_returns_records_for_all_product_ids():
    source = KimLongGoldPriceSource(product_ids=[1, 2])
    with patch("src.sources.kimlong_gold_price.requests.get", side_effect=_mock_get_side_effect):
        records = source.fetch()
    assert len(records) == 2
    assert records[0]["name"] == "NHẪN TRƠN & ÉP VĨ"
    assert records[0]["buy_price"] == "15.700.000"
    assert records[0]["sell_price"] == "16.000.000"
    assert records[0]["label"] == "9999"
    assert records[0]["purity"] == "999"
    assert records[1]["name"] == "NỮ TRANG KIM LONG"


def test_fetch_raises_on_non_200():
    source = KimLongGoldPriceSource(product_ids=[1])
    mock_resp = MagicMock()
    mock_resp.status_code = 503
    with patch("src.sources.kimlong_gold_price.requests.get", return_value=mock_resp):
        with pytest.raises(RuntimeError, match="503"):
            source.fetch()


def test_fetch_skips_malformed_response():
    source = KimLongGoldPriceSource(product_ids=[1])
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = "incomplete\ndata"
    with patch("src.sources.kimlong_gold_price.requests.get", return_value=mock_resp):
        records = source.fetch()
    assert records == []


def test_name_and_default_schedule():
    source = KimLongGoldPriceSource()
    assert source.name == "kimlong-gold-price"
    assert source.default_schedule == "0 8 * * *"


SAMPLE_RECORDS = [
    {
        "id": "1", "name": "NHẪN TRƠN & ÉP VĨ", "label": "9999",
        "purity": "999", "buy_price": "15.700.000", "sell_price": "16.000.000",
        "buy_trend": "up", "sell_trend": "up",
    },
    {
        "id": "2", "name": "NỮ TRANG KIM LONG", "label": "KLJ24K",
        "purity": "990", "buy_price": "15.400.000", "sell_price": "15.900.000",
        "buy_trend": "up", "sell_trend": "down",
    },
]


def test_format_returns_empty_for_no_records():
    source = KimLongGoldPriceSource()
    assert source.format([]) == ""


def test_format_contains_header():
    source = KimLongGoldPriceSource()
    result = source.format(SAMPLE_RECORDS)
    assert "Kim Long Đồng Tháp" in result


def test_format_contains_product_name():
    source = KimLongGoldPriceSource()
    result = source.format(SAMPLE_RECORDS)
    assert "NHẪN TRƠN" in result
    assert "NỮ TRANG KIM LONG" in result


def test_format_contains_bold_prices():
    source = KimLongGoldPriceSource()
    result = source.format(SAMPLE_RECORDS)
    assert "<b>15.700.000</b>" in result
    assert "<b>16.000.000</b>" in result


def test_format_contains_trend_arrows():
    source = KimLongGoldPriceSource()
    result = source.format(SAMPLE_RECORDS)
    assert "📈" in result


def test_format_contains_source_link():
    source = KimLongGoldPriceSource()
    result = source.format(SAMPLE_RECORDS)
    assert "kimlongdongthap" in result
