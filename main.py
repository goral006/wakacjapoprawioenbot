from playwright.sync_api import sync_playwright
from telegram import send_telegram
import time

URL = "https://www.travelplanet.pl/wakacje/?s_action=TRIPS_SEARCH&d_start_from=05.09.2026&d_end_to=05.09.2026&page=1"


def run():
    with sync_playwright() as p:
        # 🔥 PERSISTENT CONTEXT = jak normalna przeglądarka
        browser = p.chromium.launch_persistent_context(
            user_data_dir="user_data",
            headless=False,  # ważne: NIE headless
            viewport={"width": 1280, "height": 800},
            locale="pl-PL",
        )

        page = browser.new_page()

        # 🔥 stealth timing
        page.goto(URL, wait_until="networkidle")
        time.sleep(5)

        # 🔥 symulacja usera
        page.mouse.move(300, 400)
        time.sleep(1)
        page.mouse.wheel(0, 800)
        time.sleep(3)

        # 🔥 wymuszenie JS execution chain
        html = page.content()

        browser.close()

    return html


def extract_prices(html):
    import re

    prices = re.findall(r"(\d[\d\s]{3,})\s?zł", html)

    cleaned = []

    for p in prices:
        try:
            cleaned.append(int(p.replace(" ", "")))
        except:
            pass

    return sorted(cleaned)


def main():
    html = run()

    prices = extract_prices(html)

    if not prices:
        send_telegram("❌ nadal brak danych (stealth required + anti-bot)")
        return

    msg = "🏝 <b>STEALTH MODE RESULTS</b>\n\n"

    for p in prices[:10]:
        msg += f"💰 {p} zł\n"

    send_telegram(msg)


if __name__ == "__main__":
    main()
