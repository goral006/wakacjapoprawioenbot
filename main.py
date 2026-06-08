from telegram import send_telegram
import json
import re

MAX_PRICE = 8000


# =========================
# 📦 LOAD TRACE
# =========================

def load():
    with open("full_trace.json", "r", encoding="utf-8") as f:
        return json.load(f)


# =========================
# 🔎 EXTRACT PRICES FROM TEXT
# =========================

def extract_prices(text):
    # szuka "1234 zł"
    matches = re.findall(r"(\d[\d\s]{2,})\s?zł", text)
    prices = []

    for m in matches:
        try:
            prices.append(int(m.replace(" ", "")))
        except:
            pass

    return prices


# =========================
# 🔎 FIND OFFER-LIKE BLOCKS
# =========================

def extract_offers(text):
    offers = []

    # bardzo luźna heurystyka HTML/JSON mix
    blocks = re.split(r"\{|\[|</div>|</article>|</li>", text)

    for b in blocks:
        if any(k in b.lower() for k in ["hotel", "osoba", "noc", "all inclusive", "zł"]):
            offers.append(b)

    return offers


# =========================
# 🚀 MAIN
# =========================

def main():
    logs = load()

    all_text = ""
    for l in logs:
        if "body" in l:
            all_text += l["body"] + "\n"

    offers_blocks = extract_offers(all_text)

    if not offers_blocks:
        send_telegram("❌ brak bloków ofert w raw HTML")
        return

    prices = extract_prices(all_text)

    valid = [p for p in prices if p <= MAX_PRICE]

    if not valid:
        send_telegram("❌ brak cen do 8000 zł w raw danych")
        return

    valid.sort()

    msg = "🏝 <b>FINAL RAW EXTRACTION RESULT</b>\n\n"

    for p in valid[:10]:
        msg += f"💰 {p} zł\n"

    send_telegram(msg)


if __name__ == "__main__":
    main()
