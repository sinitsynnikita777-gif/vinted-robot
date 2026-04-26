
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

CHAT_BEST = "-1003867748419"
CHAT_PERSONAL = "-1003821333605"
CHAT_RESELL = "-1003958308581"

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

MAX_PRICE = 150
MAX_ITEM_AGE_HOURS = 2
FRESHNESS_FALLBACK_MAX_LIKES = 5
MIN_RESELL_PROFIT_PERCENT = 0.25

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

ACCESSORIES_CATEGORIES = ["Belts", "Backpacks"]


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
    "Backpacks": ["backpack", "rucksack"],
    "Belts": ["belt"],
}

LIQUID_CATEGORIES = {
    "T-shirts", "Shirts", "Long sleeve tops", "Hoodies & Sweatshirts",
    "Knitwear & Jumpers", "Jackets & Coats", "Trousers", "Jeans",
    "Shorts", "Trainers", "Boots", "Backpacks", "Belts"
}

ALLOWED_CLOTHING_WORDS = [
    "t-shirt", "tee", "shirt", "top", "long sleeve", "hoodie", "sweatshirt",
    "crewneck", "knit", "jumper", "cardigan", "sweater", "jacket", "coat",
    "bomber", "puffer", "parka", "vest", "trousers", "pants", "cargo",
    "jeans", "denim", "shorts", "trainers", "sneakers", "boots", "shoes",
    "backpack", "rucksack", "belt",
]

BLOCKED_CATEGORY_WORDS = [
    "books", "magazines", "entertainment", "home", "toys", "games",
    "beauty", "electronics", "stationery", "collectibles", "music",
    "films", "dvds", "cds", "art", "decor", "jewellery", "jewelry",
    "wallets", "purses",
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

    if "backpack" in text or "rucksack" in text or "backpack" in cat:
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
    favs = item.get("favourite_count") or item.get("favorites_count") or 0

    if age is not None:
        return age <= MAX_ITEM_AGE_HOURS

    return favs <= FRESHNESS_FALLBACK_MAX_LIKES

def freshness_text(item):
    age = age_hours(item)

    if age is None:
        favs = item.get("favourite_count") or item.get("favorites_count") or 0
        return f"unknown age, {favs} likes"

    if age < 1:
        return f"{int(age * 60)} min ago"

    return f"{round(age, 1)}h ago"


# =====================
# LABELS
# =====================

def market_confidence_label(comp_count):
    if comp_count >= 7:
        return "🟢🟢🟢 strong"
    if comp_count >= 3:
        return "🟡🟡 average"
    return "🔴 low data"

def demand_badge_label(item, category):
    favs = item.get("favourite_count") or item.get("favorites_count") or 0

    score = 0

    if favs >= 10:
        score += 2
    elif favs >= 3:
        score += 1

    if category in LIQUID_CATEGORIES:
        score += 1

    if score >= 3:
        return "🟢🟢🟢 high"
    if score >= 1:
        return "🟡🟡 decent"
    return "🔴 low"

def condition_badge_label(item):
    condition = (item.get("status") or item.get("status_title") or "").lower()

    if "new" in condition or "very good" in condition:
        return "🟢🟢🟢 good"
    if "good" in condition:
        return "🟡🟡 ok"
    return "🔴 weak"

def risk_badge_and_text(item, brand, market_low):
    price = price_float(item.get("price"))
    text = full_text(item)

    points = 0
    reasons = []

    if brand in POPULAR_BRANDS and price <= 30:
        points += 2
        reasons.append("too cheap")

    if market_low and price < market_low * 0.35:
        points += 2
        reasons.append("far below market")

    if "no tag" in text or "missing tag" in text or "cut tag" in text:
        points += 2
        reasons.append("no tags")

    if is_collab(item):
        points += 1
        reasons.append("collab")

    if points >= 4:
        return "🔴🔴🔴 high", ", ".join(reasons) or "high"
    if points >= 2:
        return "🟡🟡 medium", ", ".join(reasons) or "medium"
    return "🟢 low", "ok"


# =====================
# SIZE FILTER
# =====================

def size_match(item, category):
    size = (item.get("size_title") or "").lower()
    text = full_text(item)

    if not size:
        return "🟡 possible", "unknown"

    if category in ACCESSORIES_CATEGORIES:
        return "🟢 ideal", size

    if category in ["Backpacks"]:
        return "🟢 ideal", size

    if category in ["T-shirts", "Shirts", "Long sleeve tops", "Knitwear & Jumpers"]:
        if any(s == size or f" {s} " in f" {size} " for s in TOP_SIZES):
            return "🟢 ideal", size
        if "oversized" in text or "boxy" in text:
            return "🟡 possible", size
        return "🔴 bad", size

    if category in ["Hoodies & Sweatshirts"]:
        if any(s == size or f" {s} " in f" {size} " for s in HOODIE_SIZES):
            return "🟢 ideal", size
        if "oversized" in text or "boxy" in text:
            return "🟡 possible", size
        return "🔴 bad", size

    if category in ["Jackets & Coats"]:
        if any(s == size or f" {s} " in f" {size} " for s in OUTERWEAR_SIZES):
            return "🟢 ideal", size
        if "oversized" in text or "boxy" in text:
            return "🟡 possible", size
        return "🔴 bad", size

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

        return ("🟢 ideal" if ok else "🔴 bad"), size

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

        return ("🟢 ideal" if ok else "🔴 bad"), size

    return "🟡 possible", size


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

def estimated_profit_after_fees(price, sell_price):
    return sell_price - price - (sell_price * 0.15)

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

    if category in LIQUID_CATEGORIES:
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

def is_best_item(score, item, market_low, comp_count):
    price = price_float(item.get("price"))
    risk_badge, _ = risk_badge_and_text(item, "", market_low)

    if risk_badge.startswith("🔴"):
        return False

    if comp_count < 3:
        return False

    if score >= 90:
        return True

    if market_low and price < market_low * 0.45:
        return True

    return False

def is_personal_item(score, item):
    category = detect_category(item)
    size_badge, _ = size_match(item, category)
    return size_badge.startswith("🟢")

def is_resell_item(score, item, market_low):
    if not market_low:
        return False

    price = price_float(item.get("price"))
    min_profit = price * MIN_RESELL_PROFIT_PERCENT
    raw_profit = market_low - price

    return raw_profit >= min_profit


# =====================
# FORMATS
# =====================

def base_url(item):
    return item.get("url") or f"https://www.vinted.co.uk/items/{item.get('id')}"

def format_best_item(item, brand, score, market_low, market_high, comp_count):
    title = item.get("title", "No title")
    price = price_float(item.get("price"))
    category = detect_category(item)
    size_badge, size_value = size_match(item, category)
    risk_badge, risk_text = risk_badge_and_text(item, brand, market_low)

    market = f"£{market_low}–£{market_high}" if market_low and market_high else "unknown"

    return f"""!!! £{int(price)} | {score}/100 pts | Risk: {risk_badge}

{brand}
{title}

Market: {market} | {market_confidence_label(comp_count)} | {comp_count} comps
Size: {size_badge} ({size_value})
Freshness: {freshness_text(item)}
Risk notes: {risk_text}

{base_url(item)}
"""

def format_personal_item(item, brand, score, market_low, market_high, comp_count):
    title = item.get("title", "No title")
    price = price_float(item.get("price"))
    category = detect_category(item)
    condition = item.get("status") or item.get("status_title") or "?"
    size_badge, size_value = size_match(item, category)
    risk_badge, risk_text = risk_badge_and_text(item, brand, market_low)

    market = f"£{market_low}–£{market_high}" if market_low and market_high else "unknown"

    return f"""£{int(price)} | {score}/100 pts | Risk: {risk_badge}

{brand}
{title}

Fit: {size_badge}
Size: {size_value}
Condition: {condition_badge_label(item)} ({condition})
Market: {market} | {market_confidence_label(comp_count)}
Freshness: {freshness_text(item)}
Category: {category}

Risk notes: {risk_text}

{base_url(item)}
"""

def format_resell_item(item, brand, score, market_low, market_high, comp_count):
    title = item.get("title", "No title")
    price = price_float(item.get("price"))
    category = detect_category(item)
    condition = item.get("status") or item.get("status_title") or "?"
    size_badge, size_value = size_match(item, category)
    risk_badge, risk_text = risk_badge_and_text(item, brand, market_low)

    if market_low and market_high:
        sell_low = market_low
        sell_high = market_high
        profit_low = int(estimated_profit_after_fees(price, sell_low))
        profit_high = int(estimated_profit_after_fees(price, sell_high))
        estimated_sell = f"£{sell_low}–£{sell_high}"
        estimated_profit = f"£{profit_low}–£{profit_high} after fees"
    else:
        estimated_sell = "unknown"
        estimated_profit = "unknown"

    return f"""£{int(price)} | {score}/100 pts | Risk: {risk_badge}

{brand}
{title}

Buy price: £{int(price)}
Estimated sell: {estimated_sell}
Estimated profit: {estimated_profit}

Market confidence: {market_confidence_label(comp_count)} | {comp_count} comps
Demand: {demand_badge_label(item, category)}
Size: {size_badge} ({size_value})
Condition: {condition_badge_label(item)} ({condition})
Freshness: {freshness_text(item)}

Risk notes: {risk_text}

{base_url(item)}
"""

def format_private_item(item, brand, score, market_low, market_high, comp_count):
    title = item.get("title", "No title")
    price = price_float(item.get("price"))
    category = detect_category(item)
    condition = item.get("status") or item.get("status_title") or "?"
    size_badge, size_value = size_match(item, category)
    risk_badge, risk_text = risk_badge_and_text(item, brand, market_low)

    market = f"£{market_low}–£{market_high}" if market_low and market_high else "unknown"

    return f"""£{int(price)} | {score}/100 pts | Risk: {risk_badge}

{brand}
{title}

Market: {market} | {market_confidence_label(comp_count)} | {comp_count} comps
Demand: {demand_badge_label(item, category)}
Freshness: {freshness_text(item)}
Condition: {condition_badge_label(item)} ({condition})
Size: {size_badge} ({size_value})
Category: {category}

Risk notes: {risk_text}

{base_url(item)}
"""


# =====================
# FETCH / ROUTING / MAIN
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

def route_message(item, brand, score, market_low, market_high, comp_count):
    sent_to_channel = False

    if is_best_item(score, item, market_low, comp_count):
        send_to(CHAT_BEST, format_best_item(item, brand, score, market_low, market_high, comp_count))
        sent_to_channel = True

    if is_personal_item(score, item):
        send_to(CHAT_PERSONAL, format_personal_item(item, brand, score, market_low, market_high, comp_count))
        sent_to_channel = True

    if is_resell_item(score, item, market_low):
        send_to(CHAT_RESELL, format_resell_item(item, brand, score, market_low, market_high, comp_count))
        sent_to_channel = True

    if not sent_to_channel:
        send_private_copies(format_private_item(item, brand, score, market_low, market_high, comp_count))
    else:
        send_private_copies(format_private_item(item, brand, score, market_low, market_high, comp_count))

def main():
    print("FINAL BOT STARTED")
    send_to(CHAT_BEST, "FINAL BOT STARTED")
    send_private_copies("FINAL BOT STARTED")

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

            print(item.get("title"), score)
            route_message(item, brand, score, market_low, market_high, comp_count)

            time.sleep(random.randint(8, 20))

        long_delay = random.randint(CYCLE_DELAY_MIN, CYCLE_DELAY_MAX)
        print("CYCLE DONE. SLEEP:", long_delay)
        time.sleep(long_delay)

if __name__ == "__main__":
    main()
