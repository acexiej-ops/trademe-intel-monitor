import requests
import json
import os
from bs4 import BeautifulSoup

KEYWORDS = ['ryzen', 'intel', 'cpu', 'gpu', 'monitor', 'motherboard', 'laptop']
FILE_NAME = 'seen_listings.json'
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

def send_discord_message(message):
    if DISCORD_WEBHOOK_URL:
        try:
            requests.post(DISCORD_WEBHOOK_URL, json={'content': message})
        except Exception as e:
            print(f'Error sending to Discord: {e}')
    else:
        print('Discord Webhook URL not set.')

def get_listings(keyword):
    url = f'https://www.trademe.co.nz/a/marketplace/computers/search?search_string={keyword}&sort_order=expirydesc'
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        listings = []
        for card in soup.find_all('tg-search-card-renderer'):
            link_tag = card.find('a', href=True)
            title_tag = card.find('div', class_='tm-marketplace-search-card__title')
            if link_tag and title_tag:
                href = link_tag['href']
                listing_id = href.split('/')[-1].split('?')[0]
                listings.append({
                    'id': listing_id,
                    'title': title_tag.get_text(strip=True),
                    'url': 'https://www.trademe.co.nz' + href
                })
        return listings
    except Exception as e:
        print(f'Error fetching listings for {keyword}: {e}')
        return []

def main():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, 'r') as f:
            seen_ids = set(json.load(f))
    else:
        seen_ids = set()

    new_listings_found = False
    for keyword in KEYWORDS:
        print(f'Checking keyword: {keyword}')
        listings = get_listings(keyword)
        for listing in listings:
            if listing['id'] not in seen_ids:
                message = 'New listing found for **' + keyword + '**: ' + listing['title'] + '
' + listing['url']
                send_discord_message(message)
                seen_ids.add(listing['id'])
                new_listings_found = True

    if new_listings_found:
        with open(FILE_NAME, 'w') as f:
            json.dump(list(seen_ids), f)

if __name__ == '__main__':
    main()
