import requests
import json
import os
from bs4 import BeautifulSoup

KEYWORDS = ['ryzen', 'intel', 'cpu', 'gpu', 'monitor', 'motherboard', 'laptop']
FILE_NAME = 'seen_listings.json'
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

def send_discord_message(message):
    if DISCORD_WEBHOOK_URL:
        requests.post(DISCORD_WEBHOOK_URL, json={'content': message})
    else:
        print('Discord Webhook URL not set.')

def get_listings(keyword):
    url = f'https://www.trademe.co.nz/a/marketplace/computers/search?search_string={keyword}&sort_order=expirydesc'
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        listings = []
        # Find all listing cards
        for card in soup.find_all('tg-search-card-renderer'):
            link_tag = card.find('a', href=True)
            title_tag = card.find('div', class_='tm-marketplace-search-card__title')
            if link_tag and title_tag:
                listing_id = link_tag['href'].split('/')[-1].split('?')[0]
                listings.append({
                    'id': listing_id,
                    'title': title_tag.get_text(strip=True),
                    'url': 'https://www.trademe.co.nz' + link_tag['href']
                })
        return listings
    except Exception as e:
        print(f'Error fetching listings for {keyword}: {e}')
        return []

def load_seen_listings():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, 'r') as f:
            try:
                return set(json.load(f))
            except:
                return set()
    return set()

def save_seen_listings(seen_ids):
    with open(FILE_NAME, 'w') as f:
        json.dump(list(seen_ids), f)

def main():
    seen_ids = load_seen_listings()
    new_seen_ids = set(seen_ids)
    found_any_new = False

    for keyword in KEYWORDS:
        print(f'Checking keyword: {keyword}')
        listings = get_listings(keyword)
        
        for listing in listings:
            if listing['id'] not in seen_ids:
                print(f'New listing found: {listing["title"]}')
                message = f"New listing found for **{keyword}**: {listing['title']}
{listing['url']}"
                send_discord_message(message)
                new_seen_ids.add(listing['id'])
                found_any_new = True

    if found_any_new:
        save_seen_listings(new_seen_ids)
    else:
        print('No new listings found.')

if __name__ == '__main__':
    main()
