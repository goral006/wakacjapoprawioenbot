import requests
import os

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def check_offers():
    send("🔍 Sprawdzam oferty...")

    # na razie test
    offers = [
        "Turcja - 4200 zł - all inclusive - 4★",
        "Tunezja - 3900 zł - all inclusive - 3★"
    ]

    if offers:
        for o in offers:
            send("✈️ " + o)
    else:
        send("❌ Brak ofert")

if __name__ == "__main__":
    check_offers()
