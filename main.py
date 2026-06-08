import requests
import json
import re
from datetime import datetime

# =========================
# ⚙️ CONFIG
# =========================

MAX_PRICE = 6000

START_DATE = datetime(2026, 9, 5)
END_DATE = datetime(2026, 9, 15)

COUNTRIES = ["grecja", "hiszpania", "turcja", "cypr", "tunezja"]

AIRPORTS = ["kraków", "katowice", "rzeszów", "krk", "ktw", "rze"]

MEALS = ["all inclusive", "ai", "hb", "fb"]

BAD = ["kod rabatowy", "voucher", "newsletter", "promocja"]


# =========================
# 📡 TRAVELPLANET FETCH
# =========================

URL = "https://www.travelplanet.pl/direct/tour_search/ajax-get-search-form-fields-def/?nl_top_country_set_id=1&s_holiday_target=tours"


def fetch():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(URL, headers=headers, timeout=30)
    return r.text


# =========================
# 💰 PRICE
# =========================

def extract_price(text):
    m = re.findall(r"(\d[\d\s]{2,})\s?zł", text)
    if not m:
        return None
    return int(m[0].replace(" ", ""))


# =========================
# 🎯 FILTER
# =========================

def interesting(text):

    t = text.lower()

    if any(x in t for x in BAD):
        return False

    if not any(x in t for x in COUNTRIES):
        return False

    if not any(x in t for x in AIRPORTS):
        return False

    if not any(x in t for x in MEALS):
        return False

    price = extract_price(text)
    if not price or price > MAX_PRICE:
        return False

    # date + days
    m = re.search(r"(\d{2}\.\d{2}\.\d{4}).*?(\d+)\s*dni", text)
    if not m:
        return False

    try:
        dep = datetime.strptime(m.group(1), "%d.%m.%Y")
        days = int(m.group(2))
    except:
        return False

    if dep < START_DATE or dep > END_DATE:
        return False

    if days not in [7, 8]:
        return False

    return True


# =========================
# 🔎 PARSE
# =========================

def parse(raw):

    offers = []
    seen = set()

    # JSON scraping fallback
    chunks = re.findall(r"\{.*?\}", raw)

    for c in chunks:
        try:
            data = json.loads(c)

            def walk(obj):
                if isinstance(obj, dict):
                    for v in obj.values():
                        walk(v)

                elif isinstance(obj, list):
                    for v in obj:
                        walk(v)

                elif isinstance(obj, str):
                    if "zł" in obj and interesting(obj):
                        key = obj[:80]
                        if key in seen:
                            return
                        seen.add(key)

                        offers.append({
                            "text": obj,
                            "price": extract_price(obj)
                        })

            walk(data)

        except:
            continue

    return offers


# =========================
# 🚀 MAIN
# =========================

def main():

    print("🚀 TRAVELPLANET BOT START")

    raw = fetch()
    offers = parse(raw)

    print("FOUND:", len(offers))

    if not offers:
        print("❌ brak ofert")
        return

    offers.sort(key=lambda x: x["price"])

    msg = "🏝 TRAVELPLANET CIEKAWE OFERTY\n\n"

    for o in offers[:10]:
        msg += f"""
💰 {o['price']} zł
🧾 {o['text'][:200]}
-------------------
"""

    print(msg)


if __name__ == "__main__":
    main()
