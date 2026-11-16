#!/usr/bin/env python3
"""Read-only catalog audit. Does not modify products or affiliate links."""
import json
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

path = Path(__file__).resolve().parents[1] / "products.json"
products = json.loads(path.read_text(encoding="utf-8"))
if not isinstance(products, list):
    raise SystemExit("ERROR: products.json must be an array")
issues = []
links = []
for n, item in enumerate(products, 1):
    if not isinstance(item, dict):
        issues.append(f"#{n}: invalid record")
        continue
    for field in ("name", "url", "store"):
        if not isinstance(item.get(field), str) or not item[field].strip():
            issues.append(f"#{n}: missing {field}")
    url = item.get("url", "")
    if isinstance(url, str):
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.netloc:
            issues.append(f"#{n}: invalid HTTPS URL")
        elif parsed.netloc.lower() not in ("meli.la", "mercadolivre.com.br", "www.mercadolivre.com.br", "s.shopee.com.br", "shopee.com.br", "www.shopee.com.br"):
            issues.append(f"#{n}: review unfamiliar link host {parsed.netloc}")
        links.append(url)
    if not item.get("image"):
        issues.append(f"#{n}: no image")
    if not item.get("price"):
        issues.append(f"#{n}: no price")
    if not item.get("priceDate"):
        issues.append(f"#{n}: no price verification date")
duplicates = {link: count for link, count in Counter(links).items() if count > 1}
print(f"Products: {len(products)} | Duplicate links: {len(duplicates)} | Findings: {len(issues)}")
for link, count in duplicates.items():
    print(f"DUPLICATE ({count}): {link}")
for issue in issues[:100]:
    print("CHECK:", issue)
if len(issues) > 100:
    print(f"... {len(issues)-100} additional findings")
print("No catalog files were changed.")
