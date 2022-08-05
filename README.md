# Instant Gaming Tracker

This Telegram Bot monitors Instant Gaming items prices and notifies you on Telegram if the price drops.

## Usage

The following environment variables are needed to start the bot:
* `TOKEN`: Telegram bot token
* `SLEEP_INTERVAL`: the interval used by the bot to poll Instant Gaming
* `LOG_LEVEL`

### Bot commands

```
    /start - Start the bot.
    /help - Help message.
    /add - Add a new target url to track with a price.
    /update - Update an existing target url to track with a different price.
    /delete - Delete a tracked target.
    /list - List all the tracked targets.
```
