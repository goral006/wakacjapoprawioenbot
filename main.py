import requests
from bs4 import BeautifulSoup
import re
from telegram import send_telegram

URL = "https://www.wakacje.pl/wczasy/?wylot=krakow,katowice,rzeszow&dni=7-8&osoby=2+1&ocena_od=8"

MAX_PRICE = 8000

KEYWORDS = [
    "hotel",
    "all inclusive",
    "HB",
    "BB",
    "Turcja",
    "Grecja",
    "Hiszpania",
    "Cypr",
    "Egipt",
    "Tunezja"
]


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
# 🔎 PARSE OFFERS (CLEAN VERSION)
# =========================

def parse(html):
    try:
        soup = BeautifulSoup(html, "lxml")
    except:
        soup = BeautifulSoup(html, "html.parser")

    offers = []

    # 🔥 tylko potencjalne karty ofert
    blocks = soup.find_all("article")

    if not blocks:
        blocks = soup.find_all("div")

    for b in blocks:
        text = " ".join(b.stripped_strings)

        # 🔴 odfiltruj śmieci UI
        if len(text) < 100:
            continue

        if "zł" not in text:
            continue

        # 🔴 musi wyglądać jak oferta
        if not any(k.lower() in text.lower() for k in KEYWORDS):
            continue

        # 💰 cena
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

    msg = "🏝 <b>WAKACJE.PL - CLEAN OFFERS BOT</b>\n\n"

    for o in offers[:5]:
        msg += f"""
💰 {o['price']} zł
🧾 {o['text']}
-------------------
"""

    send_telegram(msg)


if __name__ == "__main__":
    main()
