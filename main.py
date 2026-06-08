import requests
from bs4 import BeautifulSoup
import re
from telegram import send_telegram

URL = "https://www.wakacje.pl/wczasy/?wylot=krakow,katowice,rzeszow&dni=7-8&osoby=2+1&ocena_od=8"

MAX_PRICE = 8000


# =========================
# 🌐 FETCH
# =========================

def fetch_html():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(URL, headers=headers, timeout=30)

    print("Status:", r.status_code)
    print("Length:", len(r.text))

    return r.text


# =========================
# 🔎 PARSE (LXML + FALLBACK)
# =========================

def parse(html):
    try:
        # 🟢 primary parser
        soup = BeautifulSoup(html, "lxml")
    except Exception as e:
        print("LXML failed, fallback html.parser:", e)
        soup = BeautifulSoup(html, "html.parser")

    text = soup.get_text(" ", strip=True)

    offers = []

    prices = re.findall(r"(\d[\d\s]{3,})\s?zł", text)

    for p in prices:
        try:
            price = int(p.replace(" ", ""))
        except:
            continue

        if price <= MAX_PRICE:
            offers.append(price)

    return offers


# =========================
# 🚀 MAIN
# =========================

def main():
    html = fetch_html()

    offers = parse(html)

    if not offers:
        send_telegram("❌ Brak ofert (HTML + lxml + fallback)")
        return

    offers = sorted(offers)

    msg = "🏝 <b>WAKACJE.PL - LXML MODE</b>\n\n"

    for p in offers[:10]:
        msg += f"💰 {p} zł\n"

    send_telegram(msg)


if __name__ == "__main__":
    main()
