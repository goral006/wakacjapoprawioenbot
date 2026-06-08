from playwright.sync_api import sync_playwright
from telegram import send_telegram
import re

URL = "https://www.travelplanet.pl/wakacje/?s_action=TRIPS_SEARCH&d_start_from=05.09.2026&d_end_to=15.09.2026&page=1"


# =========================
# 🌐 OPEN PAGE + WAIT FOR CARDS
# =========================

def get_cards():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(URL, wait_until="domcontentloaded")

        # 🔥 KLUCZ: czekamy na dynamiczne karty
        page.wait_for_timeout(12000)

        # próbujemy znaleźć realne elementy ofert
        cards = page.query_selector_all("a")

        results = []

        for c in cards:
            try:
                text = c.inner_text().strip()
                href = c.get_attribute("href")

                if not text or len(text) < 80:
                    continue

                results.append({
                    "text": text,
                    "link": href
                })
            except:
                continue

        browser.close()
        return results


# =========================
# 💰 PRICE EXTRACT
# =========================

def extract_price(text):
    match = re.search(r"(\d[\d\s]{3,})\s?zł", text)
    if not match:
        return None

    try:
        return int(match.group(1).replace(" ", ""))
    except:
        return None


# =========================
# 🚀 MAIN
# =========================

MAX_PRICE = 8000


def main():
    cards = get_cards()

    if not cards:
        send_telegram("❌ Brak cards (selector mode)")
        return

    offers = []

    for c in cards:
        price = extract_price(c["text"])

        if not price or price > MAX_PRICE:
            continue

        offers.append({
            "text": c["text"][:250],
            "price": price,
            "link": c["link"]
        })

    if not offers:
        send_telegram("❌ Brak ofert do 8000 zł (selector filtering)")
        return

    msg = "🏝 <b>TOP WAKACJE (SELECTOR MODE)</b>\n\n"

    for i, o in enumerate(offers[:5]):
        msg += f"""
🏨 Oferta {i+1}
💰 {o['price']} zł
📝 {o['text']}
🔗 {o['link']}
-------------------
"""

    send_telegram(msg)


if __name__ == "__main__":
    main()
