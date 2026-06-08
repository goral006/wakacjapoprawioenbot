import requests
import os

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

print("TOKEN:", TOKEN)
print("CHAT_ID:", CHAT_ID)

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

r = requests.post(url, data={
    "chat_id": CHAT_ID,
    "text": "TEST MIN BOT"
})

print(r.status_code)
print(r.text)
