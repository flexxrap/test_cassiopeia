import xml.etree.ElementTree as ET
from datetime import datetime


CATEGORIES = [
    {
        "id": 1,
        "name": "Чай",
        "is_active": True,
    },
    {
        "id": 2,
        "name": "Посуда",
        "is_active": True,
    },
    {
        "id": 3,
        "name": "Подарочные наборы",
        "is_active": False,
    },
]


PRODUCTS = [
    {
        "id": 101,
        "name": 'Чай "Лес & травы" <сбор №1>',
        "slug": "les-i-travy",
        "category_id": 1,
        "price": "490.00",
        "old_price": "590.00",
        "stock": 12,
        "description": "Вкус: мята & чабрец > классический чай",
        "image_url": "https://example.test/media/tea-101.jpg",
        "is_active": True,
    },
    {
        "id": 102,
        "name": "Чайник стеклянный",
        "slug": "glass-teapot",
        "category_id": 2,
        "price": "1500.00",
        "old_price": "1400.00",
        "stock": 0,
        "description": "Стеклянный чайник объёмом 800 мл",
        "image_url": "https://example.test/media/teapot-102.jpg",
        "is_active": True,
    },
    {
        "id": 103,
        "name": "Скрытый товар",
        "slug": "hidden-product",
        "category_id": 1,
        "price": "350.00",
        "old_price": None,
        "stock": 5,
        "description": "Товар отключён администратором",
        "image_url": "https://example.test/media/product-103.jpg",
        "is_active": False,
    },
    {
        "id": 104,
        "name": "Пробник чая",
        "slug": "tea-sample",
        "category_id": 1,
        "price": "0.00",
        "old_price": None,
        "stock": 30,
        "description": "Бесплатный пробник",
        "image_url": "https://example.test/media/product-104.jpg",
        "is_active": True,
    },
    {
        "id": 105,
        "name": "Чашка фарфоровая",
        "slug": "porcelain-cup",
        "category_id": 2,
        "price": "700.00",
        "old_price": "900.00",
        "stock": 4,
        "description": "Фарфоровая чашка",
        "image_url": None,
        "is_active": True,
    },
    {
        "id": 106,
        "name": "Подарочный набор",
        "slug": "gift-set",
        "category_id": 3,
        "price": "2500.00",
        "old_price": "3000.00",
        "stock": 2,
        "description": "Товар находится в неактивной категории",
        "image_url": "https://example.test/media/product-106.jpg",
        "is_active": True,
    },
    {
        "id": 107,
        "name": "Чай улун молочный",
        "slug": "milk-oolong",
        "category_id": 1,
        "price": "700.50",
        "old_price": None,
        "stock": 3,
        "description": "",
        "image_url": "https://example.test/media/product-107.jpg",
        "is_active": True,
    },
]


def _format_date(generated_at):
    """Привести дату генерации к формату YYYY-MM-DD hh:mm."""
    if isinstance(generated_at, datetime):
        return generated_at.strftime("%Y-%m-%d %H:%M")
    return str(generated_at)


def _has_valid_image(image_url):
    return isinstance(image_url, str) and (
        image_url.startswith("http://") or image_url.startswith("https://")
    )


def _parse_price(value):
    """Вернуть float цены либо None, если значение некорректно."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _is_product_allowed(product, category_map):
    """Товар проходит в фид, только если выполнены ВСЕ условия."""
    if not product.get("is_active"):
        return False

    category = category_map.get(product.get("category_id"))
    if category is None or not category.get("is_active"):
        return False

    if not product.get("name"):
        return False

    price = _parse_price(product.get("price"))
    if price is None or price <= 0:
        return False

    if not _has_valid_image(product.get("image_url")):
        return False

    return True


def build_yml(products, categories, generated_at):
    category_map = {category["id"]: category for category in categories}

    selected = [
        product
        for product in products
        if _is_product_allowed(product, category_map)
    ]
    selected.sort(key=lambda product: product["id"])

    used_category_ids = sorted({product["category_id"] for product in selected})

    root = ET.Element("yml_catalog", {"date": _format_date(generated_at)})
    shop = ET.SubElement(root, "shop")

    ET.SubElement(shop, "name").text = "Test Shop"
    ET.SubElement(shop, "company").text = "Test Company"
    ET.SubElement(shop, "url").text = "https://example.test"

    currencies = ET.SubElement(shop, "currencies")
    ET.SubElement(currencies, "currency", {"id": "RUB", "rate": "1"})

    categories_el = ET.SubElement(shop, "categories")
    for category_id in used_category_ids:
        category = category_map[category_id]
        category_el = ET.SubElement(
            categories_el, "category", {"id": str(category["id"])}
        )
        category_el.text = category["name"]

    offers_el = ET.SubElement(shop, "offers")
    for product in selected:
        available = "true" if product["stock"] > 0 else "false"
        offer = ET.SubElement(
            offers_el,
            "offer",
            {"id": str(product["id"]), "available": available},
        )

        ET.SubElement(offer, "url").text = (
            f'https://example.test/products/{product["slug"]}/'
        )

        price = _parse_price(product["price"])
        ET.SubElement(offer, "price").text = f"{price:.2f}"

        old_price = _parse_price(product.get("old_price"))
        if old_price is not None and old_price > 0 and old_price > price:
            ET.SubElement(offer, "oldprice").text = f"{old_price:.2f}"

        ET.SubElement(offer, "currencyId").text = "RUB"
        ET.SubElement(offer, "categoryId").text = str(product["category_id"])
        ET.SubElement(offer, "picture").text = product["image_url"]
        ET.SubElement(offer, "name").text = product["name"]

        description = product.get("description")
        if description:
            ET.SubElement(offer, "description").text = description

    xml_body = ET.tostring(root, encoding="unicode", xml_declaration=False)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_body


if __name__ == "__main__":
    result = build_yml(
        products=PRODUCTS,
        categories=CATEGORIES,
        generated_at=datetime(2026, 6, 18, 12, 0),
    )

    print(result)
