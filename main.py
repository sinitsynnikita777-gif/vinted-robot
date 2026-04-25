import requests
import time

URL = "https://www.vinted.co.uk/api/v2/catalog/items"

PARAMS = {
    "page": 1,
    "per_page": 10,
    "order": "newest_first"
}

while True:
    try:
        r = requests.get(URL, params=PARAMS)
        data = r.json()

        items = data.get("items", [])

        for item in items:
            print(item["title"], item["price"], item["url"])

        print("-----")
        time.sleep(30)

    except Exception as e:
        print("error:", e)
        time.sleep(10)
