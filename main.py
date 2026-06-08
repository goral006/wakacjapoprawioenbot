from playwright.sync_api import sync_playwright
from telegram import send_telegram
from bs4 import BeautifulSoup
import re

URL = "https://www.travelplanet.pl/wakacje/?s_action=TRIPS_SEARCH&d_start_from=05.09.2026&d_end_to=15.09.2026&page=1"


# =========================
# 🔧 PARAMETRY
# =========================

MAX_TOTAL_PRICE = 6000
MAX_PER_PERSON = 2200

AIRPORTS = ["kraków", "katowice", "rzeszów"]

COUNTRIES = ["hiszpania", "grecja", "turcja", "cypr", "tunezja"]

BOARD = ["all inclusive", "ai", "hb", "fb", "2 posiłki", "3 posiłki"]

PEOPLE = 3  # 2 dorosłych + dziecko


# =========================
# 🌐 PLAYWRIGHT
# =========================

def get_html():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(8000)

        html = page.content()
        browser.close()

        return html


# =========================
# 💰 CENA
# =========================

def extract_price(text):
    match = re.search(r"(\d[\d\s]{2,})\s?zł", text)
    if not match:
        return None

    try:
        return int(match.group(1).replace(" ", ""))
    except:
        return None


# =========================
# 📅 DŁUGOŚĆ POBYTU (7–8 DNI)
# =========================

def check_duration(text):
    t = text.lower()

    # najczęstsze formaty
    if "7 dni" in t or "7 noc" in t or "7 nocleg" in t:
        return True

    if "8 dni" in t or "8 noc" in t or "8 nocleg" in t:
        return True

    # jeśli brak info → NIE blokujemy (bo Travelplanet często nie pokazuje)
    return True


# =========================
# 🧠 SCORE
# =========================

def score_offer(text):
    t = text.lower()
    score = 0

    if any(a in t for a in AIRPORTS):
        score += 1

    if any(c in t for c in COUNTRIES):
        score += 2

    if any(b in t for b in BOARD):
        score += 2

    if "7 dni" in t or "8 dni" in t:
        score += 2

    return score


# =========================
# 💰 BUDŻET
# =========================

def is_valid(text, price):
    if not text or price is None:
        return False

    if price > MAX_TOTAL_PRICE:
        return False

    if price / PEOPLE > MAX_PER_PERSON:
        return False

    if not check_duration(text):
        return False

    return True


# =========================
# 📦 PARSER
# =========================

def parse_offers(html):
    soup = BeautifulSoup(html, "html.parser")

    offers = []

    for a in soup.find_all("a"):
        text = a.get_text(" ", strip=True)
        href = a.get("href")

        if not text or len(text) < 80:
            continue

        price = extract_price(text)

        if not is_valid(text, price):
            continue

        offers.append({
            "text": text[:250],
            "price": price,
            "score": score_offer(text),
            "link": href
        })

    offers.sort(key=lambda x: x["score"], reverse=True)

    return offers[:5]


# =========================
# 🚀 MAIN
# =========================

def main():
    html = get_html()

    print("HTML length:", len(html))

    offers = parse_offers(html)

    if not offers:
        send_telegram(
            "❌ Brak ofert (2+1 | 7–8 dni | 6000 zł | 2200/os)"
        )
        return

    msg = "🏝 <b>TOP WAKACJE (2+1 | 7–8 DNI | PRO)</b>\n\n"

    for i, o in enumerate(offers):
        msg += f"""
🏨 <b>Oferta {i+1}</b>
💰 Cena: {o['price']} zł
📊 Dopasowanie: {o['score']}/7
👨‍👩‍👧 2+1
📅 7–8 dni
✈️ Kraków / Katowice / Rzeszów
🌍 ES / GR / TR / CY / TN
🍽 AI / HB / FB
📝 {o['text']}
🔗 {o['link']}
-------------------
"""

    send_telegram(msg)


if __name__ == "__main__":
    main()
