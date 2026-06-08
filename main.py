import requests

url = "https://www.travelplanet.pl/wakacje/?s_action=TRIPS_SEARCH&d_start_from=05.09.2026&d_end_to=15.09.2026&nl_transportation_id[]=3_21&nl_transportation_id[]=3_18&nl_transportation_id[]=3_29&s_holiday_target=tours&duration=Custom%20range&sort=qs&page=1&nl_length_from=7&nl_length_to=8&nl_occupancy_children=1&nl_occupancy_adults=2&nl_ages_children[]=4&nd_review_rating_average_from=8&c_price_to=15000&nl_country_id[]=29&nl_country_id[]=28&nl_country_id[]=30&nl_country_id[]=35&nl_country_id[]=10&nl_country_id[]=31&nl_country_id[]=9"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.travelplanet.pl/"
}

response = requests.get(url, headers=headers)

print("Status:", response.status_code)

# czasem API zwraca HTML fallback – zabezpieczenie:
try:
    data = response.json()
except Exception:
    print("❌ To nie JSON – strona blokuje API lub zmieniła endpoint")
    exit()

# 🔍 DEBUG – sprawdzamy strukturę
print("Klucze:", data.keys())

# =========================
# 🧠 EKSTRAKCJA OFERT
# =========================

# Travelplanet zwykle trzyma wyniki w:
results = (
    data.get("results")
    or data.get("data", {}).get("results")
    or data.get("trips")
    or []
)

print(f"\nZnaleziono ofert: {len(results)}\n")

for i, item in enumerate(results[:20]):
    name = item.get("name") or item.get("title") or "Brak nazwy"
    price = item.get("price") or item.get("price_from") or "Brak ceny"
    rating = item.get("rating") or item.get("review_score") or "brak"
    link = item.get("url") or item.get("link") or ""

    print(f"{i+1}. {name}")
    print(f"   💰 Cena: {price}")
    print(f"   ⭐ Ocena: {rating}")
    print(f"   🔗 Link: {link}")
    print("-" * 40)
