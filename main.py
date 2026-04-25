import requests
import time
import os

PROXY = os.getenv("PROXY_URL")

proxies = {
    "http": PROXY,
    "https": PROXY
}

URL = "https://www.vinted.co.uk/api/v2/catalog/items"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Accept-Language": "en-GB,en;q=0.9",
}

params = {
    "search_text": "rick owens",
    "price_to": 150,
    "per_page": 10,
    "order": "newest_first",
}

while True:
    try:
        r = requests.get(URL, headers=headers, params=params, proxies=proxies, timeout=15)
        print("STATUS:", r.status_code)

        if r.status_code != 200:
            print("blocked, retry...")
            time.sleep(60)
            continue

        data = r.json()
        items = data.get("items", [])

        for item in items:
            print(item["title"], item["price"], item["url"])

        print("------")
        time.sleep(30)

    except Exception as e:
        print("error:", e)
        time.sleep(60)
