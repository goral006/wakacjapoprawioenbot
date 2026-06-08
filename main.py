from playwright.sync_api import sync_playwright
from telegram import send_telegram
from bs4 import BeautifulSoup
import re

URL = "https://www.travelplanet.pl/wakacje/?s_action=TRIPS_SEARCH&d_start_from=05.09.2026&d_end_to=15.09.2026&page=1"


ALLOWED_AIRPORTS = ["kraków", "katowice", "rzeszów"]

ALLOWED_COUNTRIES = ["hiszpania", "cypr", "grecja", "tunezja", "turcja"]

ALLOWED_BOARD = ["all inclusive", "3 posiłki", "2 posiłki"]

MIN_RATING = 8.0


def get_html():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(8000)

        html = page.content()

        browser.close()
        return html


def extract_rating(text):
    match = re.search(r"(\d\.\d|\d)", text)
    if match:
        try:
            return float(match.group())
        except:
            return None
    return None


def is_valid(text):
    t = text.lower()

    # ✈️ lotniska
    if not any(a in t for a in ALLOWED_AIRPORTS):
        return False

    # 🌍 destynacje
    if not any(c in t for c in ALLOWED_COUNTRIES):
        return False

    # 🍽 wyżywienie
    if not any(b in t for b in ALLOWED_BOARD):
        return False

    # ⭐ ocena
    rating = extract_rating(t)
    if rating and rating < MIN_RATING:
        return False

    return True


def parse_offers(html):
    soup = BeautifulSoup(html, "html.parser")

    offers = []

    for a in soup.find_all("a"):
        text = a.get_text(" ", strip=True)
        href = a.get("href")

        if not text or not href:
            continue

        if len(text) < 80:
            continue

        if not is_valid(text):
            continue

        price_match = re.search(r"\d[\d\s]*\s?zł", text)
        price = price_match.group() if price_match else "brak"

        offers.append({
            "text": text[:250],
            "price": price,
            "link": href
        })

    return offers[:5]


def main():
    html = get_html()

    print("HTML length:", len(html))

    offers = parse_offers(html)

    if not offers:
        send_telegram("❌ Brak ofert spełniających warunki (2+1, 8+, AI/HP, wybrane kraje)")
        return

    msg = "🏝 <b>TOP WYBRANE WAKACJE (PRO FILTER)</b>\n\n"

    for i, o in enumerate(offers):
        msg += f"""
🏨 <b>Oferta {i+1}</b>
✈️ Kraków / Katowice / Rzeszów
🌍 Hiszpania / Grecja / Cypr / Turcja / Tunezja
⭐ min 8.0
🍽 AI / 2-3 posiłki
💰 {o['price']}
📝 {o['text']}
🔗 {o['link']}
-------------------
"""

    send_telegram(msg)


if __name__ == "__main__":
    main()
