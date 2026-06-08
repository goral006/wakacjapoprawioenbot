import requests

url = r"""https://www.travelplanet.pl/wakacje/?s_action=TRIPS_SEARCH&d_start_from=05.09.2026&d_end_to=15.09.2026&nl_transportation_id%5B%5D=3_21&nl_transportation_id%5B%5D=3_18&nl_transportation_id%5B%5D=3_29&sort=qs&page=1&nl_length_from=7&nl_length_to=8&nl_occupancy_children=1&nl_occupancy_adults=2&nl_ages_children%5B%5D=4&nd_review_rating_average_from=8&c_price_to=15000"""

r = requests.get(
    url,
    headers={
        "User-Agent": "Mozilla/5.0"
    },
    timeout=30
)

print("STATUS:", r.status_code)
print("DLUGOSC:", len(r.text))
