import requests

session = requests.Session()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pl-PL,pl;q=0.9,en;q=0.8",
    "Referer": "https://www.travelplanet.pl/",
    "Connection": "keep-alive"
}

url = "https://www.travelplanet.pl/"

# 1. najpierw wejście na stronę (ustawia cookies)
session.get(url, headers=headers)

# 2. dopiero potem search
search_url = "https://www.travelplanet.pl/wakacje/?s_action=TRIPS_SEARCH&d_start_from=05.09.2026&d_end_to=15.09.2026&page=1"

r = session.get(search_url, headers=headers)

print("Status:", r.status_code)
print("Length:", len(r.text))

print(r.text[:500])
