import logging
import os
import re
import sys
import time
from threading import Thread

import requests
import telebot
from bs4 import BeautifulSoup

from db_helper import DBHelper, PostgreDBHelper

TOKEN = os.getenv('TOKEN')
LOG_LEVEL = os.getenv('LOG_LEVEL')
SLEEP_INTERVAL = int(os.getenv('SLEEP_INTERVAL'))
DB_TYPE = os.getenv('DB_TYPE')
DATABASE_URL = os.getenv('DATABASE_URL')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

bot = telebot.TeleBot(TOKEN)
state = {}


def get_price_from_url(url):
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, "html.parser")
    price = soup.find_all("meta", itemprop="price")
    return float(price[0]["data-price-eur"])


def search_keyword(keyword):
    search_url = f"https://www.instant-gaming.com/en/search/?q={keyword}"
    html_text = requests.get(search_url).text
    soup = BeautifulSoup(html_text, "html.parser")
    links = soup.find_all("a", href=True)
    results = []
    for link in links:
        if bool(re.search("https:\/\/www\.instant-gaming\.com/en/\d+-", link["href"])):
            results.append(link["href"])
    return results


def send_to_chat(price, url, chat_id):
    data = {
        'chat_id': chat_id,
        'text': f'Price for {url} is now {price}!',
        'parse_mode': 'Markdown'
    }
    requests.post(TELEGRAM_API_URL, data=data)


def main(logger, db):
    logger.info("Started pooling thread.")
    while True:
        try:
            logger.info(f"Fetching targets")
            targets = db.get_all_targets()
            logger.debug(f'Target list loaded: {targets}')
            for target in targets:
                target_url = target[0]
                target_price = target[1]
                target_chat = target[2]
                price = get_price_from_url(target_url)
                logger.debug(f'Price {price} for url {target_url}')
                if price <= target_price:
                    logger.info(
                        f'Hit target price {target_price} for url {target_url}')
                    send_to_chat(price, target_url, target_chat)
                    logger.debug(f'Sent message to {target_chat}')
            logger.info(f"Done fetching targets")
            logger.info(f"Next fetch in {SLEEP_INTERVAL} seconds")
            time.sleep(SLEEP_INTERVAL)
        except Exception as e:
            logger.error(e)


def parse_url(message):
    regex = r"(https:\/\/www\.instant-gaming\.com/.+)"
    url = re.findall(regex, message)
    if len(url) < 1:
        return False
    return url[0]


@bot.message_handler(commands=["help", "start"])
def add_target(message):
    logger.info(f"Help Request from chat_id {message.chat.id}")
    bot.reply_to(message, f"""
/start - Start the bot.
/help - Help message.
/search - Search for URLs to track by keyword
/add - Add a new target URL to track with a price.
/update - Update an existing target URL to track with a different price.
/delete - Delete a tracked target.
/list - List all the tracked targets.
    """)


@bot.message_handler(commands=["add"])
def add_target(message):
    logger.info(f"Add Request from chat_id {message.chat.id}")
    bot.reply_to(message, f"""
Hi, 
what URL do you want to track?
    """)
    bot.register_next_step_handler(message=message, callback=get_url_handler)


def get_url_handler(message):
    url = parse_url(message.text)
    logger.debug(f"Got url {url}, chat_id: {message.chat.id}")
    if not url:
        bot.reply_to(message, f"URL must be a proper Instant Gaming URL.")
        return
    state[message.chat.id] = {}
    state[message.chat.id]["url"] = url
    bot.reply_to(message, f"""
Hi, 
what target price you want to set? (for example: 35)
    """)
    bot.register_next_step_handler(message=message, callback=get_price_handler)


def get_price_handler(message):
    try:
        url = state[message.chat.id]["url"]
        price = float(message.text)
        logger.info(
            f"Adding target {url} - price {price} from chat_id {message.chat.id}")
        db.add_target(url, price, message.chat.id)
        bot.reply_to(message, f"Added target with URL {url} and price {price}")
    except ValueError:
        bot.reply_to(message, f"Target {url} already exists.")
    except Exception as e:
        logger.error(e)
        bot.reply_to(message, f"Sorry, something went wrong.")


@bot.message_handler(commands=["update"])
def update_target(message):
    logger.info(f"Update Request from chat_id {message.chat.id}")
    bot.reply_to(message, f"""
Hi, 
what URL do you want to update?
    """)
    bot.register_next_step_handler(
        message=message, callback=get_url_for_update_handler)


def get_url_for_update_handler(message):
    url = parse_url(message.text)
    if not url:
        bot.reply_to(message, f"URL must be a proper Instant Gaming URL.")
        return
    state[message.chat.id] = {}
    state[message.chat.id]["url"] = url
    bot.reply_to(message, f"""
Hi, 
what target price you want to set? (for example: 35)
    """)
    bot.register_next_step_handler(
        message=message, callback=get_price_for_update_handler)


def get_price_for_update_handler(message):
    try:
        url = state[message.chat.id]["url"]
        price = float(message.text)
        logger.info(
            f"Updating target {url} - price {price} from chat_id {message.chat.id}")
        db.update_target_price(url, price, message.chat.id)
        bot.reply_to(
            message, f"Updated target with URL {url} and price {price}")
    except ValueError:
        bot.reply_to(message, f"Target {url} already exists.")
    except Exception as e:
        logger.error(e)
        bot.reply_to(message, f"Sorry, something went wrong.")


@bot.message_handler(commands=["delete"])
def delete_target(message):
    logger.info(f"Delete Request from chat_id {message.chat.id}")
    bot.reply_to(message, f"""
Hi, 
what URL do you want to delete?
    """)
    bot.register_next_step_handler(
        message=message, callback=get_url_for_delete_handler)


def get_url_for_delete_handler(message):
    url = parse_url(message.text)
    if not url:
        bot.reply_to(message, f"URL must be a proper Instant Gaming URL.")
        return
    logger.info(f"Deleting target {url} from chat_id {message.chat.id}")
    db.delete_target(url, message.chat.id)
    bot.reply_to(message, f"Target {url} deleted!")


@bot.message_handler(commands=["list"])
def list_targets(message):
    logger.info(f"List Request from chat_id {message.chat.id}")
    targets = db.get_targets(message.chat.id)
    for target in targets:
        url = target[0]
        target_price = target[1]
        current_price = get_price_from_url(url)
        reply = f"""
🎮 *URL*: {url}
💶 *Current price*: {current_price}
💡 *Target price*: {target_price}
        """
        bot.reply_to(message, reply, parse_mode="Markdown")


@bot.message_handler(commands=["search"])
def search_targets(message):
    logger.info(f"Search Request from chat_id {message.chat.id}")
    bot.reply_to(message, "Insert a keyword to search: ")
    bot.register_next_step_handler(
        message=message, callback=search_keyword_handler)


def search_keyword_handler(message):
    keyword = message.text
    logger.info(f"Searching keyword {keyword} from chat_id {message.chat.id}")
    results = search_keyword(keyword)[:3]
    for url in results:
        current_price = get_price_from_url(url)
        reply = f"""
🎮 *URL*: {url}
💶 *Current price*: {current_price}
        """
        bot.reply_to(message, reply, parse_mode="Markdown")


if __name__ == '__main__':
    logging.basicConfig(format='%(process)d-%(levelname)s-%(message)s',
                        stream=sys.stdout, level=LOG_LEVEL)
    logger = logging.getLogger()

    if DB_TYPE == 'sqlite':
        db = DBHelper()
    elif DB_TYPE == 'postgresql':
        db = PostgreDBHelper(conn_string=DATABASE_URL)

    db.setup()

    thread = Thread(target=main, args=(logger, db))
    thread.start()

    bot.infinity_polling()
