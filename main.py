import os
import requests
import time
import re
import sys
import logging
from dotenv import load_dotenv
from bs4 import BeautifulSoup

import telebot
from threading import Thread
from db_helper import DBHelper, PostgreDBHelper

TOKEN = os.getenv('TOKEN')
LOG_LEVEL = os.getenv('LOG_LEVEL')
SLEEP_INTERVAL = int(os.getenv('SLEEP_INTERVAL'))
DB_TYPE = os.getenv('DB_TYPE')
HEROKU_POSTGRESQL = os.getenv('HEROKU_POSTGRESQL')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

bot = telebot.TeleBot(TOKEN)


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

def parse_message(message):
    regex = r"(https:\/\/www\.instant-gaming\.com/.+),(\d+)"
    url = re.findall(regex, message) 
    if len(url) == 0:
        return False
    return url[0]

def parse_url(message):
    regex = r"(https:\/\/www\.instant-gaming\.com/.+)"
    url = re.findall(regex, message)  
    return url[0]

@bot.message_handler(commands=["help", "start"])
def add_target(message):
    bot.reply_to(message, f"""
    /start - Start the bot.
/help - Help message.
/add {{URL}},{{TARGET_PRICE}} - Add a new target url to track with a price.
/update {{URL}},{{TARGET_PRICE}} - Update an existing target url to track with a different price.
/delete {{URL}} - Delete a tracked target.
/list - List all the tracked targets.
    """)

@bot.message_handler(commands=["add"])
def add_target(message):
    try:
        if not parse_message(message.text): 
            bot.reply_to(message, f"URL must be a proper Instant Gaming URL. Message format must be: {{URL}},{{TARGET_PRICE}}")
            return
        url = parse_message(message.text)[0]
        price = parse_message(message.text)[1]
        db.add_target(url, float(price), message.chat.id)
        bot.reply_to(message, f"Added target with URL {url} and price {price}")
    except ValueError:
        bot.reply_to(message, f"Target {url} already exists.")



@bot.message_handler(commands=["update"])
def update_target(message):
    if not parse_message(message.text): 
        bot.reply_to(message, f"URL must be a proper Instant Gaming URL. Message format must be: {{URL}},{{TARGET_PRICE}}")
        return
    url = parse_message(message.text)[0]
    price = parse_message(message.text)[1]
    db.update_target_price(url, float(price), message.chat.id)
    bot.reply_to(message, f"Updated target with URL {url} and price {price}")

@bot.message_handler(commands=["delete"])
def delete_target(message):
    url = parse_url(message.text)
    db.delete_target(url, message.chat.id)
    bot.reply_to(message, f"Target {url} deleted!")

@bot.message_handler(commands=["list"])
def list_targets(message):
    targets = db.get_targets(message.chat.id)
    for target in targets:
        reply = f'Url: {target[0]}, Target price: {target[1]}'
        bot.reply_to(message, reply)

if __name__ == '__main__':
    logging.basicConfig(format='%(process)d-%(levelname)s-%(message)s', stream = sys.stdout, level = LOG_LEVEL)
    logger = logging.getLogger()

    if DB_TYPE == 'sqlite':
        db = DBHelper()
    elif DB_TYPE == 'postgresql':
        db = PostgreDBHelper(conn_string=HEROKU_POSTGRESQL)

    db.setup()

    thread = Thread(target = main, args = (logger, db))
    thread.start()

    bot.infinity_polling()
