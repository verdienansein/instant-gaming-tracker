# Instant Gaming Tracker

This Telegram Bot monitors Instant Gaming items prices and notifies you on Telegram if the price drops.

Bot username on Telegram is: `@instantgaming_tracker_bot`.

## Usage

The following environment variables are needed to start the bot:
* `TOKEN`: Telegram bot token
* `SLEEP_INTERVAL`: the interval used by the bot to poll Instant Gaming
* `DB_TYPE`: the database type to use. Value can be either `postgresql` or `sqlite`
* `DATABASE_URL`: postgresql database connection string
* `LOG_LEVEL`

### Bot commands

```
    /start - Start the bot.
    /help - Help message.
    /search - Search for URLs to track by keyword
    /add - Add a new target url to track with a price.
    /update - Update an existing target url to track with a different price.
    /delete - Delete a tracked target.
    /list - List all the tracked targets.
```
