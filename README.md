# Instant Gaming Tracker

This Telegram Bot monitors Instant Gaming items prices and notifies you on Telegram if the price drops.

## Usage

The following environment variables are needed to start the bot:
* `TOKEN`: Telegram bot token
* `CHAT_IDS`: List of Telegram Chat Ids to send notifications
* `SLEEP_INTERVAL`: the interval used by the bot to poll Instant Gaming
* `TARGET_<YOUR_TARGET>`: all the environment variables starting with `TARGET_` will be used for tracking. These variables must have the following format: `<URL>,<TARGET_PRICE>`. Example: `https://www.instant-gaming.com/en/2157-buy-steam-game-steam-factorio/,22`. This bot will monitoring the URL, and notify you if the price drops below 22€.
* `LOG_LEVEL`
