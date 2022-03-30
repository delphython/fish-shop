from textwrap import dedent

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from moltin_api import (
    fetch_fish_shop_goods,
    get_cart_items,
    get_cart_total,
)


def send_total_cart_message(chat_id, bot, query):
    message_text = ""
    keyboard = []

    cart_items = get_cart_items(chat_id)

    for cart_item in cart_items["data"]:
        display_price = cart_item["meta"]["display_price"]["with_tax"]

        message_text += dedent(
            f"""\
        {cart_item['name']}
        {cart_item['description']}
        {display_price['unit']['formatted']} per kg
        {cart_item['quantity']} kg in cart for {display_price['value']['formatted']}

        """
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

    bot.delete_message(
        chat_id=chat_id,
        message_id=query.message.message_id,
    )


def send_initial_message(chat_id, bot):
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
