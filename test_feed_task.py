import xml.etree.ElementTree as ET
from datetime import datetime

import pytest

from feed_task import CATEGORIES, PRODUCTS, build_yml


@pytest.fixture(scope="module")
def result():
    return build_yml(PRODUCTS, CATEGORIES, datetime(2026, 6, 18, 12, 0))


@pytest.fixture(scope="module")
def root(result):
    # result is a str with an XML encoding declaration, so it must be parsed
    # as bytes (ET.fromstring rejects unicode strings that declare encoding).
    return ET.fromstring(result.encode("utf-8"))


@pytest.fixture(scope="module")
def offers(root):
    return {o.get("id"): o for o in root.findall(".//offer")}


# 1. Результат работы — валидный XML
def test_valid_xml(result):
    ET.fromstring(result.encode("utf-8"))


def test_returns_str_with_declaration(result):
    assert isinstance(result, str)
    assert result.startswith('<?xml version="1.0" encoding="UTF-8"?>')


# 2. Дата генерации
def test_date_format(root):
    assert root.tag == "yml_catalog"
    assert root.get("date") == "2026-06-18 12:00"


# 3. / 5. Правила включения и порядок товаров
def test_only_expected_products(offers):
    assert list(offers.keys()) == ["101", "102", "107"]


# 4. Категории
def test_categories_sorted_no_duplicates(root):
    cats = root.findall(".//category")
    assert [c.get("id") for c in cats] == ["1", "2"]
    assert [c.text for c in cats] == ["Чай", "Посуда"]


# 6. Наличие
def test_available_values(offers):
    assert offers["101"].get("available") == "true"
    assert offers["102"].get("available") == "false"
    assert offers["107"].get("available") == "true"


# 7. Цена
def test_price_values(offers):
    assert offers["101"].find("price").text == "490.00"
    assert offers["102"].find("price").text == "1500.00"
    assert offers["107"].find("price").text == "700.50"


# 8. Старая цена
def test_oldprice_present_for_101(offers):
    assert offers["101"].find("oldprice") is not None
    assert offers["101"].find("oldprice").text == "590.00"


def test_oldprice_absent_for_102(offers):
    assert offers["102"].find("oldprice") is None


def test_oldprice_absent_for_107(offers):
    assert offers["107"].find("oldprice") is None


# 9. Формирование предложения — обязательные поля и slug-url
def test_offer_fields(offers):
    expected_slug = {
        "101": "les-i-travy",
        "102": "glass-teapot",
        "107": "milk-oolong",
    }
    for offer_id, offer in offers.items():
        assert (
            offer.find("url").text
            == f"https://example.test/products/{expected_slug[offer_id]}/"
        )
        assert offer.find("currencyId").text == "RUB"
        assert offer.find("picture") is not None
        assert offer.find("categoryId") is not None


def test_picture_value_101(offers):
    assert (
        offers["101"].find("picture").text
        == "https://example.test/media/tea-101.jpg"
    )


# 10. Спецсимволы
def test_special_characters_in_name(offers):
    name_el = offers["101"].find("name")
    assert name_el is not None
    assert name_el.text == 'Чай "Лес & травы" <сбор №1>'


def test_special_characters_in_description(offers):
    assert (
        offers["101"].find("description").text
        == "Вкус: мята & чабрец > классический чай"
    )


# 11. Описание
def test_description_absent_for_107(offers):
    assert offers["107"].find("description") is None


# Структура: валюты и категории перед предложениями (официальный формат YML)
def test_shop_header(root):
    shop = root.find("shop")
    assert shop.find("name").text == "Test Shop"
    assert shop.find("company").text == "Test Company"
    assert shop.find("url").text == "https://example.test"
    currency = shop.find("currencies/currency")
    assert currency.get("id") == "RUB"
    assert currency.get("rate") == "1"

    tags = [child.tag for child in shop]
    assert tags.index("currencies") < tags.index("offers")
    assert tags.index("categories") < tags.index("offers")
