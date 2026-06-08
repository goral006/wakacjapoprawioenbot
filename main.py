from playwright.sync_api import sync_playwright
from telegram import send_telegram
import json

URL = "https://www.travelplanet.pl/wakacje/?s_action=TRIPS_SEARCH&d_start_from=05.09.2026&d_end_to=15.09.2026&page=1"


# =========================
# 🌐 CAPTURE API RESPONSE
# =========================

def get_api_data():
    data_holder = {"json": None}

    def handle_response(response):
        try:
            url = response.url.lower()

            # 🔥 KLUCZ: Travelplanet ładuje oferty przez XHR/fetch
            if "trip" in url or "search" in url or "offer" in url:
                if response.headers.get("content-type", "").find("json") != -1:
                    data_holder["json"] = response.json()
        except:
            pass

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.on("response", handle_response)

        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_timeout(15000)

        browser.close()

    return data_holder["json"]


# =========================
# 🧠 PARSING SAFE (FALLBACK)
# =========================

def extract_offers(data):
    offers = []

    if not data:
        return offers

    # 🔴 struktura może się różnić — dlatego "safe parsing"
    for item in data.get("offers", []) if isinstance(data, dict) else []:

        try:
            offers.append({
                "name": item.get("name", "brak nazwy"),
                "price": item.get("price", "brak ceny"),
                "rating": item.get("rating", "brak oceny"),
                "link": item.get("url", "")
            })
        except:
            continue

    return offers


# =========================
# 🚀 MAIN
# =========================

def main():
    print("🚀 Starting bot...")

    data = get_api_data()

    # 🔍 DEBUG
    if not data:
        send_telegram("❌ Nie przechwyciłem API (Travelplanet blokuje lub zmienił endpoint)")
        return

    with open("debug_api.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    offers = extract_offers(data)

    if not offers:
        send_telegram("❌ API działa, ale brak ofert w strukturze JSON (zmieniony format)")
        return

    msg = "🏝 <b>TOP OFERTY (API MODE)</b>\n\n"

    for i, o in enumerate(offers[:5]):
        msg += f"""
🏨 <b>{o['name']}</b>
💰 {o['price']}
⭐ {o['rating']}
🔗 {o['link']}
-------------------
"""

    send_telegram(msg)


if __name__ == "__main__":
    main()
