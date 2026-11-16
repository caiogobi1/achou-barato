#!/usr/bin/env python3
"""Send one harmless Telegram connection-test message, without reading the catalog."""
import json
import os
import urllib.error
import urllib.parse
import urllib.request

def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat:
        raise SystemExit("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
    message = ("✅ Teste de conexão do Buscoubarato!\n"
               "O bot conseguiu publicar neste canal.\n"
               "Esta é apenas uma mensagem de teste, sem ofertas ou preços.")
    payload = urllib.parse.urlencode({"chat_id": chat, "text": message,
                                      "disable_web_page_preview": "true"}).encode("utf-8")
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        # Never print response bodies: they may contain sensitive data.
        raise SystemExit(f"Telegram HTTP error {exc.code}. Check channel username and bot permissions.") from None
    except urllib.error.URLError:
        raise SystemExit("Telegram network error; no confirmation of delivery.") from None
    if not result.get("ok"):
        raise SystemExit("Telegram did not confirm message delivery.")
    print("Connection test succeeded: Telegram confirmed message delivery.")

if __name__ == "__main__":
    main()
