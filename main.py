from playwright.sync_api import sync_playwright
from telegram import send_telegram
import json

URL = "https://www.travelplanet.pl/wakacje/?s_action=TRIPS_SEARCH&d_start_from=05.09.2026&d_end_to=15.09.2026&page=1"


# =========================
# 🌐 ZBIERANIE WSZYSTKICH JSON
# =========================

def get_all_json_responses():
    responses = []

    def handle_response(response):
        try:
            if "json" in response.headers.get("content-type", "").lower():
                try:
                    data = response.json()
                    responses.append({
                        "url": response.url,
                        "data": data
                    })
                except:
                    pass
        except:
            pass

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.on("response", handle_response)

        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_timeout(15000)

        browser.close()

    return responses


# =========================
# 🔍 SZUKANIE NAJWIĘKSZEGO JSON (POTENCJALNE OFERTY)
# =========================

def find_best_payload(responses):
    if not responses:
        return None

    # wybieramy największy JSON (heurystyka: najwięcej danych)
    best = max(responses, key=lambda x: len(str(x["data"])))

    return best


# =========================
# 🚀 MAIN
# =========================

def main():
    print("🚀 START DEBUG SCRAPER")

    responses = get_all_json_responses()

    print(f"📡 JSON responses found: {len(responses)}")

    # zapis pełnego debug
    with open("debug_all.json", "w", encoding="utf-8") as f:
        json.dump(responses, f, ensure_ascii=False, indent=2)

    best = find_best_payload(responses)

    if not best:
        send_telegram("❌ Nie znaleziono żadnych JSON response")
        return

    # zapis najlepszego payloadu
    with open("best_payload.json", "w", encoding="utf-8") as f:
        json.dump(best, f, ensure_ascii=False, indent=2)

    # przygotuj info do Telegrama
    msg = (
        "📡 <b>DEBUG API Travelplanet</b>\n\n"
        f"🔎 Liczba JSON response: {len(responses)}\n"
        f"📦 Największy endpoint:\n{best['url']}\n\n"
        "👉 zapisano best_payload.json"
    )

    send_telegram(msg)


if __name__ == "__main__":
    main()
