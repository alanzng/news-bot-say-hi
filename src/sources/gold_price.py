import logging
import requests
from src.base import DataSource

logger = logging.getLogger(__name__)

_URL = "https://sjc.com.vn/GoldPrice/Services/PriceService.ashx"
_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; news-bot/1.0)"}
_BRANCH = "Hồ Chí Minh"

_ALLOWED_TYPES = {
    "Vàng SJC 5 chỉ",
    "Vàng SJC 0.5 chỉ, 1 chỉ, 2 chỉ",
    "Vàng nhẫn SJC 99,99% 1 chỉ, 2 chỉ, 5 chỉ",
}

_GROUPS = [
    ("Vàng miếng SJC", "Vàng SJC"),
    ("Vàng nhẫn SJC", "Vàng nhẫn"),
]


class GoldPriceSource(DataSource):
    name = "gold-price"
    default_schedule = "0 8 * * *"

    def __init__(self) -> None:
        self._latest_date: str = ""

    def fetch(self) -> list[dict]:
        resp = requests.get(_URL, headers=_HEADERS, timeout=15)
        if resp.status_code != 200:
            raise RuntimeError(f"SJC API returned HTTP {resp.status_code}")

        data = resp.json()
        if not data.get("success"):
            raise RuntimeError("SJC API returned success=false")

        self._latest_date = data.get("latestDate", "")

        records = [
            {
                "type": item["TypeName"],
                "buy_price": item["Buy"],
                "sell_price": item["Sell"],
            }
            for item in data.get("data", [])
            if item.get("BranchName") == _BRANCH and item.get("TypeName") in _ALLOWED_TYPES
        ]

        if not records:
            logger.warning("[gold-price] no records found for branch '%s'", _BRANCH)
        return records

    def format(self, records: list[dict]) -> str:
        if not records:
            return ""

        header = "Gia vang SJC hom nay (TP.HCM)"
        if self._latest_date:
            header += f" — {self._latest_date}"
        lines = [header, "Don vi: nghin dong/chi", ""]

        for section_label, prefix in _GROUPS:
            group = [r for r in records if r["type"].startswith(prefix)]
            if not group:
                continue
            lines.append(f"[{section_label}]")
            for r in group:
                lines.append(f"  {r['type']}: Mua {r['buy_price']} | Ban {r['sell_price']}")
            lines.append("")

        lines.append("")
        lines.append("Nguon: https://sjc.com.vn")
        return "\n".join(lines).rstrip()
