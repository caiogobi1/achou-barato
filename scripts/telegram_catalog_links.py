#!/usr/bin/env python3
"""Post up to two existing affiliate catalog links, without stale prices or discounts."""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "telegram-sent.json"
ALLOWED_HOSTS = {"meli.la", "mercadolivre.com.br", "www.mercadolivre.com.br",
                 "shopee.com.br", "www.shopee.com.br", "s.shopee.com.br"}

def eligible(items, already):
    seen = set(already)
    for item in items:
        if not isinstance(item, dict) or item.get("affiliate") is not True:
            continue
        name, url = item.get("name"), item.get("url")
        if not isinstance(name, str) or not name.strip() or not isinstance(url, str):
            continue
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != "https" or (parsed.hostname or "").lower() not in ALLOWED_HOSTS:
            continue
        if url in seen:
            continue
        seen.add(url)
        yield name.strip(), url

def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat:
        raise SystemExit("Missing Telegram secrets")
    items = json.loads((ROOT / "products.json").read_text(encoding="utf-8"))
    if not isinstance(items, list):
        raise SystemExit("Invalid products.json")
    history = json.loads(HISTORY.read_text(encoding="utf-8")) if HISTORY.exists() else []
    if not isinstance(history, list) or not all(isinstance(x, str) for x in history):
        raise SystemExit("Invalid send history")
    selected = list(eligible(items, history))[:2]
    if not selected:
        print("No new eligible affiliate links. Nothing sent.")
        return
    for name, url in selected:
        message = (f"🛍️ {name}\n\n🔗 Confira o preço atual na loja:\n{url}\n\n"
                   "Publicidade: link de afiliado. Preço e disponibilidade podem mudar.")
        payload = urllib.parse.urlencode({"chat_id": chat, "text": message,
                                         "disable_web_page_preview": "true"}).encode()
        request = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage",
                                         data=payload, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                if not json.load(response).get("ok"):
                    raise RuntimeError("Telegram did not confirm delivery")
        except (urllib.error.URLError, ValueError, RuntimeError):
            print("Telegram send failed. Check bot access and channel.", file=sys.stderr)
            raise SystemExit(1) from None
        history.append(url)
        HISTORY.write_text(json.dumps(history, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
        print("Sent one catalog link successfully.")
    print(f"Sent {len(selected)} links without unverified prices.")

if __name__ == "__main__":
    main()
