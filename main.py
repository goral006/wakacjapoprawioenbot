from telegram import send_telegram
import json

MAX_PRICE = 8000


# =========================
# 📦 LOAD NETWORK FILE
# =========================

def load_network():
    with open("best_network.json", "r", encoding="utf-8") as f:
        return json.load(f)


# =========================
# 🔎 REKURENCYJNE SZUKANIE OFERT
# =========================

def find_offers(obj):
    offers = []

    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():

                # 🔥 typowe klucze ofert
                if k.lower() in ["offers", "offer", "results", "trips", "items", "data", "list"]:
                    if isinstance(v, list):
                        for item in v:
                            offers.append(item)

                walk(v)

        elif isinstance(x, list):
            for i in x:
                walk(i)

    walk(obj)
    return offers


# =========================
# 💰 PRICE EXTRACTION
# =========================

def get_price(o):
    if not isinstance(o, dict):
        return None

    for key in ["price", "totalPrice", "total_price", "amount"]:
        if key in o:
            try:
                return float(str(o[key]).replace(" ", ""))
            except:
                pass

    return None


# =========================
# 🧠 FILTER
# =========================

def is_valid(o):
    price = get_price(o)

    if price is None:
        return False

    return price <= MAX_PRICE


# =========================
# 🚀 MAIN
# =========================

def main():
    data = load_network()

    offers = find_offers(data)

    if not offers:
        send_telegram("❌ Nie znaleziono ofert w best_network.json")
        return

    valid = [o for o in offers if is_valid(o)]

    if not valid:
        send_telegram("❌ Brak ofert do 8000 zł")
        return

    msg = "🏝 <b>TOP WAKACJE (NETWORK FINAL MODE)</b>\n\n"

    for i, o in enumerate(valid[:5]):
        msg += f"""
🏨 {o.get('name', o.get('title', 'Brak nazwy'))}
💰 {get_price(o)} zł
⭐ {o.get('rating', 'brak oceny')}
🌍 {o.get('country', 'brak')}
🔗 {o.get('url', '')}
-------------------
"""

    send_telegram(msg)


if __name__ == "__main__":
    main()
