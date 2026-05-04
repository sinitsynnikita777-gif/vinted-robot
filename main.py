import requests

DOMAINS = [
    "https://www.vinted.ie",
    "https://www.vinted.co.uk",
    "https://www.vinted.fr",
    "https://www.vinted.de",
    "https://www.vinted.it",
    "https://www.vinted.es",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en",
}

s = requests.Session()
s.headers.update(HEADERS)

for domain in DOMAINS:
    print("=" * 40)
    print(domain)

    try:
        home = s.get(domain, timeout=20)
        print("home:", home.status_code, home.headers.get("content-type"))
        print("cookies:", s.cookies.get_dict())

        url = f"{domain}/api/v2/catalog/items"
        params = {
            "search_text": "rick owens",
            "order": "newest_first",
            "per_page": 5,
            "page": 1,
            "price_to": 200,
        }

        r = s.get(url, params=params, timeout=20)
        print("catalog:", r.status_code, r.headers.get("content-type"))
        print("text:", r.text[:500])

    except Exception as e:
        print("error:", e)
