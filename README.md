# my-news-bot

A scheduled Telegram bot that delivers daily market data and trending developer content to a channel. Each data source runs on its own cron schedule and pushes a formatted message via the Telegram Bot API.

## Data sources

| Source | What it sends | Default schedule |
|---|---|---|
| `gold-price` | SJC gold buy/sell prices (sjc.com.vn) | 8 AM daily |
| `kimlong-gold-price` | Kim Long Đồng Tháp jewelry prices | 8 AM daily |
| `bitcoin-price` | BTC/USD price + 24h change (CoinGecko) | Every 6 hours |
| `stock-price` | Vietnamese stock prices via VCI (vnstock3) | 9 AM Mon–Fri |
| `github-trending` | Top trending GitHub repositories | 9 AM daily |

## Requirements

- Python 3.11+
- A Telegram bot token and a target channel ID

## Setup

**1. Install dependencies**

```bash
pip install -e .
```

Or with a virtual environment:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

**2. Configure sources**

Copy the example config and edit it:

```bash
cp sources.example.yaml sources.yaml
```

Edit `sources.yaml` to enable/disable sources, set schedules, and configure per-source options (tickers, language, etc.).

**3. Set secrets**

```bash
export TELEGRAM_BOT_TOKEN=your_bot_token
export TELEGRAM_CHANNEL_ID=your_channel_id
```

Or create a `.env` file in the project root:

```
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHANNEL_ID=your_channel_id
```

**4. Run**

```bash
python -m src.main
```

The process blocks and runs all sources on their configured cron schedules. Send `SIGINT` or `SIGTERM` to stop gracefully.

### Option B: Run with GitHub Actions (no server needed)

The bot can run entirely on GitHub Actions — no server required.

**1. Add repository secrets**

Go to your repo → Settings → Secrets and variables → Actions → New repository secret:

- `TELEGRAM_BOT_TOKEN` — your bot token from @BotFather
- `TELEGRAM_CHANNEL_ID` — your channel ID

**2. Workflows**

Each source has its own workflow in `.github/workflows/` with a cron schedule:

| Workflow | Source | Schedule (UTC) | Vietnam time |
|---|---|---|---|
| `gold-price.yml` | SJC Gold | `0 1 * * *` | 8 AM daily |
| `kimlong-gold-price.yml` | Kim Long Gold | `0 1 * * *` | 8 AM daily |
| `bitcoin-price.yml` | Bitcoin | `0 */6 * * *` | Every 6 hours |
| `stock-price.yml` | Stock | `0 2 * * 1-5` | 9 AM weekdays |
| `github-trending.yml` | GitHub Trending | `0 2 * * *` | 9 AM daily |

**3. Manual trigger**

All workflows support `workflow_dispatch` — click "Run workflow" in the Actions tab to test.

**4. Run a single source locally**

```bash
python -m src.cli --source gold-price
```

## Configuration

`sources.yaml` controls which sources are active and when they run:

```yaml
sources:
  gold-price:
    enabled: true
    schedule: "0 8 * * *"   # 8 AM daily

  bitcoin-price:
    enabled: true
    schedule: "0 */6 * * *" # Every 6 hours

  stock-price:
    enabled: true
    schedule: "0 9 * * 1-5" # 9 AM on Vietnamese trading weekdays
    tickers:
      - VNM   # Vinamilk
      - HPG   # Hoa Phat Group
      - VIC   # Vingroup
      - VCB   # Vietcombank
      - FPT   # FPT Corporation

  github-trending:
    enabled: true
    schedule: "0 9 * * *"
    language: ""    # empty = all languages, or e.g. "python"
    since: "daily"  # daily | weekly | monthly
    limit: 5
```

Set `enabled: false` to disable a source without removing it.

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Yes | Bot token from [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_CHANNEL_ID` | Yes | Channel username (`@mychannel`) or numeric chat ID |
| `RUN_ON_STARTUP` | No | Set to `true` to fire all sources immediately on start |

## Running tests

```bash
pytest
```

## Project structure

```
src/
  main.py              # Entry point — APScheduler long-running process
  cli.py               # CLI entry point — run a single source once (for GitHub Actions)
  config.py            # Loads sources.yaml and environment secrets
  registry.py          # SourceRegistry — schedules and runs each source via APScheduler
  notifier.py          # TelegramNotifier — sends messages via Telegram Bot API
  base.py              # DataSource abstract base class
  sources/
    gold_price.py            # SJC gold prices (sjc.com.vn API)
    kimlong_gold_price.py    # Kim Long Dong Thap jewelry prices
    bitcoin_price.py         # Bitcoin price via CoinGecko API
    stock_price.py           # Vietnamese stock prices via vnstock3
    github_trending.py       # GitHub trending scraper
.github/workflows/     # GitHub Actions cron workflows (one per source + CI)
tests/                 # Unit tests mirroring src/ structure
sources.yaml           # Local config (not committed)
```
