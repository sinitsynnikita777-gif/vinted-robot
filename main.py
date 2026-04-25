import time
import random
import sqlite3
import requests
from datetime import datetime, timezone
from difflib import SequenceMatcher
from urllib.parse import quote_plus

# =====================
# TELEGRAM
# =====================

BOT_TOKEN = "8714724829:AAGZ1HLaq4tRJgKCwD1Clif_3CjvYK1IFpE"
CHAT_ID = "8104561365"

def send(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": msg,
                "disable_web_page_preview": False,
            },
            timeout=15,
        )
    except Exception as e:
        print("TG ERROR:", e)


# =====================
# SETTINGS
# =====================

BASE = "https://www.vinted.co.uk"
API = "https://www.vinted.co.uk/api/v2/catalog/items"

MAX_PRICE = 150
MAX_ITEM_AGE_HOURS = 24
PER_PAGE = 12

MIN_DELAY = 45
MAX_DELAY = 115
CYCLE_DELAY_MIN = 240
CYCLE_DELAY_MAX = 600

BLOCK_SLEEP_MIN = 900
BLOCK_SLEEP_MAX = 1800

SUPER_DEAL_SCORE = 90
RESELL_SCORE = 75
PERSONAL_SCORE = 55

DB_PATH = "seen.db"

# =====================
# BRANDS + ALIASES
# =====================

BRAND_ALIASES = {
    "Insky": ["insky"],
    "Gosha Rubchinskiy": ["gosha rubchinskiy", "gosha rubchinsky", "gosha"],
    "Boris Bidjan Saberi": ["boris bidjan saberi", "boris bidjan", "bbs"],
    "Raf Simons": ["raf simons", "rafsimons", "raf"],
    "Maison Mihara Yasuhiro": ["maison mihara yasuhiro", "mihara yasuhiro", "mihara", "mmy"],
    "Helmut Lang": ["helmut lang", "helmut"],
    "1017 ALYX 9SM": ["1017 alyx 9sm", "1017 alyx", "alyx"],
    "Moon Boot": ["moon boot", "moon boots"],
    "New Rock": ["new rock"],
    "SWEAR London": ["swear london", "swear"],
    "Enfants Riches Deprimes": ["enfants riches deprimes", "enfants riches déprimés", "erd"],
    "Vetements": ["vetements", "vetement"],
    "Rick Owens": ["rick owens", "rickowens", "rick"],
    "Rick Owens DRKSHDW": ["rick owens drkshdw", "drkshdw", "darkshadow", "dark shadow"],
    "No Faith Studios": ["no faith studios", "no faith", "nfs"],
    "Attachment": ["attachment"],
    "Julius": ["julius", "julius 7"],
    "Miu Miu": ["miu miu", "miumiu"],
    "Takahiromiyashita The Soloist": ["takahiromiyashita the soloist", "the soloist", "soloist", "tts"],
    "Cav Empt": ["cav empt", "cavempt", "c.e"],
    "If Six Was Nine": ["if six was nine", "ifsixwasnine", "iswn"],
    "In The Attic": ["in the attic", "ita"],
    "West Coast Choppers": ["west coast choppers", "wcc"],
    "Hysteric Glamour": ["hysteric glamour", "hysteric", "husteric"],
    "Martine Rose": ["martine rose"],
    "Maison Margiela": ["maison margiela", "margiela", "maison martin margiela", "margeila", "margela", "margiella", "mm6"],
    "Carol Christian Poell": ["carol christian poell", "ccp"],
    "5351 Pour Les Hommes": ["5351 pour les hommes", "5351 for les hommes", "5351"],
    "Demonia Cult": ["demonia cult", "demonia"],
    "Acne Studios": ["acne studios", "acne"],
    "KMRii": ["kmrii"],
    "Le Grande Bleu": ["le grande bleu", "le grand bleu", "l.g.b.", "lgb"],
    "Jun Takahashi": ["jun takahashi"],
    "Junya Watanabe": ["junya watanabe", "junya"],
    "Kiko Kostadinov": ["kiko kostadinov", "kiko"],
    "Seditionaries": ["seditionaries"],
    "20471120": ["20471120"],
    "Tornado Mart": ["tornado mart"],
    "semanticdesign": ["semanticdesign", "semantic design"],
    "Ne-Net": ["ne-net", "nenet"],
    "Roen": ["roen"],
    "14th Addiction": ["14th addiction", "fourteenth addiction"],
    "VTMNTS": ["vtmnts"],
    "Beauty Beast": ["beauty beast", "beauty:beast"],
    "PACCBET": ["paccbet", "rassvet", "рассвет"],
    "Vivienne Westwood": ["vivienne westwood", "westwood"],
    "Balenciaga": ["balenciaga"],
}

STRONG_BRANDS = {
    "Rick Owens",
    "Rick Owens DRKSHDW",
    "Maison Margiela",
    "Raf Simons",
    "Vetements",
    "Balenciaga",
    "Boris Bidjan Saberi",
    "Carol Christian Poell",
    "Kiko Kostadinov",
    "Julius",
    "Enfants Riches Deprimes",
}

SEARCHES = list(BRAND_ALIASES.keys())

# =====================
# FILTERS
# =====================

BAD_WORDS = [
    "fake", "replica", "replica", "rep ", "reps", "ua",
    "inspired", "dupe", "custom", "bootleg",
    "not authentic", "not real", "aliexpress", "dhgate",
    "damaged", "ripped", "stains", "stained", "hole", "holes",
    "kids", "child", "junior", "youth",
]

WOMEN_WORDS = ["women", "womens", "ladies", "girl", "girls"]
UNISEX_WORDS = ["unisex", "mens", "men", "male", "oversized"]

CATEGORY_KEYWORDS = {
    "T-shirts": ["t-shirt", "tee", "shirt"],
    "Long sleeve tops": ["long sleeve", "longsleeve"],
    "Hoodies & Sweatshirts": ["hoodie", "sweatshirt", "crewneck", "zip"],
    "Knitwear & Jumpers": ["knit", "jumper", "cardigan"],
    "Jackets & Coats": ["jacket", "coat", "bomber", "puffer", "parka"],
    "Trousers": ["trousers", "pants", "cargo"],
    "Jeans": ["jeans", "denim"],
    "Shorts": ["shorts"],
    "Trainers": ["sneakers", "trainers"],
    "Boots": ["boots", "boot"],
    "Bags": ["bag", "backpack", "tote"],
    "Belts": ["belt"],
    "Hats & Caps": ["cap", "hat", "beanie"],
    "Jewellery": ["ring", "necklace", "bracelet", "jewellery", "jewelry"],
}

# =====================
# DB
# =====================

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS seen_items (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

def is_seen(item_id):
    cur.execute("SELECT id FROM seen_items WHERE id=?", (item_id,))
    return cur.fetchone() is not None

def save_seen(item_id):
    cur.execute("INSERT OR IGNORE INTO seen_items (id) VALUES (?)", (item_id,))
    conn.commit()


# =====================
# SESSION
# =====================

session = requests.Session()

USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
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
        time.sleep(random.randint(3, 8))
    except Exception as e:
        print("REFRESH ERROR:", e)


# =====================
# HELPERS
# =====================

def clean_price(price):
    if isinstance(price, dict):
        return price.get("amount", 999)
    return price or 999

def price_float(price):
    try:
        return float(clean_price(price))
    except:
        return 999

def has_any(text, words):
    text = text.lower()
    return any(w in text for w in words)

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def match_brand(item):
    text = " ".join([
        item.get("title") or "",
        item.get("description") or "",
        item.get("brand_title") or "",
    ]).lower()

    best_brand = None
    best_score = 0

    for brand, aliases in BRAND_ALIASES.items():
        for alias in aliases:
            if alias in text:
                return brand, 1.0

            score = similarity(alias, text)
            if score > best_score:
                best_score = score
                best_brand = brand

    if best_score >= 0.72:
        return best_brand, best_score

    return None, best_score

def is_collab(item):
    text = f"{item.get('title','')} {item.get('description','')}".lower()
    return " x " in text or " collab" in text or "collaboration" in text

def is_bad_item(item):
    text = f"{item.get('title','')} {item.get('description','')}".lower()

    if has_any(text, BAD_WORDS):
        return True, "bad words"

    if has_any(text, WOMEN_WORDS) and not has_any(text, UNISEX_WORDS):
        return True, "women-only"

    return False, ""

def detect_category(item):
    direct = item.get("catalog_title") or item.get("category_title")
    if direct:
        return direct

    text = f"{item.get('title','')} {item.get('description','')}".lower()

    for cat, keys in CATEGORY_KEYWORDS.items():
        if any(k in text for k in keys):
            return cat

    return "Other"

def parse_created_at(item):
    keys = ["created_at_ts", "created_at", "created_at_datetime", "photo_high_resolution_created_at"]

    for key in keys:
        val = item.get(key)

        if not val:
            continue

        if isinstance(val, int):
            return datetime.fromtimestamp(val, tz=timezone.utc)

        if isinstance(val, str):
            try:
                return datetime.fromisoformat(val.replace("Z", "+00:00"))
            except:
                pass

    return None

def age_hours(item):
    created = parse_created_at(item)
    if not created:
        return None

    return (datetime.now(timezone.utc) - created).total_seconds() / 3600

def fresh_enough(item):
    age = age_hours(item)

    if age is None:
        return True

    return age <= MAX_ITEM_AGE_HOURS

def age_text(item):
    age = age_hours(item)

    if age is None:
        return "unknown"

    if age < 1:
        return f"{int(age * 60)} min"

    return f"{round(age, 1)} h"

def price_badge(price):
    p = price_float(price)

    if p <= 50:
        return "🟢 до £50"
    if p <= 100:
        return "🟡🟡 до £100"
    return "🔴🔴🔴 до £150"

def risk_level(item, brand, market_low):
    price = price_float(item.get("price"))
    text = f"{item.get('title','')} {item.get('description','')}".lower()

    risk = 0
    reasons = []

    if brand in STRONG_BRANDS and price <= 30:
        risk += 2
        reasons.append("very cheap strong brand")

    if "no tag" in text or "missing tag" in text or "cut tag" in text:
        risk += 2
        reasons.append("tag issue")

    if market_low and price < market_low * 0.35:
        risk += 2
        reasons.append("too far below market")

    if is_collab(item):
        risk += 1
        reasons.append("collab/check legit")

    if risk >= 4:
        return "high", reasons
    if risk >= 2:
        return "medium", reasons
    return "low", reasons

def vinted_market_estimate(brand, title, current_id):
    query = f"{brand} {title}".strip()[:80]

    try:
        r = session.get(
            API,
            headers=headers(),
            params={
                "search_text": query,
                "price_to": 300,
                "per_page": 12,
                "order": "newest_first",
            },
            timeout=20,
        )

        if r.status_code != 200:
            return None, None, 0

        items = r.json().get("items", [])
        prices = []

        for item in items:
            if str(item.get("id")) == str(current_id):
                continue

            p = price_float(item.get("price"))
            if 5 <= p <= 300:
                prices.append(p)

        if len(prices) < 3:
            return None, None, len(prices)

        prices = sorted(prices)
        low = int(sum(prices[:max(2, len(prices)//2)]) / max(2, len(prices)//2))
        high = int(sum(prices) / len(prices) * 1.25)

        return low, high, len(prices)

    except Exception as e:
        print("MARKET ERROR:", e)
        return None, None, 0

def score_item(item, brand, market_low, market_high):
    price = price_float(item.get("price"))
    favs = item.get("favourite_count") or item.get("favorites_count") or 0
    category = detect_category(item)

    score = 0
    reasons = []

    if price <= 50:
        score += 30
        reasons.append("+ до £50")
    elif price <= 100:
        score += 18
        reasons.append("+ до £100")
    else:
        score += 8
        reasons.append("+ до £150")

    if brand in STRONG_BRANDS:
        score += 25
        reasons.append("+ сильный бренд")
    else:
        score += 12
        reasons.append("+ бренд из списка")

    if market_low and price < market_low * 0.7:
        score += 25
        reasons.append("+ ниже рынка")
    elif market_low and price < market_low:
        score += 14
        reasons.append("+ немного ниже рынка")
    elif market_low:
        score += 3
        reasons.append("- около рынка")

    if favs >= 10:
        score += 8
        reasons.append("+ есть интерес")
    elif favs >= 3:
        score += 4
        reasons.append("+ немного лайков")

    if category in ["Jackets & Coats", "Trousers", "Jeans", "Boots", "Trainers", "Hoodies & Sweatshirts"]:
        score += 8
        reasons.append("+ ликвидная категория")

    age = age_hours(item)
    if age is not None:
        if age <= 1:
            score += 10
            reasons.append("+ очень свежее")
        elif age <= 6:
            score += 6
            reasons.append("+ свежее")
        elif age <= 24:
            score += 2
            reasons.append("+ сегодня")

    if is_collab(item):
        score += 5
        reasons.append("+ коллаборация")

    return max(1, min(100, score)), reasons

def mode(score):
    if score >= SUPER_DEAL_SCORE:
        return "🚨 SUPER DEAL"
    if score >= RESELL_SCORE:
        return "🔥 RESELL"
    if score >= PERSONAL_SCORE:
        return "🧥 PERSONAL"
    return "👀 LOW"

def market_links(brand, title):
    q = quote_plus(f"{brand} {title}")
    return (
        f"Grailed: https://www.grailed.com/shop/{q}\n"
        f"eBay: https://www.ebay.co.uk/sch/i.html?_nkw={q}\n"
        f"Vestiaire: https://www.vestiairecollective.com/search/?q={q}\n"
        f"Depop: https://www.depop.com/search/?q={q}"
    )

def format_item(item, search, brand, score, reasons, market_low, market_high, comp_count):
    title = item.get("title", "No title")
    price = price_float(item.get("price"))
    size = item.get("size_title") or "?"
    condition = item.get("status") or item.get("status_title") or "?"
    favs = item.get("favourite_count") or item.get("favorites_count") or 0
    url = item.get("url") or f"https://www.vinted.co.uk/items/{item.get('id')}"
    category = detect_category(item)

    risk, risk_reasons = risk_level(item, brand, market_low)

    if market_low and market_high:
        market = f"£{market_low}–£{market_high}"
        profit_low = int(market_low - price)
        profit_high = int(market_high - price)
        profit = f"+£{profit_low}–£{profit_high}"
    else:
        market = "unknown"
        profit = "unknown"

    text_reasons = "\n".join(reasons[:7])
    risk_text = ", ".join(risk_reasons) if risk_reasons else "none"

    return f"""{mode(score)}
{price_badge(price)} | {score}/100

🏷 Бренд: {brand}
🔎 Поиск: {search}
👕 Вещь: {title}

💰 Цена: £{price}
📈 Рынок Vinted: {market}
💸 Потенциал: {profit}
📊 Comps: {comp_count}

⏱ Возраст: {age_text(item)}
📏 Размер: {size}
📦 Состояние: {condition}
🧩 Категория: {category}
❤️ Лайки: {favs}
⚠️ Риск: {risk}

Почему оценка:
{text_reasons}

Риск причины:
{risk_text}

🔗 {url}

Проверить рынок:
{market_links(brand, title)}
"""


# =====================
# FETCH
# =====================

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
            timeout=25,
        )

        print(search, "STATUS:", r.status_code)

        if r.status_code in [401, 403, 429]:
            sleep_time = random.randint(900, 1800)
            print("BLOCKED. SLEEP:", sleep_time)
            refresh_cookies()
            time.sleep(sleep_time)
            return []

        if r.status_code != 200:
            print("BAD:", r.status_code, r.text[:120])
            return []

        return r.json().get("items", [])

    except Exception as e:
        print("FETCH ERROR:", e)
        return []


# =====================
# MAIN
# =====================

def main():
    print("🚀 FINAL VINTED BOT STARTED")
    send("🚀 FINAL VINTED BOT STARTED")

    refresh_cookies()

    while True:
        random.shuffle(SEARCHES)

        for search in SEARCHES:
            items = fetch(search)

            for item in items:
                item_id = str(item.get("id"))

                if not item_id or is_seen(item_id):
                    continue

                save_seen(item_id)

                if not fresh_enough(item):
                    print("OLD SKIP:", item.get("title"))
                    continue

                bad, bad_reason = is_bad_item(item)
                if bad:
                    print("BAD SKIP:", bad_reason, item.get("title"))
                    continue

                brand, confidence = match_brand(item)
                if not brand:
                    print("NO BRAND:", item.get("title"))
                    continue

                market_low, market_high, comp_count = vinted_market_estimate(
                    brand,
                    item.get("title", ""),
                    item_id
                )

                s, reasons = score_item(item, brand, market_low, market_high)

                msg = format_item(
                    item,
                    search,
                    brand,
                    s,
                    reasons,
                    market_low,
                    market_high,
                    comp_count
                )

                print(msg)
                send(msg)

                time.sleep(random.randint(3, 9))

            delay = random.randint(MIN_DELAY, MAX_DELAY)
            print("SLEEP:", delay)
            time.sleep(delay)

        long_delay = random.randint(CYCLE_DELAY_MIN, CYCLE_DELAY_MAX)
        print("CYCLE DONE. SLEEP:", long_delay)
        time.sleep(long_delay)


if __name__ == "__main__":
    main()
