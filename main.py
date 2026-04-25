import time
import random
import requests

BASE = "https://www.vinted.co.uk"
API = "https://www.vinted.co.uk/api/v2/catalog/items"

SEARCHES = [
    "rick owens",
    "balenciaga",
    "raf simons",
    "vetements",
    "maison margiela",
]

MIN_DELAY = 30
MAX_DELAY = 60

session = requests.Session()
seen = set()

USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0)",
]

def headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json",
        "Referer": BASE
    }

def refresh():
    try:
        r = session.get(BASE, headers=headers(), timeout=15)
        print("REFRESH:", r.status_code)
    except Exception as e:
        print("REFRESH ERROR:", e)

def fetch(search):
    try:
        r = session.get(API, headers=headers(), params={
            "search_text": search,
            "price_to": 150,
            "per_page": 10,
            "order": "newest_first"
        }, timeout=20)

        print(search, "STATUS:", r.status_code)

        if r.status_code != 200:
            return []

        return r.json().get("items", [])

    except Exception as e:
        print("FETCH ERROR:", e)
        return []

print("🚀 BOT STARTED")

refresh()

while True:
    for search in SEARCHES:
        items = fetch(search)

        for item in items:
            item_id = item.get("id")

            if item_id in seen:
                continue

            seen.add(item_id)

            title = item.get("title")
            price = item.get("price")
            url = item.get("url")

            print("\n🔥 NEW ITEM")
            print("SEARCH:", search)
            print("TITLE:", title)
            print("PRICE:", price)
            print("LINK:", url)

        time.sleep(random.randint(MIN_DELAY, MAX_DELAY))

    time.sleep(random.randint(60, 120))
