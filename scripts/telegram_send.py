#!/usr/bin/env python3
"""Send at most two verified, recently dated catalog offers to a Telegram channel.

Requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables.
Never modifies products.json or affiliate URLs.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from telegram_preview import candidates

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "telegram-sent.json"

def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat:
        raise SystemExit("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
    items = json.loads((ROOT / "products.json").read_text(encoding="utf-8"))
    sent = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else []
    if not isinstance(sent, list):
        raise SystemExit("Invalid send history")
    already = set(sent)
    selected = [item for item in candidates(items, 1) if item["url"] not in already][:2]
    if not selected:
        print("No new offers with recently verified price. Nothing sent.")
        return
    for item in selected:
        msg = (f"{item['name']}\n{item['price']} · {item['store']}\n"
               f"{item['url']}\nConfira preço e disponibilidade na loja.")
        payload = urllib.parse.urlencode({"chat_id": chat, "text": msg, "disable_web_page_preview": "true"}).encode()
        request = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage", data=payload, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                result = json.load(response)
                if not result.get("ok"):
                    raise RuntimeError("Telegram rejected message")
        except (urllib.error.URLError, ValueError) as exc:
            print("Telegram send failed; stopping without marking failed message.", file=sys.stderr)
            raise SystemExit(1) from exc
        sent.append(item["url"])
        STATE.write_text(json.dumps(sent, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Sent: {item['name']}")
    print(f"Successfully sent {len(selected)} offers.")

if __name__ == "__main__":
    main()
