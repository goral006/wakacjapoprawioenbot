from playwright.sync_api import sync_playwright
from telegram import send_telegram
from bs4 import BeautifulSoup
import re

URL = "https://www.travelplanet.pl/wakacje/?s_action=TRIPS_SEARCH&d_start_from=05.09.2026&d_end_to=15.09.2026&page=1"


# =========================
# 🌐 RENDER STRONY (JS)
# =========================

def get_rendered_html():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(URL, wait_until="networkidle")

        # czekamy aż JS dociągnie oferty
        page.wait_for_timeout(12000)

        html = page.content()

        browser.close()
        return html


# =========================
# 🔎 EXTRACT OFERT Z HTML (REAL DOM)
# =========================

def parse_offers(html):
    soup = BeautifulSoup(html, "html.parser")

    offers = []

    # 🔥 Travelplanet - karty / linki / bloki
    cards = soup.find_all("a")

    for c in cards:
        text = c.get_text(" ", strip=True)
        href = c.get("href")

        if not text or len(text) < 80:
            continue

        # cena
        price_match = re.search(r"(\d[\d\s]{3,})\s?zł", text)
        price = None

        if price_match:
            try:
                price = int(price_match.group(1).replace(" ", ""))
            except:
                pass

        offers.append({
            "text": text[:250],
            "price": price,
            "link": href
        })

    return offers


# =========================
# 💰 FILTER
# =========================

MAX_PRICE = 8000


def is_valid(o):
    if not o["price"]:
        return False

    if o["price"] > MAX_PRICE:
        return False

    return True


# =========================
# 🚀 MAIN
# =========================

def main():
    html = get_rendered_html()

    offers = parse_offers(html)

    valid = [o for o in offers if is_valid(o)]

    if not valid:
        send_telegram("❌ Brak ofert do 8000 zł (HTML render mode)")
        return

    msg = "🏝 <b>TOP WAKACJE (RENDER MODE)</b>\n\n"

    for i, o in enumerate(valid[:5]):
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
