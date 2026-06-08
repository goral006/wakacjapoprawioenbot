from playwright.sync_api import sync_playwright
from telegram import send_telegram
import re

URL = "https://www.travelplanet.pl/wakacje/?s_action=TRIPS_SEARCH&d_start_from=05.09.2026&d_end_to=05.09.2026&page=1"

MAX_PRICE = 8000


# =========================
# 🌐 CAPTURE + EXTRACT IN ONE RUN
# =========================

def run_browser():
    texts = []

    def handle_response(response):
        try:
            txt = response.text()
            texts.append(txt)
        except:
            pass

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.on("response", handle_response)

        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(15000)

        browser.close()

    return texts


# =========================
# 🔎 EXTRACT PRICES
# =========================

def extract_prices(text):
    matches = re.findall(r"(\d[\d\s]{2,})\s?zł", text)
    prices = []

    for m in matches:
        try:
            prices.append(int(m.replace(" ", "")))
        except:
            pass

    return prices


# =========================
# 🚀 MAIN
# =========================

def main():
    texts = run_browser()

    if not texts:
        send_telegram("❌ brak danych z network")
        return

    all_text = "\n".join(texts)

    prices = extract_prices(all_text)

    if not prices:
        send_telegram("❌ brak cen w raw response (blokada / JS runtime data)")
        return

    valid = [p for p in prices if p <= MAX_PRICE]

    if not valid:
        send_telegram("❌ brak ofert do 8000 zł")
        return

    valid.sort()

    msg = "🏝 <b>FINAL ATOMIC SCRAPER</b>\n\n"

    for p in valid[:10]:
        msg += f"💰 {p} zł\n"

    send_telegram(msg)


if __name__ == "__main__":
    main()
