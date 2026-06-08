from playwright.sync_api import sync_playwright
from telegram import send_telegram
import json

URL = "https://www.travelplanet.pl/wakacje/?s_action=TRIPS_SEARCH&d_start_from=05.09.2026&d_end_to=15.09.2026&page=1"


# =========================
# 🌐 FULL NETWORK CAPTURE
# =========================

def capture_network():
    logs = []

    def handle_response(response):
        try:
            req = response.request
            url = response.url

            if any(x in url.lower() for x in ["search", "trip", "offer", "result", "api"]):
                entry = {
                    "url": url,
                    "method": req.method,
                    "headers": dict(req.headers),
                }

                try:
                    if "json" in response.headers.get("content-type", ""):
                        entry["json"] = response.json()
                    else:
                        entry["text"] = response.text()[:500]
                except:
                    pass

                logs.append(entry)

        except:
            pass

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.on("response", handle_response)

        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_timeout(20000)

        browser.close()

    return logs


# =========================
# 🚀 MAIN
# =========================

def main():
    print("🚀 NETWORK HARVEST START")

    logs = capture_network()

    if not logs:
        send_telegram("❌ Brak requestów network (blokada / lazy load)")
        return

    with open("network_dump.json", "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

    # znajdź największy response JSON
    jsons = [l for l in logs if "json" in l]

    if not jsons:
        send_telegram(
            f"📡 Zebrano {len(logs)} requestów\n❌ brak JSON z ofertami\n👉 sprawdzamy network_dump.json"
        )
        return

    biggest = max(jsons, key=lambda x: len(str(x["json"])))

    with open("best_network.json", "w", encoding="utf-8") as f:
        json.dump(biggest, f, ensure_ascii=False, indent=2)

    send_telegram(
        "📡 NETWORK CAPTURE OK\n"
        f"🔎 Requests: {len(logs)}\n"
        f"📦 JSON: {len(jsons)}\n"
        "👉 zapisano best_network.json"
    )


if __name__ == "__main__":
    main()
