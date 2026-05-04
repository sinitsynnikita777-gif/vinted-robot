import requests
import time
import urllib.parse
from collections import Counter

DOMAINS = [
    "https://www.vinted.ie",
    "https://www.vinted.co.uk",
    "https://www.vinted.fr",
    "https://www.vinted.de",
    "https://www.vinted.it",
    "https://www.vinted.es",
    "https://www.vinted.nl",
    "https://www.vinted.be",
]

BRANDS_TO_FIND = [
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
    "Alyx",
    "Helmut Lang",
    "Vetements",
    "Cav Empt",
    "Carol Christian Poell",
    "Takahiromiyashita The Soloist",
    "Martine Rose",
    "Miu Miu",
    "No Faith Studios",
    "Enfants Riches Deprimes",
    "Gosha Rubchinskiy",
    "SWEAR London",
    "KMRii",
    "If Six Was Nine",
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
    "Carpe Diem",
    "Number (N)ine",
    "Jun Takahashi",
    "Junya Watanabe",
    "Vivienne Westwood",
    "Seditionaries",
    "Mastermind Japan",
    "Mastermind World",
    "Yasuyuki Ishii",
]

ALIASES = {
    "Rick Owens Drkshdw": ["rick owens drkshdw", "drkshdw"],
    "Maison Margiela": ["maison margiela", "margiela", "maison martin margiela"],
    "Maison Mihara Yasuhiro": ["maison mihara yasuhiro", "mihara yasuhiro", "mihara"],
    "Boris Bidjan Saberi": ["boris bidjan saberi", "boris bidjan", "bbs"],
    "Alyx": ["alyx", "1017 alyx 9sm", "1017 alyx"],
    "Carol Christian Poell": ["carol christian poell", "ccp"],
    "Takahiromiyashita The Soloist": [
        "takahiromiyashita the soloist",
        "takahiromiyashita",
        "the soloist",
        "soloist",
    ],
    "Enfants Riches Deprimes": [
        "enfants riches deprimes",
        "enfants riches déprimés",
        "erd",
    ],
    "SWEAR London": ["swear london", "swear"],
    "If Six Was Nine": ["if six was nine", "ifsixwasnine"],
    "Le Grande Bleu": ["le grande bleu", "lgb", "l.g.b."],
    "West Coast Choppers": ["west coast choppers", "wcc"],
    "semanticdesign": ["semanticdesign", "semantic design"],
    "Number (N)ine": ["number (n)ine", "number nine", "number n ine"],
    "Mastermind Japan": ["mastermind japan", "mastermind"],
    "Mastermind World": ["mastermind world", "mastermind"],
    "Vivienne Westwood": ["vivienne westwood", "vivienne", "westwood"],
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en",
}

session = requests.Session()
session.headers.update(HEADERS)


def norm(x):
    return (
        str(x or "")
        .lower()
        .replace(".", "")
        .replace("-", " ")
        .replace("_", " ")
        .replace("'", "")
        .replace("’", "")
        .strip()
    )


def get_cookie(domain):
    try:
        session.get(domain, timeout=20)
    except Exception:
        pass


def brand_search(domain, query):
    urls = [
        f"{domain}/api/v2/brands",
        f"{domain}/api/v2/brands/search",
        f"{domain}/api/v2/catalog/brands",
    ]

    results = []

    for url in urls:
        params_options = [
            {"search_text": query},
            {"query": query},
            {"q": query},
        ]

        for params in params_options:
            try:
                r = session.get(url, params=params, timeout=20)

                if r.status_code != 200:
                    continue

                data = r.json()

                if isinstance(data, dict):
                    for key in ["brands", "items", "data"]:
                        if isinstance(data.get(key), list):
                            results.extend(data[key])

                    if isinstance(data.get("brand"), dict):
                        results.append(data["brand"])

                elif isinstance(data, list):
                    results.extend(data)

            except Exception:
                continue

    return results


def catalog_search(domain, query):
    url = f"{domain}/api/v2/catalog/items"

    params = {
        "search_text": query,
        "order": "newest_first",
        "per_page": 24,
        "page": 1,
        "price_to": 200,
    }

    try:
        r = session.get(url, params=params, timeout=25)

        if r.status_code != 200:
            return []

        data = r.json()
        return data.get("items") or []

    except Exception:
        return []


def extract_brand_from_item(item):
    out = []

    brand_id = item.get("brand_id")
    brand_title = item.get("brand_title") or item.get("brand")

    if brand_id and brand_title:
        out.append({"id": brand_id, "title": brand_title})

    brand_dto = item.get("brand_dto")
    if isinstance(brand_dto, dict):
        bid = brand_dto.get("id")
        title = brand_dto.get("title") or brand_dto.get("name")
        if bid and title:
            out.append({"id": bid, "title": title})

    return out


def is_match(target, found):
    found_n = norm(found)
    aliases = [target] + ALIASES.get(target, [])

    for a in aliases:
        a_n = norm(a)

        if not a_n:
            continue

        if a_n == found_n:
            return True

        if len(a_n) >= 5 and (a_n in found_n or found_n in a_n):
            return True

    return False


def find_brand_id(brand):
    aliases = [brand] + ALIASES.get(brand, [])

    counter = Counter()
    examples = {}

    for domain in DOMAINS:
        get_cookie(domain)

        for query in aliases:
            direct = brand_search(domain, query)

            for b in direct:
                bid = b.get("id")
                title = b.get("title") or b.get("name")

                if bid and title:
                    key = (int(bid), str(title))
                    counter[key] += 3
                    examples[key] = f"{domain} direct query={query}"

            items = catalog_search(domain, query)

            for item in items:
                for b in extract_brand_from_item(item):
                    bid = b.get("id")
                    title = b.get("title")

                    if bid and title:
                        key = (int(bid), str(title))
                        counter[key] += 1
                        examples[key] = f"{domain} item query={query} title={item.get('title')}"

            time.sleep(0.4)

        time.sleep(0.8)

    matches = []

    for (bid, title), count in counter.items():
        if is_match(brand, title):
            matches.append((bid, title, count, examples.get((bid, title))))

    matches.sort(key=lambda x: x[2], reverse=True)

    if matches:
        return matches[0], matches

    fallback = counter.most_common(5)
    return None, [(bid, title, count, examples.get((bid, title))) for (bid, title), count in fallback]


def main():
    print("VINTED BRAND ID SCAN STARTED")
    print("VINTED_BRAND_IDS_TO_ADD = {")

    not_found = []

    for brand in BRANDS_TO_FIND:
        best, candidates = find_brand_id(brand)

        if best:
            bid, title, count, ex = best
            print(f'    "{brand}": {bid},  # matched {title}, score {count}')
        else:
            print(f'    # "{brand}": NOT_FOUND,')
            not_found.append((brand, candidates))

        time.sleep(1.0)

    print("}")

    if not_found:
        print("\nNOT FOUND / UNCERTAIN:")
        for brand, candidates in not_found:
            print("\n==============================")
            print("BRAND:", brand)
            for bid, title, count, ex in candidates:
                print(f'"{title}": {bid},  # score {count}')
                print(" ", ex)

    print("\nDONE")


if __name__ == "__main__":
    main()
