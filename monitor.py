import requests
import json
import os
from bs4 import BeautifulSoup

URL = 'https://www.trademe.co.nz/a/marketplace/computers/search?search_string=intel&sort_order=expirydesc'
FILE_NAME = 'seen_listings.json'
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

def send_discord_message(message):
    if DISCORD_WEBHOOK_URL:
        requests.post(DISCORD_WEBHOOK_URL, json={'content': message})
    else:
        print('Discord Webhook URL not set.')

def get_listings():
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    listings = []
    for card in soup.find_all('tm-marketplace-search-card-viewer')[:5]:
        title_tag = card.find('div', class_='tm-marketplace-search-card__title')
        link_tag = card.find('a', class_='tm-marketplace-search-card__link')
        if title_tag and link_tag:
            listings.append({
                'title': title_tag.get_text(strip=True),
                'url': 'https://www.trademe.co.nz' + link_tag['href']
            })
    return listings

def main():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, 'r') as f:
            seen = json.load(f)
    else:
        seen = []

    current_listings = get_listings()
    new_listings = [l for l in current_listings if l['url'] not in [s['url'] for s in seen]]

    if new_listings:
        print(f'Found {len(new_listings)} new listings!')
        for l in new_listings:
            msg = f"NEW INTEL LISTING: {l['title']} - {l['url']}"
            print(msg)
            send_discord_message(msg)
        
        seen.extend(new_listings)
        with open(FILE_NAME, 'w') as f:
            json.dump(seen[-50:], f, indent=4)
    else:
        print('No new listings found.')

if __name__ == '__main__':
    main()
