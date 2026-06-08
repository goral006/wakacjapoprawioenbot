import re
import json
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from telegram import send_telegram

MAX_PRICE = 8000

SOURCES = {
    "RAINBOW": "https://www.rainbowtours.pl/wczasy",
    "ITAKA": "https://www.itaka.pl/wczasy/",
    "TUI": "https://www.tui.pl/wczasy/"
}


# =========================
# 🧠 PRICE
# =========================

def extract_price(text):
    m = re.findall(r"(\d[\d\s]{3,})\s?zł", text)
    if not m:
        return None
    try:
        return int(m[0].replace(" ", ""))
    except:
        return None


# =========================
# 🟢 JSON DETECTOR (CORE FIX)
# =========================

def extract_json_objects(text):
    objects = []
    stack = 0
    start = None

    for i, ch in enumerate(text):
        if ch == "{":
            if stack == 0:
                start = i
            stack += 1

        elif ch == "}":
            stack -= 1
            if stack == 0 and start is not None:
                chunk = text[start:i+1]
                objects.append(chunk)

    return objects


def parse_json_from_text(text):
    results = []

    json_chunks = extract_json_objects(text)

    for chunk in json_chunks:
        try:
            data = json.loads(chunk)

            # 🔥 UNIVERSAL SEARCH (recursive)
            def walk(obj):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        if isinstance(v, (dict, list)):
                            walk(v)

                        elif isinstance(v, str):
                            if "zł" in v:
                                price = extract_price(v)
                                if price and price <= MAX_PRICE:
                                    results.append({
                                        "price": price,
                                        "text": v[:200]
                                    })

                elif isinstance(obj, list):
                    for x in obj:
                        walk(x)

            walk(data)

        except:
            continue

    return results


# =========================
# 🟡 HTML FALLBACK
# =========================

def parse_html(html, url):
    soup = BeautifulSoup(html, "lxml")

    results = []

    for el in soup.find_all(["article", "div", "a"]):
        text = " ".join(el.stripped_strings)

        if len(text) < 80:
            continue

        if "zł" not in text:
            continue

        price = extract_price(text)

        if not price or price > MAX_PRICE:
            continue

        results.append({
            "price": price,
            "text": text[:200]
        })

    return results


# =========================
# 🚀 SCRAPER (PLAYWRIGHT)
# =========================

def scrape():
    pages = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for name, url in SOURCES.items():
            print("OPEN:", name, url)

            try:
                page.goto(url, timeout=60000)
                page.wait_for_timeout(7000)

                content = page.content()
                pages.append({
                    "source": name,
                    "url": url,
                    "html": content
                })

            except Exception as e:
                print("ERROR:", name, e)

        browser.close()

    return pages


# =========================
# 🔎 PARSE ENGINE
# =========================

def parse(pages):
    all_offers = []
    seen = set()

    for p in pages:
        html = p["html"]
        url = p["url"]
        source = p["source"]

        # 🟢 1. JSON FIRST
        json_offers = parse_json_from_text(html)

        if json_offers:
            print(source, "JSON OFFERS:", len(json_offers))

            for o in json_offers:
                key = o["text"][:120]

                if key in seen:
                    continue
                seen.add(key)

                all_offers.append(o)

        # 🟡 2. HTML fallback
        else:
            html_offers = parse_html(html, url)

            print(source, "HTML OFFERS:", len(html_offers))

            for o in html_offers:
                key = o["text"][:120]

                if key in seen:
                    continue
                seen.add(key)

                all_offers.append(o)

    return all_offers


# =========================
# 🚀 MAIN
# =========================

def main():
    print("🚀 UNIVERSAL PRO BOT START")

    pages = scrape()
    offers = parse(pages)

    print("TOTAL OFFERS:", len(offers))

    if not offers:
        send_telegram("❌ Brak ofert (UNIVERSAL PRO)")
        return

    offers.sort(key=lambda x: x["price"])

    msg = "🏝 <b>UNIVERSAL PRO TRAVEL BOT</b>\n\n"

    for o in offers[:10]:
        msg += f"""
💰 {o['price']} zł
🧾 {o['text']}
-------------------
"""

    send_telegram(msg)


if __name__ == "__main__":
    main()
