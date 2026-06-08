from playwright.sync_api import sync_playwright
from telegram import send_telegram
import json

URL = "https://www.travelplanet.pl/wakacje/?s_action=TRIPS_SEARCH&d_start_from=05.09.2026&d_end_to=15.09.2026&page=1"


# =========================
# 🌐 NETWORK CAPTURE (FULL)
# =========================

def capture_network():
    logs = []

    def handle_response(response):
        try:
            req = response.request

            entry = {
                "url": response.url,
                "method": req.method,
                "post_data": req.post_data or None,
            }

            # JSON response
            try:
                if "json" in response.headers.get("content-type", "").lower():
                    entry["json"] = response.json()
            except:
                pass

            # TEXT fallback
            try:
                if "text" in response.headers.get("content-type", "").lower():
                    entry["text"] = response.text()[:500]
            except:
                pass

            logs.append(entry)

        except:
            pass

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.on("response", handle_response)

        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_timeout(20000)

        browser.close()

    return logs


# =========================
# 🔎 SEARCH FOR MEANINGFUL DATA
# =========================

def find_suspicious_data(logs):
    candidates = []

    for l in logs:
        data = l.get("json")

        if not data:
            continue

        text = str(data).lower()

        # heurystyka: szukamy rzeczy wyglądających jak oferty
        keywords = ["price", "hotel", "offer", "trip", "board", "country", "rating"]

        score = sum(1 for k in keywords if k in text)

        if score >= 2:
            candidates.append({
                "url": l["url"],
                "score": score,
                "data": data
            })

    return sorted(candidates, key=lambda x: x["score"], reverse=True)


# =========================
# 🚀 MAIN
# =========================

def main():
    print("🚀 START FULL NETWORK DEBUG")

    logs = capture_network()

    # zapis pełny dump
    with open("network_full.json", "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

    candidates = find_suspicious_data(logs)

    if not candidates:
        send_telegram(
            "❌ Nie znaleziono żadnych danych przypominających oferty\n"
            f"📡 Requests: {len(logs)}\n"
            "👉 zapisano network_full.json"
        )
        return

    best = candidates[0]

    with open("best_candidate.json", "w", encoding="utf-8") as f:
        json.dump(best, f, ensure_ascii=False, indent=2)

    msg = (
        "📡 <b>NETWORK ANALYSIS COMPLETE</b>\n\n"
        f"🔎 Requests: {len(logs)}\n"
        f"🏆 Best candidate score: {best['score']}\n"
        f"🔗 URL: {best['url']}\n\n"
        "👉 zapisano best_candidate.json"
    )

    send_telegram(msg)


if __name__ == "__main__":
    main()
