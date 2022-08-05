import os
import requests
import time
import sys
import logging
from dotenv import load_dotenv
from bs4 import BeautifulSoup

TOKEN = os.getenv('TOKEN')
CHAT_IDS = os.getenv('CHAT_IDS').split(",")
LOG_LEVEL = os.getenv('LOG_LEVEL')
SLEEP_INTERVAL = int(os.getenv('SLEEP_INTERVAL'))
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

def get_price_from_url(url):
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, "html.parser")
    price = soup.find_all("meta", itemprop="price")
    return float(price[0]["data-price-eur"])

def send_to_chat(price, url, chat_id):
    data = {
        'chat_id': chat_id,
        'text': f'Price for {url} is now {price}!',
        'parse_mode': 'Markdown'
    }
    requests.post(TELEGRAM_API_URL, data=data)

def create_targets_list():
    targets = []
    for key, value in os.environ.items():
      if key.startswith('TARGET_'):
        target = { 'url': value.split(',')[0], 'price_target': float(value.split(',')[1])}
        targets.append(target)
    return targets

def main(logger):
    targets = create_targets_list()
    logger.info(f'Target list loaded: {targets}')
    while True:
        for target in targets:
            price = get_price_from_url(target['url'])
            logger.debug(f'Price {price} for url {target["url"]}')
            if price <= target['price_target']:
                logger.info(f'Hit price target for url {target["url"]}')
                for chat_id in CHAT_IDS:
                    send_to_chat(price, target['url'], chat_id)
                    logger.debug(f'Sent message to {chat_id}')
        time.sleep(SLEEP_INTERVAL)

if __name__ == '__main__':
    logging.basicConfig(format='%(process)d-%(levelname)s-%(message)s', stream = sys.stdout, level = LOG_LEVEL)
    logger = logging.getLogger()
    main(logger)