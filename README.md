# PrimeTrade — Binance Futures Testnet Trading Bot 🚀

A structured Python trading bot for placing orders on Binance Futures Testnet (USDT-M). Includes a CLI with interactive mode and a lightweight web UI.

## Project Structure

```
primetrade/
├── bot/
│   ├── __init__.py          # Package init
│   ├── client.py            # Binance Futures Testnet client wrapper
│   ├── orders.py            # Order placement logic + response formatting
│   ├── validators.py        # Input validation (symbol, side, type, qty, price)
│   └── logging_config.py    # Rotating file + console logging config
├── web/
│   ├── app.py               # Lightweight HTTP server + order API
│   └── index.html           # Web UI (trading panel + intern details)
├── logs/
│   └── trading_bot.log      # Generated at runtime
├── cli.py                   # CLI entry point (Click + Rich)
├── requirements.txt         # Python dependencies
├── .env.example             # Template for API credentials
├── .gitignore
└── README.md
```

## Setup

### 1. Prerequisites
- Python 3.10+
- Binance Futures Testnet account ([Register here](https://testnet.binancefuture.com/))

### 2. Install Dependencies

```bash
cd primetrade
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure API Keys

Copy the example env file and fill in your Binance Futures Testnet credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here
```

> **Note**: Never commit your `.env` file. It is included in `.gitignore`.

## How to Run

### CLI Mode

#### Direct Command

```bash
# MARKET order — Buy 0.001 BTC
python cli.py order --symbol BTCUSDT --side BUY --order-type MARKET --quantity 0.001

# LIMIT order — Sell 0.01 ETH at $3000
python cli.py order -s ETHUSDT -d SELL -t LIMIT -q 0.01 -p 3000

# STOP_LIMIT order (bonus) — Buy BTC with stop at 49000, limit 50000
python cli.py order -s BTCUSDT -d BUY -t STOP_LIMIT -q 0.001 -p 50000 -sp 49000
```

#### Interactive Mode

```bash
python cli.py interactive
```

Follow the guided prompts to place orders with validation and confirmation.

#### Help

```bash
python cli.py --help
python cli.py order --help
```

### Web UI Mode

```bash
python web/app.py
```

Open [http://localhost:8080](http://localhost:8080) in your browser.

The web UI has three tabs:
- **🔄 Trading Panel** — Place orders via the form
- **📋 Order Log** — View order history for the session
- **👤 Intern Details** — Resume / profile information

## Order Types Supported

| Type | Description | Required Fields |
|------|-------------|-----------------|
| `MARKET` | Immediate execution at market price | symbol, side, quantity |
| `LIMIT` | Execute at specified price or better | symbol, side, quantity, price |
| `STOP_LIMIT` | Triggered when stop price is hit (bonus) | symbol, side, quantity, price, stop_price |

## Logging

All API requests, responses, and errors are logged to `logs/trading_bot.log`.

Log format:
```
2026-03-25 12:30:00 | INFO     | bot.client           | Placing MARKET order — {...}
2026-03-25 12:30:01 | INFO     | bot.client           | MARKET order response — orderId: 123, status: FILLED
```

- File rotation: 5 MB max, 3 backup files
- Console output: warnings and errors only

## Assumptions

1. **Testnet only** — All API calls target `https://testnet.binancefuture.com`. No real funds are involved.
2. **API credentials** — Read from environment variables (`BINANCE_API_KEY`, `BINANCE_API_SECRET`) or a `.env` file.
3. **Order validation** — Basic client-side validation is performed (symbol format, side, type, quantity > 0, price required for LIMIT). Exchange-level validation (e.g., lot size, min notional) is handled by the Binance API.
4. **Time in force** — Defaults to GTC (Good Till Cancelled) for LIMIT and STOP_LIMIT orders.
5. **python-binance** — Uses the `python-binance` library for API interactions.

## Tech Stack

- **Python 3.10+**
- **python-binance** — Binance API wrapper
- **Click** — CLI framework with enhanced UX
- **Rich** — Beautiful terminal output
- **python-dotenv** — Environment variable management

## Author

**Vishwa Panchal**  
Backend Developer & Cloud Practitioner  
[GitHub](https://github.com/vishwapanchal) · [LinkedIn](https://linkedin.com/in/thevishwapanchal) · [Portfolio](https://thevishwapanchal.pages.dev)
