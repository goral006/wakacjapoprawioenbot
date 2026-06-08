import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
from telegram import send_telegram

MAX_PRICE = 8000

SOURCES = {
    "RAINBOW": "https://www.rainbowtours.pl/wczasy",
    "TUI": "https://www.tui.pl/wczasy",
    "ITAKA": "https://www.itaka.pl/wczasy/",
    "CORAL": "https://www.coraltravel.pl/wczasy",
    "LASTMINUTE": "https://www.lastminuter.pl/wczasy"
}


# =========================
# 🌐 FETCH
# =========================

def fetch(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=25)
        print("GET:", url, "STATUS:", r.status_code)
        return r.text
    except:
        return ""


# =========================
# 🔎 PARSER (CARD BASED - FIXED)
# =========================

def parse(html, source, base_url):
    try:
        soup = BeautifulSoup(html, "lxml")
    except:
        soup = BeautifulSoup(html, "html.parser")

    offers = []
    seen = set()

    # 🔥 KLUCZ: tylko potencjalne “karty”
    cards = soup.find_all("article")
    if not cards:
        cards = soup.select("div")

    for card in cards:

        text = " ".join(card.stripped_strings)

        if len(text) < 100:
            continue

        if "zł" not in text:
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

        # 🌍 filtr jakości
        keywords = [
            "hotel", "all inclusive", "HB", "BB",
            "Turcja", "Grecja", "Hiszpania", "Egipt", "Cypr", "Tunezja"
        ]

        if not any(k.lower() in text.lower() for k in keywords):
            continue

        # 📅 daty (tylko jeśli są w tej SAMEJ karcie)
        date_match = re.search(r"\d{2}\.\d{2}\.\d{4}", text)
        date = date_match.group(0) if date_match else "brak"

        # ⏱ długość (tylko lokalnie)
        days_match = re.search(r"(\d+)\s*dni", text)
        days = days_match.group(1) if days_match else "brak"

        # 🔗 link (najlepszy możliwy z karty)
        link = None

        if card.name == "a":
            link = card.get("href")

        if not link:
            a = card.find("a")
            if a:
                link = a.get("href")

        if not link:
            link = base_url

        link = urljoin(base_url, link)

        # 🔴 deduplikacja
        key = link + str(price)
        if key in seen:
            continue
        seen.add(key)

        offers.append({
            "source": source,
            "price": price,
            "date": date,
            "days": days,
            "text": text[:220],
            "link": link
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

        offers = parse(html, name, url)

        print(f"{name}: {len(offers)} offers")

        all_offers.extend(offers)

    if not all_offers:
        send_telegram("❌ Brak stabilnych ofert (HTML parsing)")
        return

    all_offers.sort(key=lambda x: x["price"])

    msg = "🏝 <b>MULTI TRAVEL DEALS (STABLE MODE)</b>\n\n"

    for o in all_offers[:10]:
        msg += f"""
🏷 {o['source']}
💰 {o['price']} zł
📅 {o['date']}
⏱ {o['days']} dni
🔗 {o['link']}
🧾 {o['text']}
-------------------
"""

    send_telegram(msg)


if __name__ == "__main__":
    main()
