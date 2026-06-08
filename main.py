from playwright.sync_api import sync_playwright
from telegram import send_telegram
import json

URL = "https://www.travelplanet.pl/wakacje/?s_action=TRIPS_SEARCH&d_start_from=05.09.2026&d_end_to=15.09.2026&page=1"


def capture_full():
    logs = []

    def handle_response(response):
        try:
            req = response.request

            entry = {
                "url": response.url,
                "method": req.method,
                "post": req.post_data,
            }

            # 🔥 RAW RESPONSE (NAJWAŻNIEJSZE)
            try:
                body = response.text()
                entry["body"] = body[:2000]  # ograniczenie
            except:
                pass

            logs.append(entry)

        except:
            pass

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.on("response", handle_response)

        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(20000)

        browser.close()

    return logs


def main():
    logs = capture_full()

    with open("full_trace.json", "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

    # 🔍 szukamy podejrzanych endpointów
    candidates = [
        l for l in logs
        if any(x in l["url"].lower() for x in ["search", "trip", "result", "offer", "ajax"])
    ]

    send_telegram(
        "📡 FINAL TRACE RAW\n"
        f"🔎 Requests: {len(logs)}\n"
        f"🎯 Candidates: {len(candidates)}\n"
        "👉 zapisano full_trace.json"
    )


if __name__ == "__main__":
    main()
