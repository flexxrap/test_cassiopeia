import xml.etree.ElementTree as ET
from datetime import datetime

CATEGORIES = [
    {"id": 1, "name": "Чай", "is_active": True},
    {"id": 2, "name": "Кофе", "is_active": True},
    {"id": 3, "name": "Неактивная", "is_active": False},
]

PRODUCTS = [
    # Проходит фильтр: активен, кат.1 активна, цена>0, картинка https, stock>0
    # old_price(200) > price(150) => добавляем <oldprice>
    {
        "id": 101,
        "category_id": 1,
        "name": 'Чай "Лес & травы" <сбор №1>',
        "price": "150.00",
        "old_price": "200.00",
        "image_url": "https://example.com/tea.jpg",
        "is_active": True,
        "stock": 5,
        "description": "Вкусный чай",
    },
    # Проходит фильтр: stock=0 => available=false
    # old_price(50) < price(100) => <oldprice> не добавляем
    {
        "id": 102,
        "category_id": 1,
        "name": "Чай чёрный",
        "price": "100.00",
        "old_price": "50.00",
        "image_url": "https://example.com/black.jpg",
        "is_active": True,
        "stock": 0,
        "description": "Чёрный чай",
    },
    # Проходит фильтр: картинка http://, description="" => <description> не добавляем
    {
        "id": 107,
        "category_id": 2,
        "name": "Кофе молотый",
        "price": "300.00",
        "old_price": None,
        "image_url": "http://example.com/coffee.jpg",
        "is_active": True,
        "stock": 10,
        "description": "",
    },
    # Отфильтрован: is_active=False
    {
        "id": 103,
        "category_id": 1,
        "name": "Скрытый товар",
        "price": "200.00",
        "old_price": None,
        "image_url": "https://example.com/hidden.jpg",
        "is_active": False,
        "stock": 5,
        "description": "",
    },
    # Отфильтрован: категория 3 неактивна
    {
        "id": 104,
        "category_id": 3,
        "name": "Товар в неактивной категории",
        "price": "200.00",
        "old_price": None,
        "image_url": "https://example.com/inactive_cat.jpg",
        "is_active": True,
        "stock": 5,
        "description": "",
    },
    # Отфильтрован: пустое имя
    {
        "id": 105,
        "category_id": 1,
        "name": "",
        "price": "200.00",
        "old_price": None,
        "image_url": "https://example.com/noname.jpg",
        "is_active": True,
        "stock": 5,
        "description": "",
    },
    # Отфильтрован: price=0
    {
        "id": 106,
        "category_id": 1,
        "name": "Бесплатный",
        "price": "0.00",
        "old_price": None,
        "image_url": "https://example.com/free.jpg",
        "is_active": True,
        "stock": 5,
        "description": "",
    },
    # Отфильтрован: image_url=None
    {
        "id": 108,
        "category_id": 2,
        "name": "Без картинки",
        "price": "100.00",
        "old_price": None,
        "image_url": None,
        "is_active": True,
        "stock": 5,
        "description": "",
    },
    # Отфильтрован: image_url начинается с ftp://
    {
        "id": 109,
        "category_id": 2,
        "name": "Плохая картинка",
        "price": "100.00",
        "old_price": None,
        "image_url": "ftp://example.com/img.jpg",
        "is_active": True,
        "stock": 5,
        "description": "",
    },
]


def build_yml(products, categories, generated_at):
    if isinstance(generated_at, datetime):
        date_str = generated_at.strftime("%Y-%m-%d %H:%M")
    else:
        date_str = str(generated_at)

    category_map = {cat["id"]: cat for cat in categories}

    filtered_products = []
    for product in products:
        if not product["is_active"]:
            continue
        cat = category_map.get(product["category_id"])
        if not cat or not cat["is_active"]:
            continue
        if not product["name"]:
            continue
        try:
            price_val = float(product["price"])
        except (ValueError, TypeError):
            continue
        if price_val <= 0:
            continue
        if product["image_url"] is None:
            continue
        if not (
            product["image_url"].startswith("http://")
            or product["image_url"].startswith("https://")
        ):
            continue
        filtered_products.append(product)

    filtered_products.sort(key=lambda p: p["id"])

    used_category_ids = sorted({p["category_id"] for p in filtered_products})

    root = ET.Element("yml_catalog")
    root.set("date", date_str)

    shop = ET.SubElement(root, "shop")

    shop_name_el = ET.SubElement(shop, "name")
    shop_name_el.text = "Test Shop"

    company_el = ET.SubElement(shop, "company")
    company_el.text = "Test Company"

    shop_url_el = ET.SubElement(shop, "url")
    shop_url_el.text = "https://example.test"

    currencies_el = ET.SubElement(shop, "currencies")
    currency_el = ET.SubElement(currencies_el, "currency")
    currency_el.set("id", "RUB")
    currency_el.set("rate", "1")

    categories_el = ET.SubElement(shop, "categories")
    for cat_id in used_category_ids:
        cat = category_map[cat_id]
        cat_el = ET.SubElement(categories_el, "category")
        cat_el.set("id", str(cat["id"]))
        cat_el.text = cat["name"]

    offers_el = ET.SubElement(shop, "offers")
    for product in filtered_products:
        offer = ET.SubElement(offers_el, "offer")
        offer.set("id", str(product["id"]))
        offer.set("available", "true" if product["stock"] > 0 else "false")

        slug = str(product["id"])
        url_el = ET.SubElement(offer, "url")
        url_el.text = f"https://example.test/products/{slug}/"

        name_el = ET.SubElement(offer, "name")
        name_el.text = product["name"]

        price_el = ET.SubElement(offer, "price")
        price_el.text = f"{float(product['price']):.2f}"

        old_price = product.get("old_price")
        if old_price is not None:
            try:
                old_price_val = float(old_price)
                cur_price_val = float(product["price"])
            except (ValueError, TypeError):
                old_price_val = 0.0
                cur_price_val = 0.0
            if old_price_val > 0 and old_price_val > cur_price_val:
                oldprice_el = ET.SubElement(offer, "oldprice")
                oldprice_el.text = f"{old_price_val:.2f}"

        currency_id_el = ET.SubElement(offer, "currencyId")
        currency_id_el.text = "RUB"

        cat_id_el = ET.SubElement(offer, "categoryId")
        cat_id_el.text = str(product["category_id"])

        picture_el = ET.SubElement(offer, "picture")
        picture_el.text = product["image_url"]

        desc = product.get("description", "")
        if desc:
            desc_el = ET.SubElement(offer, "description")
            desc_el.text = desc

    xml_body = ET.tostring(root, encoding="unicode", xml_declaration=False)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_body


if __name__ == "__main__":
    result = build_yml(PRODUCTS, CATEGORIES, datetime(2026, 6, 18, 12, 0))
    print(result)
