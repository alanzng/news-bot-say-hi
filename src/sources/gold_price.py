import logging
import requests
from src.base import DataSource

logger = logging.getLogger(__name__)

_URL = "https://sjc.com.vn/GoldPrice/Services/PriceService.ashx"
_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; news-bot/1.0)"}
_BRANCH = "Hồ Chí Minh"


class GoldPriceSource(DataSource):
    name = "gold-price"
    default_schedule = "0 8 * * *"

    def fetch(self) -> list[dict]:
        resp = requests.get(_URL, headers=_HEADERS, timeout=15)
        if resp.status_code != 200:
            raise RuntimeError(f"SJC API returned HTTP {resp.status_code}")

        data = resp.json()
        if not data.get("success"):
            raise RuntimeError("SJC API returned success=false")

        records = [
            {
                "type": item["TypeName"],
                "buy_price": item["Buy"],
                "sell_price": item["Sell"],
            }
            for item in data.get("data", [])
            if item.get("BranchName") == _BRANCH
        ]

        if not records:
            logger.warning("[gold-price] no records found for branch '%s'", _BRANCH)
        return records

    def format(self, records: list[dict]) -> str:
        if not records:
            return ""
        lines = ["Giá vàng SJC hôm nay (TP.HCM)"]
        for r in records:
            lines.append(f"- {r['type']}: Mua {r['buy_price']} | Bán {r['sell_price']} (nghìn đồng/chỉ)")
        return "\n".join(lines)
