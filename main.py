import requests
from telegram import send_telegram

# =========================
# 🔥 PARAMETRY WYSZUKIWANIA
# =========================

PAYLOAD = {
    "d_start_from": "05.09.2026",
    "d_end_to": "15.09.2026",
    "nl_length_from": 7,
    "nl_length_to": 8,
    "nl_occupancy_adults": 2,
    "nl_occupancy_children": 1,
    "nl_ages_children[]": 4,

    "nl_country_id[]": [29, 28, 30, 35, 10, 31, 9],  # Hiszpania, Grecja, Turcja, Tunezja, Cypr itd.

    "nd_review_rating_average_from": 8,
    "c_price_to": 8000,

    "s_holiday_target": "tours",
    "sort": "qs"
}

URL = "https://www.travelplanet.pl/wakacje/?s_action=TRIPS_SEARCH"


# =========================
# 🌐 FETCH API
# =========================

def fetch():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest"
    }

    r = requests.get(URL, params=PAYLOAD, headers=headers, timeout=30)

    print("Status:", r.status_code)
    print("Length:", len(r.text))

    try:
        return r.json()
    except:
        return None


# =========================
# 🔎 PARSE JSON OFFERS
# =========================

def parse(data):
    offers = []

    if not data:
        return offers

    # różne struktury API (zabezpieczenie)
    items = data.get("offers") or data.get("data") or []

    for o in items:
        try:
            price = o.get("price_total") or o.get("price") or 999999
            name = o.get("hotel_name") or o.get("name")
            country = o.get("country_name")
            rating = o.get("rating")

            if not price or price > 8000:
                continue

            if rating and rating < 8:
                continue

            offers.append({
                "price": price,
                "name": name,
                "country": country,
                "rating": rating
            })

        except:
            continue

    return offers


# =========================
# 🚀 MAIN
# =========================

def main():
    data = fetch()

    offers = parse(data)

    if not offers:
        send_telegram("❌ Brak ofert w API response")
        return

    offers = sorted(offers, key=lambda x: x["price"])

    msg = "🏝 <b>TRAVEL API - PRO BOT</b>\n\n"

    for o in offers[:10]:
        msg += f"""
🏨 {o['name']}
🌍 {o['country']}
⭐ {o['rating']}
💰 {o['price']} zł
-------------------
"""

    send_telegram(msg)


if __name__ == "__main__":
    main()
