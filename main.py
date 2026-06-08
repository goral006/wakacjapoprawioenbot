import requests
from bs4 import BeautifulSoup
import os

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://www.travelplanet.pl/wakacje/?s_action=TRIPS_SEARCH&d_start_from=05.09.2026&d_end_to=15.09.2026&nl_transportation_id%5B%5D=3_21&nl_transportation_id%5B%5D=3_18&nl_transportation_id%5B%5D=3_29&s_holiday_target=tours&duration=Custom%20range&sort=qs&page=1&nl_length_from=7&nl_length_to=8&nl_occupancy_children=1&nl_occupancy_adults=2&nl_ages_children%5B%5D=4&nd_review_rating_average_from=8&c_price_to=15000&nl_country_id%5B%5D=29&nl_country_id%5B%5D=28&nl_country_id%5B%5D=30&nl_country_id%5B%5D=35&nl_country_id%5B%5D=10&nl_country_id%5B%5D=31&nl_country_id%5B%5D=9"


def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": msg
        },
        timeout=30
    )


try:
    send("🔍 Sprawdzam Travelplanet...")

    r = requests.get(
        URL,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30
    )

    send(f"✅ Status strony: {r.status_code}")
    send(f"📄 Długość strony: {len(r.text)} znaków")

    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.title.text if soup.title else "Brak tytułu"

    send(f"📰 Tytuł strony:\n{title}")

except Exception as e:
    send(f"❌ Błąd:\n{str(e)}")

print("KONIEC")
