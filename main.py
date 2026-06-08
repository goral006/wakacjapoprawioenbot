from playwright.sync_api import sync_playwright
from telegram import send_telegram

URL = "https://www.travelplanet.pl/wakacje/?s_action=TRIPS_SEARCH&d_start_from=05.09.2026&d_end_to=15.09.2026&page=1"

MAX_PRICE = 8000


# =========================
# 🌐 CAPTURE NETWORK
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

        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(15000)

        browser.close()

    return responses


# =========================
# 🔎 FIND OFFERS RECURSIVE
# =========================

def find_offers(obj):
    offers = []

    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():

                if isinstance(v, list):
                    for i in v:
                        if isinstance(i, dict):
                            # heurystyka: wygląda jak oferta
                            if any(key in i for key in ["price", "title", "name", "hotel"]):
                                offers.append(i)

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

    for k in ["price", "totalPrice", "amount"]:
        if k in o:
            try:
                return float(str(o[k]).replace(" ", ""))
            except:
                pass
    return None


# =========================
# 🚀 MAIN
# =========================

def main():
    jsons = capture_network()

    if not jsons:
        send_telegram("❌ Brak JSON w network (Travelplanet blokuje API)")
        return

    offers = []
    for j in jsons:
        offers.extend(find_offers(j))

    if not offers:
        send_telegram("❌ Nie znaleziono ofert w JSON response")
        return

    valid = []
    for o in offers:
        price = get_price(o)
        if price and price <= MAX_PRICE:
            valid.append((price, o))

    if not valid:
        send_telegram("❌ Brak ofert do 8000 zł")
        return

    valid.sort(key=lambda x: x[0])

    msg = "🏝 <b>TOP WAKACJE (FINAL WORKING BOT)</b>\n\n"

    for price, o in valid[:5]:
        msg += f"""
🏨 {o.get('name', o.get('title', 'Brak nazwy'))}
💰 {price} zł
⭐ {o.get('rating', 'brak')}
-------------------
"""

    send_telegram(msg)


if __name__ == "__main__":
    main()
