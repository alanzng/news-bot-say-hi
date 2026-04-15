import logging
import os
import signal
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from src.base import DataSource
from src.notifier import TelegramNotifier

logger = logging.getLogger(__name__)


class SourceRegistry:
    """Manages multiple DataSource instances, scheduling each independently."""

    def __init__(
        self,
        sources: list[DataSource],
        notifier: TelegramNotifier,
        schedules: dict[str, str] | None = None,
    ) -> None:
        self.sources = sources
        self.notifier = notifier
        self._schedules = schedules or {}
        self._scheduler = BackgroundScheduler()

    def _get_schedule(self, source: DataSource) -> str:
        return self._schedules.get(source.name, source.default_schedule)

    def _run_source(self, source: DataSource) -> None:
        try:
            records = source.fetch()
            if not records:
                logger.warning("[%s] fetch returned empty list, skipping send", source.name)
                return
            message = source.format(records)
            if not message:
                logger.warning("[%s] format returned empty string, skipping send", source.name)
                return
            self.notifier.send_message(message)
            logger.info("[%s] message sent successfully", source.name)
        except Exception as exc:
            logger.error("[%s] pipeline error: %s", source.name, exc)

    def start(self) -> None:
        """Register all sources with the scheduler and block until shutdown."""
        for source in self.sources:
            cron = self._get_schedule(source)
            self._scheduler.add_job(
                self._run_source,
                CronTrigger.from_crontab(cron),
                args=[source],
                id=source.name,
                name=source.name,
            )
            logger.info("[%s] scheduled: %s", source.name, cron)

        if os.environ.get("RUN_ON_STARTUP", "").lower() == "true":
            for source in self.sources:
                logger.info("[%s] running on startup", source.name)
                self._run_source(source)

        self._scheduler.start()
        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)

        try:
            while True:
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            self._scheduler.shutdown()

    def _shutdown(self, signum, frame) -> None:
        logger.info("Received signal %s, shutting down...", signum)
        self._scheduler.shutdown()
        raise SystemExit(0)
