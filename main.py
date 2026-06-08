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

def fetch_html():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    r = requests.get(URL, headers=headers, timeout=30)

    print("Status:", r.status_code)
    print("Length:", len(r.text))

    return r.text


# =========================
# 🔎 PARSE OFFERS (LXML + FALLBACK)
# =========================

def parse(html):
    try:
        soup = BeautifulSoup(html, "lxml")
    except:
        soup = BeautifulSoup(html, "html.parser")

    offers = []

    blocks = soup.find_all(["article", "div", "li"])

    for b in blocks:
        text = b.get_text(" ", strip=True)

        if not text:
            continue

        if "zł" not in text:
            continue

        # cena
        price_match = re.findall(r"(\d[\d\s]{3,})\s?zł", text)
        if not price_match:
            continue

        try:
            price = int(price_match[0].replace(" ", ""))
        except:
            continue

        if price > MAX_PRICE:
            continue

        # filtr krajów
        if not any(c in text for c in COUNTRIES):
            continue

        offers.append({
            "price": price,
            "text": text[:300]
        })

    return offers


# =========================
# 🚀 MAIN
# =========================

def main():
    html = fetch_html()

    offers = parse(html)

    if not offers:
        send_telegram("❌ Brak ofert spełniających warunki")
        return

    offers = sorted(offers, key=lambda x: x["price"])

    msg = "🏝 <b>WAKACJE.PL - REAL OFFERS BOT</b>\n\n"

    for o in offers[:5]:
        msg += f"""
💰 {o['price']} zł
🧾 {o['text']}
-------------------
"""

    send_telegram(msg)


if __name__ == "__main__":
    main()
