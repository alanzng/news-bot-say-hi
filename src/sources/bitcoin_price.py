import requests
from src.base import DataSource

_COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"


class BitcoinPriceSource(DataSource):
    name = "bitcoin-price"
    default_schedule = "0 */6 * * *"

    def fetch(self) -> list[dict]:
        resp = requests.get(
            _COINGECKO_URL,
            params={"ids": "bitcoin", "vs_currencies": "usd", "include_24hr_change": "true"},
            timeout=10,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"CoinGecko API returned HTTP {resp.status_code}")
        data = resp.json()
        btc = data.get("bitcoin")
        if not btc:
            raise RuntimeError("CoinGecko response missing 'bitcoin' key")
        return [{
            "symbol": "BTC",
            "price_usd": btc["usd"],
            "price_change_24h": btc.get("usd_24h_change", 0.0),
        }]

    def format(self, records: list[dict]) -> str:
        if not records:
            return ""
        r = records[0]
        change = r["price_change_24h"]
        sign = "+" if change >= 0 else ""
        trend = "📈" if change >= 0 else "📉"

        return "\n".join([
            "₿ <b>Bitcoin Price</b>",
            "",
            f"💰 BTC/USD: <b>${r['price_usd']:,.2f}</b>",
            f"📊 24h: <b>{sign}{change:.2f}%</b> {trend}",
            "",
            '🔗 Nguồn: <a href="https://www.coingecko.com">coingecko.com</a>',
        ])
