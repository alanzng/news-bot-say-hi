from src.sources.gold_price import GoldPriceSource


def _source():
    return GoldPriceSource()


SAMPLE_RECORDS = [
    {"type": "Vàng SJC 5 chỉ", "buy_price": "168,500", "sell_price": "172,520"},
    {"type": "Vàng SJC 0.5 chỉ, 1 chỉ, 2 chỉ", "buy_price": "168,500", "sell_price": "172,530"},
    {"type": "Vàng nhẫn SJC 99,99% 1 chỉ, 2 chỉ, 5 chỉ", "buy_price": "168,200", "sell_price": "172,200"},
]


def test_format_returns_empty_string_for_empty_records():
    assert _source().format([]) == ""


def test_format_contains_header():
    result = _source().format(SAMPLE_RECORDS)
    assert "Giá vàng SJC hôm nay" in result


def test_format_contains_buy_price_bolded():
    result = _source().format(SAMPLE_RECORDS)
    assert "<b>168,500</b>" in result


def test_format_contains_sell_price_bolded():
    result = _source().format(SAMPLE_RECORDS)
    assert "<b>172,520</b>" in result


def test_format_contains_mien_section():
    result = _source().format(SAMPLE_RECORDS)
    assert "Vàng miếng SJC" in result


def test_format_contains_nhan_section():
    result = _source().format(SAMPLE_RECORDS)
    assert "Vàng nhẫn SJC" in result


def test_format_contains_source_link():
    result = _source().format(SAMPLE_RECORDS)
    assert "sjc.com.vn" in result


def test_format_contains_buy_sell_emojis():
    result = _source().format(SAMPLE_RECORDS)
    assert "🟢" in result
    assert "🔴" in result
