#!/usr/bin/env python3
"""Read-only freshness report. A catalog date is not independent price verification."""
import json
from collections import Counter
from datetime import date, datetime
from pathlib import Path

catalog = Path(__file__).resolve().parents[1] / "products.json"
items = json.loads(catalog.read_text(encoding="utf-8"))
if not isinstance(items, list):
    raise SystemExit("Invalid catalog")
counts = Counter()
for item in items:
    if not isinstance(item, dict):
        counts["invalid record"] += 1
        continue
    value = item.get("priceDate")
    if not item.get("price"):
        counts["no price"] += 1
    try:
        checked = datetime.strptime(value, "%d/%m/%Y").date()
        age = (date.today() - checked).days
        counts["date within 1 day (not independently verified)"] += 0 <= age <= 1
        counts["stale or future date"] += age < 0 or age > 1
    except (ValueError, TypeError):
        counts["missing or invalid date"] += 1
print(f"Catalog items: {len(items)}")
for label, count in sorted(counts.items()):
    print(f"{label}: {count}")
print("No live marketplace price API is connected by this report.")
print("No products, affiliate links or prices were modified.")
