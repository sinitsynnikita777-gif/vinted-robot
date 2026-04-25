import requests
import time

URL = "https://www.vinted.co.uk/api/v2/catalog/items"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Accept-Language": "en-GB,en;q=0.9",
}

PARAMS = {
    "search_text": "rick owens",
    "price_to": 150,
    "per_page": 10,
    "page": 1,
    "order": "newest_first",
}

while True:
    try:
        r = requests.get(URL, params=PARAMS, headers=HEADERS, timeout=20)

        print("STATUS:", r.status_code)
        print("TEXT START:", r.text[:100])

        if r.status_code != 200:
            print("bad status")
            time.sleep(30)
            continue

        data = r.json()
        items = data.get("items", [])

        print("ITEMS:", len(items))

        for item in items:
            title = item.get("title")
            price = item.get("price")
            url = item.get("url")
            print(title, price, url)

        print("-----")
        time.sleep(30)

    except Exception as e:
        print("error:", e)
        time.sleep(30)
