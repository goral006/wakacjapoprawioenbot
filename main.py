import requests
from bs4 import BeautifulSoup

url = r"""TU_WKLEJ_TEN_SAM_LINK_Z_TRAVELPLANET"""

r = requests.get(
    url,
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=30
)

print("STATUS:", r.status_code)

soup = BeautifulSoup(r.text, "html.parser")

text = soup.get_text(" ", strip=True)

print(text[:5000])
