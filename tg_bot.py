import os

import redis

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler
from validate_email import validate_email

from moltin_api import (
    fetch_fish_shop_goods,
    fetch_fish_shop_good,
    add_good_to_cart,
    get_cart_items,
    get_product_image_url,
    get_cart_total,
    remove_cart_item,
    create_customer,
)

_database = None


def send_total_cart_message(chat_id, bot, query):
    message_text = ""
    keyboard = []

    cart_items = get_cart_items(chat_id)

    for cart_item in cart_items["data"]:
        display_price = cart_item["meta"]["display_price"]["with_tax"]

        message_text += (
            f"{cart_item['name']}\n"
            f"{cart_item['description']}\n"
            f"{display_price['unit']['formatted']} per kg\n"
            f"{cart_item['quantity']} kg in cart for "
            f"{display_price['value']['formatted']}\n\n"
        )

        keyboard.append(
            [
                InlineKeyboardButton(
                    f"Убрать из корзины {cart_item['name']}",
                    callback_data=cart_item["id"],
                )
            ]
        )

    cart_total = get_cart_total(chat_id)["data"]["meta"]
    message_text += (
        f"Total: {cart_total['display_price']['with_tax']['formatted']}"
    )

    keyboard.append(
        [InlineKeyboardButton("Оплатить", callback_data="payment")]
    )
    keyboard.append([InlineKeyboardButton("В меню", callback_data="menu")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    bot.send_message(
        chat_id=chat_id,
        text=message_text,
        reply_markup=reply_markup,
    )

    bot.deleteMessage(
        chat_id=chat_id,
        message_id=query.message.message_id,
    )


def send_initial_menu(chat_id, bot):
    keyboard = []

    fish_shop_goods = fetch_fish_shop_goods()

    for fish_shop_good in fish_shop_goods["data"]:
        keyboard.append(
            [
                InlineKeyboardButton(
                    fish_shop_good["name"], callback_data=fish_shop_good["id"]
                )
            ]
        )
    keyboard.append([InlineKeyboardButton("Корзина", callback_data="cart")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    bot.send_message(
        chat_id=chat_id,
        text="Выберите:",
        reply_markup=reply_markup,
    )


def start(bot, update):
    chat_id = update.effective_chat.id

    send_initial_menu(chat_id, bot)

    return "HANDLE_MENU"


def handle_menu(bot, update):
    query = update.callback_query
    chat_id = query.message.chat_id

    if query.data == "cart":
        send_total_cart_message(chat_id, bot, query)

        return "HANDLE_CART"
    else:
        weight_buttons = []
        max_good_quantity = 3

        good_id = query.data

        fish_shop_good = fetch_fish_shop_good(good_id)["data"]

        good_price = fish_shop_good["meta"]["display_price"]["with_tax"][
            "formatted"
        ]
        good_weight = fish_shop_good["weight"]["kg"]

        message_text = (
            f"{fish_shop_good['name']}\n\n"
            f"{good_price} per {good_weight} kg\n"
            f"{fish_shop_good['meta']['stock']['level']} kg in stock\n\n"
            f"{fish_shop_good['description']}"
        )

        image_id = (
            fish_shop_good.get("relationships", None)
            .get("main_image", None)
            .get("data", None)
            .get("id", None)
        )

        for good_quantity in range(1, max_good_quantity + 1):
            weight_buttons.append(
                InlineKeyboardButton(
                    f"{good_weight * good_quantity} kg",
                    callback_data=f"{good_id}|{good_quantity}",
                )
            )

        keyboard = [
            weight_buttons,
            [InlineKeyboardButton("Корзина", callback_data="cart")],
            [InlineKeyboardButton("Назад", callback_data="back")],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        if image_id:
            bot.send_photo(
                chat_id=chat_id,
                photo=get_product_image_url(image_id)["data"]["link"]["href"],
                caption=message_text,
                parse_mode="html",
                reply_markup=reply_markup,
            )
        else:
            bot.send_message(
                chat_id=chat_id,
                text=message_text,
                reply_markup=reply_markup,
            )

        bot.deleteMessage(
            chat_id=chat_id,
            message_id=query.message.message_id,
        )

    return "HANDLE_DESCRIPTION"


def handle_description(bot, update):
    query = update.callback_query
    chat_id = query.message.chat_id

    if query.data == "back":
        send_total_cart_message(chat_id, bot, query)
    elif query.data == "cart":
        send_total_cart_message(chat_id, bot, query)

        return "HANDLE_CART"
    else:
        good_id, good_quantity = query.data.split("|")

        add_good_to_cart(
            good_id,
            chat_id,
            int(good_quantity),
        )

        return "HANDLE_DESCRIPTION"

    return "HANDLE_MENU"


def handle_cart(bot, update):
    query = update.callback_query
    chat_id = query.message.chat_id

    if query.data == "menu":
        send_initial_menu(chat_id, bot)

        bot.deleteMessage(
            chat_id=chat_id,
            message_id=query.message.message_id,
        )

        return "HANDLE_MENU"
    elif query.data == "payment":
        bot.send_message(
            chat_id=chat_id,
            text="Введите адрес электронной почты:",
        )
        return "WAITING_EMAIL"
    else:
        remove_cart_item(chat_id, query.data)
        send_total_cart_message(chat_id, bot, query)

    return "HANDLE_CART"


def waiting_email(bot, update):
    user_email = update.message.text
    user_id = update.message.chat_id

    is_email_valid = validate_email(
        email_address=user_email,
        check_format=True,
        check_blacklist=False,
        check_dns=False,
        check_smtp=False,
    )

    if is_email_valid:
        update.message.reply_text(
            f"Вы ввели адрес электронной почты: {user_email}"
        )

        create_customer(str(user_id), user_email)

        return "START"
    else:
        update.message.reply_text(
            "Вы ввели некорректный адрес электронной почты"
        )

        return "WAITING_EMAIL"


def handle_users_reply(bot, update):
    db = get_database_connection()
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == "/start":
        user_state = "START"
    else:
        user_state = db.get(chat_id).decode("utf-8")

    states_functions = {
        "START": start,
        "HANDLE_MENU": handle_menu,
        "HANDLE_DESCRIPTION": handle_description,
        "HANDLE_CART": handle_cart,
        "WAITING_EMAIL": waiting_email,
    }
    state_handler = states_functions[user_state]

    try:
        next_state = state_handler(bot, update)
        db.set(chat_id, next_state)
    except Exception as err:
        print(err)


def get_database_connection():
    global _database
    if not _database:
        database_password = os.getenv("REDIS_PASS")
        database_host = os.getenv("REDIS_HOST")
        database_port = os.getenv("REDIS_PORT")
        _database = redis.Redis(
            host=database_host, port=database_port, password=database_password
        )
    return _database


def main():
    load_dotenv()

    telegram_token = os.getenv("TELEGRAM_TOKEN")

    updater = Updater(telegram_token)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler("start", handle_users_reply))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
