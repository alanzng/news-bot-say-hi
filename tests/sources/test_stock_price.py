import pandas as pd
import pytest
from unittest.mock import MagicMock, patch
from src.sources.stock_price import StockPriceSource


def _mock_price_board(rows: list[dict]) -> pd.DataFrame:
    """Build a mock DataFrame matching vnstock3 price_board output."""
    return pd.DataFrame(rows)


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

    with patch("src.sources.stock_price.Vnstock") as MockVnstock:
        MockVnstock.return_value.stock.return_value = mock_stock
        records = source.fetch()

    assert len(records) == 2
    assert records[0]["symbol"] == "VNM"
    assert records[0]["match_price"] == 75000.0
    assert records[0]["ref_price"] == 74000.0
    assert abs(records[0]["change_percent"] - 1.351) < 0.01
    assert records[1]["symbol"] == "HPG"
    assert abs(records[1]["change_percent"] - (-1.852)) < 0.01


def test_fetch_skips_symbol_missing_from_result():
    source = StockPriceSource(tickers=["VNM", "BADINVALID"])
    # Only VNM returned by the API
    df = _mock_price_board([
        {"symbol": "VNM", "close_price": 75000.0, "reference_price": 74000.0, "percent_change": 1.351},
    ])
    mock_stock = MagicMock()
    mock_stock.trading.price_board.return_value = df

    with patch("src.sources.stock_price.Vnstock") as MockVnstock:
        MockVnstock.return_value.stock.return_value = mock_stock
        records = source.fetch()

    assert len(records) == 1
    assert records[0]["symbol"] == "VNM"


def test_fetch_returns_empty_list_on_api_error():
    source = StockPriceSource(tickers=["VNM"])
    mock_stock = MagicMock()
    mock_stock.trading.price_board.side_effect = Exception("API unavailable")

    with patch("src.sources.stock_price.Vnstock") as MockVnstock:
        MockVnstock.return_value.stock.return_value = mock_stock
        records = source.fetch()

    assert records == []


def test_format_shows_symbol_price_and_change():
    source = StockPriceSource(tickers=["VNM"])
    records = [{"symbol": "VNM", "match_price": 75000.0, "ref_price": 74000.0, "change_percent": 1.35}]
    msg = source.format(records)
    assert "<b>VNM</b>" in msg
    assert "<b>75,000</b>" in msg
    assert "📈" in msg
    assert "Giá cổ phiếu" in msg
    assert 'href="https://vnstocks.com/"' in msg


def test_format_shows_negative_change():
    source = StockPriceSource(tickers=["HPG"])
    records = [{"symbol": "HPG", "match_price": 26500.0, "ref_price": 27000.0, "change_percent": -1.85}]
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
