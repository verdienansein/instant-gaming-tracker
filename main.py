import os
import requests
import time
import re
import sys
import logging
from dotenv import load_dotenv
from bs4 import BeautifulSoup

import telebot
from db_helper import DBHelper

TOKEN = os.getenv('TOKEN')
CHAT_IDS = os.getenv('CHAT_IDS').split(",")
LOG_LEVEL = os.getenv('LOG_LEVEL')
SLEEP_INTERVAL = int(os.getenv('SLEEP_INTERVAL'))
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")


def get_price_from_url(url):
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, "html.parser")
    return float(soup.find_all("div", class_="total")[-1].get_text()[:-1])

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

def main(logger, db):
    targets = db.get_all_targets()
    logger.info(f'Target list loaded: {targets}')
    while True:
        for target in targets:
            target_url = target[0]
            target_price = target[1]
            target_chat = target[2]
            price = get_price_from_url(target_url)
            logger.debug(f'Price {price} for url {target_url}')
            if price <= target_price:
                logger.info(f'Hit price target for url {target_url}')
                send_to_chat(price, target_url, target_chat)
                logger.debug(f'Sent message to {target_chat}')
        time.sleep(SLEEP_INTERVAL)

def get_url(message):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, message)      
    return [x[0] for x in url]

def get_price(message):
    regex = r",\s*(\d+)"
    price = re.findall(regex, message)      
    return price[0]

@bot.message_handler(regexp="add target .+,.+")
def echo_all(message):
    url = get_url(message.text)[0]
    price = get_price(message.text)
    db.add_target(url, float(price), message.chat.id)

@bot.message_handler(regexp="list.*target.*")
def echo_all(message):
    targets = db.get_targets(message.chat.id)
    for target in targets:
        reply = f'Url: {target[0]}, Target price: {target[1]}'
        bot.reply_to(message, reply)

if __name__ == '__main__':
    logging.basicConfig(format='%(process)d-%(levelname)s-%(message)s', stream = sys.stdout, level = LOG_LEVEL)
    logger = logging.getLogger()
    db = DBHelper()
    db.setup()

    main(logger, db)

    bot.infinity_polling()
