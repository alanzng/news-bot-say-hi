import argparse
import logging
import sys

from dotenv import load_dotenv

from src.base import DataSource
from src.config import ConfigError, load_config, load_secrets
from src.notifier import TelegramNotifier
from src.sources.bitcoin_price import BitcoinPriceSource
from src.sources.github_trending import GitHubTrendingSource
from src.sources.gold_price import GoldPriceSource
from src.sources.kimlong_gold_price import KimLongGoldPriceSource
from src.sources.stock_price import StockPriceSource

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

_SOURCE_FACTORIES: dict[str, callable] = {
    "gold-price": lambda cfg: GoldPriceSource(),
    "kimlong-gold-price": lambda cfg: KimLongGoldPriceSource(
        product_ids=cfg.get("product_ids", None)
    ),
    "bitcoin-price": lambda cfg: BitcoinPriceSource(),
    "stock-price": lambda cfg: StockPriceSource(
        tickers=cfg.get("tickers", [])
    ),
    "github-trending": lambda cfg: GitHubTrendingSource(
        language=cfg.get("language", ""),
        since=cfg.get("since", "daily"),
        limit=cfg.get("limit", 5),
    ),
}

AVAILABLE_SOURCES = list(_SOURCE_FACTORIES.keys())


def get_source_by_name(name: str, config: dict) -> DataSource:
    """Instantiate a source by name. Raises ValueError if unknown."""
    if name not in _SOURCE_FACTORIES:
        raise ValueError(
            f"Unknown source '{name}'. Available: {', '.join(AVAILABLE_SOURCES)}"
        )
    source_cfg = config.get("sources", {}).get(name, {})
    return _SOURCE_FACTORIES[name](source_cfg)


def run_source(source: DataSource, notifier: TelegramNotifier) -> None:
    """Run a single source: fetch -> format -> send. Skips if empty."""
    records = source.fetch()
    if not records:
        logger.warning("[%s] fetch returned empty list, skipping send", source.name)
        return
    message = source.format(records)
    if not message:
        logger.warning("[%s] format returned empty string, skipping send", source.name)
        return
    notifier.send_message(message)
    logger.info("[%s] message sent successfully", source.name)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a single news-bot source")
    parser.add_argument(
        "--source",
        required=True,
        choices=AVAILABLE_SOURCES,
        help="Source to run",
    )
    args = parser.parse_args()

    load_dotenv()

    try:
        config = load_config()
        secrets = load_secrets()
    except ConfigError as exc:
        logger.error("Configuration error: %s", exc)
        sys.exit(1)

    notifier = TelegramNotifier(secrets["bot_token"], secrets["channel_id"])
    source = get_source_by_name(args.source, config)

    try:
        run_source(source, notifier)
    except Exception as exc:
        logger.error("[%s] pipeline error: %s", args.source, exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
