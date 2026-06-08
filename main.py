from playwright.sync_api import sync_playwright
from telegram import send_telegram
import json

URL = "https://www.travelplanet.pl/wakacje/?s_action=TRIPS_SEARCH&d_start_from=05.09.2026&d_end_to=15.09.2026&page=1"


def capture_requests():
    logs = []

    def handle_response(response):
        try:
            req = response.request

            logs.append({
                "url": response.url,
                "method": req.method,
                "post": req.post_data,
                "headers": dict(req.headers)
            })

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


def main():
    logs = capture_requests()

    with open("all_requests.json", "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

    # 🔥 filtr POST
    posts = [l for l in logs if l["method"] == "POST"]

    send_telegram(
        "📡 FINAL DEBUG\n"
        f"🔎 Requests: {len(logs)}\n"
        f"📤 POST: {len(posts)}\n"
        "👉 zapisano all_requests.json"
    )


if __name__ == "__main__":
    main()
