import time
import random
import requests

# =====================
# TELEGRAM
# =====================

BOT_TOKEN = "8714724829:AAGZ1HLaq4tRJgKCwD1Clif_3CjvYK1IFpE"
CHAT_ID = "8104561365"

def send(msg):
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": msg,
                "disable_web_page_preview": False,
            },
            timeout=10
        )
        print("TG STATUS:", r.status_code)
        print("TG RESPONSE:", r.text[:200])
    except Exception as e:
        print("TG ERROR:", e)


# =====================
# VINTED
# =====================

BASE = "https://www.vinted.co.uk"
API = "https://www.vinted.co.uk/api/v2/catalog/items"

SEARCHES = [
    "rick owens",
    "rick owens drkshdw",
    "balenciaga",
    "raf simons",
    "vetements",
    "maison margiela",
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

MAX_PRICE = 150
PER_PAGE = 10

MIN_DELAY = 30
MAX_DELAY = 75

session = requests.Session()
seen = set()

USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36",
]


def headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-GB,en;q=0.9",
        "Referer": BASE + "/",
        "Origin": BASE,
        "Connection": "keep-alive",
    }


def refresh_cookies():
    try:
        r = session.get(BASE, headers=headers(), timeout=20)
        print("REFRESH:", r.status_code)
        print("COOKIES:", list(session.cookies.get_dict().keys()))
        time.sleep(random.randint(3, 8))
    except Exception as e:
        print("REFRESH ERROR:", e)


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
        "boris bidjan saberi",
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
    try:
        r = session.get(
            API,
            headers=headers(),
            params={
                "search_text": search,
                "price_to": MAX_PRICE,
                "per_page": PER_PAGE,
                "page": 1,
                "order": "newest_first",
            },
            timeout=25
        )

        print(search, "STATUS:", r.status_code)

        if r.status_code in [401, 403, 429]:
            print("BLOCKED / LIMITED")
            refresh_cookies()
            time.sleep(300)
            return []

        if r.status_code != 200:
            print("BAD STATUS:", r.status_code, r.text[:120])
            return []

        return r.json().get("items", [])

    except Exception as e:
        print("FETCH ERROR:", e)
        return []


def main():
    print("🚀 BOT STARTED")
    send("✅ Vinted bot started")

    refresh_cookies()

    while True:
        random.shuffle(SEARCHES)

        for search in SEARCHES:
            items = fetch(search)

            for item in items:
                item_id = str(item.get("id"))

                if not item_id:
                    continue

                if item_id in seen:
                    continue

                seen.add(item_id)

                if is_bad_item(item):
                    print("SKIPPED BAD:", item.get("title"))
                    continue

                msg = format_item(item, search)

                print(msg)
                send(msg)

            delay = random.randint(MIN_DELAY, MAX_DELAY)
            print(f"SLEEP {delay}s")
            time.sleep(delay)

        long_delay = random.randint(180, 420)
        print(f"CYCLE DONE. SLEEP {long_delay}s")
        time.sleep(long_delay)


if __name__ == "__main__":
    main()
