import os

import requests


def get_elasticpath_headers():
    elasticpath_client_id = os.environ["ELASTICPATH_CLIENTD_ID"]
    elasticpath_client_secret = os.environ["ELASTICPATH_CLIENTD_SECRET"]

    elasticpath_api_key_url = "https://api.moltin.com/oauth/access_token"
    data = {
        "client_id": elasticpath_client_id,
        "client_secret": elasticpath_client_secret,
        "grant_type": "client_credentials",
    }

    response = requests.post(elasticpath_api_key_url, data=data)
    response.raise_for_status()

    return {
        "Authorization": f"Bearer {response.json()['access_token']}",
        "X-MOLTIN_CURRENCY": "USD",
    }


def fetch_fish_shop_goods():
    headers = get_elasticpath_headers()

    fish_shop_url = "https://api.moltin.com/v2/products"

    response = requests.get(fish_shop_url, headers=headers)
    response.raise_for_status()

    return response.json()


def fetch_fish_shop_good(good_id):
    headers = get_elasticpath_headers()

    fish_shop_url = f"https://api.moltin.com/v2/products/{good_id}"

    response = requests.get(fish_shop_url, headers=headers)
    response.raise_for_status()

    return response.json()


def add_good_to_cart(good_id, cart_id, quantity):
    headers = get_elasticpath_headers()

    add_good_to_cart_url = f"https://api.moltin.com/v2/carts/{cart_id}/items"

    payload = {
        "data": {
            "id": good_id,
            "type": "cart_item",
            "quantity": quantity,
        },
    }

    response = requests.post(
        add_good_to_cart_url,
        headers=headers,
        json=payload,
    )
    response.raise_for_status()

    return response.json()


def get_cart_items(cart_id):
    headers = get_elasticpath_headers()

    cart_items_url = f"https://api.moltin.com/v2/carts/{cart_id}/items"

    response = requests.get(cart_items_url, headers=headers)
    response.raise_for_status()

    return response.json()


def get_cart_total(cart_id):
    headers = get_elasticpath_headers()

    total_cart_url = f"https://api.moltin.com/v2/carts/{cart_id}"

    response = requests.get(total_cart_url, headers=headers)
    response.raise_for_status()

    return response.json()


def get_or_create_cart(cart_id):
    headers = get_elasticpath_headers()

    cart_url = f"https://api.moltin.com/v2/carts/{cart_id}"

    response = requests.get(cart_url, headers=headers)
    response.raise_for_status()

    return response.json()


def get_product_image_url(file_id):
    headers = get_elasticpath_headers()

    image_url = f"https://api.moltin.com/v2/files/{file_id}"

    response = requests.get(image_url, headers=headers)
    response.raise_for_status()

    return response.json()


def remove_cart_item(cart_id, product_id):
    headers = get_elasticpath_headers()

    remove_cart_item_url = (
        f"https://api.moltin.com/v2/carts/{cart_id}/items/{product_id}"
    )

    response = requests.delete(remove_cart_item_url, headers=headers)
    response.raise_for_status()

    return response.json()


def create_customer(user_name, user_email):
    headers = get_elasticpath_headers()

    create_customer_url = "https://api.moltin.com/v2/customers"

    payload = {
        "data": {
            "type": "customer",
            "name": user_name,
            "email": user_email,
        },
    }

    response = requests.post(
        create_customer_url,
        headers=headers,
        json=payload,
    )
    response.raise_for_status()

    return response.json()
