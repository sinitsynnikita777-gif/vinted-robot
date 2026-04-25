import requests
import time
import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })

URL = "https://www.vinted.co.uk/api/v2/catalog/items"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Accept-Language": "en-GB,en;q=0.9",
}

params = {
    "search_text": "",
    "price_to": 150,
    "per_page": 10,
    "order": "newest_first",
}

seen = set()

print("🚀 Bot started")

while True:
    try:
        r = requests.get(URL, headers=headers, params=params, timeout=15)
        print("STATUS:", r.status_code)

        if r.status_code != 200:
            print("⛔ Blocked, retry later...")
            time.sleep(60)
            continue

        data = r.json()
        items = data.get("items", [])

        for item in items:
            item_id = item["id"]

            if item_id in seen:
                continue

            seen.add(item_id)

            text = f"{item['title']}\n£{item['price']}\n{item['url']}"
            print(text)
            send(text)

        time.sleep(30)

    except Exception as e:
        print("error:", e)
        time.sleep(60)
