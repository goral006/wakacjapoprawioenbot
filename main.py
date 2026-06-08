from playwright.sync_api import sync_playwright
from telegram import send_telegram

MAX_PRICE = 8000


# =========================
# 🌐 CAPTURE + RESPONSE
# =========================

def capture():
    data = []

    def handle_response(response):
        try:
            req = response.request

            item = {
                "url": response.url,
                "method": req.method,
                "post": req.post_data
            }

            try:
                if "json" in response.headers.get("content-type", ""):
                    item["json"] = response.json()
            except:
                pass

            data.append(item)

        except:
            pass

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.on("response", handle_response)

        page.goto(
            "https://www.travelplanet.pl/wakacje/?s_action=TRIPS_SEARCH&d_start_from=05.09.2026&d_end_to=15.09.2026&page=1",
            wait_until="domcontentloaded"
        )

        page.wait_for_timeout(20000)

        browser.close()

    return data


# =========================
# 🔎 FIND OFFERS ANYWHERE
# =========================

def find_offers(obj):
    offers = []

    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():

                if isinstance(v, list):
                    for i in v:
                        if isinstance(i, dict):
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
    logs = capture()

    jsons = [x.get("json") for x in logs if x.get("json")]

    if not jsons:
        send_telegram("❌ Brak JSON w network")
        return

    offers = []

    for j in jsons:
        offers.extend(find_offers(j))

    if not offers:
        send_telegram("❌ Nie znaleziono ofert (single-file mode)")
        return

    valid = [o for o in offers if get_price(o) and get_price(o) <= MAX_PRICE]

    if not valid:
        send_telegram("❌ Brak ofert do 8000 zł")
        return

    msg = "🏝 <b>FINAL WORKING SCRAPER</b>\n\n"

    for i, o in enumerate(valid[:5]):
        msg += f"""
🏨 {o.get('name', o.get('title', 'Brak'))}
💰 {get_price(o)} zł
⭐ {o.get('rating', 'brak')}
-------------------
"""

    send_telegram(msg)


if __name__ == "__main__":
    main()
