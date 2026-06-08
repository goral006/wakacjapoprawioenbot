from playwright.sync_api import sync_playwright
from telegram import send_telegram

URL = "https://www.travelplanet.pl/wakacje/?s_action=TRIPS_SEARCH&d_start_from=05.09.2026&d_end_to=15.09.2026&page=1"

def get_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(8000)

        html = page.content()

        browser.close()
        return html

def main():
    html = get_page()

    print("HTML length:", len(html))
    print(html[:1000])

    send_telegram("TEST: Playwright działa ✔️")

if __name__ == "__main__":
    main()
