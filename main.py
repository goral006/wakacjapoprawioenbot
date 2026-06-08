import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
from telegram import send_telegram

MAX_PRICE = 8000

DATE_START = "05.09.2026"
DATE_END = "15.09.2026"

MIN_DAYS = 7
MAX_DAYS = 8


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
        return r.text
    except:
        return ""


# =========================
# 🔎 HELPERS (DATES + DAYS)
# =========================

def date_ok(text):
    return DATE_START.replace(".", "") in text.replace(" ", "") or DATE_END.replace(".", "") in text.replace(" ", "")


def days_ok(text):
    match = re.search(r"(\d+)\s*dni", text)
    if not match:
        return False
    days = int(match.group(1))
    return MIN_DAYS <= days <= MAX_DAYS


# =========================
# 🔎 PARSER
# =========================

def parse(html, source, base_url):
    try:
        soup = BeautifulSoup(html, "lxml")
    except:
        soup = BeautifulSoup(html, "html.parser")

    offers = []
    seen = set()

    elements = soup.find_all("a") + soup.find_all("article") + soup.find_all("div")

    for el in elements:
        text = " ".join(el.stripped_strings)

        if len(text) < 80:
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

        # 🌍 filtr krajów / ofert
        keywords = [
            "hotel", "all inclusive", "HB", "BB",
            "Turcja", "Grecja", "Hiszpania", "Cypr", "Egipt", "Tunezja"
        ]

        if not any(k.lower() in text.lower() for k in keywords):
            continue

        # 📅 filtr dat
        if not date_ok(text):
            continue

        # ⏱ filtr długości
        if not days_ok(text):
            continue

        # 🔗 link
        href = el.get("href") or el.get("data-url") or el.get("data-href")

        link = urljoin(base_url, href) if href else base_url

        # 🔴 deduplikacja
        key = link + str(price)
        if key in seen:
            continue
        seen.add(key)

        offers.append({
            "source": source,
            "price": price,
            "text": text[:200],
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
        send_telegram("❌ Brak ofert w zakresie dat i 7-8 dni")
        return

    all_offers.sort(key=lambda x: x["price"])

    msg = "🏝 <b>TRAVEL DEALS FILTERED (DATE + DAYS)</b>\n\n"

    msg += f"📅 {DATE_START} → {DATE_END}\n"
    msg += f"⏱ {MIN_DAYS}-{MAX_DAYS} dni\n\n"

    for o in all_offers[:10]:
        msg += f"""
🏷 {o['source']}
💰 {o['price']} zł
🔗 {o['link']}
🧾 {o['text']}
-------------------
"""

    send_telegram(msg)


if __name__ == "__main__":
    main()
