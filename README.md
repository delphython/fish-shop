# Fish Shop Telegram Bot

Fish Shop Telegram Bot is the bot for online store where customers can place their orders.

## Prerequisites

Python3 should be already installed. Use `pip` to install dependencies:
```bash
pip install -r requirements.txt
```

## Installation for developer mode
You have to set TELEGRAM_TOKEN, ELASTICPATH_CLIENTD_ID, ELASTICPATH_CLIENTD_SECRET and Redis connection environment variables before using the script.

1. Create .env file in the project directory.
2. Create the bot and get a token from Telegram, see [this tutorial](https://www.siteguarding.com/en/how-to-get-telegram-bot-api-token) for instructions. Copy your Telegram API token to .env file:
```
export TELEGRAM_TOKEN="1234567890:AAHOoGbQZQripXSKTn1ZRmKf6g3-wwwwwww"
```
3. Create the online store [here](https://euwest.cm.elasticpath.com/) and copy `Client ID` and `Client secret` to .env file:
```
export ELASTICPATH_CLIENTD_ID="mvQqgldYG4DiOZaEWtLFnq0MUk12FuOh34X56xmbVZ"
export ELASTICPATH_CLIENTD_SECRET="xnMU7E3P6RtXry3hsjdMGwR3nJE4ut6CU7ZP9ZjHpM"
```
4. To get Redis connection environment variables (REDIS_HOST, REDIS_PORT and REDIS_PASS) you should register [here](https://redis.com/), then choose a Subscription plan and add a new database. Get `REDIS_HOST` and `REDIS_PORT` data in `Public endpoint` section and in `Security` section set `Default user password` - it will be `REDIS_PASS` environment variable. Copy it to .env file:
```
export REDIS_HOST="redis-12345.c12.us-east-1-2.ec2.cloud.redislabs.com"
export REDIS_PORT="12345"
export REDIS_PASS="ruQMaD11FJdbOymGuBgiKk2ZgDP3pAD"
```

## Usage

For Telegram bot run python script:
```sh
python tg_bot.py
```
Use Ctrl+C to interrupt the script.   

## Installation for production mode and deploy
For deploying on [Heroku](https://www.heroku.com) you should:
1. Login or register there.
2. Create a new app.
3. Connect GitHub repository.
4. Create `Procfile` in the project root directory and add the text:
```
bot-tg: python3 tg_bot.py
```
5. Add TELEGRAM_TOKEN, ELASTICPATH_CLIENTD_ID, ELASTICPATH_CLIENTD_SECRET, REDIS_HOST, REDIS_PORT and REDIS_PASS environment variables in the Settings tab of the Heroku site.
6. Don't forget to renew the project repository on Heroku.

## Try the bot
Link to the Telegram bot: [@my_cooking_timer_bot](https://t.me/my_cooking_timer_bot)
![alt text](./tg_bot.gif)

## Meta

Vitaly Klyukin — [@delphython](https://t.me/delphython) — [delphython@gmail.com](mailto:delphython@gmail.com)

[https://github.com/delphython](https://github.com/delphython/)
