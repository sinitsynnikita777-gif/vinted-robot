import os
import time
import random
import requests

# =====================
# ENV VARIABLES
# =====================

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BASE = "https://www.vinted.co.uk"
API = "https://www.vinted.co.uk/api/v2/catalog/items"

# =====================
# SETTINGS
# =====================

SEARCHES = [
    "rick owens",
    "rick owens drkshdw",
    "maison margiela",
    "raf simons",
    "helmut lang",
    "junya watanabe",
    "vetements",
    "balenciaga",
    "acne studios",
    "kiko kostadinov",
    "julius",
    "boris bidjan saberi",
    "vivienne westwood",
    "martine rose",
    "no faith studios",
    "maison mihara yasuhiro",
    "alyx",
    "new rock",
    "hysteric glamour",
    "cav empt",
    "gosha rubchinskiy",
    "paccbet",
]

MAX_PRICE = 150
PER_PAGE = 10

MIN_DELAY = 35
MAX_DELAY = 85

COOKIE_REFRESH_EVERY = 20 * 60
LONG_SLEEP_AFTER_BLOCK = 15 * 60

USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
]

BAD_WORDS = [
    "fake",
    "replica",
    "rep",
    "reps",
    "inspired",
    "dupe",
    "custom",
    "bootleg",
    "not authentic",
    "not real",
    "damaged",
    "ripped",
    "stains",
    "kids",
    "child",
    "junior",
]

seen = set()
session = requests.Session()
last_cookie_refresh = 0


# =====================
# HELPERS
# =====================

def make_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-GB,en;q=0.9",
        "Referer": BASE + "/",
        "Origin": BASE,
        "Connection": "keep-alive",
    }


def send(msg):
    if not TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN missing")
        return

    if not CHAT_ID:
        print("ERROR: TELEGRAM_CHAT_ID missing")
        return

    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": msg,
                "disable_web_page_preview": False,
            },
            timeout=15,
        )

        print("Telegram status:", r.status_code)
        print("Telegram response:", r.text)

    except Exception as e:
        print("Telegram error:", e)


def refresh_cookies(force=False):
    global last_cookie_refresh

    now = time.time()

    if not force and now - last_cookie_refresh < COOKIE_REFRESH_EVERY:
        return

    try:
        print("Refreshing cookies...")
        r = session.get(BASE, headers=make_headers(), timeout=20)

        print("HOME:", r.status_code)
        print("COOKIES:", list(session.cookies.get_dict().keys()))

        last_cookie_refresh = now

        time.sleep(random.randint(3, 8))

    except Exception as e:
        print("Cookie refresh error:", e)


def is_bad_item(item):
    title = (item.get("title") or "").lower()
    desc = (item.get("description") or "").lower()
    text = title + " " + desc

    return any(word in text for word in BAD_WORDS)


def clean_price(price):
    if isinstance(price, dict):
        return price.get("amount", "?")
    return price


def score_item(item):
    price = clean_price(item.get("price", 999))

    try:
        price_num = float(price)
    except:
        price_num = 999

    score = 0

    if price_num <= 30:
        score += 35
    elif price_num <= 75:
        score += 25
    elif price_num <= 120:
        score += 12
    else:
        score += 5

    favs = item.get("favourite_count") or item.get("favorites_count") or 0

    if favs >= 20:
        score += 15
    elif favs >= 5:
        score += 8

    brand = (item.get("brand_title") or "").lower()

    main_brands = [
        "rick owens",
        "maison margiela",
        "raf simons",
        "balenciaga",
        "vetements",
        "acne studios",
        "julius",
        "kiko kostadinov",
    ]

    if any(b in brand for b in main_brands):
        score += 25
    else:
        score += 10

    return max(1, min(100, score))


def mode_from_score(score):
    if score >= 80:
        return "🔥 RESELL"
    if score >= 55:
        return "🧥 PERSONAL"
    return "👀 LOW"


def format_item(item, search):
    title = item.get("title", "No title")
    brand = item.get("brand_title") or "unknown"
    price = clean_price(item.get("price", "?"))
    size = item.get("size_title") or "?"
    condition = item.get("status") or item.get("status_title") or "?"
    favs = item.get("favourite_count") or item.get("favorites_count") or 0
    url = item.get("url") or f"https://www.vinted.co.uk/items/{item.get('id')}"

    score = score_item(item)
    mode = mode_from_score(score)

    return f"""{mode}

🏷 Бренд: {brand}
🔎 Поиск: {search}

👕 Название: {title}
💰 Цена: £{price}
📏 Размер: {size}
📦 Состояние: {condition}
❤️ Лайки: {favs}
📊 Оценка: {score}/100

🔗 {url}"""


def fetch(search):
    params = {
        "search_text": search,
        "price_to": MAX_PRICE,
        "per_page": PER_PAGE,
        "page": 1,
        "order": "newest_first",
    }

    try:
        r = session.get(API, headers=make_headers(), params=params, timeout=25)

        print(search, "STATUS:", r.status_code)
        print("TEXT:", r.text[:120])

        if r.status_code in [401, 403, 429]:
            print("Blocked / limited. Refreshing cookies and sleeping...")
            refresh_cookies(force=True)
            time.sleep(LONG_SLEEP_AFTER_BLOCK)
            return []

        if r.status_code != 200:
            print("Bad status:", r.status_code)
            time.sleep(120)
            return []

        return r.json().get("items", [])

    except Exception as e:
        print("Fetch error:", e)
        time.sleep(120)
        return []


# =====================
# MAIN
# =====================

def main():
    print("🚀 Vinted bot started")
    send("✅ Telegram test: Vinted bot started")

    refresh_cookies(force=True)

    while True:
        random.shuffle(SEARCHES)

        for search in SEARCHES:
            refresh_cookies()

            items = fetch(search)

            for item in items:
                item_id = str(item.get("id"))

                if not item_id:
                    continue

                if item_id in seen:
                    continue

                seen.add(item_id)

                if is_bad_item(item):
                    print("Skipped bad item:", item.get("title"))
                    continue

                msg = format_item(item, search)
                print(msg)
                send(msg)

            delay = random.randint(MIN_DELAY, MAX_DELAY)
            print(f"Sleeping {delay}s...")
            time.sleep(delay)

        big_delay = random.randint(180, 420)
        print(f"Cycle done. Sleeping {big_delay}s...")
        time.sleep(big_delay)


if __name__ == "__main__":
    main()
