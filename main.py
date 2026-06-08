from playwright.sync_api import sync_playwright
from telegram import send_telegram
import json

URL = "https://www.travelplanet.pl/wakacje/?s_action=TRIPS_SEARCH&d_start_from=05.09.2026&d_end_to=15.09.2026&page=1"


def capture_pairs():
    pairs = []

    def handle_response(response):
        try:
            req = response.request

            data = {
                "url": response.url,
                "method": req.method,
                "post": req.post_data,
                "headers": dict(req.headers)
            }

            # tylko POST + potencjalne search
            if req.method == "POST":
                try:
                    if "json" in response.headers.get("content-type", ""):
                        data["response"] = response.json()
                    else:
                        data["response_text"] = response.text()[:1000]
                except:
                    pass

                pairs.append(data)

        except:
            pass

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.on("response", handle_response)

        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_timeout(20000)

        browser.close()

    return pairs


def find_best(pairs):
    # heurystyka: szukamy największej odpowiedzi
    best = None
    best_size = 0

    for p in pairs:
        r = p.get("response") or p.get("response_text")

        if not r:
            continue

        size = len(str(r))

        if size > best_size:
            best_size = size
            best = p

    return best


def main():
    pairs = capture_pairs()

    with open("post_pairs.json", "w", encoding="utf-8") as f:
        json.dump(pairs, f, ensure_ascii=False, indent=2)

    best = find_best(pairs)

    if not best:
        send_telegram("❌ Nie znaleziono odpowiedzi POST z danymi")
        return

    with open("best_post.json", "w", encoding="utf-8") as f:
        json.dump(best, f, ensure_ascii=False, indent=2)

    send_telegram(
        "📡 FINAL TRACE DONE\n"
        f"📤 POST pairs: {len(pairs)}\n"
        "🏆 zapisano best_post.json\n"
        "👉 analizujemy odpowiedź"
    )


if __name__ == "__main__":
    main()
