import pytest
from src.base import DataSource


def test_datasource_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        DataSource()  # type: ignore


def test_subclass_missing_fetch_raises_on_instantiation():
    class BadSource(DataSource):
        name = "bad"
        default_schedule = "0 * * * *"

        def format(self, records: list[dict]) -> str:
            return ""

    with pytest.raises(TypeError):
        BadSource()


def test_subclass_missing_format_raises_on_instantiation():
    class BadSource(DataSource):
        name = "bad"
        default_schedule = "0 * * * *"

        def fetch(self) -> list[dict]:
            return []

    with pytest.raises(TypeError):
        BadSource()


def test_valid_subclass_is_instantiable_and_has_correct_attributes():
    class GoodSource(DataSource):
        name = "good"
        default_schedule = "0 8 * * *"

        def fetch(self) -> list[dict]:
            return [{"value": 1}]

        def format(self, records: list[dict]) -> str:
            return "formatted"

    source = GoodSource()
    assert source.name == "good"
    assert source.default_schedule == "0 8 * * *"
    assert source.fetch() == [{"value": 1}]
    assert source.format([]) == "formatted"
