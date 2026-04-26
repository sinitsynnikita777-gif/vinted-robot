import time
import random
import sqlite3
import requests
from datetime import datetime, timezone
from difflib import SequenceMatcher

# =====================
# TELEGRAM
# =====================

BOT_TOKEN = "8714724829:AAGZ1HLaq4tRJgKCwD1Clif_3CjvYK1IFpE"

# Все / All
CHAT_ALL = "-1003867748419"

# Для себя / Personal
CHAT_PERSONAL = "-1003821333605"

# Ресейл / Resell
CHAT_RESELL = "-1003958308581"

# Личные дубли
USER_IDS = [
    "8104561365",
    "1508784719"
]


def send_to(chat_id, msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={
                "chat_id": chat_id,
                "text": msg,
                "disable_web_page_preview": False,
            },
            timeout=15
        )
    except Exception as e:
        print("TG ERROR:", e)


def send_private_copies(msg):
    for user_id in USER_IDS:
        send_to(user_id, msg)


# =====================
# SETTINGS
# =====================

BASE = "https://www.vinted.co.uk"
API = "https://www.vinted.co.uk/api/v2/catalog/items"

MAX_PRICE = 250
MAX_ITEM_AGE_HOURS = 24
PER_PAGE = 20

CYCLE_DELAY_MIN = 180
CYCLE_DELAY_MAX = 420

BLOCK_SLEEP_MIN = 900
BLOCK_SLEEP_MAX = 1800

DB_PATH = "seen.db"


# =====================
# YOUR SIZES
# =====================

TOP_SIZES = ["m", "l", "xl", "48", "50", "52", "3", "4", "5"]
OUTERWEAR_SIZES = ["m", "l", "xl", "48", "50", "52", "3", "4", "5"]
HOODIE_SIZES = ["m", "l", "xl", "48", "50", "52", "3", "4", "5"]

PANTS_W = list(range(30, 35))
PANTS_LETTER = ["m", "l"]
PANTS_EU = ["46", "48", "50", "52"]
PANTS_JP = ["3", "4", "5"]

SHOES_EU = ["42", "42.5", "43", "43.5", "44"]
SHOES_UK = ["8", "8.5", "9", "9.5", "10"]
SHOES_US = ["9", "9.5", "10", "10.5", "11"]
SHOES_JP_CM = ["27", "27.5", "28", "28.5"]

ACCESSORIES_CATEGORIES = ["Belts"]


# =====================
# BRANDS / ALIASES
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
    "New Rock": ["new rock", "nr"],
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
    "Cav Empt": ["cav empt", "cavempt", "c.e", "ce cav empt"],
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

POPULAR_BRANDS = {
    "Rick Owens", "Rick Owens DRKSHDW", "Maison Margiela", "Raf Simons",
    "Vetements", "Balenciaga", "Acne Studios", "Vivienne Westwood",
    "Kiko Kostadinov", "Boris Bidjan Saberi", "Carol Christian Poell",
}

SEARCHES = list(BRAND_ALIASES.keys())


# =====================
# FILTERS
# =====================

BAD_WORDS = [
    "fake", "replica", "rep ", " reps", "ua",
    "inspired", "dupe", "custom", "customised", "customized",
    "bootleg", "not authentic", "not real", "aliexpress", "dhgate",
    "damaged", "ripped", "stains", "stained", "dirty", "poor condition",
    "hole", "holes", "destroyed", "needs repair", "flawed",
    "no tag", "no tags", "cut tag", "missing tag", "tag cut",
    "kids", "child", "junior", "youth", "boys", "girls",
    "women's fit", "female fit", "slim fit women",
    "petite", "uk 6", "uk 8", "uk 10",
]

JUNK_WORDS = [
    "book", "books", "magazine", "magazines", "poster", "posters",
    "sticker", "stickers", "cd", "dvd", "vinyl", "record",
    "toy", "toys", "figure", "figurine", "collectible", "collectibles",
    "wallet", "wallets", "purse", "bracelet", "necklace", "ring",
    "keyring", "keychain", "phone case", "case", "perfume",
    "cosmetic", "makeup", "homeware", "decor", "decoration",
    "mug", "cup", "plate", "calendar", "notebook", "stationery",
    "pin badge", "badge", "patch", "cards", "card",
]

WOMEN_WORDS = [
    "women", "womens", "woman", "ladies", "lady",
    "girl", "girls", "female", "femme",
    "dress", "skirt", "bra", "heels", "blouse",
    "crop top", "cropped", "mini dress"
]

UNISEX_WORDS = [
    "unisex", "mens", "men", "male", "oversized",
    "boxy", "boyfriend fit"
]

CATEGORY_KEYWORDS = {
    "T-shirts": ["t-shirt", "tee", "graphic tee"],
    "Shirts": ["shirt", "button up", "button-up"],
    "Long sleeve tops": ["long sleeve", "longsleeve", "ls tee"],
    "Hoodies & Sweatshirts": ["hoodie", "sweatshirt", "crewneck", "zip hoodie"],
    "Knitwear & Jumpers": ["knit", "jumper", "cardigan", "sweater"],
    "Jackets & Coats": ["jacket", "coat", "bomber", "puffer", "parka", "vest"],
    "Trousers": ["trousers", "pants", "cargo", "slacks"],
    "Jeans": ["jeans", "denim"],
    "Shorts": ["shorts"],
    "Trainers": ["sneakers", "trainers"],
    "Boots": ["boots", "boot"],
    "Belts": ["belt"],
}

GOOD_CATEGORIES = {
    "Jackets & Coats", "Trousers", "Jeans", "Boots",
    "Trainers", "Hoodies & Sweatshirts", "Knitwear & Jumpers"
}

ALLOWED_CLOTHING_WORDS = [
    "t-shirt", "tee", "shirt", "top", "long sleeve", "hoodie", "sweatshirt",
    "crewneck", "knit", "jumper", "cardigan", "sweater", "jacket", "coat",
    "bomber", "puffer", "parka", "vest", "trousers", "pants", "cargo",
    "jeans", "denim", "shorts", "trainers", "sneakers", "boots", "shoes",
    "belt",
]

BLOCKED_CATEGORY_WORDS = [
    "books", "magazines", "entertainment", "home", "toys", "games",
    "beauty", "electronics", "stationery", "collectibles", "music",
    "films", "dvds", "cds", "art", "decor", "jewellery", "jewelry",
    "bags", "wallets", "purses", "accessories",
]


# =====================
# DATABASE
# =====================

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
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
# SESSION / ANTIBAN
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

def full_text(item):
    return " ".join([
        item.get("title") or "",
        item.get("description") or "",
        item.get("brand_title") or "",
        item.get("size_title") or "",
        item.get("status") or "",
        item.get("status_title") or "",
        item.get("catalog_title") or "",
        item.get("category_title") or "",
        item.get("catalog_path") or "",
    ]).lower()

def category_text(item):
    return " ".join([
        str(item.get("catalog_title") or ""),
        str(item.get("category_title") or ""),
        str(item.get("catalog_path") or ""),
    ]).lower()

def clean_price(price):
    if isinstance(price, dict):
        return price.get("amount", 999)
    return price or 999

def price_float(price):
    try:
        return float(clean_price(price))
    except:
        return 999

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def has_any(text, words):
    return any(w in text.lower() for w in words)

def match_brand(item):
    text = full_text(item)

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
    text = full_text(item)
    return " x " in text or " collab" in text or "collaboration" in text

def is_allowed_fashion_item(item):
    text = full_text(item)
    cat = category_text(item)

    if "belt" in text or "belt" in cat:
        return True

    if any(word in cat for word in BLOCKED_CATEGORY_WORDS):
        return False

    if has_any(text, JUNK_WORDS):
        return False

    if any(word in text for word in ALLOWED_CLOTHING_WORDS):
        return True

    if any(word in cat for word in ALLOWED_CLOTHING_WORDS):
        return True

    size = (item.get("size_title") or "").lower()
    if size in ["xs", "s", "m", "l", "xl", "xxl"] or size.startswith("w"):
        return True

    return False

def is_bad_item(item):
    text = full_text(item)
    cat = category_text(item)

    if has_any(text, BAD_WORDS):
        return True

    if has_any(text, JUNK_WORDS):
        return True

    if has_any(text, WOMEN_WORDS) and not has_any(text, UNISEX_WORDS):
        return True

    if ("women" in cat or "ladies" in cat or "girls" in cat) and not has_any(text, UNISEX_WORDS):
        return True

    if not is_allowed_fashion_item(item):
        return True

    title = item.get("title") or ""
    if len(title.strip()) < 5:
        return True

    return False

def detect_category(item):
    direct = item.get("catalog_title") or item.get("category_title")
    if direct:
        return direct

    text = full_text(item)

    for cat, keys in CATEGORY_KEYWORDS.items():
        if any(k in text for k in keys):
            return cat

    return "Other"

def parse_created_at(item):
    for key in [
        "created_at_ts",
        "created_at",
        "created_at_datetime",
        "photo_high_resolution_created_at",
        "created_at_timestamp"
    ]:
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

def freshness_text(item):
    age = age_hours(item)

    if age is None:
        return "newest search / новый поиск"

    if age < 1:
        minutes = int(age * 60)
        return f"{minutes} min ago / {minutes} мин назад"

    hours = round(age, 1)
    return f"{hours}h ago / {hours} ч назад"


# =====================
# LABELS
# =====================

def market_confidence_label(comp_count):
    if comp_count >= 7:
        return "🟢🟢🟢 strong / сильный"
    if comp_count >= 3:
        return "🟡🟡 average / средний"
    return "🔴 low data / мало данных"

def demand_badge_label(item, category):
    favs = item.get("favourite_count") or item.get("favorites_count") or 0

    score = 0

    if favs >= 10:
        score += 2
    elif favs >= 3:
        score += 1

    if category in GOOD_CATEGORIES:
        score += 1

    if score >= 3:
        return "🟢🟢🟢 high / высокий"
    if score >= 1:
        return "🟡🟡 decent / норм"
    return "🔴 low / слабый"

def condition_badge_label(item):
    condition = (item.get("status") or item.get("status_title") or "").lower()

    if "new" in condition or "very good" in condition:
        return "🟢🟢🟢 good / хорошее"
    if "good" in condition:
        return "🟡🟡 ok / норм"
    return "🔴 weak / слабое"

def risk_badge_and_text(item, brand, market_low):
    price = price_float(item.get("price"))
    text = full_text(item)

    points = 0
    reasons = []

    if brand in POPULAR_BRANDS and price <= 30:
        points += 2
        reasons.append("too cheap / очень дешево")

    if market_low and price < market_low * 0.35:
        points += 2
        reasons.append("far below market / сильно ниже рынка")

    if "no tag" in text or "missing tag" in text or "cut tag" in text:
        points += 2
        reasons.append("no tags / нет бирок")

    if is_collab(item):
        points += 1
        reasons.append("collab / коллаборация")

    if points >= 4:
        return "🔴🔴🔴 high / высокий", ", ".join(reasons) or "high / высокий"
    if points >= 2:
        return "🟡🟡 medium / средний", ", ".join(reasons) or "medium / средний"
    return "🟢 low / низкий", "ok / ок"


# =====================
# SIZE FILTER
# =====================

def size_match(item, category):
    size = (item.get("size_title") or "").lower()
    text = full_text(item)

    if not size:
        return "🟡 possible / возможно", "unknown"

    if category in ACCESSORIES_CATEGORIES:
        return "🟢 ideal / подходит", size

    if category in ["T-shirts", "Shirts", "Long sleeve tops", "Knitwear & Jumpers"]:
        if any(s == size or f" {s} " in f" {size} " for s in TOP_SIZES):
            return "🟢 ideal / подходит", size
        if "oversized" in text or "boxy" in text:
            return "🟡 possible / возможно", size
        return "🔴 bad / не твой", size

    if category in ["Hoodies & Sweatshirts"]:
        if any(s == size or f" {s} " in f" {size} " for s in HOODIE_SIZES):
            return "🟢 ideal / подходит", size
        if "oversized" in text or "boxy" in text:
            return "🟡 possible / возможно", size
        return "🔴 bad / не твой", size

    if category in ["Jackets & Coats"]:
        if any(s == size or f" {s} " in f" {size} " for s in OUTERWEAR_SIZES):
            return "🟢 ideal / подходит", size
        if "oversized" in text or "boxy" in text:
            return "🟡 possible / возможно", size
        return "🔴 bad / не твой", size

    if category in ["Trousers", "Jeans", "Shorts"]:
        ok = False

        for w in PANTS_W:
            if f"w{w}" in text or f" {w} " in f" {size} " or size == str(w):
                ok = True

        if any(s == size or f" {s} " in f" {size} " for s in PANTS_LETTER):
            ok = True

        if any(eu in size for eu in PANTS_EU):
            ok = True

        if any(jp == size for jp in PANTS_JP):
            ok = True

        return ("🟢 ideal / подходит" if ok else "🔴 bad / не твой"), size

    if category in ["Trainers", "Boots"]:
        ok = False

        for eu in SHOES_EU:
            if f"eu {eu}" in text or f"eu{eu}" in text or str(eu) == size:
                ok = True

        for uk in SHOES_UK:
            if f"uk {uk}" in text or f"uk{uk}" in text:
                ok = True

        for us in SHOES_US:
            if f"us {us}" in text or f"us{us}" in text:
                ok = True

        for jp in SHOES_JP_CM:
            if f"{jp}cm" in text or f"jp {jp}" in text:
                ok = True

        return ("🟢 ideal / подходит" if ok else "🔴 bad / не твой"), size

    return "🟡 possible / возможно", size


# =====================
# MARKET / SCORE
# =====================

def fetch_item_details(item_id):
    try:
        r = session.get(
            f"https://www.vinted.co.uk/api/v2/items/{item_id}",
            headers=headers(),
            timeout=20
        )

        if r.status_code != 200:
            return None

        data = r.json()
        return data.get("item") or data

    except Exception as e:
        print("DETAIL ERROR:", e)
        return None

def vinted_market_estimate(brand, title, current_id):
    query = f"{brand} {title}".strip()[:80]

    try:
        r = session.get(
            API,
            headers=headers(),
            params={
                "search_text": query,
                "price_to": 350,
                "per_page": 16,
                "order": "newest_first",
            },
            timeout=20,
        )

        if r.status_code != 200:
            return None, None, 0

        prices = []

        for item in r.json().get("items", []):
            if str(item.get("id")) == str(current_id):
                continue

            if is_bad_item(item):
                continue

            p = price_float(item.get("price"))
            if 5 <= p <= 350:
                prices.append(p)

        if len(prices) < 3:
            return None, None, len(prices)

        prices = sorted(prices)
        half = max(2, len(prices) // 2)

        low = int(sum(prices[:half]) / half)
        high = int((sum(prices) / len(prices)) * 1.25)

        return low, high, len(prices)

    except Exception as e:
        print("MARKET ERROR:", e)
        return None, None, 0

def score_item(item, brand, market_low, comp_count):
    price = price_float(item.get("price"))
    category = detect_category(item)
    favs = item.get("favourite_count") or item.get("favorites_count") or 0

    score = 0

    if price <= 50:
        score += 30
    elif price <= 100:
        score += 22
    elif price <= 150:
        score += 14
    else:
        score += 6

    score += 15

    if brand in POPULAR_BRANDS:
        score += 7

    if market_low and price < market_low * 0.7:
        score += 25
    elif market_low and price < market_low:
        score += 14
    elif market_low:
        score += 4

    if comp_count >= 7:
        score += 8
    elif comp_count >= 3:
        score += 4

    if favs == 0:
        score -= 5
    elif favs >= 5:
        score += 6
    elif favs >= 3:
        score += 4

    if category in GOOD_CATEGORIES:
        score += 7

    if is_collab(item):
        score += 4

    size_badge, _ = size_match(item, category)
    if size_badge.startswith("🟢"):
        score += 5
    elif size_badge.startswith("🟡"):
        score += 1
    elif size_badge.startswith("🔴"):
        score -= 8

    return max(1, min(100, score))

def super_signal(score, item, market_low):
    price = price_float(item.get("price"))

    if score >= 88:
        return True

    if market_low and price < market_low * 0.50:
        return True

    return False

def is_personal_item(score, item):
    category = detect_category(item)
    size_badge, _ = size_match(item, category)
    return size_badge.startswith("🟢") and score >= 55

def is_resell_item(score, item, market_low):
    price = price_float(item.get("price"))

    if super_signal(score, item, market_low):
        return True

    if not market_low:
        return False

    return (market_low - price >= 30) and score >= 60


# =====================
# FORMAT
# =====================

def format_item(item, search, brand, score, market_low, market_high, comp_count, vip=False):
    title = item.get("title", "No title")
    price = price_float(item.get("price"))
    condition = item.get("status") or item.get("status_title") or "?"
    url = item.get("url") or f"https://www.vinted.co.uk/items/{item.get('id')}"
    category = detect_category(item)

    risk_badge, risk_text = risk_badge_and_text(item, brand, market_low)
    size_badge, size_value = size_match(item, category)

    if market_low and market_high:
        market = f"£{market_low}–£{market_high}"
    else:
        market = "unknown / неизвестно"

    prefix = "!!! " if vip else ""

    return f"""{prefix}£{int(price)} | {score}/100 pts | Risk / Риск: {risk_badge}

{brand}
{title}

Market / Рынок: {market} | {market_confidence_label(comp_count)} | {comp_count} comps
Demand / Спрос: {demand_badge_label(item, category)}

Freshness / Свежесть: {freshness_text(item)}
Condition / Состояние: {condition_badge_label(item)} ({condition})
Size / Размер: {size_badge} ({size_value})
Category / Категория: {category}

Risk notes / Риск-факторы: {risk_text}

{url}
"""


# =====================
# FETCH / MAIN
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
            sleep_time = random.randint(BLOCK_SLEEP_MIN, BLOCK_SLEEP_MAX)
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

def route_message(item, score, market_low, msg):
    sent = False

    if is_resell_item(score, item, market_low):
        send_to(CHAT_RESELL, msg)
        sent = True

    if is_personal_item(score, item):
        send_to(CHAT_PERSONAL, msg)
        sent = True

    # Все / All — всё, что прошло фильтры
    send_to(CHAT_ALL, msg)

    # Личные дубли тебе и другу
    send_private_copies(msg)

    return sent

def main():
    print("FINAL FULL BOT STARTED")
    send_to(CHAT_ALL, "FINAL FULL BOT STARTED")
    send_private_copies("FINAL FULL BOT STARTED")

    refresh_cookies()

    while True:
        random.shuffle(SEARCHES)

        collected_items = []

        for search in SEARCHES:
            items = fetch(search)

            for item in items:
                collected_items.append((search, item))

            time.sleep(random.randint(8, 18))

        random.shuffle(collected_items)

        for search, item in collected_items:
            item_id = str(item.get("id"))

            if not item_id or is_seen(item_id):
                continue

            save_seen(item_id)

            details = fetch_item_details(item_id)
            if details:
                item.update(details)

            if not fresh_enough(item):
                continue

            if is_bad_item(item):
                print("SKIP WOMEN/JUNK:", item.get("title"))
                continue

            brand, confidence = match_brand(item)
            if not brand:
                continue

            market_low, market_high, comp_count = vinted_market_estimate(
                brand,
                item.get("title", ""),
                item_id
            )

            score = score_item(item, brand, market_low, comp_count)
            is_vip = super_signal(score, item, market_low)

            msg = format_item(
                item,
                search,
                brand,
                score,
                market_low,
                market_high,
                comp_count,
                vip=is_vip
            )

            print(msg)
            route_message(item, score, market_low, msg)

            time.sleep(random.randint(8, 20))

        long_delay = random.randint(CYCLE_DELAY_MIN, CYCLE_DELAY_MAX)
        print("CYCLE DONE. SLEEP:", long_delay)
        time.sleep(long_delay)


if __name__ == "__main__":
    main()
