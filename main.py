import time
import random
import sqlite3
import requests
import re
from datetime import datetime, timezone
from dataclasses import dataclass

# ================= CONFIG =================

BOT_TOKEN = "8714724829:AAGZ1HLaq4tRJgKCwD1Clif_3CjvYK1IFpE"
CHAT_IDS = ["8104561365", "1508784719"]

DB_PATH = "seen.db"

MAX_PRICE = 150
MAX_PER_CYCLE = 35

# Freshness
MAX_ITEM_AGE_MINUTES = 60

UNKNOWN_TOP_BRAND_MAX_LIKES = 1
UNKNOWN_TOP_BRAND_MAX_POSITION = 15
UNKNOWN_TOP_BRAND_MAX_PRICE = 150

UNKNOWN_OTHER_MAX_LIKES = 1
UNKNOWN_OTHER_MAX_POSITION = 8
UNKNOWN_OTHER_MAX_PRICE = 150

# Search
MEN_CATALOG_ID = "5"
PER_PAGE = 25
LATEST_FLOW_PER_PAGE = 60
LATEST_FLOW_ENABLED = True
BRAND_SEARCH_ENABLED = True

REGIONS_PER_CYCLE = 2
OTHER_BRANDS_PER_CYCLE = 8

# Delays
SEARCH_DELAY = (7, 13)
DOMAIN_DELAY = (15, 30)
CYCLE_DELAY = (90, 180)
TELEGRAM_DELAY = (1.2, 1.8)

# Anti-ban
DOMAIN_COOLDOWN_ON_403 = (20 * 60, 45 * 60)
GLOBAL_COOLDOWN_ON_MANY_BLOCKS = (20 * 60, 40 * 60)

# Detail requests
DETAIL_ENABLED = True
DETAIL_ALLOWED_REGIONS = ["UK"]
DETAIL_MAX_POSITION = 5
DETAIL_MIN_PRE_SCORE = 78
DETAIL_DELAY = (18, 35)
DETAIL_COOLDOWN_ON_403 = (45 * 60, 90 * 60)

# ================= REGIONS =================

REGIONS = {
    "UK": {"base": "https://www.vinted.co.uk", "tier": 1, "country_codes": ["gb", "uk"]},
    "FR": {"base": "https://www.vinted.fr", "tier": 1, "country_codes": ["fr"]},
    "ES": {"base": "https://www.vinted.es", "tier": 2, "country_codes": ["es"]},
    "IT": {"base": "https://www.vinted.it", "tier": 2, "country_codes": ["it"]},
    "DE": {"base": "https://www.vinted.de", "tier": 3, "country_codes": ["de"]},
    "BE": {"base": "https://www.vinted.be", "tier": 3, "country_codes": ["be"]},
    "NL": {"base": "https://www.vinted.nl", "tier": 3, "country_codes": ["nl"]},
    "IE": {"base": "https://www.vinted.ie", "tier": 3, "country_codes": ["ie"]},
}

ALLOWED_COUNTRIES = ["gb", "uk", "ie", "fr", "es", "it", "de", "be", "nl"]

BASE_TO_REGION = {
    data["base"]: region
    for region, data in REGIONS.items()
}

# ================= SIZES =================

TOP_SIZES = ["m", "l", "xl", "48", "50", "52", "3", "4", "5"]

PANTS_W = list(range(30, 35))
PANTS_LETTER = ["m", "l"]
PANTS_EU = ["46", "48", "50", "52"]
PANTS_JP = ["3", "4", "5"]

SHOES_EU = ["42", "42.5", "43", "43.5", "44"]
SHOES_UK = ["8", "8.5", "9", "9.5", "10"]
SHOES_US = ["9", "9.5", "10", "10.5", "11"]
SHOES_JP_CM = ["27", "27.5", "28", "28.5"]

ALLOW_ONE_SIZE = True

# ================= BRANDS =================

BRANDS_MAP = {
    "Insky": ["insky"],
    "Gosha Rubchinskiy": ["gosha rubchinskiy", "gosha rubchinsky"],
    "Boris Bidjan Saberi": ["boris bidjan saberi", "boris bidjan", "bbs"],
    "Raf Simons": ["raf simons", "rafsimons"],
    "Maison Mihara Yasuhiro": ["maison mihara yasuhiro", "mihara yasuhiro", "mihara", "mmy"],
    "Helmut Lang": ["helmut lang"],
    "1017 ALYX 9SM": ["1017 alyx 9sm", "1017 alyx", "alyx"],
    "Moon Boot": ["moon boot", "moon boots"],
    "New Rock": ["new rock"],
    "SWEAR London": ["swear london"],
    "Enfants Riches Deprimes": ["enfants riches deprimes", "enfants riches déprimés"],
    "Vetements": ["vetements", "vetement"],
    "Rick Owens": ["rick owens", "rickowens", "drkshdw", "darkshadow", "dark shadow"],
    "No Faith Studios": ["no faith studios", "no faith"],
    "Attachment": ["attachment"],
    "Julius": ["julius"],
    "Miu Miu": ["miu miu", "miumiu"],
    "Takahiromiyashita The Soloist": ["takahiromiyashita the soloist", "the soloist"],
    "Cav Empt": ["cav empt", "cavempt", "ce cav empt"],
    "If Six Was Nine": ["if six was nine", "ifsixwasnine"],
    "In The Attic": ["in the attic"],
    "West Coast Choppers": ["west coast choppers"],
    "Hysteric Glamour": ["hysteric glamour"],
    "Martine Rose": ["martine rose"],
    "Maison Margiela": [
        "maison margiela",
        "margiela",
        "maison martin margiela",
        "margeila",
        "margela",
        "margiella",
        "mm6",
    ],
    "Carol Christian Poell": ["carol christian poell"],
    "5351 Pour Les Hommes": ["5351 pour les hommes", "5351 for les hommes"],
    "Demonia Cult": ["demonia cult", "demonia"],
    "Acne Studios": ["acne studios"],
    "KMRii": ["kmrii"],
    "Le Grande Bleu": ["le grande bleu", "le grand bleu"],
    "Jun Takahashi": ["jun takahashi"],
    "Junya Watanabe": ["junya watanabe"],
    "Kiko Kostadinov": ["kiko kostadinov"],
    "Seditionaries": ["seditionaries"],
    "20471120": ["20471120"],
    "Tornado Mart": ["tornado mart"],
    "semanticdesign": ["semanticdesign", "semantic design"],
    "Ne-Net": ["ne-net", "nenet"],
    "Roen": ["roen"],
    "14th Addiction": ["14th addiction", "fourteenth addiction"],
    "VTMNTS": ["vtmnts"],
    "Beauty Beast": ["beauty beast"],
    "PACCBET": ["paccbet", "rassvet"],
    "Vivienne Westwood": ["vivienne westwood"],
    "Balenciaga": ["balenciaga"],
}

TOP_BRANDS = [
    "Rick Owens",
    "Maison Margiela",
    "Raf Simons",
    "Vetements",
    "Balenciaga",
    "Acne Studios",
    "New Rock",
    "Maison Mihara Yasuhiro",
    "Helmut Lang",
    "Kiko Kostadinov",
    "Cav Empt",
    "Boris Bidjan Saberi",
    "Julius",
]

OTHER_BRANDS = [
    brand for brand in BRANDS_MAP.keys()
    if brand not in TOP_BRANDS
]

brand_queue = []

# ================= FILTER WORDS =================

BAD_WORDS = [
    "fake", "replica", "rep ", " reps", "copy", "bootleg", "ua", "mirror", "1:1",
    "not authentic", "not real", "inspired", "dupe", "aliexpress", "dhgate",
    "фейк", "реплика", "пал", "паль", "подделка", "не оригинал",
    "no tag", "no tags", "missing tag", "cut tag", "tag cut", "without tag",
    "без бирки", "нет бирки", "срезана бирка",
    "damaged", "ripped", "stains", "stained", "dirty", "poor condition",
    "hole", "holes", "destroyed", "needs repair", "flawed",
    "kids", "child", "junior", "youth", "boys", "girls",
    "vintage style", "custom", "handmade", "reworked",
]

WOMEN_WORDS = [
    "women", "womens", "woman", "ladies", "lady", "female", "femme",
    "dress", "skirt", "bra", "heels", "blouse", "crop top", "cropped",
    "mini dress", "petite", "women's fit", "female fit",
]

UNISEX_WORDS = [
    "unisex", "mens", "men", "male", "oversized", "boxy", "boyfriend fit"
]

JUNK_WORDS = [
    "book", "books", "magazine", "poster", "sticker", "cd", "dvd", "vinyl",
    "toy", "figure", "wallet", "purse", "bracelet", "necklace", "ring",
    "keyring", "keychain", "phone case", "perfume", "cosmetic", "makeup",
    "homeware", "decor", "mug", "cup", "plate", "notebook", "stationery",
]

CLOTHING_WORDS = [
    "t-shirt", "tee", "shirt", "top", "long sleeve", "hoodie", "sweatshirt",
    "crewneck", "knit", "jumper", "cardigan", "sweater", "jacket", "coat",
    "bomber", "puffer", "parka", "vest", "trousers", "pants", "cargo",
    "jeans", "denim", "shorts", "trainers", "sneakers", "boots", "shoes",
    "backpack", "rucksack", "belt",
    "sunglasses", "glasses", "eyewear", "shades", "frames", "spectacles",

    "zip", "zipper", "zip up", "half zip",
    "sweat", "pullover", "overshirt",
    "blazer", "gilet", "shell", "windbreaker",
    "leather", "fleece",
    "loafer", "derby", "sandals",
    "bag", "crossbody", "messenger", "shoulder bag",
    "cap", "beanie", "hat",
]

# ================= DATABASE =================

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cur = conn.cursor()

cur.execute("PRAGMA journal_mode=WAL")
cur.execute("PRAGMA synchronous=NORMAL")

cur.execute("""
CREATE TABLE IF NOT EXISTS seen_items (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS seen_hashes (
    hash TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()

# ================= SESSIONS =================

USER_AGENT_PROFILES = [
    {
        "name": "iphone",
        "ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 "
              "(KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1",
        "lang": "en-GB,en;q=0.9",
    },
    {
        "name": "mac_chrome",
        "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "lang": "en-GB,en;q=0.9",
    },
    {
        "name": "windows_chrome",
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "lang": "en-GB,en;q=0.9",
    },
]

@dataclass
class DomainSlot:
    region: str
    base: str
    session: requests.Session
    profile: dict
    cooldown_until: float = 0
    detail_cooldown_until: float = 0
    health: float = 1.0
    last_request_at: float = 0
    warmed: bool = False

slots = {}

def build_headers(base, profile):
    return {
        "User-Agent": profile["ua"],
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": profile["lang"],
        "Referer": base + "/",
        "Origin": base,
        "Connection": "keep-alive",
        "DNT": "1",
    }

def build_slot(region, base):
    profile = random.choice(USER_AGENT_PROFILES)
    session = requests.Session()
    session.headers.update(build_headers(base, profile))

    return DomainSlot(
        region=region,
        base=base,
        session=session,
        profile=profile,
    )

def init_slots():
    for region, data in REGIONS.items():
        slots[region] = build_slot(region, data["base"])

def refresh_slot(region):
    data = REGIONS[region]
    slots[region] = build_slot(region, data["base"])

def now_ts():
    return time.time()
# ================= BASIC HELPERS =================

def norm(x):
    return str(x or "").lower()

def clean_price(price):
    if isinstance(price, dict):
        return price.get("amount", 999)
    return price or 999

def price_float(price):
    try:
        return float(clean_price(price))
    except:
        return 999

def clean_brand_text(x):
    return re.sub(r"[^a-z0-9]+", " ", str(x or "").lower()).strip()

def has_phrase(text, phrase):
    return re.search(rf"\b{re.escape(phrase)}\b", text) is not None

def has_any(text, words):
    text = norm(text)
    return any(w in text for w in words)

def full_text(item):
    return " ".join([
        str(item.get("title") or ""),
        str(item.get("description") or ""),
        str(item.get("brand_title") or ""),
        str(item.get("size_title") or ""),
        str(item.get("status") or ""),
        str(item.get("status_title") or ""),
        str(item.get("catalog_title") or ""),
        str(item.get("category_title") or ""),
        str(item.get("catalog_path") or ""),
    ]).lower()


# ================= SEEN / DEDUP =================

def is_seen(item_id):
    cur.execute("SELECT id FROM seen_items WHERE id=?", (str(item_id),))
    return cur.fetchone() is not None

def save_seen(item_id):
    cur.execute(
        "INSERT OR IGNORE INTO seen_items (id) VALUES (?)",
        (str(item_id),)
    )
    conn.commit()

def item_hash(item):
    brand = clean_brand_text(item.get("brand"))
    title = clean_brand_text(item.get("title"))
    size = clean_brand_text(item.get("size_title"))
    price = int(price_float(item.get("price")))
    price_bucket = round(price / 5) * 5

    return f"{brand}|{title}|{size}|{price_bucket}"

def is_seen_hash(item):
    h = item_hash(item)
    cur.execute("SELECT hash FROM seen_hashes WHERE hash=?", (h,))
    return cur.fetchone() is not None

def save_seen_hash(item):
    h = item_hash(item)
    cur.execute(
        "INSERT OR IGNORE INTO seen_hashes (hash) VALUES (?)",
        (h,)
    )
    conn.commit()

def cleanup_seen():
    cur.execute("""
    DELETE FROM seen_items
    WHERE id NOT IN (
        SELECT id FROM seen_items
        ORDER BY created_at DESC
        LIMIT 15000
    )
    """)

    cur.execute("""
    DELETE FROM seen_hashes
    WHERE hash NOT IN (
        SELECT hash FROM seen_hashes
        ORDER BY created_at DESC
        LIMIT 15000
    )
    """)

    conn.commit()


# ================= BRAND DETECTION =================

def detect_brand(item):
    brand_title = clean_brand_text(item.get("brand_title"))
    title = clean_brand_text(item.get("title"))
    desc = clean_brand_text(item.get("description"))

    text = f"{brand_title} {title} {desc}"

    for brand, variants in BRANDS_MAP.items():
        brand_clean = clean_brand_text(brand)

        if brand_title == brand_clean:
            return brand

        for variant in variants:
            v = clean_brand_text(variant)

            if len(v) < 5:
                continue

            if has_phrase(text, v):
                return brand

    return None


# ================= REGION / SHIPPING =================

def item_source_region(item):
    base = item.get("source_base")
    return BASE_TO_REGION.get(base, "?")

def seller_country_code(item):
    user = item.get("user") or {}
    country = user.get("country_code") or user.get("country") or ""
    return str(country).lower()

def item_region(item):
    country = seller_country_code(item)

    if country in ["gb", "uk"]:
        return "UK"
    if country == "ie":
        return "IE"
    if country == "fr":
        return "FR"
    if country == "es":
        return "ES"
    if country == "it":
        return "IT"
    if country == "de":
        return "DE"
    if country == "be":
        return "BE"
    if country == "nl":
        return "NL"

    return item_source_region(item)

def is_shipping_ok(item):
    country = seller_country_code(item)

    if country:
        return country in ALLOWED_COUNTRIES

    return True


# ================= CATEGORY / FILTERS =================

def category(item):
    text = full_text(item)

    if any(x in text for x in [
        "sunglasses", "glasses", "eyewear",
        "shades", "frames", "spectacles"
    ]):
        return "Eyewear"

    if "backpack" in text or "rucksack" in text:
        return "Backpack"

    if "belt" in text:
        return "Belt"

    if any(x in text for x in ["bag", "crossbody", "messenger", "shoulder bag"]):
        return "Bag"

    if any(x in text for x in ["cap", "beanie", "hat"]):
        return "Hat"

    if any(x in text for x in [
        "hoodie", "sweatshirt", "zip", "zipper",
        "zip up", "half zip", "pullover", "sweat"
    ]):
        return "Hoodie/Sweatshirt"

    if any(x in text for x in [
        "jacket", "coat", "bomber", "puffer", "parka", "vest",
        "blazer", "gilet", "shell", "windbreaker", "leather", "fleece"
    ]):
        return "Outerwear"

    if any(x in text for x in ["trousers", "pants", "cargo"]):
        return "Pants"

    if "jeans" in text or "denim" in text:
        return "Jeans"

    if "boots" in text or "boot" in text:
        return "Boots"

    if any(x in text for x in [
        "sneakers", "trainers", "shoes",
        "loafer", "derby", "sandals"
    ]):
        return "Shoes"

    if any(x in text for x in [
        "shirt", "tee", "t-shirt", "top", "long sleeve", "overshirt"
    ]):
        return "Top"

    return "Clothing"

def is_fake_or_bad(item):
    return has_any(full_text(item), BAD_WORDS)

def is_women(item):
    text = full_text(item)

    catalog = " ".join([
        str(item.get("catalog_path") or ""),
        str(item.get("catalog_title") or ""),
        str(item.get("category_title") or ""),
    ]).lower()

    if any(x in catalog for x in [
        "women", "ladies", "girls", "kids", "children", "baby"
    ]):
        if not has_any(text, UNISEX_WORDS):
            return True

    if has_any(text, WOMEN_WORDS) and not has_any(text, UNISEX_WORDS):
        return True

    return False

def is_junk(item):
    return has_any(full_text(item), JUNK_WORDS)

def is_mens_clothing_or_shoes(item):
    return has_any(full_text(item), CLOTHING_WORDS)


# ================= SIZE FILTER =================

def size_ok(item):
    size = norm(item.get("size_title"))
    text = full_text(item)
    cat = category(item)

    if cat in ["Belt", "Backpack", "Eyewear"]:
        return True

    if not size:
        return False

    if ALLOW_ONE_SIZE and ("one size" in size or size == "one"):
        return True

    if cat in ["Top", "Hoodie/Sweatshirt", "Outerwear", "Clothing"]:
        return (
            size in TOP_SIZES
            or any(f" {s} " in f" {size} " for s in TOP_SIZES)
            or "oversized" in text
            or "boxy" in text
        )

    if cat in ["Pants", "Jeans"]:
        if size in PANTS_LETTER or size in PANTS_EU or size in PANTS_JP:
            return True

        for w in PANTS_W:
            if (
                size == str(w)
                or f"w{w}" in text
                or f"w {w}" in text
                or f" {w} " in f" {size} "
            ):
                return True

        return False

    if cat in ["Shoes", "Boots"]:
        if size in SHOES_EU:
            return True

        for eu in SHOES_EU:
            if f"eu {eu}" in text or f"eu{eu}" in text:
                return True

        for uk in SHOES_UK:
            if f"uk {uk}" in text or f"uk{uk}" in text:
                return True

        for us in SHOES_US:
            if f"us {us}" in text or f"us{us}" in text:
                return True

        for jp in SHOES_JP_CM:
            if f"{jp}cm" in text or f"jp {jp}" in text:
                return True

        return False

    return False


# ================= FRESHNESS =================

def parse_created_at(item):
    for key in [
        "created_at_ts",
        "created_at",
        "created_at_datetime",
        "photo_high_resolution_created_at",
        "created_at_timestamp",
        "created_at_date",
        "updated_at",
        "updated_at_ts",
    ]:
        value = item.get(key)

        if not value:
            continue

        if isinstance(value, int):
            return datetime.fromtimestamp(value, tz=timezone.utc)

        if isinstance(value, float):
            return datetime.fromtimestamp(value, tz=timezone.utc)

        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except:
                pass

    return None

def age_minutes(item):
    dt = parse_created_at(item)

    if not dt:
        return None

    return (datetime.now(timezone.utc) - dt).total_seconds() / 60

def freshness_score(item):
    age = age_minutes(item)
    likes = item.get("favourite_count") or item.get("favorites_count") or 0
    pos = item.get("pos", 999)
    brand = item.get("brand")
    source_mode = item.get("source_mode", "brand")

    if age is not None:
        if age <= 15:
            return 100
        if age <= 30:
            return 90
        if age <= 60:
            return 80
        if age <= 120:
            return 55
        return 0

    score = 0

    if source_mode == "latest":
        score += 35
    else:
        score += 20

    if pos <= 3:
        score += 35
    elif pos <= 6:
        score += 25
    elif pos <= 10:
        score += 15
    elif pos <= 15:
        score += 5

    if likes == 0:
        score += 25
    elif likes == 1:
        score += 15
    elif likes <= 3:
        score += 5

    if brand in TOP_BRANDS:
        score += 10

    return min(score, 100)

def freshness_ok(item):
    age = age_minutes(item)
    brand = item.get("brand")
    pos = item.get("pos", 999)
    likes = item.get("favourite_count") or item.get("favorites_count") or 0
    price = price_float(item.get("price"))

    if age is not None:
        return age <= MAX_ITEM_AGE_MINUTES

    if price > MAX_PRICE:
        return False

    if brand in TOP_BRANDS:
        return (
            freshness_score(item) >= 65
            and pos <= UNKNOWN_TOP_BRAND_MAX_POSITION
            and likes <= UNKNOWN_TOP_BRAND_MAX_LIKES
        )

    return (
        freshness_score(item) >= 70
        and pos <= UNKNOWN_OTHER_MAX_POSITION
        and likes <= UNKNOWN_OTHER_MAX_LIKES
    )

def freshness_text(item):
    age = age_minutes(item)
    likes = item.get("favourite_count") or item.get("favorites_count") or 0
    pos = item.get("pos", "?")
    fs = freshness_score(item)

    if age is None:
        return f"unknown, {likes} likes, Top {pos}, fresh-score {fs}"

    if age < 60:
        return f"{int(age)} min ago"

    return f"{round(age / 60, 1)}h ago"


# ================= SCORE / RISK =================

def risk(item):
    text = full_text(item)
    price = price_float(item.get("price"))
    brand = item.get("brand")

    if has_any(text, [
        "fake", "replica", "not authentic", "not real",
        "no tag", "missing tag", "cut tag", "without tag"
    ]):
        return "high"

    if brand in TOP_BRANDS and price <= 25:
        return "medium"

    if price > 120:
        return "medium"

    return "low"

def score_pre_item(item):
    score = 0

    price = price_float(item.get("price"))
    brand = item.get("brand")
    pos = item.get("pos", 999)
    title = norm(item.get("title"))
    condition = norm(item.get("status") or item.get("status_title"))
    likes = item.get("favourite_count") or item.get("favorites_count") or 0

    if price < 40:
        score += 35
    elif price < 80:
        score += 28
    elif price < 120:
        score += 20
    elif price <= 150:
        score += 12

    if brand in TOP_BRANDS:
        score += 25
    elif brand:
        score += 10

    if pos <= 3:
        score += 18
    elif pos <= 5:
        score += 14
    elif pos <= 10:
        score += 8
    elif pos <= 20:
        score += 4

    if likes == 0:
        score += 5
    elif likes <= 2:
        score += 2

    if "new" in condition:
        score += 8
    elif "very" in condition:
        score += 6
    elif "good" in condition:
        score += 3

    if any(x in title for x in ["archive", "rare", "runway", "sample"]):
        score += 6

    fs = freshness_score(item)
    if fs >= 90:
        score += 10
    elif fs >= 75:
        score += 6
    elif fs >= 60:
        score += 3

    return min(score, 100)

def score_item(item):
    score = score_pre_item(item)

    if size_ok(item):
        score += 5

    age = age_minutes(item)
    if age is not None:
        if age <= 30:
            score += 8
        elif age <= 60:
            score += 5
        elif age <= 120:
            score += 2

    return min(score, 100)

def color(score):
    if score >= 80:
        return "🟢"
    if score >= 50:
        return "🟡"
    return "🔴"

def is_meat(item):
    price = price_float(item.get("price"))
    score = item["score"]
    brand = item.get("brand")

    if brand in TOP_BRANDS and score >= 82:
        return True

    return score >= 88 or (price <= 50 and score >= 78)


# ================= TELEGRAM =================

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    for chat in CHAT_IDS:
        try:
            requests.post(
                url,
                json={
                    "chat_id": chat,
                    "text": msg,
                    "disable_web_page_preview": False,
                },
                timeout=15
            )
            time.sleep(random.uniform(*TELEGRAM_DELAY))
        except Exception as e:
            print("TG ERROR:", e)

def format_msg(item):
    prefix = "!!! MEAT | " if is_meat(item) else ""

    price = price_float(item.get("price"))
    score = item["score"]
    brand = item.get("brand") or "Unknown"
    title = item.get("title", "No title")
    size = item.get("size_title") or "?"
    condition = item.get("status") or item.get("status_title") or "?"
    pos = item.get("pos", "?")
    source_region = item_source_region(item)
    region = item_region(item)
    source_mode = item.get("source_mode", "?")

    link = item.get("url") or f"{item.get('source_base')}/items/{item.get('id')}"

    msg = f"{prefix}{color(score)} {score}/100\n\n"
    msg += f"Brand: {brand}\n"
    msg += f"Name: {title}\n\n"
    msg += f"Price: £{int(price)}\n"
    msg += f"Region: {region}\n"
    msg += f"Source: {source_region} / {source_mode}\n"
    msg += f"Size: {size}\n"
    msg += f"Condition: {condition}\n"
    msg += f"Category: {category(item)}\n"
    msg += f"Freshness: {freshness_text(item)}\n"
    msg += f"Risk: {risk(item)}\n\n"
    msg += f"Position: Top {pos}\n\n"
    msg += f"Link: {link}"

    return msg
# ================= REGION ROTATION =================

def region_weight(region):
    tier = REGIONS[region]["tier"]

    if tier == 1:
        return 6
    if tier == 2:
        return 3
    return 1


def active_regions():
    now = now_ts()
    result = []

    for region, slot in slots.items():
        if slot.cooldown_until <= now:
            result.append(region)

    return result


def choose_regions():
    available = active_regions()

    if not available:
        return []

    if len(available) <= REGIONS_PER_CYCLE:
        random.shuffle(available)
        return available

    weighted = []

    for region in available:
        weighted.extend([region] * region_weight(region))

    selected = []
    attempts = 0

    while len(selected) < REGIONS_PER_CYCLE and attempts < 80:
        r = random.choice(weighted)
        if r not in selected:
            selected.append(r)
        attempts += 1

    if len(selected) < REGIONS_PER_CYCLE:
        rest = [r for r in available if r not in selected]
        random.shuffle(rest)
        selected.extend(rest[:REGIONS_PER_CYCLE - len(selected)])

    random.shuffle(selected)
    return selected


# ================= BRAND ROTATION =================

def get_next_brands():
    global brand_queue

    if len(brand_queue) < OTHER_BRANDS_PER_CYCLE:
        brand_queue = OTHER_BRANDS[:]
        random.shuffle(brand_queue)

    selected_other = brand_queue[:OTHER_BRANDS_PER_CYCLE]
    brand_queue = brand_queue[OTHER_BRANDS_PER_CYCLE:]

    final = TOP_BRANDS[:] + selected_other
    final = list(dict.fromkeys(final))
    random.shuffle(final)

    return final


# ================= COOLDOWNS / ANTI-BAN =================

def cooldown_slot(region, reason="unknown"):
    slot = slots[region]
    cooldown = random.randint(*DOMAIN_COOLDOWN_ON_403)

    slot.cooldown_until = now_ts() + cooldown
    slot.health = max(0.1, slot.health * 0.6)
    slot.warmed = False

    print(f"DOMAIN COOLDOWN: {region} for {cooldown} sec | reason={reason}")


def cooldown_detail(region, reason="detail"):
    slot = slots[region]
    cooldown = random.randint(*DETAIL_COOLDOWN_ON_403)

    slot.detail_cooldown_until = now_ts() + cooldown
    slot.health = max(0.1, slot.health * 0.75)

    print(f"DETAIL COOLDOWN: {region} for {cooldown} sec | reason={reason}")


def global_cooldown_if_needed():
    active = active_regions()

    if len(active) >= 2:
        return

    cooldown = random.randint(*GLOBAL_COOLDOWN_ON_MANY_BLOCKS)
    print("GLOBAL COOLDOWN:", cooldown)

    time.sleep(cooldown)

    for region in REGIONS.keys():
        refresh_slot(region)


def controlled_sleep(slot, delay_range):
    lo, hi = delay_range
    gap = random.uniform(lo, hi)

    wait = max(0, slot.last_request_at + gap - now_ts())
    if wait > 0:
        time.sleep(wait)

    slot.last_request_at = now_ts()


def warmup_region(region):
    slot = slots[region]

    if slot.cooldown_until > now_ts():
        return False

    if slot.warmed:
        return True

    try:
        r = slot.session.get(slot.base + "/", timeout=25)
        print(region, "WARMUP", r.status_code)

        if r.status_code in [401, 403, 429]:
            cooldown_slot(region, f"{r.status_code} warmup")
            return False

        slot.warmed = True
        time.sleep(random.uniform(2, 5))
        return True

    except Exception as e:
        print("WARMUP ERROR:", region, e)
        return False


# ================= FETCH LATEST / SEARCH / DETAIL =================

def fetch_latest(region):
    slot = slots[region]
    base = slot.base

    if slot.cooldown_until > now_ts():
        print("SKIP BLOCKED REGION:", region)
        return []

    if not warmup_region(region):
        print("SKIP LATEST AFTER WARMUP FAIL:", region)
        return []

    controlled_sleep(slot, SEARCH_DELAY)

    url = f"{base}/api/v2/catalog/items"

    params = {
        "catalog_ids": MEN_CATALOG_ID,
        "price_to": MAX_PRICE,
        "per_page": LATEST_FLOW_PER_PAGE,
        "page": 1,
        "order": "newest_first",
    }

    try:
        r = slot.session.get(url, params=params, timeout=25)
        print(region, "LATEST", r.status_code)

        if r.status_code in [401, 403]:
            cooldown_slot(region, f"{r.status_code} latest")
            return []

        if r.status_code == 429:
            cooldown_slot(region, "429 latest")
            return []

        if r.status_code != 200:
            return []

        raw_items = r.json().get("items", [])
        items = []

        for i, item in enumerate(raw_items):
            item["pos"] = i + 1
            item["source_base"] = base
            item["source_region"] = region
            item["source_mode"] = "latest"
            items.append(item)

        slot.health = min(1.0, slot.health + 0.02)
        return items

    except Exception as e:
        print("LATEST ERROR:", region, e)
        slot.health = max(0.2, slot.health * 0.9)
        return []


def fetch_search(region, search):
    slot = slots[region]
    base = slot.base

    if slot.cooldown_until > now_ts():
        print("SKIP BLOCKED REGION:", region)
        return []

    if not warmup_region(region):
        print("SKIP SEARCH AFTER WARMUP FAIL:", region)
        return []

    controlled_sleep(slot, SEARCH_DELAY)

    url = f"{base}/api/v2/catalog/items"

    params = {
        "search_text": search,
        "catalog_ids": MEN_CATALOG_ID,
        "price_to": MAX_PRICE,
        "per_page": PER_PAGE,
        "page": 1,
        "order": "newest_first",
    }

    try:
        r = slot.session.get(url, params=params, timeout=25)
        print(region, "SEARCH", search, r.status_code)

        if r.status_code in [401, 403]:
            cooldown_slot(region, f"{r.status_code} search")
            return []

        if r.status_code == 429:
            cooldown_slot(region, "429 search")
            return []

        if r.status_code != 200:
            return []

        raw_items = r.json().get("items", [])
        items = []

        for i, item in enumerate(raw_items):
            item["pos"] = i + 1
            item["source_base"] = base
            item["source_region"] = region
            item["source_mode"] = "brand"
            items.append(item)

        slot.health = min(1.0, slot.health + 0.02)
        return items

    except Exception as e:
        print("SEARCH ERROR:", region, e)
        slot.health = max(0.2, slot.health * 0.9)
        return []


def should_fetch_detail(item):
    if not DETAIL_ENABLED:
        return False

    region = item_source_region(item)
    slot = slots.get(region)

    if not slot:
        return False

    if region not in DETAIL_ALLOWED_REGIONS:
        return False

    if slot.detail_cooldown_until > now_ts():
        return False

    if slot.cooldown_until > now_ts():
        return False

    if item.get("pos", 999) > DETAIL_MAX_POSITION:
        return False

    if item.get("score_pre", 0) < DETAIL_MIN_PRE_SCORE:
        return False

    likes = item.get("favourite_count") or item.get("favorites_count") or 0
    if likes > 3:
        return False

    return True


def fetch_item_details(item):
    region = item_source_region(item)
    slot = slots.get(region)

    if not slot:
        return item

    if not should_fetch_detail(item):
        return item

    if not warmup_region(region):
        return item

    controlled_sleep(slot, DETAIL_DELAY)

    item_id = item.get("id")
    if not item_id:
        return item

    url = f"{slot.base}/api/v2/items/{item_id}"

    try:
        r = slot.session.get(url, timeout=25)
        print(region, "DETAIL", item_id, r.status_code)

        if r.status_code in [401, 403]:
            cooldown_detail(region, f"{r.status_code} detail")
            return item

        if r.status_code == 429:
            cooldown_detail(region, "429 detail")
            return item

        if r.status_code != 200:
            return item

        data = r.json()
        details = data.get("item") or data

        if isinstance(details, dict):
            item.update(details)

        slot.health = min(1.0, slot.health + 0.02)
        return item

    except Exception as e:
        print("DETAIL ERROR:", region, e)
        slot.health = max(0.2, slot.health * 0.9)
        return item


# ================= PROCESSING =================

def process_items(collected):
    processed = []

    stats = {
        "collected": len(collected),
        "seen": 0,
        "hash_dup": 0,
        "price": 0,
        "brand": 0,
        "shipping": 0,
        "fake": 0,
        "women": 0,
        "junk": 0,
        "category": 0,
        "size": 0,
        "freshness": 0,
        "passed": 0,
    }

    for item in collected:
        item_id = str(item.get("id") or "")

        if not item_id or is_seen(item_id):
            stats["seen"] += 1
            continue

        if price_float(item.get("price")) > MAX_PRICE:
            stats["price"] += 1
            continue

        brand = detect_brand(item)
        if not brand:
            stats["brand"] += 1
            continue

        item["brand"] = brand

        if is_seen_hash(item):
            stats["hash_dup"] += 1
            continue

        if not is_shipping_ok(item):
            stats["shipping"] += 1
            continue

        if is_fake_or_bad(item):
            stats["fake"] += 1
            continue

        if is_women(item):
            stats["women"] += 1
            continue

        if is_junk(item):
            stats["junk"] += 1
            continue

        if not is_mens_clothing_or_shoes(item):
            stats["category"] += 1
            continue

        if not size_ok(item):
            stats["size"] += 1
            continue

        item["score_pre"] = score_pre_item(item)

        item = fetch_item_details(item)

        if not freshness_ok(item):
            stats["freshness"] += 1
            continue

        item["score"] = score_item(item)

        processed.append(item)
        stats["passed"] += 1

    return processed, stats


def sort_items(items):
    return sorted(
        items,
        key=lambda x: (
            x.get("pos", 999),
            -int(is_meat(x)),
            -x.get("score", 0),
            -freshness_score(x),
            random.random()
        )
    )


def send_items(items):
    sent = 0

    for item in items:
        if sent >= MAX_PER_CYCLE:
            break

        item_id = str(item.get("id") or "")

        if not item_id or is_seen(item_id):
            continue

        if is_seen_hash(item):
            continue

        save_seen(item_id)
        save_seen_hash(item)

        msg = format_msg(item)
        print(msg)
        send(msg)

        sent += 1

    return sent


# ================= MAIN LOOP =================

def run():
    print("FINAL SMART VINTED BOT STARTED")
    send("FINAL SMART VINTED BOT STARTED")

    init_slots()

    cycle = 0

    while True:
        try:
            cycle += 1

            print("\n==============================")
            print("CYCLE:", cycle)
            print("==============================")

            global_cooldown_if_needed()

            selected_regions = choose_regions()
            selected_brands = get_next_brands()

            print("REGIONS:", selected_regions)
            print("BRANDS:", selected_brands)

            if not selected_regions:
                print("NO ACTIVE REGIONS")
                time.sleep(120)
                continue

            collected = []

            for region in selected_regions:
                slot = slots[region]

                if slot.cooldown_until > now_ts():
                    print("SKIP REGION COOLDOWN:", region)
                    continue

                print("START REGION:", region)

                if not warmup_region(region):
                    print("SKIP REGION AFTER WARMUP FAIL:", region)
                    continue

                if LATEST_FLOW_ENABLED:
                    latest_items = fetch_latest(region)
                    collected.extend(latest_items)

                if BRAND_SEARCH_ENABLED:
                    for brand in selected_brands:
                        items = fetch_search(region, brand)
                        collected.extend(items)

                        if random.random() < 0.08:
                            extra = random.randint(25, 70)
                            print("BURST PAUSE:", extra)
                            time.sleep(extra)

                domain_pause = random.randint(*DOMAIN_DELAY)
                print("DOMAIN PAUSE:", domain_pause)
                time.sleep(domain_pause)

            processed, stats = process_items(collected)

            print("FILTER STATS:", stats)

            processed = sort_items(processed)
            sent = send_items(processed)

            print("CYCLE DONE. SENT:", sent)

            if cycle % 20 == 0:
                cleanup_seen()

            sleep_time = random.randint(*CYCLE_DELAY)
            print("SLEEP:", sleep_time)
            time.sleep(sleep_time)

        except KeyboardInterrupt:
            print("STOPPED BY USER")
            break

        except Exception as e:
            print("MAIN ERROR:", e)
            time.sleep(60)


if __name__ == "__main__":
    run()
