import os
import requests
import time
from dotenv import load_dotenv
from bs4 import BeautifulSoup

TOKEN = os.getenv('TOKEN')
CHAT_IDS = os.getenv('CHAT_IDS').split(",")
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

TARGETS = [{
    'url': "https://www.instant-gaming.com/en/8144-buy-steam-total-war-warhammer-iii-pc-game-steam-europe/",
    'price_target': 29
}]

def get_price_from_url( url ):
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, "html.parser")
    return float(soup.find_all("div", class_="total")[-1].get_text()[:-1])

def send_to_chat( price, url, chat_id ):
    data = {
        'chat_id': chat_id,
        'text': f'Price for {url} is now {price}!',
        'parse_mode': 'Markdown'
    }
    r = requests.post(TELEGRAM_API_URL, data=data)

def main():
    while True:
        for target in TARGETS:
            price = get_price_from_url(target['url'])
            if price <= target['price_target']:
                for chat_id in CHAT_IDS:
                    send_to_chat(price, target['url'], chat_id)
            time.sleep(120)

if __name__ == '__main__':
    main()