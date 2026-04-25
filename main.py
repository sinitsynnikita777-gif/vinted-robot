import requests
import time

BASE_URL = "https://www.vinted.co.uk"
API_URL = "https://www.vinted.co.uk/api/v2/catalog/items"

session = requests.Session()

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-GB,en;q=0.9",
}

def get_token():
    r = session.get(BASE_URL, headers=headers)
    
    # вытаскиваем токен из cookies
    token = session.cookies.get("access_token_web")

    if not token:
        print("❌ token not found")
    else:
        print("✅ token found")

    return token

def fetch_items(token):
    headers_api = headers.copy()
    headers_api["Authorization"] = f"Bearer {token}"

    params = {
        "search_text": "rick owens",
        "price_to": 150,
        "per_page": 10,
        "page": 1,
        "order": "newest_first",
    }

    r = session.get(API_URL, headers=headers_api, params=params)

    print("STATUS:", r.status_code)

    if r.status_code != 200:
        print(r.text[:200])
        return

    data = r.json()
    items = data.get("items", [])

    print("ITEMS:", len(items))

    for item in items:
        print(item["title"], item["price"], item["url"])


while True:
    try:
        token = get_token()

        if token:
            fetch_items(token)

        print("-----")
        time.sleep(30)

    except Exception as e:
        print("error:", e)
        time.sleep(30)
