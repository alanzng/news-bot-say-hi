import logging

import requests
from src.base import DataSource

logger = logging.getLogger(__name__)

_BASE_URL = "https://bg2.kimlongdongthap.vn/_info.aspx"
_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; news-bot/1.0)"}
_DEFAULT_PRODUCT_IDS = [1, 2, 8, 3, 4, 5]


class KimLongGoldPriceSource(DataSource):
    name = "kimlong-gold-price"
    default_schedule = "0 8 * * *"

    def __init__(self, product_ids: list[int] | None = None) -> None:
        self._product_ids = product_ids if product_ids is not None else _DEFAULT_PRODUCT_IDS

    def _fetch_product(self, product_id: int) -> dict | None:
        resp = requests.get(
            _BASE_URL,
            params={"ID": product_id, "OGP": "0"},
            headers=_HEADERS,
            timeout=15,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Kim Long API returned HTTP {resp.status_code}")

        fields = resp.text.strip().split("\n")
        if len(fields) < 12:
            logger.warning(
                "[kimlong-gold-price] malformed response for ID=%d: expected 12 fields, got %d",
                product_id,
                len(fields),
            )
            return None

        return {
            "id": fields[0],
            "name": fields[2],
            "label": fields[4],
            "purity": fields[6],
            "buy_price": fields[7],
            "sell_price": fields[8],
            "buy_trend": fields[9],
            "sell_trend": fields[10],
        }

    def fetch(self) -> list[dict]:
        records = []
        for pid in self._product_ids:
            record = self._fetch_product(pid)
            if record is not None:
                records.append(record)
        if not records:
            logger.warning("[kimlong-gold-price] no records fetched")
        return records

    def format(self, records: list[dict]) -> str:
        if not records:
            return ""
        return ""  # placeholder — implemented in Task 2
