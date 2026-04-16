# AGENTS.md

Guidance for AI coding agents (Claude Code, Codex, Cursor, etc.) working on this repository.

## Project overview

`my-news-bot` is a scheduled Telegram bot that pushes daily market data and trending content to a Telegram channel. Each data source runs on its own cron schedule via GitHub Actions and is implemented as a small Python plugin behind a common `DataSource` interface.

- **Language:** Python 3.11+
- **Test runner:** `pytest`
- **Linter:** `ruff`
- **Scheduler (prod):** GitHub Actions cron workflows (one per source)
- **Scheduler (local):** `APScheduler` long-running process via `python -m src.main`
- **Telegram delivery:** HTML `parse_mode`, `disable_web_page_preview=True`

## Repository layout

```
src/
  base.py             # DataSource ABC — fetch() + format() contract
  cli.py              # CLI for one-shot runs: python -m src.cli --source <name>
  config.py           # Loads sources.yaml (falls back to sources.example.yaml)
  main.py             # APScheduler entry — long-running process
  notifier.py         # TelegramNotifier — Bot API wrapper
  registry.py         # SourceRegistry — wires sources to schedules
  sources/
    bitcoin_price.py        # BTC/USD via CoinGecko
    github_trending.py      # github.com/trending scraper
    gold_price.py           # SJC gold prices
    kimlong_gold_price.py   # Kim Long Đồng Tháp gold
    stock_price.py          # Vietnamese stocks (vnstock/KBS) + VN-Index/VN30 (CafeF)
.github/workflows/    # One cron workflow per source + ci.yml
tests/                # pytest, mirrors src/ structure
sources.example.yaml  # Default config (used in CI when sources.yaml missing)
sources.yaml          # Local config — gitignored
```

## Core contract: `DataSource`

Every source in `src/sources/` extends `src.base.DataSource` and implements:

```python
class MySource(DataSource):
    name: str = "my-source"           # CLI/config key
    default_schedule: str = "0 9 * * *"  # cron expression

    def fetch(self) -> list[dict]:
        """Return list of records. Raise on hard failure, return [] on soft failure."""

    def format(self, records: list[dict]) -> str:
        """Return Telegram HTML message. Return '' to skip sending."""
```

**Conventions for new sources:**
- Catch external API errors inside `fetch()` and `logger.error(...)` rather than crashing the scheduler.
- `format([])` MUST return `""` (signals "skip send" to the registry).
- Use HTML formatting: `<b>`, `<a href="...">`, line breaks via `\n`.
- End every message with a source link: `🔗 Nguồn: <a href="...">name</a>`.
- URLs go inside `<a>` tags — link previews are disabled globally in `notifier.py`.
- Keep emoji style consistent with existing sources (📈/📉 for change, 🔗 for source, etc.).

## Common commands

```bash
# Install
pip install -r requirements.txt

# Run all sources on schedule (long-running)
make run
python -m src.main

# Run a single source once (used by GitHub Actions)
python -m src.cli --source gold-price

# Tests
pytest
pytest tests/sources/test_stock_price.py -v

# Lint
ruff check .
make lint
```

## Adding a new source — checklist

1. Create `src/sources/<name>.py` with a class extending `DataSource`.
2. Write tests first in `tests/sources/test_<name>.py`. Mock `requests.get` / external calls — never hit live APIs in tests.
3. Register the source in `src/registry.py` (`_SOURCE_CLASSES`).
4. Add a default block to `sources.example.yaml`.
5. Add a workflow file `.github/workflows/<name>.yml` (copy an existing one and edit `--source` arg + cron).
6. Update `README.md` data sources table.
7. Run `pytest` and `ruff check .` before committing.

## Telegram message style guide

Match the existing tone — Vietnamese-first, emoji-led headers, bold values:

```
📈 <b>Giá cổ phiếu Việt Nam</b>

🏛 <b>Chỉ số thị trường</b>
  • <b>VN-Index</b>: <b>1,819.83</b> 📈 +1.07%

💹 <b>Cổ phiếu</b>
  • <b>VNM</b>: <b>75,000</b> VNĐ 📈 +1.35%

🔗 Nguồn: <a href="https://vnstocks.com">vnstocks</a>
```

- Number formatting: `f"{value:,.0f}"` for VND, `f"{value:,.2f}"` for indices/USD.
- Trend emoji: `📈` if change ≥ 0, else `📉`.
- Sign prefix: `+` for non-negative, empty for negative (the `-` is already in the number).

## Testing conventions

- One test file per source, mirrored at `tests/sources/test_<name>.py`.
- Mock all network calls with `unittest.mock.patch`.
- Cover at least: constructor validation, `fetch` happy path, `fetch` API error, `format` happy path, `format` empty records, `name` and `default_schedule` constants.
- Use substring assertions on formatted output (e.g. `"vnstocks" in msg`) so cosmetic link/text tweaks don't break tests.

## Git workflow

- **Never push to `main`.** Always work on a feature branch (`feat/...`, `fix/...`, `refactor/...`, `chore/...`, `docs/...`).
- One commit per logical change with a descriptive message.
- Include this trailer when authored by AI:
  ```
  Co-Authored-By: Claude <noreply@anthropic.com>
  ```
- Open a PR against `main` for human review.
- CI (`.github/workflows/ci.yml`) runs `pytest` and `ruff check` — both must pass.

## GitHub Actions

- Production scheduling lives in `.github/workflows/<source>.yml`.
- All workflows support `workflow_dispatch` (manual trigger) — useful for verifying changes after deploy.
- Cron times are UTC. Vietnam is UTC+7. Convert before editing.
- Secrets `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHANNEL_ID` are injected at workflow runtime.
- Workflows use `sources.example.yaml` because `sources.yaml` is gitignored — keep the example file representative.

## Things to avoid

- Don't reintroduce `vnstock3` or the VCI source for stocks — both are blocked. Use `vnstock>=3.4.0` with `source="KBS"`.
- Don't add `disable_web_page_preview=False` — link previews clutter the channel.
- Don't hard-code secrets; always read from environment via `python-dotenv` / `os.getenv`.
- Don't commit `sources.yaml`, `.env`, or any file containing the bot token.
- Don't add new top-level dependencies without pinning a version in `requirements.txt`.
- Don't skip writing tests for new sources — TDD is preferred.

## Quick references

- DataSource base: `src/base.py`
- Registry / scheduler wiring: `src/registry.py`
- CLI for single-source runs: `src/cli.py`
- Telegram client: `src/notifier.py`
- Example config: `sources.example.yaml`
