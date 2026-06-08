import re
from playwright.sync_api import sync_playwright
from telegram import send_telegram

MAX_PRICE = 8000

SOURCES = [
    "https://www.rainbowtours.pl/wczasy",
    "https://www.itaka.pl/wczasy/",
    "https://www.tui.pl/wczasy/"
]


def extract_price(text):
    match = re.findall(r"(\d[\d\s]{3,})\s?zł", text)
    if not match:
        return None
    try:
        return int(match[0].replace(" ", ""))
    except:
        return None


def is_valid(text):
    if "zł" not in text:
        return False

    price = extract_price(text)
    if not price or price > MAX_PRICE:
        return False

    keywords = [
        "Turcja", "Grecja", "Hiszpania", "Egipt", "Cypr", "Tunezja",
        "hotel", "all inclusive"
    ]

    return any(k.lower() in text.lower() for k in keywords)


def scrape():
    pages = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for url in SOURCES:
            print("OPEN:", url)
            page.goto(url, timeout=60000)
            page.wait_for_timeout(8000)

            pages.append({
                "url": url,
                "html": page.content()
            })

        browser.close()

    return pages


def parse(pages):
    import re

    results = []
    seen = set()

    for p in pages:
        html = p["html"]
        url = p["url"]

        blocks = re.split(r"</article>|</div>", html)

        for b in blocks:
            text = re.sub(r"<[^>]+>", " ", b)
            text = " ".join(text.split())

            if len(text) < 100:
                continue

            if not is_valid(text):
                continue

            price = extract_price(text)
            if not price:
                continue

            key = text[:120]
            if key in seen:
                continue
            seen.add(key)

            results.append({
                "price": price,
                "text": text[:250],
                "source": url
            })

    return results


def main():
    print("🚀 START BOT")

    pages = scrape()
    offers = parse(pages)

    print("OFFERS:", len(offers))

    if not offers:
        send_telegram("❌ Brak ofert PRO BOT")
        return

    offers.sort(key=lambda x: x["price"])

    msg = "🏝 <b>PRO TRAVEL BOT</b>\n\n"

    for o in offers[:10]:
        msg += f"""
💰 {o['price']} zł
🔗 {o['source']}
🧾 {o['text']}
-------------------
"""

    send_telegram(msg)


if __name__ == "__main__":
    main()
