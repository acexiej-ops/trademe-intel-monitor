import os
import requests
import json
from bs4 import BeautifulSoup

WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')
KEYWORDS = ['ryzen', 'intel', 'cpu', 'gpu', 'monitor', 'motherboard', 'laptop']
SEEN_FILE = 'seen_listings.json'

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    with open(SEEN_FILE, 'w') as f:
        json.dump(list(seen), f)

def check_keyword(keyword):
    url = 'https://www.trademe.co.nz/browse/searchresults.aspx?searchstring=' + keyword + '&sort_order=newest'
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    listings = []
    for item in soup.select('.tm-marketplace-search-card__detail-section'):
        link_el = item.select_one('a')
        if not link_el: continue
        title = link_el.get_text(strip=True)
        url_suffix = link_el.get('href', '')
        full_url = 'https://www.trademe.co.nz' + url_suffix
        listing_id = url_suffix.split('/')[-1].split('?')[0]
        listings.append({'id': listing_id, 'title': title, 'url': full_url})
    return listings

def main():
    seen = load_seen()
    new_found = False
    for kw in KEYWORDS:
        print('Checking: ' + kw)
        listings = check_keyword(kw)
        for l in listings:
            if l['id'] not in seen:
                print('New: ' + l['title'])
                msg = 'New listing for ' + kw + ': ' + l['title'] + ' - ' + l['url']
                requests.post(WEBHOOK_URL, json={'content': msg})
                seen.add(l['id'])
                new_found = True
    if new_found:
        save_seen(seen)

if __name__ == '__main__':
    main()
