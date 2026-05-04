import os
import time
import random
import sqlite3
import requests
import urllib.parse
from datetime import datetime, timezone

BOT_TOKEN = "8784534898:AAHAm1FbZBcdOr-sPuoymDTk2shYl9dHutY"
CHAT_IDS = ["8104561365"]

MAX_PRICE = 100
MAX_AGE_HOURS = 30 / 60

APP_ID = "MNRWEFSS2Q"
API_KEY = "c89dbaddf15fe70e1941a109bf7c2a3d"
INDEX = "Listing_by_date_added_production"

HITS_PER_PAGE = 80
BRAND_DELAY = (1.5, 3.0)
CYCLE_DELAY = (6, 12)
TELEGRAM_DELAY = (1.2, 2.0)

DB_PATH = "grailed_seen.db"

DESIGNER_IDS = {
    "Rick Owens": 32,
    "Rick Owens Drkshdw": 583,
    "Maison Margiela": 2308,
    "Raf Simons": 39,
    "Balenciaga": 136,
    "Acne Studios": 66,
    "Maison Mihara Yasuhiro": 39900,
    "Kiko Kostadinov": 29833,
    "Julius": 1,
    "Boris Bidjan Saberi": 632,
    "Alyx": 36568,
    "Helmut Lang": 9712,
    "Vetements": 9910,
    "Cav Empt": 50,
    "Carol Christian Poell": 114,
    "Takahiromiyashita The Soloist": 18702,
    "Martine Rose": 3594,
    "Miu Miu": 601,
    "No Faith Studios": 39724,
    "Enfants Riches Deprimes": 12908,
    "Gosha Rubchinskiy": 120,
    "SWEAR London": 968,
    "KMRii": 32317,
    "If Six Was Nine": 9612,
    "Le Grande Bleu": 10045,
    "In The Attic": 36192,
    "Tornado Mart": 31996,
    "20471120": 35991,
    "Beauty Beast": 32392,
    "Hysteric Glamour": 3442,
    "14th Addiction": 39645,
    "5351 Pour Les Hommes": 5635,
    "West Coast Choppers": 24640,
    "PACCBET": 34551,
    "semanticdesign": 40052,
    "Ne-Net": 36880,
    "Roen": 7553,
    "Carpe Diem": 1169,
    "Number (N)ine": 799,
    "Jun Takahashi": 50472,
    "Junya Watanabe": 503,
    "Vivienne Westwood": 661,
    "Seditionaries": 11757,
    "Mastermind Japan": 2296,
    "Mastermind World": 39167,
    "Yasuyuki Ishii": 27166,
}

FREQUENT_BRANDS = [
    "Rick Owens",
    "Maison Margiela",
    "Raf Simons",
    "Balenciaga",
    "Acne Studios",
    "Kiko Kostadinov",
    "Julius",
    "Boris Bidjan Saberi",
    "Helmut Lang",
    "Vetements",
    "Cav Empt",
    "Carpe Diem",
]

MEDIUM_BRANDS = [
    "Rick Owens Drkshdw",
    "Maison Mihara Yasuhiro",
    "Alyx",
    "Takahiromiyashita The Soloist",
    "Martine Rose",
    "Miu Miu",
    "No Faith Studios",
    "Enfants Riches Deprimes",
    "Gosha Rubchinskiy",
    "SWEAR London",
    "KMRii",
    "If Six Was Nine",
    "Number (N)ine",
    "Vivienne Westwood",
    "Junya Watanabe",
    "Mastermind Japan",
]

RARE_BRANDS = [
    "Carol Christian Poell",
    "Le Grande Bleu",
    "In The Attic",
    "Tornado Mart",
    "20471120",
    "Beauty Beast",
    "Hysteric Glamour",
    "14th Addiction",
    "5351 Pour Les Hommes",
    "West Coast Choppers",
    "PACCBET",
    "semanticdesign",
    "Ne-Net",
    "Roen",
    "Jun Takahashi",
    "Seditionaries",
    "Mastermind World",
    "Yasuyuki Ishii",
]

TOP_BRANDS = [
    "Rick Owens",
    "Rick Owens Drkshdw",
    "Maison Margiela",
    "Raf Simons",
    "Balenciaga",
    "Acne Studios",
    "Maison Mihara Yasuhiro",
    "Kiko Kostadinov",
    "Julius",
    "Boris Bidjan Saberi",
    "Helmut Lang",
    "Vetements",
    "Cav Empt",
    "Carol Christian Poell",
    "Carpe Diem",
    "Vivienne Westwood",
    "Junya Watanabe",
    "Mastermind Japan",
]

TOP_SIZES = [
    "m", "l", "xl",
    "medium", "large", "extra large",
    "48", "50", "52", "54", "56",
    "3", "4", "5",
]

PANTS_SIZES = [
    "30", "31", "32", "33", "34",
    "m", "l",
    "medium", "large",
    "48", "50", "52",
]

SHOE_SIZES = [
    "8.5", "9", "9.5", "10", "10.5",
    "42", "43", "44",
]

ACCESSORY_SIZES = [
    "os", "one size",
    "26", "28", "30", "32", "34",
    "36", "38", "40", "42", "44", "46",
]

FAKE_KEYWORDS = [
    "fake",
    "rep",
    "reps",
    "replica",
    "unauthentic",
    "not authentic",
    "not original",
    "1:1",
    "1 to 1",
    "mirror",
    "ua",
    "unauthorized",
    "batch",
    "best batch",
    "og batch",
    "pk batch",
    "ljr",
    "budget batch",
    "pandabuy",
    "taobao",
    "dhgate",
    "aliexpress",
    "cnfans",
    "cssbuy",
    "sugargoo",
    "weidian",
    "yupoo",
    "copy",
    "dupe",
    "duplicate",
    "inspired",
    "style",
    "similar to",
    "like rick",
    "like balenciaga",
    "like margiela",
    "like raf",
    "like vetements",
    "rick owens style",
    "balenciaga style",
    "margiela style",
    "raf simons style",
    "vetements style",
]

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS seen_items (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()


def norm(x):
    return str(x or "").lower().strip()


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
        LIMIT 30000
    )
    """)
    conn.commit()


def parse_time(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except Exception:
        return None


def age_hours(item):
    dates = [
        parse_time(item.get("created_at")),
        parse_time(item.get("bumped_at")),
        parse_time(item.get("price_updated_at")),
    ]

    dates = [d for d in dates if d]

    if not dates:
        return None

    newest = max(dates)
    return (datetime.now(timezone.utc) - newest).total_seconds() / 3600


def freshness_ok(item):
    age = age_hours(item)
    return age is not None and age <= MAX_AGE_HOURS


def freshness_text(item):
    age = age_hours(item)

    if age is None:
        return "unknown"

    if age < 1:
        return f"{int(age * 60)} min ago"

    return f"{round(age, 1)}h ago"


def price_value(item):
    try:
        return float(item.get("price_i") or item.get("price") or 999999)
    except Exception:
        return 999999


def price_ok(item):
    return price_value(item) <= MAX_PRICE


def department_ok(item):
    return norm(item.get("department")) == "menswear"


def designer_id_ok(item, expected_designer_id):
    designers = item.get("designers") or []

    for d in designers:
        try:
            if int(d.get("id")) == int(expected_designer_id):
                return True
        except Exception:
            pass

    return False


def item_text(item):
    title = norm(item.get("title"))
    desc = norm(item.get("description"))
    category = norm(item.get("category"))
    category_path = norm(item.get("category_path"))
    return f"{title} {desc} {category} {category_path}"


def fake_ok(item):
    text = item_text(item)

    for word in FAKE_KEYWORDS:
        if word in text:
            return False

    return True


def grailed_category(item):
    cat = norm(item.get("category"))
    path = norm(item.get("category_path"))
    title = norm(item.get("title"))
    text = f"{cat} {path} {title}"

    if "long sleeve" in text:
        return "Long Sleeve T-Shirts"
    if "polo" in text:
        return "Polos"
    if "button" in text or "button up" in text:
        return "Shirts (Button Ups)"
    if "short sleeve" in text or "t-shirt" in text or "tee" in text:
        return "Short Sleeve T-Shirts"
    if any(x in text for x in ["sweater", "knit", "knitwear", "cardigan", "jumper"]):
        return "Sweaters & Knitwear"
    if any(x in text for x in ["hoodie", "sweatshirt", "sweat"]):
        return "Sweatshirts & Hoodies"
    if any(x in text for x in ["tank", "sleeveless"]):
        return "Tank Tops & Sleeveless"
    if "jersey" in text:
        return "Jerseys"

    if any(x in text for x in ["casual pants", "trouser", "pants", "cargo"]):
        return "Casual Pants"
    if "cropped pants" in text:
        return "Cropped Pants"
    if "denim" in text or "jeans" in text:
        return "Denim"
    if "leggings" in text:
        return "Leggings"
    if "overalls" in text or "jumpsuit" in text:
        return "Overalls & Jumpsuits"
    if "shorts" in text:
        return "Shorts"
    if "sweatpants" in text or "joggers" in text:
        return "Sweatpants & Joggers"
    if "swimwear" in text:
        return "Swimwear"

    if "bomber" in text:
        return "Bombers"
    if "cloak" in text or "cape" in text:
        return "Cloaks & Capes"
    if "denim jacket" in text:
        return "Denim Jackets"
    if "heavy coat" in text or "coat" in text:
        return "Heavy Coats"
    if "leather jacket" in text:
        return "Leather Jackets"
    if "light jacket" in text or "jacket" in text:
        return "Light Jackets"
    if "parka" in text:
        return "Parkas"
    if "raincoat" in text:
        return "Raincoats"
    if "vest" in text:
        return "Vests"

    if "boot" in text:
        return "Boots"
    if "leather shoes" in text or "loafer" in text or "derby" in text:
        return "Casual Leather Shoes"
    if "formal shoes" in text:
        return "Formal Shoes"
    if "hi-top" in text or "high top" in text:
        return "Hi-Top Sneakers"
    if "low-top" in text or "low top" in text or "sneaker" in text:
        return "Low-Top Sneakers"
    if "sandals" in text:
        return "Sandals"
    if "slip on" in text or "slip-ons" in text:
        return "Slip Ons"

    if "bag" in text or "luggage" in text or "backpack" in text:
        return "Bags & Luggage"
    if "belt" in text:
        return "Belts"
    if "glasses" in text or "eyewear" in text:
        return "Glasses"
    if "glove" in text or "scarf" in text:
        return "Gloves & Scarves"
    if "hat" in text or "beanie" in text or "cap" in text:
        return "Hats"
    if "jewelry" in text or "watch" in text:
        return "Jewelry & Watches"
    if "wallet" in text:
        return "Wallets"
    if "periodical" in text or "magazine" in text:
        return "Periodicals"
    if "socks" in text or "underwear" in text:
        return "Socks & Underwear"
    if "sunglasses" in text:
        return "Sunglasses"
    if "tie" in text or "pocketsquare" in text:
        return "Ties & Pocketsquares"

    if "tops" in path or "tops" in cat:
        return "All Tops"
    if "bottoms" in path or "bottoms" in cat:
        return "All Bottoms"
    if "outerwear" in path or "outerwear" in cat:
        return "All Outerwear"
    if "footwear" in path or "footwear" in cat:
        return "All Footwear"
    if "accessories" in path or "accessories" in cat:
        return "All Accessories"

    return "Unknown"
def main_category(item):
    c = grailed_category(item)

    if c in [
        "Long Sleeve T-Shirts", "Polos", "Shirts (Button Ups)",
        "Short Sleeve T-Shirts", "Sweaters & Knitwear",
        "Sweatshirts & Hoodies", "Tank Tops & Sleeveless",
        "Jerseys", "All Tops",
    ]:
        return "Tops"

    if c in [
        "Casual Pants", "Cropped Pants", "Denim", "Leggings",
        "Overalls & Jumpsuits", "Shorts", "Sweatpants & Joggers",
        "Swimwear", "All Bottoms",
    ]:
        return "Bottoms"

    if c in [
        "Bombers", "Cloaks & Capes", "Denim Jackets", "Heavy Coats",
        "Leather Jackets", "Light Jackets", "Parkas", "Raincoats",
        "Vests", "All Outerwear",
    ]:
        return "Outerwear"

    if c in [
        "Boots", "Casual Leather Shoes", "Formal Shoes", "Hi-Top Sneakers",
        "Low-Top Sneakers", "Sandals", "Slip Ons", "All Footwear",
    ]:
        return "Footwear"

    if c in [
        "Bags & Luggage", "Belts", "Glasses", "Gloves & Scarves",
        "Hats", "Jewelry & Watches", "Wallets", "Miscellaneous",
        "Periodicals", "Socks & Underwear", "Sunglasses", "Supreme",
        "Ties & Pocketsquares", "All Accessories",
    ]:
        return "Accessories"

    return "Unknown"


def size_ok(item):
    size = norm(item.get("size"))
    title = norm(item.get("title"))
    cat = main_category(item)

    if cat == "Accessories":
        if not size:
            return True
        return size in ACCESSORY_SIZES or "one size" in size or size == "os"

    if not size:
        return False

    if "one size" in size or size == "os":
        return True

    if cat in ["Tops", "Outerwear"]:
        return size in TOP_SIZES or "oversized" in title or "boxy" in title

    if cat == "Bottoms":
        return size in PANTS_SIZES or any(
            f"w{x}" in title or f"w {x}" in title
            for x in PANTS_SIZES
        )

    if cat == "Footwear":
        return size in SHOE_SIZES or any(
            f"us {x}" in title or f"us{x}" in title or f"eu {x}" in title or f"eu{x}" in title
            for x in SHOE_SIZES
        )

    return False


def condition_en(item):
    raw = norm(item.get("condition"))

    mapping = {
        "is_new": "New",
        "is_gently_used": "Gently used",
        "is_used": "Used",
        "is_worn": "Worn",
    }

    return mapping.get(raw, raw or "Unknown")


def item_link(item):
    item_id = item.get("id") or item.get("objectID")
    return f"https://www.grailed.com/listings/{item_id}"


def score_item(item, brand):
    score = 0

    price = price_value(item)
    followers = int(item.get("followerno") or 0)
    age = age_hours(item)
    title = norm(item.get("title"))
    condition = condition_en(item)

    if brand in TOP_BRANDS:
        score += 30
    elif brand in FREQUENT_BRANDS:
        score += 22
    elif brand in MEDIUM_BRANDS:
        score += 16
    else:
        score += 10

    if age is not None:
        if age <= 0.05:
            score += 30
        elif age <= 0.15:
            score += 25
        elif age <= 0.30:
            score += 20
        elif age <= 0.50:
            score += 15

    if price <= 40:
        score += 25
    elif price <= 60:
        score += 22
    elif price <= 80:
        score += 18
    elif price <= 100:
        score += 14

    if followers == 0:
        score += 10
    elif followers <= 2:
        score += 7
    elif followers <= 5:
        score += 4
    elif followers <= 10:
        score += 2

    if condition == "New":
        score += 6
    elif condition == "Gently used":
        score += 4
    elif condition == "Used":
        score += 1

    if any(x in title for x in ["archive", "rare", "runway", "sample", "ss", "aw", "fw"]):
        score += 7

    if item.get("buynow"):
        score += 3

    if not fake_ok(item):
        score -= 50

    return max(0, min(score, 100))


def color(score):
    if score >= 80:
        return "🟢"
    if score >= 55:
        return "🟡"
    return "🔴"


def is_meat(item, brand):
    price = price_value(item)
    followers = int(item.get("followerno") or 0)
    age = age_hours(item)
    score = item.get("score", 0)

    if age is None:
        return False

    if brand in TOP_BRANDS and price <= 100 and followers <= 5 and age <= MAX_AGE_HOURS:
        return True

    if brand in TOP_BRANDS and score >= 85:
        return True

    return False


def item_image_url(item):
    cover = item.get("cover_photo")

    if isinstance(cover, dict):
        for key in ["url", "large_url", "medium_url", "small_url"]:
            if cover.get(key):
                return cover.get(key)

    if isinstance(cover, str):
        return cover

    photos = item.get("photos") or []

    if isinstance(photos, list) and photos:
        first = photos[0]

        if isinstance(first, dict):
            for key in ["url", "large_url", "medium_url", "small_url"]:
                if first.get(key):
                    return first.get(key)

        if isinstance(first, str):
            return first

    return None


def send_telegram(msg, item=None):
    image_url = item_image_url(item or {})
    link = item_link(item or {})

    reply_markup = {
        "inline_keyboard": [
            [
                {
                    "text": "view link",
                    "url": link,
                }
            ]
        ]
    }

    for chat_id in CHAT_IDS:
        try:
            if image_url and len(msg) <= 1024:
                r = requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                    json={
                        "chat_id": chat_id,
                        "photo": image_url,
                        "caption": msg,
                        "reply_markup": reply_markup,
                    },
                    timeout=20,
                )

            elif image_url and len(msg) > 1024:
                r = requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                    json={
                        "chat_id": chat_id,
                        "photo": image_url,
                        "caption": "photo",
                        "reply_markup": reply_markup,
                    },
                    timeout=20,
                )

                print("TG PHOTO:", r.status_code)

                r = requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": msg,
                        "disable_web_page_preview": False,
                    },
                    timeout=20,
                )

            else:
                r = requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": msg,
                        "disable_web_page_preview": False,
                        "reply_markup": reply_markup,
                    },
                    timeout=20,
                )

            print("TG:", r.status_code)
            time.sleep(random.uniform(*TELEGRAM_DELAY))

        except Exception as e:
            print("TG ERROR:", e)


def format_msg(item, brand):
    score = item["score"]
    prefix = "!!! MEAT | " if is_meat(item, brand) else ""

    msg = f"{prefix}{color(score)} {score}/100\n\n"
    msg += f"Brand: {brand}\n"
    msg += f"Name: {item.get('title')}\n\n"
    msg += f"Price: ${item.get('price_i') or item.get('price')}\n"
    msg += f"Size: {item.get('size') or '?'}\n"
    msg += f"Condition: {condition_en(item)}\n"
    msg += f"Category: {main_category(item)} → {grailed_category(item)}\n"
    msg += f"Freshness: {freshness_text(item)}\n"
    msg += f"Location: {item.get('location') or '?'}\n"
    msg += f"Seller: {item.get('user', {}).get('username', '?')}\n"
    msg += f"Followers: {item.get('followerno', 0)}\n\n"
    msg += f"Link: {item_link(item)}"

    return msg


session = requests.Session()

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "X-Algolia-Application-Id": APP_ID,
    "X-Algolia-API-Key": API_KEY,
}


def algolia_request(params):
    url = f"https://{APP_ID}-dsn.algolia.net/1/indexes/{INDEX}/query"
    payload = {"params": urllib.parse.urlencode(params)}
    return session.post(url, headers=HEADERS, json=payload, timeout=25)


def algolia_search_designer_id(brand, designer_id):
    params = {
        "query": "",
        "hitsPerPage": HITS_PER_PAGE,
        "page": 0,
        "filters": f"price_i <= {MAX_PRICE} AND designers.id:{designer_id}",
    }

    try:
        r = algolia_request(params)
        print("SEARCH DESIGNER ID", brand, designer_id, r.status_code)

        if r.status_code == 200:
            hits = r.json().get("hits", [])
            if hits:
                print("HITS", brand, len(hits), "MODE: designer_id_filter")
                return hits

        if r.status_code != 200:
            print("DESIGNER ID FILTER ERROR:", r.text[:300])

    except Exception as e:
        print("DESIGNER ID FILTER REQUEST ERROR:", brand, e)

    params = {
        "query": brand,
        "hitsPerPage": HITS_PER_PAGE,
        "page": 0,
        "filters": f"price_i <= {MAX_PRICE}",
    }

    try:
        r = algolia_request(params)
        print("SEARCH FALLBACK", brand, designer_id, r.status_code)

        if r.status_code != 200:
            print("FALLBACK ERROR:", r.text[:300])
            return []

        raw_hits = r.json().get("hits", [])
        hits = [item for item in raw_hits if designer_id_ok(item, designer_id)]

        print("HITS", brand, len(hits), "MODE: fallback_query")
        return hits

    except Exception as e:
        print("FALLBACK REQUEST ERROR:", brand, e)
        return []


def get_cycle_brands(cycle):
    brands = FREQUENT_BRANDS[:]

    if cycle % 2 == 0:
        brands += MEDIUM_BRANDS
    else:
        brands += random.sample(MEDIUM_BRANDS, min(8, len(MEDIUM_BRANDS)))

    if cycle % 3 == 0:
        brands += RARE_BRANDS
    else:
        brands += random.sample(RARE_BRANDS, min(8, len(RARE_BRANDS)))

    unique = []
    seen = set()

    for b in brands:
        if b in DESIGNER_IDS and b not in seen:
            seen.add(b)
            unique.append(b)

    return unique


def process_hits(hits, brand, designer_id):
    sent = 0

    stats = {
        "hits": len(hits),
        "seen": 0,
        "designer": 0,
        "fake": 0,
        "price": 0,
        "department": 0,
        "freshness": 0,
        "size": 0,
        "passed": 0,
        "sent": 0,
    }

    for item in hits:
        item_id = str(item.get("id") or item.get("objectID") or "")

        if not item_id or is_seen(item_id):
            stats["seen"] += 1
            continue

        if not designer_id_ok(item, designer_id):
            stats["designer"] += 1
            continue

        if not fake_ok(item):
            stats["fake"] += 1
            continue

        if not price_ok(item):
            stats["price"] += 1
            continue

        if not department_ok(item):
            stats["department"] += 1
            continue

        if not freshness_ok(item):
            stats["freshness"] += 1
            continue

        if not size_ok(item):
            stats["size"] += 1
            continue

        item["score"] = score_item(item, brand)
        stats["passed"] += 1

        save_seen(item_id)

        msg = format_msg(item, brand)
        print(msg)
        send_telegram(msg, item)

        sent += 1
        stats["sent"] += 1

        if sent >= 999:
            break

    return sent, stats


def run():
    print("GRAILED DESIGNER-ID BOT STARTED")
    send_telegram("Grailed designer-id bot started")

    cycle = 0

    while True:
        try:
            cycle += 1
            total_sent = 0

            cycle_stats = {
                "hits": 0,
                "seen": 0,
                "designer": 0,
                "fake": 0,
                "price": 0,
                "department": 0,
                "freshness": 0,
                "size": 0,
                "passed": 0,
                "sent": 0,
            }

            brands = get_cycle_brands(cycle)

            print("\n==============================")
            print("CYCLE:", cycle)
            print("BRANDS:", brands)
            print("==============================")

            for brand in brands:
                designer_id = DESIGNER_IDS[brand]
                hits = algolia_search_designer_id(brand, designer_id)
                sent, stats = process_hits(hits, brand, designer_id)

                total_sent += sent

                for k in cycle_stats:
                    cycle_stats[k] += stats.get(k, 0)

                print("FILTER STATS", brand, stats)

                time.sleep(random.uniform(*BRAND_DELAY))

            print("CYCLE FILTER STATS:", cycle_stats)
            print("CYCLE DONE. SENT:", total_sent)

            if cycle % 100 == 0:
                cleanup_seen()

            sleep_time = random.randint(*CYCLE_DELAY)
            print("SLEEP:", sleep_time)
            time.sleep(sleep_time)

        except Exception as e:
            print("MAIN ERROR:", e)
            time.sleep(60)


if __name__ == "__main__":
    run()
