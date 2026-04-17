# Contributing to news-bot-say-hi

Thanks for your interest in contributing! This project is intentionally small and pluggable — most contributions fall into one of three buckets:

1. **Add a new data source** (most common)
2. **Improve an existing source** (better formatting, fix an API change, etc.)
3. **Improve the core** (scheduler, notifier, tests, docs)

## Getting started

```bash
git clone https://github.com/alanzng/news-bot-say-hi.git
cd news-bot-say-hi
pip install -r requirements.txt
cp .env.example .env
make test
```

All tests should pass on a fresh clone. If they don't, open an issue.

## Development workflow

1. **Open an issue first** for non-trivial changes so we can discuss design before you write code.
2. **Fork** the repo and create a feature branch:
   - `feat/<name>` — new features or data sources
   - `fix/<name>` — bug fixes
   - `refactor/<name>` — restructuring
   - `docs/<name>` — documentation only
   - `chore/<name>` — dependencies, tooling, CI
3. **Write tests first** (TDD preferred). Mock all external API calls — never hit live APIs in tests.
4. **Run `make test` and `make lint`** before committing. CI runs both.
5. **Open a PR** against `main` with a clear description and rationale.

## Coding conventions

- **Python 3.11+**, type hints encouraged on public functions.
- **Linter:** `ruff`. Run `make lint` or `ruff check .`
- **Tests:** `pytest`. Put source tests at `tests/sources/test_<name>.py`.
- **Logging:** use `logger = logging.getLogger(__name__)`, not `print`.
- **Errors in `fetch()`:** catch external API errors, log with `logger.error`, return `[]` so the scheduler doesn't crash.
- **Empty results:** `format([])` must return `""` (signals "skip send").
- **Telegram messages:** use HTML (`<b>`, `<a href="...">`). Link previews are globally disabled in the notifier.
- **Style:** keep emoji usage consistent with existing sources — match the tone.

## Adding a new data source — checklist

- [ ] `src/sources/<name>.py` with a class extending `DataSource`
- [ ] `tests/sources/test_<name>.py` covering: constructor, fetch happy path, fetch error, format output, format empty, name/schedule constants
- [ ] Registered in `src/registry.py`
- [ ] Default block added to `sources.example.yaml`
- [ ] Workflow file at `.github/workflows/<name>.yml` (copy an existing one)
- [ ] README data sources table updated
- [ ] `make test` and `make lint` pass

## Commit messages

Keep them short and descriptive. Prefixes (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`) are encouraged but not required.

## Code of Conduct

Be kind. Assume good faith. No harassment, no spam, no crypto schemes in PRs.

## Secrets & security

- **Never commit** `.env`, `sources.yaml` (gitignored), or anything containing a bot token.
- If you accidentally leak a token, rotate it immediately via [@BotFather](https://t.me/BotFather).
- Report security issues privately via GitHub Security Advisories, not a public issue.

## Questions?

Open a [Discussion](https://github.com/alanzng/news-bot-say-hi/discussions) or issue. Response time is best-effort — this is a hobby project.
