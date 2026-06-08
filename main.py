from playwright.sync_api import sync_playwright
from telegram import send_telegram
import re

URL = "https://www.travelplanet.pl/wakacje/?s_action=TRIPS_SEARCH&d_start_from=05.09.2026&d_end_to=15.09.2026&page=1"


# =========================
# 🌐 ZBIERANIE JSON Z API
# =========================

def get_best_json():
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

    if not responses:
        return None

    return max(responses, key=lambda x: len(str(x)))


# =========================
# 🔎 REKURENCYJNE SZUKANIE OFERT
# =========================

def extract_offers(obj):
    offers = []

    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():

                if k.lower() in ["offers", "offer", "results", "trips", "items", "data"]:
                    if isinstance(v, list):
                        offers.extend(v)

                walk(v)

        elif isinstance(x, list):
            for i in x:
                walk(i)

    walk(obj)
    return offers


# =========================
# 💰 CENA
# =========================

def get_price(o):
    for key in ["price", "totalPrice", "total_price"]:
        if isinstance(o, dict) and key in o:
            try:
                return float(str(o[key]).replace(" ", ""))
            except:
                pass
    return None


# =========================
# 🧠 FILTR
# =========================

MAX_PRICE = 8000


def is_valid(o):
    price = get_price(o)

    if price is None:
        return False

    if price > MAX_PRICE:
        return False

    return True


# =========================
# 🚀 MAIN
# =========================

def main():
    data = get_best_json()

    if not data:
        send_telegram("❌ Brak danych API (Travelplanet blokuje lub zmienił strukturę)")
        return

    offers = extract_offers(data)

    if not offers:
        send_telegram("❌ Nie znaleziono ofert w JSON strukturze")
        return

    valid = [o for o in offers if is_valid(o)]

    if not valid:
        send_telegram("❌ Brak ofert do 8000 zł (2+1, 05–15.09.2026)")
        return

    msg = "🏝 <b>TOP WAKACJE (API FINAL)</b>\n\n"

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
