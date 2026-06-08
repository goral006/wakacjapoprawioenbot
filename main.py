import requests
from bs4 import BeautifulSoup
import re
from telegram import send_telegram

URL = "https://www.wakacje.pl/wczasy/?wylot=krakow,katowice,rzeszow&dni=7-8&osoby=2+1&ocena_od=8"

MAX_PRICE = 8000

COUNTRIES = ["Hiszpania", "Grecja", "Turcja", "Tunezja", "Cypr"]


# =========================
# 🌐 FETCH HTML
# =========================

def fetch():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    r = requests.get(URL, headers=headers, timeout=30)
    return r.text


# =========================
# 🔎 PARSE OFFERS
# =========================

def parse(html):
    soup = BeautifulSoup(html, "lxml")

    offers = []

    cards = soup.select("div, article, li")

    for c in cards:
        text = c.get_text(" ", strip=True)

        if not text:
            continue

        if "zł" not in text:
            continue

        if not any(k in text for k in COUNTRIES):
            continue

        price_match = re.findall(r"(\d[\d\s]{3,})\s?zł", text)

        if not price_match:
            continue

        try:
            price = int(price_match[0].replace(" ", ""))
        except:
            continue

        if price > MAX_PRICE:
            continue

        offers.append({
            "text": text[:300],
            "price": price
        })

    return offers


# =========================
# 🚀 MAIN
# =========================

def main():
    html = fetch()
    offers = parse(html)

    if not offers:
        send_telegram("❌ Brak ofert spełniających warunki")
        return

    offers = sorted(offers, key=lambda x: x["price"])

    msg = "🏝 <b>OFERTY WAKACJE.PL (BOT v2)</b>\n\n"

    for o in offers[:5]:
        msg += f"""
💰 {o['price']} zł
🧾 {o['text']}
-------------------
"""

    send_telegram(msg)


if __name__ == "__main__":
    main()
