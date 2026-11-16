#!/usr/bin/env python3
"""Prepare Telegram messages; preview only, never posts or modifies the catalog."""
import argparse
import json
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlparse

CATALOG = Path(__file__).resolve().parents[1] / "products.json"

def recent_price(value, max_age_days=1):
    try:
        checked = datetime.strptime(value, "%d/%m/%Y").date()
        age = (date.today() - checked).days
        return 0 <= age <= max_age_days
    except (TypeError, ValueError):
        return False

def candidates(items, max_age_days):
    seen = set()
    for item in items:
        if not isinstance(item, dict):
            continue
        link = item.get("url")
        if not isinstance(link, str) or link in seen:
            continue
        parsed = urlparse(link)
        if parsed.scheme != "https" or not parsed.netloc:
            continue
        if item.get("affiliate") is not True:
            continue
        if not all(isinstance(item.get(k), str) and item[k].strip() for k in ("name", "price", "store")):
            continue
        if not recent_price(item.get("priceDate"), max_age_days):
            continue
        seen.add(link)
        yield item

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=2)
    parser.add_argument("--max-price-age-days", type=int, default=1)
    args = parser.parse_args()
    if args.limit < 1 or args.max_price_age_days < 0:
        parser.error("limit must be positive and max-price-age-days nonnegative")
    items = json.loads(CATALOG.read_text(encoding="utf-8"))
    if not isinstance(items, list):
        raise SystemExit("Invalid catalog")
    offers = list(candidates(items, args.max_price_age_days))[:args.limit]
    print(f"Telegram preview only: {len(offers)} eligible offers")
    for item in offers:
        print("\n--- PREVIEW (NOT SENT) ---")
        print(f"{item['name']}\n{item['price']} · {item['store']}\n{item['url']}")
        print("Confira o preço e a disponibilidade na loja antes de comprar.")
    if not offers:
        print("No offers with recent verified price dates. Nothing will be posted.")
    print("No messages sent; no products or affiliate links modified.")

if __name__ == "__main__":
    main()
