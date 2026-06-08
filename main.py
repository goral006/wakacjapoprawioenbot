from playwright.sync_api import sync_playwright
from telegram import send_telegram
from bs4 import BeautifulSoup

URL = "https://www.travelplanet.pl/wakacje/?s_action=TRIPS_SEARCH&d_start_from=05.09.2026&d_end_to=15.09.2026&page=1"

def get_html():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(8000)

        html = page.content()
        browser.close()

        return html

def parse_offers(html):
    soup = BeautifulSoup(html, "html.parser")

    offers = []

    # bardzo elastyczny parser (bo Travelplanet zmienia strukturę)
    for a in soup.find_all("a"):
        text = a.get_text(" ", strip=True)

        if not text:
            continue

        if len(text) > 50 and ("zł" in text or "hotel" in text.lower()):
            offers.append({
                "text": text[:200],
                "link": a.get("href")
            })

    return offers[:5]

def main():
    html = get_html()

    print("HTML length:", len(html))

    offers = parse_offers(html)

    if not offers:
        send_telegram("❌ Nie znalazłem ofert (parser)")
        return

    msg = "🏝 <b>Travelplanet - oferty</b>\n\n"

    for i, o in enumerate(offers):
        msg += f"""
🏨 <b>Oferta {i+1}</b>
{o['text']}
🔗 {o.get('link','brak')}
-------------------
"""

    send_telegram(msg)

if __name__ == "__main__":
    main()
