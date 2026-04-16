import pytest
from unittest.mock import patch, MagicMock
from src.sources.gold_price import GoldPriceSource

SAMPLE_API_RESPONSE = {
    "success": True,
    "latestDate": "14:52 15/04/2026",
    "data": [
        {
            "Id": 1,
            "TypeName": "Vàng SJC 5 chỉ",
            "BranchName": "Hồ Chí Minh",
            "Buy": "170,000",
            "BuyValue": 170000000.0,
            "Sell": "173,520",
            "SellValue": 173520000.0,
            "BuyDiffer": None,
            "BuyDifferValue": 0,
            "SellDiffer": None,
            "SellDifferValue": 0,
            "GroupDate": "/Date(-62135596800000)/",
        },
        {
            "Id": 2,
            "TypeName": "Vàng nhẫn SJC 99,99% 1 chỉ, 2 chỉ, 5 chỉ",
            "BranchName": "Hồ Chí Minh",
            "Buy": "169,700",
            "BuyValue": 169700000.0,
            "Sell": "173,200",
            "SellValue": 173200000.0,
            "BuyDiffer": None,
            "BuyDifferValue": 0,
            "SellDiffer": None,
            "SellDifferValue": 0,
            "GroupDate": "/Date(-62135596800000)/",
        },
        {
            "Id": 3,
            "TypeName": "Vàng SJC 5 chỉ",
            "BranchName": "Hà Nội",
            "Buy": "170,000",
            "BuyValue": 170000000.0,
            "Sell": "173,520",
            "SellValue": 173520000.0,
            "BuyDiffer": None,
            "BuyDifferValue": 0,
            "SellDiffer": None,
            "SellDifferValue": 0,
            "GroupDate": "/Date(-62135596800000)/",
        },
    ],
}


def _mock_response(payload: dict, status: int = 200):
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = payload
    return resp


def test_fetch_returns_only_hcm_records():
    source = GoldPriceSource()
    with patch("src.sources.gold_price.requests.get", return_value=_mock_response(SAMPLE_API_RESPONSE)):
        records = source.fetch()
    assert len(records) == 2
    assert records[0] == {"type": "Vàng SJC 5 chỉ", "buy_price": "170,000", "sell_price": "173,520"}
    assert records[1] == {"type": "Vàng nhẫn SJC 99,99% 1 chỉ, 2 chỉ, 5 chỉ", "buy_price": "169,700", "sell_price": "173,200"}


def test_fetch_raises_on_non_200():
    source = GoldPriceSource()
    with patch("src.sources.gold_price.requests.get", return_value=_mock_response({}, 503)):
        with pytest.raises(RuntimeError, match="503"):
            source.fetch()


def test_fetch_raises_when_success_false():
    source = GoldPriceSource()
    payload = {"success": False, "data": []}
    with patch("src.sources.gold_price.requests.get", return_value=_mock_response(payload)):
        with pytest.raises(RuntimeError, match="success=false"):
            source.fetch()


def test_fetch_returns_empty_list_when_no_hcm_branch():
    source = GoldPriceSource()
    payload = {
        "success": True,
        "latestDate": "now",
        "data": [
            {"TypeName": "Vàng SJC", "BranchName": "Hà Nội", "Buy": "170,000", "Sell": "173,500"},
        ],
    }
    with patch("src.sources.gold_price.requests.get", return_value=_mock_response(payload)):
        records = source.fetch()
    assert records == []


def test_format_produces_header_and_lines():
    source = GoldPriceSource()
    records = [
        {"type": "Vàng SJC 5 chỉ", "buy_price": "170,000", "sell_price": "173,520"},
    ]
    msg = source.format(records)
    assert "Giá vàng SJC hôm nay" in msg
    assert "Vàng SJC 5 chỉ" in msg
    assert "<b>170,000</b>" in msg
    assert "<b>173,520</b>" in msg


def test_format_returns_empty_string_for_empty_records():
    source = GoldPriceSource()
    assert source.format([]) == ""


def test_name_and_default_schedule():
    source = GoldPriceSource()
    assert source.name == "gold-price"
    assert source.default_schedule == "0 8 * * *"
