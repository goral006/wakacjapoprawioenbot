import requests
from bs4 import BeautifulSoup
import re
from telegram import send_telegram

MAX_PRICE = 8000

SOURCES = {
    "TUI": "https://www.tui.pl/wczasy",
    "ITAKA": "https://www.itaka.pl/wczasy/",
    "CORAL": "https://www.coraltravel.pl/wczasy",
    "RAINBOW": "https://www.rainbowtours.pl/wczasy",
    "LASTMINUTE": "https://www.lastminuter.pl/wczasy"
}


# =========================
# 🌐 FETCH
# =========================

def fetch(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        r = requests.get(url, headers=headers, timeout=20)
        print("GET:", url, "status:", r.status_code)
        return r.text
    except:
        return ""


# =========================
# 🔎 PARSER (UNIVERSAL HEURISTIC)
# =========================

def parse(html, source):
    try:
        soup = BeautifulSoup(html, "lxml")
    except:
        soup = BeautifulSoup(html, "html.parser")

    offers = []

    blocks = soup.find_all("article")
    if not blocks:
        blocks = soup.find_all("div")

    for b in blocks:
        text = " ".join(b.stripped_strings)

        if len(text) < 80:
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

        # heurystyka: musi wyglądać jak oferta
        keywords = ["hotel", "all inclusive", "HB", "BB", "Turcja", "Grecja", "Hiszpania", "Egipt", "Cypr"]

        if not any(k.lower() in text.lower() for k in keywords):
            continue

        offers.append({
            "source": source,
            "price": price,
            "text": text[:200]
        })

    return offers


# =========================
# 🚀 MAIN
# =========================

def main():
    all_offers = []

    for name, url in SOURCES.items():
        html = fetch(url)

        if not html:
            continue

        offers = parse(html, name)
        all_offers.extend(offers)

    if not all_offers:
        send_telegram("❌ Brak ofert ze wszystkich źródeł")
        return

    all_offers.sort(key=lambda x: x["price"])

    msg = "🏝 <b>MULTI TRAVEL DEALS BOT</b>\n\n"

    for o in all_offers[:10]:
        msg += f"""
🏷 {o['source']}
💰 {o['price']} zł
🧾 {o['text']}
-------------------
"""

    send_telegram(msg)


if __name__ == "__main__":
    main()
