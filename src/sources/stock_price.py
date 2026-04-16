import logging
from vnstock import Vnstock
from src.base import DataSource

logger = logging.getLogger(__name__)


class StockPriceSource(DataSource):
    name = "stock-price"
    default_schedule = "0 9 * * 1-5"  # 9 AM on Vietnamese trading weekdays

    def __init__(self, tickers: list[str]) -> None:
        if not tickers:
            raise ValueError("StockPriceSource requires at least one ticker symbol")
        self.tickers = tickers

    def fetch(self) -> list[dict]:
        try:
            stock = Vnstock().stock(symbol=self.tickers[0], source="KBS")
            df = stock.trading.price_board(self.tickers)
        except Exception as exc:
            logger.error("[stock-price] failed to fetch price board: %s", exc)
            return []

        records = []
        for _, row in df.iterrows():
            symbol = row.get("symbol", "")
            if not symbol:
                continue
            match_price = float(row.get("match_price", 0) or 0)
            ref_price = float(row.get("ref_price", 0) or 0)
            change_pct = ((match_price - ref_price) / ref_price * 100) if ref_price else 0.0
            records.append({
                "symbol": symbol,
                "match_price": match_price,
                "ref_price": ref_price,
                "change_percent": change_pct,
            })

        if len(records) < len(self.tickers):
            found = {r["symbol"] for r in records}
            missing = [t for t in self.tickers if t not in found]
            for sym in missing:
                logger.warning("[stock-price] symbol not found in response: %s", sym)

        return records

    def format(self, records: list[dict]) -> str:
        if not records:
            return ""

        def row(r: dict) -> str:
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
        parts.extend(row(r) for r in records)
        parts.append("")
        parts.append("🔗 Nguồn: KBS")

        return "\n".join(parts)
