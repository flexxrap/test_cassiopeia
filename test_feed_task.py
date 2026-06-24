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


def test_returns_str_with_declaration(result):
    assert isinstance(result, str)
    assert result.startswith('<?xml version="1.0" encoding="UTF-8"?>')


def test_valid_xml(result):
    ET.fromstring(result.encode("utf-8"))


def test_only_expected_products(offers):
    assert set(offers.keys()) == {"101", "102", "107"}


def test_categories_sorted_no_duplicates(root):
    cat_ids = [cat.get("id") for cat in root.findall(".//category")]
    assert cat_ids == ["1", "2"]


def test_available_true_101_and_107(offers):
    assert offers["101"].get("available") == "true"
    assert offers["107"].get("available") == "true"


def test_available_false_102(offers):
    assert offers["102"].get("available") == "false"


def test_oldprice_present_for_101(offers):
    assert offers["101"].find("oldprice") is not None


def test_oldprice_absent_for_102(offers):
    assert offers["102"].find("oldprice") is None


def test_oldprice_absent_for_107(offers):
    assert offers["107"].find("oldprice") is None


def test_description_absent_for_107(offers):
    assert offers["107"].find("description") is None


def test_special_characters_in_name(offers):
    name_el = offers["101"].find("name")
    assert name_el is not None
    assert name_el.text == 'Чай "Лес & травы" <сбор №1>'


def test_date_format(root):
    assert root.get("date") == "2026-06-18 12:00"


def test_offer_url_and_currency(offers):
    for offer_id, offer in offers.items():
        url_el = offer.find("url")
        assert url_el is not None
        assert url_el.text == f"https://example.test/products/{offer_id}/"
        currency_el = offer.find("currencyId")
        assert currency_el is not None
        assert currency_el.text == "RUB"


def test_offer_picture_present(offers):
    for offer in offers.values():
        assert offer.find("picture") is not None


def test_shop_header_fields(root):
    shop = root.find("shop")
    assert shop.find("name").text == "Test Shop"
    assert shop.find("company").text == "Test Company"
    assert shop.find("url").text == "https://example.test"
    currency = shop.find("currencies/currency")
    assert currency is not None
    assert currency.get("id") == "RUB"
    assert currency.get("rate") == "1"


def test_shop_header_before_categories(root):
    children = [child.tag for child in root.find("shop")]
    assert children.index("name") < children.index("categories")
    assert children.index("currencies") < children.index("categories")
