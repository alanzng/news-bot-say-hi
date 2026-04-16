import logging
import requests
from vnstock import Vnstock
from src.base import DataSource

logger = logging.getLogger(__name__)

_CAFEF_MARKET_URL = "https://cafef.vn/du-lieu/Ajax/PageNew/RealtimeChartHeader.ashx"
_INDEX_MAP = {"1": "VN-Index", "11": "VN30"}
_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; news-bot/1.0)"}


class StockPriceSource(DataSource):
    name = "stock-price"
    default_schedule = "0 9 * * 1-5"  # 9 AM on Vietnamese trading weekdays

    def __init__(self, tickers: list[str]) -> None:
        if not tickers:
            raise ValueError("StockPriceSource requires at least one ticker symbol")
        self.tickers = tickers

    def _fetch_indices(self) -> list[dict]:
        """Fetch VN-Index and VN30 from CafeF."""
        try:
            resp = requests.get(
                _CAFEF_MARKET_URL,
                params={"index": ";".join(_INDEX_MAP.keys()), "type": "market"},
                headers=_HEADERS,
                timeout=10,
            )
            data = resp.json()
        except Exception as exc:
            logger.error("[stock-price] failed to fetch market indices: %s", exc)
            return []

        indices = []
        for key, name in _INDEX_MAP.items():
            item = data.get(key)
            if not item:
                continue
            current = float(item.get("CurrentIndex", 0) or 0)
            prev = float(item.get("PrevIndex", 0) or 0)
            change_pct = ((current - prev) / prev * 100) if prev else 0
            indices.append({
                "symbol": name,
                "value": current,
                "prev_value": prev,
                "change_percent": round(change_pct, 2),
                "type": "index",
            })
        return indices

    def fetch(self) -> list[dict]:
        indices = self._fetch_indices()

        try:
            stock = Vnstock().stock(symbol=self.tickers[0], source="KBS")
            df = stock.trading.price_board(self.tickers)
        except Exception as exc:
            logger.error("[stock-price] failed to fetch price board: %s", exc)
            return indices  # still return indices if stock fetch fails

        records = []
        for _, row in df.iterrows():
            symbol = row.get("symbol", "")
            if not symbol:
                continue
            close_price = float(row.get("close_price", 0) or 0)
            ref_price = float(row.get("reference_price", 0) or 0)
            change_pct = float(row.get("percent_change", 0) or 0)
            records.append({
                "symbol": symbol,
                "match_price": close_price,
                "ref_price": ref_price,
                "change_percent": change_pct,
                "type": "stock",
            })

        if len(records) < len(self.tickers):
            found = {r["symbol"] for r in records}
            missing = [t for t in self.tickers if t not in found]
            for sym in missing:
                logger.warning("[stock-price] symbol not found in response: %s", sym)

        return indices + records

    def format(self, records: list[dict]) -> str:
        if not records:
            return ""

        indices = [r for r in records if r.get("type") == "index"]
        stocks = [r for r in records if r.get("type") != "index"]

        def fmt_index(r: dict) -> str:
            sign = "+" if r["change_percent"] >= 0 else ""
            trend = "📈" if r["change_percent"] >= 0 else "📉"
            return (
                f"  • <b>{r['symbol']}</b>: <b>{r['value']:,.2f}</b>"
                f" {trend} {sign}{r['change_percent']:.2f}%"
            )

        def fmt_stock(r: dict) -> str:
            sign = "+" if r["change_percent"] >= 0 else ""
            trend = "📈" if r["change_percent"] >= 0 else "📉"
            return (
                f"  • <b>{r['symbol']}</b>: <b>{r['match_price']:,.0f}</b> VNĐ"
                f" {trend} {sign}{r['change_percent']:.2f}%"
            )

        parts = [
            "📈 <b>Giá cổ phiếu Việt Nam</b>",
            "",
        ]

        if indices:
            parts.append("🏛 <b>Chỉ số thị trường</b>")
            parts.extend(fmt_index(r) for r in indices)
            parts.append("")

        if stocks:
            parts.append("💹 <b>Cổ phiếu</b>")
            parts.extend(fmt_stock(r) for r in stocks)
            parts.append("")

        parts.append("🔗 Nguồn: <a href=\"https://vnstocks.com\">vnstocks</a>")

        return "\n".join(parts)
