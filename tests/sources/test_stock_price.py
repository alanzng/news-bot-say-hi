import pandas as pd
import pytest
from unittest.mock import MagicMock, patch
from src.sources.stock_price import StockPriceSource


def _mock_price_board(rows: list[dict]) -> pd.DataFrame:
    """Build a mock DataFrame matching vnstock price_board output."""
    return pd.DataFrame(rows)


def _patch_indices(indices=None):
    """Patch _fetch_indices to return given list (default empty)."""
    return patch.object(StockPriceSource, "_fetch_indices", return_value=indices or [])


def test_constructor_raises_if_no_tickers():
    with pytest.raises(ValueError, match="ticker"):
        StockPriceSource(tickers=[])


def test_fetch_returns_record_per_ticker():
    source = StockPriceSource(tickers=["VNM", "HPG"])
    df = _mock_price_board([
        {"symbol": "VNM", "close_price": 75000.0, "reference_price": 74000.0, "percent_change": 1.351},
        {"symbol": "HPG", "close_price": 26500.0, "reference_price": 27000.0, "percent_change": -1.852},
    ])
    mock_stock = MagicMock()
    mock_stock.trading.price_board.return_value = df

    with _patch_indices(), patch("src.sources.stock_price.Vnstock") as MockVnstock:
        MockVnstock.return_value.stock.return_value = mock_stock
        records = source.fetch()

    stocks = [r for r in records if r.get("type") == "stock"]
    assert len(stocks) == 2
    assert stocks[0]["symbol"] == "VNM"
    assert stocks[0]["match_price"] == 75000.0
    assert stocks[0]["ref_price"] == 74000.0
    assert abs(stocks[0]["change_percent"] - 1.351) < 0.01
    assert stocks[1]["symbol"] == "HPG"
    assert abs(stocks[1]["change_percent"] - (-1.852)) < 0.01


def test_fetch_includes_indices():
    source = StockPriceSource(tickers=["VNM"])
    df = _mock_price_board([
        {"symbol": "VNM", "close_price": 75000.0, "reference_price": 74000.0, "percent_change": 1.0},
    ])
    mock_stock = MagicMock()
    mock_stock.trading.price_board.return_value = df
    mock_indices = [
        {"symbol": "VN-Index", "value": 1819.83, "prev_value": 1800.65, "change_percent": 1.07, "type": "index"},
        {"symbol": "VN30", "value": 1979.19, "prev_value": 1961.6, "change_percent": 0.90, "type": "index"},
    ]

    with _patch_indices(mock_indices), patch("src.sources.stock_price.Vnstock") as MockVnstock:
        MockVnstock.return_value.stock.return_value = mock_stock
        records = source.fetch()

    indices = [r for r in records if r.get("type") == "index"]
    stocks = [r for r in records if r.get("type") == "stock"]
    assert len(indices) == 2
    assert indices[0]["symbol"] == "VN-Index"
    assert len(stocks) == 1


def test_fetch_skips_symbol_missing_from_result():
    source = StockPriceSource(tickers=["VNM", "BADINVALID"])
    df = _mock_price_board([
        {"symbol": "VNM", "close_price": 75000.0, "reference_price": 74000.0, "percent_change": 1.351},
    ])
    mock_stock = MagicMock()
    mock_stock.trading.price_board.return_value = df

    with _patch_indices(), patch("src.sources.stock_price.Vnstock") as MockVnstock:
        MockVnstock.return_value.stock.return_value = mock_stock
        records = source.fetch()

    stocks = [r for r in records if r.get("type") == "stock"]
    assert len(stocks) == 1
    assert stocks[0]["symbol"] == "VNM"


def test_fetch_returns_indices_on_stock_api_error():
    source = StockPriceSource(tickers=["VNM"])
    mock_stock = MagicMock()
    mock_stock.trading.price_board.side_effect = Exception("API unavailable")
    mock_indices = [
        {"symbol": "VN-Index", "value": 1819.83, "prev_value": 1800.65, "change_percent": 1.07, "type": "index"},
    ]

    with _patch_indices(mock_indices), patch("src.sources.stock_price.Vnstock") as MockVnstock:
        MockVnstock.return_value.stock.return_value = mock_stock
        records = source.fetch()

    assert len(records) == 1
    assert records[0]["type"] == "index"


def test_fetch_returns_empty_list_on_all_errors():
    source = StockPriceSource(tickers=["VNM"])
    mock_stock = MagicMock()
    mock_stock.trading.price_board.side_effect = Exception("API unavailable")

    with _patch_indices([]), patch("src.sources.stock_price.Vnstock") as MockVnstock:
        MockVnstock.return_value.stock.return_value = mock_stock
        records = source.fetch()

    assert records == []


def test_format_shows_indices_and_stocks():
    source = StockPriceSource(tickers=["VNM"])
    records = [
        {"symbol": "VN-Index", "value": 1819.83, "prev_value": 1800.65, "change_percent": 1.07, "type": "index"},
        {"symbol": "VNM", "match_price": 75000.0, "ref_price": 74000.0, "change_percent": 1.35, "type": "stock"},
    ]
    msg = source.format(records)
    assert "Chỉ số thị trường" in msg
    assert "<b>VN-Index</b>" in msg
    assert "<b>1,819.83</b>" in msg
    assert "Cổ phiếu" in msg
    assert "<b>VNM</b>" in msg
    assert "<b>75,000</b>" in msg
    assert "📈" in msg
    assert "Giá cổ phiếu" in msg
    assert "vnstocks" in msg


def test_format_shows_negative_change():
    source = StockPriceSource(tickers=["HPG"])
    records = [{"symbol": "HPG", "match_price": 26500.0, "ref_price": 27000.0, "change_percent": -1.85, "type": "stock"}]
    msg = source.format(records)
    assert "📉" in msg
    assert "-1.85%" in msg


def test_format_returns_empty_string_for_empty_records():
    source = StockPriceSource(tickers=["VNM"])
    assert source.format([]) == ""


def test_name_and_default_schedule():
    source = StockPriceSource(tickers=["VNM"])
    assert source.name == "stock-price"
    assert source.default_schedule == "0 9 * * 1-5"
