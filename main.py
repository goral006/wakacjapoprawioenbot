import requests
from bs4 import BeautifulSoup
import os

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

MAX_PRICE = 15000


def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


def check():
    send("🔍 Sprawdzam wakacje...")

    url = "https://www.wakacje.pl/wczasy/"

    r = requests.get(url, timeout=30)
    soup = BeautifulSoup(r.text, "lxml")

    offers = []

    for item in soup.select("div"):
        text = item.get_text(" ", strip=True)

        if "Turcja" in text or "Tunezja" in text or "Grecja" in text:
            if "all inclusive" in text.lower():
                offers.append(text)

    if not offers:
        send("❌ Brak ofert")
    else:
        for o in offers[:5]:
            send("✈️ " + o[:300])


if __name__ == "__main__":
    check()
