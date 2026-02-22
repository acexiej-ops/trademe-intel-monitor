""import requests

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
        
    except Exception as e:
        
        print(f'Error fetching listings for {keyword}: {e}')
        
        return []
        


def main():
    
    if os.path.exists(FILE_NAME):
        
        with open(FILE_NAME, 'r') as f:
            
            try:
                
                seen = json.load(f)
                
            except:
                
                seen = []
                
    else:
        
        seen = []
        


    new_seen = list(seen)
    


    for keyword in KEYWORDS:
        
        print(f'Checking keyword: {keyword}')
        
        listings = get_listings(keyword)
        
        for listing in listings:
            
            if listing['url'] not in seen:
                
                message = f"New listing found for **{keyword}**: {listing['title']}\\n{listing['url']}"
                
                send_discord_message(message)
                
                new_seen.append(listing['url'])
                


    # Keep only the last 1000 listings to prevent file growth

    with open(FILE_NAME, 'w') as f:
        
        json.dump(new_seen[-1000:], f)
        


if __name__ == '__main__':
    
    main()
    
""













































