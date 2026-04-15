import logging
import requests
from bs4 import BeautifulSoup
from src.base import DataSource

logger = logging.getLogger(__name__)

_URL = "https://cafef.vn/du-lieu/gia-vang-hom-nay/trong-nuoc.chn"
_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; news-bot/1.0)"}


class GoldPriceSource(DataSource):
    name = "gold-price"
    default_schedule = "0 8 * * *"

    def fetch(self) -> list[dict]:
        resp = requests.get(_URL, headers=_HEADERS, timeout=15)
        if resp.status_code != 200:
            raise RuntimeError(f"cafef.vn returned HTTP {resp.status_code}")

        soup = BeautifulSoup(resp.text, "html.parser")
        table = soup.find("table", {"class": "tablesorter"})
        if not table:
            logger.warning("[gold-price] price table not found in HTML response")
            return []

        rows = table.find_all("tr")[1:]  # skip header row
        records = []
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 3:
                continue
            records.append({
                "type": cells[0].get_text(strip=True),
                "buy_price": cells[1].get_text(strip=True),
                "sell_price": cells[2].get_text(strip=True),
            })

        if not records:
            logger.warning("[gold-price] table found but zero data rows parsed")
        return records

    def format(self, records: list[dict]) -> str:
        if not records:
            return ""
        lines = ["Gi\u00e1 v\u00e0ng trong n\u01b0\u1edbc h\u00f4m nay"]
        for r in records:
            lines.append(f"- {r['type']}: Mua {r['buy_price']} | B\u00e1n {r['sell_price']}")
        return "\n".join(lines)
