# news-bot-say-hi

[![CI](https://github.com/alanzng/news-bot-say-hi/actions/workflows/ci.yml/badge.svg)](https://github.com/alanzng/news-bot-say-hi/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A scheduled Telegram bot that pushes Vietnamese market data and developer trends to a channel — gold prices, Bitcoin, stocks, and GitHub trending repos. Each data source runs on its own cron schedule via GitHub Actions, so **no server is required**.

## ✨ Features

- 📈 **Vietnamese stock prices** — VN-Index, VN30, and configurable tickers (via [vnstock](https://vnstocks.com/))
- 🏆 **Gold prices** — SJC and Kim Long Đồng Tháp jewelry
- ₿ **Bitcoin** — BTC/USD with 24h change (via CoinGecko)
- 🔥 **GitHub Trending** — top repos with clickable links
- ⚙️ **Plugin architecture** — add new sources by implementing a simple 2-method interface
- 🕐 **Zero-ops scheduling** — runs entirely on GitHub Actions cron
- 🎨 **Beautiful messages** — HTML formatting with emojis, no link-preview clutter

## 📸 Sample output

```
📈 Giá cổ phiếu Việt Nam

🏛 Chỉ số thị trường
  • VN-Index: 1,819.83 📈 +1.07%
  • VN30: 1,979.19 📈 +0.90%

💹 Cổ phiếu
  • VNM: 61,100 VNĐ 📉 -0.33%
  • HPG: 26,500 VNĐ 📈 +1.85%

🔗 Nguồn: vnstocks
```

## 📦 Data sources

| Source | What it sends | Default schedule (VN time) |
|---|---|---|
| `gold-price` | SJC gold buy/sell prices | 8:00 AM daily |
| `kimlong-gold-price` | Kim Long Đồng Tháp jewelry prices | 8:10 AM daily |
| `bitcoin-price` | BTC/USD price + 24h change | 8:05 AM daily |
| `stock-price` | VN-Index, VN30, + configurable tickers | 9:00 AM Mon–Fri |
| `github-trending` | Top trending GitHub repositories | 9:00 AM daily |

## 🚀 Quick start (with GitHub Actions — recommended)

**1. Fork this repo** (or use it as a template).

**2. Create a Telegram bot** via [@BotFather](https://t.me/BotFather), then add it as admin to your channel.

**3. Add repository secrets** — Settings → Secrets and variables → Actions:
- `TELEGRAM_BOT_TOKEN` — your bot token
- `TELEGRAM_CHANNEL_ID` — `@mychannel` or numeric chat ID (e.g. `-1001234567890`)

**4. Customize** `sources.example.yaml` (copy to `sources.yaml` for local use; GitHub Actions falls back to the example).

**5. Trigger manually** — go to Actions tab → pick a workflow → Run workflow. Or wait for the cron.

That's it! No server, no Docker, no money spent.

## 🧑‍💻 Local development

```bash
# Clone and install
git clone https://github.com/alanzng/news-bot-say-hi.git
cd news-bot-say-hi
pip install -r requirements.txt

# Configure
cp sources.example.yaml sources.yaml
cp .env.example .env
# edit .env with your bot token + channel ID

# Run all sources on schedule (long-running process)
make run

# Run a single source once (useful for debugging)
python -m src.cli --source gold-price

# Run tests
make test

# Lint
make lint
```

## ⚙️ Configuration

`sources.yaml` (or `sources.example.yaml` as a fallback) controls enabled sources and their options:

```yaml
sources:
  stock-price:
    enabled: true
    schedule: "0 9 * * 1-5"   # cron (local mode only; GitHub Actions uses .github/workflows/)
    tickers:
      - HPG   # Hoa Phat Group
      - MBB   # MB Bank
      - SSI   # SSI Securities

  github-trending:
    enabled: true
    language: ""              # empty = all languages; or "python", "rust", etc.
    since: "daily"            # daily | weekly | monthly
    limit: 5
```

Set `enabled: false` to disable any source.

### Environment variables

| Variable | Required | Description |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | ✅ | Bot token from [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_CHANNEL_ID` | ✅ | Channel username (`@mychannel`) or numeric chat ID |
| `RUN_ON_STARTUP` | ❌ | `true` to fire all sources immediately on start (local mode) |

## 🏗️ Project structure

```
src/
├── base.py              # DataSource abstract base class
├── cli.py               # Single-source runner (used by GitHub Actions)
├── main.py              # APScheduler long-running process (local mode)
├── config.py            # Loads sources.yaml + env secrets
├── notifier.py          # Telegram Bot API wrapper
├── registry.py          # Wires sources to schedules
└── sources/
    ├── gold_price.py
    ├── kimlong_gold_price.py
    ├── bitcoin_price.py
    ├── stock_price.py
    └── github_trending.py
.github/workflows/       # One cron workflow per source + CI
tests/                   # pytest suite mirroring src/
```

## 🧩 Adding a new data source

1. Create `src/sources/my_source.py` extending `DataSource`:

   ```python
   from src.base import DataSource

   class MySource(DataSource):
       name = "my-source"
       default_schedule = "0 9 * * *"

       def fetch(self) -> list[dict]:
           # return records or [] on soft failure
           ...

       def format(self, records: list[dict]) -> str:
           # return HTML Telegram message, or "" to skip sending
           ...
   ```

2. Register in `src/registry.py`.
3. Add a block in `sources.example.yaml`.
4. Copy an existing `.github/workflows/*.yml` and update the `--source` arg + cron.
5. Add tests at `tests/sources/test_my_source.py`.

See [AGENTS.md](AGENTS.md) for the full contributor playbook.

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for the workflow, coding conventions, and PR checklist. For AI-assisted contributions (Claude Code, Cursor, etc.), see [AGENTS.md](AGENTS.md).

## 📄 License

[MIT](LICENSE) © Alan Ng

## 🙏 Acknowledgements

- [vnstock](https://vnstocks.com/) — Vietnamese stock market data
- [SJC](https://sjc.com.vn/), [Kim Long Đồng Tháp](https://kimlongdongthap.vn/) — gold price data
- [CoinGecko](https://www.coingecko.com/) — crypto prices
- [CafeF](https://cafef.vn/) — market index data
