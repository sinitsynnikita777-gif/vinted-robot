import requests
import time
import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BASE = "https://www.vinted.co.uk"
API = "https://www.vinted.co.uk/api/v2/catalog/items"

session = requests.Session()

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-GB,en;q=0.9",
}

def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg}
    )

def refresh_session():
    r = session.get(BASE, headers=headers, timeout=20)
    print("HOME:", r.status_code)
    print("COOKIES:", session.cookies.get_dict())

print("🚀 Bot started")
refresh_session()

seen = set()

while True:
    try:
        params = {
            "search_text": "rick owens",
            "price_to": 150,
            "per_page": 10,
            "page": 1,
            "order": "newest_first",
        }

        r = session.get(API, headers=headers, params=params, timeout=20)
        print("STATUS:", r.status_code)
        print("TEXT:", r.text[:120])

        if r.status_code in [401, 403]:
            refresh_session()
            time.sleep(60)
            continue

        data = r.json()
        items = data.get("items", [])

        for item in items:
            item_id = item["id"]
            if item_id in seen:
                continue

            seen.add(item_id)

            text = f'{item.get("title")}\n£{item.get("price")}\n{item.get("url")}'
            print(text)
            send(text)

        time.sleep(30)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(60)
