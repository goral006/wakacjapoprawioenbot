from playwright.sync_api import sync_playwright
from telegram import send_telegram
import json

URL = "https://www.travelplanet.pl/wakacje/?s_action=TRIPS_SEARCH&d_start_from=05.09.2026&d_end_to=15.09.2026&page=1"

MAX_PRICE = 8000


# =========================
# 🌐 CAPTURE + PARSE W JEDNYM
# =========================

def capture_network():
    responses = []

    def handle_response(response):
        try:
            if "json" in response.headers.get("content-type", "").lower():
                try:
                    responses.append(response.json())
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
# 🔎 FIND OFFERS
# =========================

def find_offers(obj):
    offers = []

    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():

                if k.lower() in ["offers", "offer", "results", "trips", "items", "data", "list"]:
                    if isinstance(v, list):
                        offers.extend(v)

                walk(v)

        elif isinstance(x, list):
            for i in x:
                walk(i)

    walk(obj)
    return offers


# =========================
# 💰 PRICE
# =========================

def get_price(o):
    if not isinstance(o, dict):
        return None

    for key in ["price", "totalPrice", "total_price", "amount"]:
        if key in o:
            try:
                return float(str(o[key]).replace(" ", ""))
            except:
                pass

    return None


# =========================
# 🚀 MAIN
# =========================

def main():
    print("🚀 START SCRAPER")

    data_list = capture_network()

    if not data_list:
        send_telegram("❌ Brak JSON w network")
        return

    # 🔥 znajdź największy JSON
    best = max(data_list, key=lambda x: len(str(x)))

    offers = find_offers(best)

    if not offers:
        send_telegram("❌ Nie znaleziono ofert w network JSON")
        return

    valid = []
    for o in offers:
        price = get_price(o)
        if price and price <= MAX_PRICE:
            valid.append(o)

    if not valid:
        send_telegram("❌ Brak ofert do 8000 zł")
        return

    msg = "🏝 <b>TOP WAKACJE (FINAL ONE-FILE MODE)</b>\n\n"

    for i, o in enumerate(valid[:5]):
        msg += f"""
🏨 {o.get('name', o.get('title', 'Brak nazwy'))}
💰 {get_price(o)} zł
⭐ {o.get('rating', 'brak oceny')}
🌍 {o.get('country', 'brak')}
🔗 {o.get('url', '')}
-------------------
"""

    send_telegram(msg)


if __name__ == "__main__":
    main()
