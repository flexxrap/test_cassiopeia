import xml.etree.ElementTree as ET
from datetime import datetime

import pytest

from feed_task import CATEGORIES, PRODUCTS, build_yml


@pytest.fixture(scope="module")
def result():
    return build_yml(PRODUCTS, CATEGORIES, datetime(2026, 6, 18, 12, 0))


@pytest.fixture(scope="module")
def root(result):
    return ET.fromstring(result)


@pytest.fixture(scope="module")
def offers(root):
    return {o.get("id"): o for o in root.findall(".//offer")}


def test_valid_xml(result):
    ET.fromstring(result)


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
