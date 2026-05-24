#!/usr/bin/env python3
"""
portfolio-tracker.py — Multi-asset cryptocurrency portfolio tracker

Track your crypto portfolio with real-time prices, P&L, and performance metrics.
Supports BTC, ETH, SOL, LTC, and more. Zero dependencies.

Usage:
    python portfolio-tracker.py --add BTC 0.5 50000
    python portfolio-tracker.py --list
    python portfolio-tracker.py --json

Support: https://github.com/will-work-for-bitcoin/portfolio-tracker
"""

import sys
import json
import urllib.request
from datetime import datetime
from pathlib import Path

PORTFOLIO_FILE = Path.home() / ".portfolio.json"
COIN_SYMBOLS = {"bitcoin": "BTC", "ethereum": "ETH", "solana": "SOL", "litecoin": "LTC", "cardano": "ADA"}


def fetch_current_prices():
    ids = "bitcoin,ethereum,solana,litecoin,cardano"
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"
    req = urllib.request.Request(url, headers={"User-Agent": "portfolio-tracker/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}


def load_portfolio():
    if PORTFOLIO_FILE.exists():
        with open(PORTFOLIO_FILE) as f:
            return json.load(f)
    return []


def save_portfolio(portfolio):
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(portfolio, f, indent=2)


def add_asset(coin, amount, buy_price):
    portfolio = load_portfolio()
    asset = {
        "coin": coin.upper(),
        "amount": float(amount),
        "buy_price": float(buy_price),
        "added": datetime.now().isoformat(),
    }
    portfolio.append(asset)
    save_portfolio(portfolio)
    print(f"Added {amount} {coin.upper()} at ${buy_price:,.2f}")


def display_portfolio():
    portfolio = load_portfolio()
    if not portfolio:
        print("Portfolio empty. Use --add <coin> <amount> <buy_price> to add assets.")
        return
    current_prices = fetch_current_prices()
    total_usd = 0
    total_cost = 0
    print("COIN    AMOUNT    BUY PRICE  CURRENT    VALUE      P&L")
    print("-" * 60)
    for asset in portfolio:
        coin = asset["coin"]
        amount = asset["amount"]
        buy_price = asset["buy_price"]
        coin_lower = coin.lower()
        current_price = 0
        if coin_lower in current_prices:
            current_price = current_prices[coin_lower].get("usd", 0)
        value = amount * current_price
        cost = amount * buy_price
        pnl = value - cost
        pnl_pct = (pnl / cost * 100) if cost > 0 else 0
        total_usd += value
        total_cost += cost
        pnl_str = f"${pnl:,.2f} ({pnl_pct:+.1f}%)"
        print(f"{coin:<8} {amount:>.6f} ${buy_price:>9,.2f} ${current_price:>9,.2f} ${value:>11,.2f} {pnl_str}")
    total_pnl = total_usd - total_cost
    total_pnl_pct = (total_pnl / total_cost * 100) if total_cost > 0 else 0
    print("-" * 60)
    print(f"{'TOTAL':<42} ${total_usd:>11,.2f} ${total_pnl:>9,.2f} ({total_pnl_pct:+.1f}%)")


def display_json():
    portfolio = load_portfolio()
    current_prices = fetch_current_prices()
    result = []
    for asset in portfolio:
        coin = asset["coin"]
        amount = asset["amount"]
        buy_price = asset["buy_price"]
        coin_lower = coin.lower()
        current_price = 0
        if coin_lower in current_prices:
            current_price = current_prices[coin_lower].get("usd", 0)
        entry = dict(asset)
        entry["current_price"] = current_price
        entry["value"] = amount * current_price
        result.append(entry)
    print(json.dumps(result, indent=2))


def main():
    args = sys.argv[1:]
    if not args or "--help" in args or "-h" in args:
        print(__doc__)
        return
    if "add" in args and len(args) >= 4:
        add_asset(args[args.index("add") + 1], args[args.index("add") + 2], args[args.index("add") + 3])
    elif "json" in args:
        display_json()
    else:
        display_portfolio()


if __name__ == "__main__":
    main()
