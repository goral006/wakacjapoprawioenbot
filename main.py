from telegram import send_telegram
import json

MAX_PRICE = 8000


# =========================
# 📦 LOAD DATA
# =========================

def load():
    with open("best_post.json", "r", encoding="utf-8") as f:
        return json.load(f)


# =========================
# 🔎 FIND ANY LISTS IN RESPONSE
# =========================

def deep_search(obj):
    results = []

    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():

                # 🔥 każdy podejrzany klucz
                if isinstance(v, list):
                    if len(v) > 0:
                        results.append(v)

                walk(v)

        elif isinstance(x, list):
            for i in x:
                walk(i)

    walk(obj)
    return results


# =========================
# 💰 PRICE EXTRACTION (FLEXIBLE)
# =========================

def get_price(item):
    if not isinstance(item, dict):
        return None

    possible_keys = [
        "price",
        "totalPrice",
        "total_price",
        "amount",
        "priceValue",
        "minPrice",
        "fromPrice"
    ]

    for k in possible_keys:
        if k in item:
            try:
                return float(str(item[k]).replace(" ", ""))
            except:
                pass

    return None


# =========================
# 🔎 CHECK IF LOOKS LIKE OFFER
# =========================

def looks_like_offer(item):
    if not isinstance(item, dict):
        return False

    keys = " ".join(item.keys()).lower()

    keywords = ["hotel", "price", "rating", "country", "board", "name", "title"]

    score = sum(1 for k in keywords if k in keys)

    return score >= 2


# =========================
# 🚀 MAIN
# =========================

def main():
    data = load()

    lists = deep_search(data)

    offers = []

    for lst in lists:
        for item in lst:
            if looks_like_offer(item):
                offers.append(item)

    if not offers:
        send_telegram("❌ Nie znaleziono ofert w best_post.json")
        return

    valid = []

    for o in offers:
        price = get_price(o)

        if price and price <= MAX_PRICE:
            valid.append(o)

    if not valid:
        send_telegram("❌ Brak ofert do 8000 zł")
        return

    msg = "🏝 <b>FINAL OFFERS (POST ENGINE)</b>\n\n"

    for i, o in enumerate(valid[:5]):
        msg += f"""
🏨 {o.get('name', o.get('title', 'Brak nazwy'))}
💰 {get_price(o)} zł
⭐ {o.get('rating', 'brak oceny')}
🌍 {o.get('country', 'brak')}
-------------------
"""

    send_telegram(msg)


if __name__ == "__main__":
    main()
