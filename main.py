import time
import random
import sqlite3
import requests
import re
from datetime import datetime, timezone

# ================= CONFIG =================

BOT_TOKEN = "8714724829:AAGZ1HLaq4tRJgKCwD1Clif_3CjvYK1IFpE"
CHAT_IDS = ["8104561365", "1508784719","7552373815"]

MAX_PRICE = 150

MAX_ITEM_AGE_MINUTES = 90
UNKNOWN_AGE_MAX_LIKES = 5
UNKNOWN_AGE_MAX_POSITION = 30

PER_PAGE = 30
MAX_PER_CYCLE = 40

DOMAINS_PER_CYCLE = 2
BRANDS_PER_CYCLE = 10

REQUEST_DELAY = (1.5, 3.5)
BRAND_DELAY = (3, 7)
DOMAIN_DELAY = (6, 12)
CYCLE_DELAY = (60, 120)

DOMAIN_COOLDOWN_ON_BLOCK = (600, 1200)
GLOBAL_COOLDOWN_ON_MANY_BLOCKS = (900, 1800)

DB_PATH = "seen.db"

VINTED_BASES = [
    "https://www.vinted.co.uk",
    "https://www.vinted.ie",
    "https://www.vinted.fr",
    "https://www.vinted.es",
    "https://www.vinted.be",
    "https://www.vinted.nl",
]

ALLOWED_COUNTRIES = ["gb", "uk", "ie", "fr", "es", "be", "nl"]

BASE_REGION = {
    "https://www.vinted.co.uk": "UK",
    "https://www.vinted.ie": "IE",
    "https://www.vinted.fr": "FR",
    "https://www.vinted.es": "ES",
    "https://www.vinted.be": "BE",
    "https://www.vinted.nl": "NL",
}

domain_blocked_until = {}

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
    "Maison Margiela": ["maison margiela", "margiela", "maison martin margiela", "margeila", "margela", "margiella", "mm6"],
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

TARGETED_SEARCHES = list(BRANDS_MAP.keys())
brand_queue = []

TOP_BRANDS = [
    "Rick Owens",
    "Maison Margiela",
    "Raf Simons",
    "Vetements",
    "Balenciaga",
    "Kiko Kostadinov",
    "Boris Bidjan Saberi",
    "Carol Christian Poell",
]

# ================= FILTERS =================

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
]

# ================= DATABASE =================

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
    cur.execute("SELECT id FROM seen_items WHERE id=?", (str(item_id),))
    return cur.fetchone() is not None

def save_seen(item_id):
    cur.execute("INSERT OR IGNORE INTO seen_items (id) VALUES (?)", (str(item_id),))
    conn.commit()

def cleanup_seen():
    cur.execute("""
    DELETE FROM seen_items
    WHERE id NOT IN (
        SELECT id FROM seen_items
        ORDER BY created_at DESC
        LIMIT 10000
    )
    """)
    conn.commit()

# ================= SESSION =================

session = requests.Session()

USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
]

def headers(base):
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-GB,en;q=0.9",
        "Referer": base + "/",
        "Origin": base,
        "Connection": "keep-alive",
        "DNT": "1",
    }

def refresh_cookies(base):
    try:
        r = session.get(base, headers=headers(base), timeout=20)
        print("REFRESH:", base, r.status_code)
        time.sleep(random.uniform(1, 2.5))
    except Exception as e:
        print("REFRESH ERROR:", e)

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
        except Exception as e:
            print("TG ERROR:", e)

# ================= HELPERS =================

def norm(x):
    return (x or "").lower()

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

def has_any(text, words):
    text = norm(text)
    return any(w in text for w in words)

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
    if country == "be":
        return "BE"
    if country == "nl":
        return "NL"

    return BASE_REGION.get(item.get("source_base"), "?")

def is_shipping_ok(item):
    country = seller_country_code(item)

    if country:
        return country in ALLOWED_COUNTRIES

    return True

def parse_created_at(item):
    for key in [
        "created_at_ts",
        "created_at",
        "created_at_datetime",
        "photo_high_resolution_created_at",
        "created_at_timestamp",
    ]:
        value = item.get(key)

        if not value:
            continue

        if isinstance(value, int):
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

def freshness_ok(item):
    age = age_minutes(item)
    likes = item.get("favourite_count") or item.get("favorites_count") or 0
    pos = item.get("pos", 999)

    if age is not None:
        return age <= MAX_ITEM_AGE_MINUTES

    return likes <= UNKNOWN_AGE_MAX_LIKES and pos <= UNKNOWN_AGE_MAX_POSITION

def freshness_text(item):
    age = age_minutes(item)
    likes = item.get("favourite_count") or item.get("favorites_count") or 0

    if age is None:
        return f"unknown, {likes} likes"

    if age < 60:
        return f"{int(age)} min ago"

    return f"{round(age / 60, 1)}h ago"

def is_fake_or_bad(item):
    return has_any(full_text(item), BAD_WORDS)

def is_women(item):
    text = full_text(item)

    if has_any(text, WOMEN_WORDS) and not has_any(text, UNISEX_WORDS):
        return True

    cat = norm(item.get("catalog_path") or item.get("catalog_title") or "")
    if ("women" in cat or "ladies" in cat or "girls" in cat) and not has_any(text, UNISEX_WORDS):
        return True

    return False

def is_junk(item):
    return has_any(full_text(item), JUNK_WORDS)

def is_mens_clothing_or_shoes(item):
    return has_any(full_text(item), CLOTHING_WORDS)

def category(item):
    text = full_text(item)

    if any(x in text for x in ["sunglasses", "glasses", "eyewear", "shades", "frames", "spectacles"]):
        return "Eyewear"
    if "backpack" in text or "rucksack" in text:
        return "Backpack"
    if "belt" in text:
        return "Belt"
    if "hoodie" in text or "sweatshirt" in text:
        return "Hoodie/Sweatshirt"
    if "jacket" in text or "coat" in text or "bomber" in text or "puffer" in text:
        return "Outerwear"
    if "trousers" in text or "pants" in text or "cargo" in text:
        return "Pants"
    if "jeans" in text or "denim" in text:
        return "Jeans"
    if "boots" in text or "boot" in text:
        return "Boots"
    if "sneakers" in text or "trainers" in text or "shoes" in text:
        return "Shoes"
    if "shirt" in text or "tee" in text or "t-shirt" in text or "top" in text:
        return "Top"

    return "Clothing"

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
            size in TOP_SIZES or
            any(f" {s} " in f" {size} " for s in TOP_SIZES) or
            "oversized" in text or
            "boxy" in text
        )

    if cat in ["Pants", "Jeans"]:
        if size in PANTS_LETTER or size in PANTS_EU or size in PANTS_JP:
            return True

        for w in PANTS_W:
            if size == str(w) or f"w{w}" in text or f" {w} " in f" {size} ":
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

def risk(item):
    text = full_text(item)
    price = price_float(item.get("price"))
    condition = norm(item.get("status") or item.get("status_title"))

    if has_any(text, [
        "fake", "replica", "not authentic", "not real",
        "no tag", "missing tag", "cut tag", "without tag"
    ]):
        return "high"

    if price > 120:
        return "medium"

    if "good" in condition and "very" not in condition and "new" not in condition:
        return "medium"

    return "low"

def score_item(item):
    score = 0

    price = price_float(item.get("price"))
    brand = item.get("brand")
    condition = norm(item.get("status") or item.get("status_title"))
    pos = item.get("pos", 999)
    title = norm(item.get("title"))

    if price < 50:
        score += 35
    elif price < 100:
        score += 25
    elif price <= 150:
        score += 15

    if brand in TOP_BRANDS:
        score += 20
    elif brand:
        score += 10

    if "new" in condition:
        score += 10
    elif "very" in condition:
        score += 7
    elif "good" in condition:
        score += 4

    if size_ok(item):
        score += 10

    if pos <= 5:
        score += 12
    elif pos <= 10:
        score += 8
    elif pos <= 20:
        score += 4

    if any(x in title for x in ["archive", "rare", "runway", "sample"]):
        score += 5

    likes = item.get("favourite_count") or item.get("favorites_count") or 0
    if likes == 0:
        score += 3
    elif likes <= 5:
        score += 1

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
    return score >= 90 or (price < 60 and score >= 80)

def format_msg(item):
    prefix = "!!! MEAT | " if is_meat(item) else ""

    price = price_float(item.get("price"))
    score = item["score"]
    brand = item.get("brand") or "Unknown"
    title = item.get("title", "No title")
    size = item.get("size_title") or "?"
    condition = item.get("status") or item.get("status_title") or "?"
    pos = item.get("pos", "?")
    link = item.get("url") or f"{item.get('source_base', 'https://www.vinted.co.uk')}/items/{item.get('id')}"

    msg = f"{prefix}{color(score)} {score}/100\n\n"
    msg += f"Brand: {brand}\n"
    msg += f"Name: {title}\n\n"
    msg += f"Price: £{int(price)}\n"
    msg += f"Region: {item_region(item)}\n"
    msg += f"Size: {size}\n"
    msg += f"Condition: {condition}\n"
    msg += f"Category: {category(item)}\n"
    msg += f"Freshness: {freshness_text(item)}\n"
    msg += f"Risk: {risk(item)}\n\n"
    msg += f"Position: Top {pos}\n\n"
    msg += f"Link: {link}"

    return msg

# ================= BRAND QUEUE =================

def get_next_brands():
    global brand_queue

    if len(brand_queue) < BRANDS_PER_CYCLE:
        brand_queue = TARGETED_SEARCHES[:]
        random.shuffle(brand_queue)

    selected = brand_queue[:BRANDS_PER_CYCLE]
    brand_queue = brand_queue[BRANDS_PER_CYCLE:]

    return selected

# ================= ANTI-BLOCK =================

def domain_is_blocked(base):
    until = domain_blocked_until.get(base, 0)
    return time.time() < until

def block_domain(base):
    cooldown = random.randint(*DOMAIN_COOLDOWN_ON_BLOCK)
    domain_blocked_until[base] = time.time() + cooldown
    print(f"DOMAIN COOLDOWN: {base} for {cooldown} sec")

def active_domains():
    now = time.time()
    return [
        base for base in VINTED_BASES
        if domain_blocked_until.get(base, 0) <= now
    ]

def active_domains_count():
    return len(active_domains())

def global_cooldown_if_needed():
    global session

    if active_domains_count() > 1:
        return

    sleep_time = random.randint(*GLOBAL_COOLDOWN_ON_MANY_BLOCKS)
    print("GLOBAL COOLDOWN:", sleep_time)

    session = requests.Session()
    time.sleep(sleep_time)

    for base in VINTED_BASES:
        domain_blocked_until[base] = 0
        refresh_cookies(base)

# ================= FETCH =================

def fetch_search(base, search):
    if domain_is_blocked(base):
        print("SKIP BLOCKED DOMAIN:", base)
        return []

    url = f"{base}/api/v2/catalog/items"

    params = {
        "search_text": search,
        "price_to": MAX_PRICE,
        "per_page": PER_PAGE,
        "page": 1,
        "order": "newest_first",
    }

    try:
        r = session.get(url, params=params, headers=headers(base), timeout=25)
        print(base, "SEARCH", search, r.status_code)

        if r.status_code in [401, 403, 429]:
            block_domain(base)
            refresh_cookies(base)
            return []

        if r.status_code != 200:
            return []

        raw_items = r.json().get("items", [])
        items = []

        for i, item in enumerate(raw_items):
            item["pos"] = i + 1
            item["source_base"] = base
            item["source_region"] = BASE_REGION.get(base, "?")
            items.append(item)

        return items

    except Exception as e:
        print("SEARCH ERROR:", e)
        return []

# ================= MAIN =================

def run():
    print("FINAL BRAND ROUND-ROBIN BOT STARTED")
    send("FINAL BRAND ROUND-ROBIN BOT STARTED")

    for base in VINTED_BASES:
        refresh_cookies(base)

    cycle = 0

    while True:
        try:
            cycle += 1
            global_cooldown_if_needed()

            collected = []

            bases = active_domains()
            random.shuffle(bases)
            bases = bases[:DOMAINS_PER_CYCLE]

            if not bases:
                print("NO ACTIVE DOMAINS")
                time.sleep(60)
                continue

            targeted = get_next_brands()

            for base in bases:
                for search in targeted:
                    items = fetch_search(base, search)
                    collected.extend(items)
                    time.sleep(random.uniform(*BRAND_DELAY))

                time.sleep(random.uniform(*DOMAIN_DELAY))

            processed = []

            stats = {
                "collected": len(collected),
                "seen": 0,
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
                item_id = str(item.get("id"))

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

                if not freshness_ok(item):
                    stats["freshness"] += 1
                    continue

                item["score"] = score_item(item)
                processed.append(item)
                stats["passed"] += 1

            print("FILTER STATS:", stats)

            processed.sort(
                key=lambda x: (
                    x.get("pos", 999),
                    -x["score"],
                    random.random()
                )
            )

            sent = 0

            for item in processed:
                if sent >= MAX_PER_CYCLE:
                    break

                item_id = str(item.get("id"))

                if is_seen(item_id):
                    continue

                save_seen(item_id)

                msg = format_msg(item)
                print(msg)
                send(msg)

                sent += 1
                time.sleep(random.uniform(*REQUEST_DELAY))

            if cycle % 20 == 0:
                cleanup_seen()

            sleep_time = random.randint(*CYCLE_DELAY)
            print("CYCLE DONE. SENT:", sent, "SLEEP:", sleep_time)
            time.sleep(sleep_time)

        except Exception as e:
            print("MAIN ERROR:", e)
            time.sleep(30)

if __name__ == "__main__":
    run()
