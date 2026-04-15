from abc import ABC, abstractmethod


class DataSource(ABC):
    """Plugin contract that all data sources must implement."""

    name: str
    default_schedule: str

    @abstractmethod
    def fetch(self) -> list[dict]:
        """Fetch raw data records from the external source.

        Returns a list of dicts on success.
        Raises an exception on failure.
        """

    @abstractmethod
    def format(self, records: list[dict]) -> str:
        """Convert raw records into a Telegram message string.

        Returns empty string if records is empty (signals: skip send).
        """
