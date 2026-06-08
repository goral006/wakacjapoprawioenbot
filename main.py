from playwright.sync_api import sync_playwright
from telegram import send_telegram

URL = "https://www.travelplanet.pl/wakacje/?s_action=TRIPS_SEARCH&d_start_from=05.09.2026&d_end_to=15.09.2026&page=1"


def capture():
    data = []

    def handle_response(response):
        try:
            req = response.request

            if "json" in response.headers.get("content-type", ""):
                try:
                    data.append(response.json())
                except:
                    pass
        except:
            pass

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.on("response", handle_response)

        page.goto(URL, wait_until="networkidle")

        # 🔥 KLUCZ: wymuszenie JS execution + lazy load trigger
        page.wait_for_timeout(3000)
        page.mouse.wheel(0, 1000)
        page.wait_for_timeout(5000)

        browser.close()

    return data


def extract(obj):
    results = []

    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if isinstance(v, list):
                    for i in v:
                        if isinstance(i, dict):
                            results.append(i)
                walk(v)
        elif isinstance(x, list):
            for i in x:
                walk(i)

    walk(obj)
    return results


def get_price(o):
    for k in ["price", "totalPrice", "amount"]:
        if k in o:
            try:
                return float(str(o[k]).replace(" ", ""))
            except:
                pass
    return None


def main():
    jsons = capture()

    if not jsons:
        send_telegram("❌ brak JSON po user-flow")
        return

    offers = []
    for j in jsons:
        offers.extend(extract(j))

    valid = []
    for o in offers:
        price = get_price(o)
        if price:
            valid.append((price, o))

    if not valid:
        send_telegram("❌ nadal brak ofert — strona lazy-load / bot detection")
        return

    valid.sort(key=lambda x: x[0])

    msg = "🏝 <b>FINAL FLOW SCRAPER</b>\n\n"

    for price, o in valid[:5]:
        msg += f"""
🏨 {o.get('name', o.get('title', 'Brak'))}
💰 {price} zł
-------------------
"""

    send_telegram(msg)


if __name__ == "__main__":
    main()
