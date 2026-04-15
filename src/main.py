import logging
import os
from dotenv import load_dotenv

from src.config import ConfigError, load_config, load_secrets
from src.notifier import TelegramNotifier
from src.registry import SourceRegistry
from src.sources.bitcoin_price import BitcoinPriceSource
from src.sources.github_trending import GitHubTrendingSource
from src.sources.gold_price import GoldPriceSource
from src.sources.stock_price import StockPriceSource

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def _build_sources(config: dict) -> list:
    """Instantiate enabled sources from config."""
    sources_cfg = config.get("sources", {})

    def cfg(name: str) -> dict:
        return sources_cfg.get(name, {})

    def enabled(name: str) -> bool:
        return cfg(name).get("enabled", True)

    factories = {
        "gold-price": lambda: GoldPriceSource(),
        "bitcoin-price": lambda: BitcoinPriceSource(),
        "stock-price": lambda: StockPriceSource(tickers=cfg("stock-price").get("tickers", [])),
        "github-trending": lambda: GitHubTrendingSource(
            language=cfg("github-trending").get("language", ""),
            since=cfg("github-trending").get("since", "daily"),
            limit=cfg("github-trending").get("limit", 5),
        ),
    }

    sources = []
    for name, factory in factories.items():
        if not enabled(name):
            logger.info("[%s] disabled in config, skipping", name)
            continue
        sources.append(factory())
        logger.info("[%s] registered", name)
    return sources


def main() -> None:
    load_dotenv()

    try:
        config = load_config()
        secrets = load_secrets()
    except ConfigError as exc:
        logger.error("Configuration error: %s", exc)
        raise SystemExit(1) from exc

    notifier = TelegramNotifier(secrets["bot_token"], secrets["channel_id"])

    schedules = {
        name: src_cfg["schedule"]
        for name, src_cfg in config.get("sources", {}).items()
        if "schedule" in src_cfg
    }

    sources = _build_sources(config)
    if not sources:
        logger.error("No sources are enabled. Check sources.yaml.")
        raise SystemExit(1)

    registry = SourceRegistry(sources, notifier, schedules)
    registry.start()


if __name__ == "__main__":
    main()
