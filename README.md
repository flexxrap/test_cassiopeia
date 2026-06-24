# test_cassiopeia

Генератор YML-фида (Yandex Market Language) для каталога товаров.

Функция `build_yml(products, categories, generated_at)` собирает валидный XML
через `xml.etree.ElementTree` с фильтрацией товаров, экранированием спецсимволов
и корректным форматированием цен.

## Структура

| Файл                | Назначение                                              |
|---------------------|---------------------------------------------------------|
| `feed_task.py`      | `build_yml()` + демо-данные `CATEGORIES` / `PRODUCTS`   |
| `test_feed_task.py` | Тесты на `pytest`                                       |
| `views_example.py`  | Пример Django-view, отдающего фид                       |
| `urls.py`           | Пример подключения view в маршруты Django               |

## Правила фильтрации

Товар попадает в фид, только если выполнены **все** условия:

- `is_active == True`;
- категория товара активна (`is_active == True`);
- `name` не пустое;
- `float(price) > 0`;
- `image_url` не `None` и начинается с `http://` или `https://`.

Прочее поведение:

- категории — только используемые отфильтрованными товарами, без дублей, по `id`;
- товары в `<offers>` отсортированы по `id`;
- `available="true"` при `stock > 0`, иначе `"false"`;
- цена — точка-разделитель, два знака после точки;
- `<oldprice>` добавляется только если `old_price` задан, `> 0` и больше текущей цены;
- `<description>` не добавляется для пустого описания;
- дата фида — формат `YYYY-MM-DD HH:MM`.

## Запуск

```bash
pip install -r requirements.txt

# Сгенерировать и вывести XML
python feed_task.py

# Прогнать тесты
pytest -v
```

## Django

```python
# urls.py проекта
from django.urls import path
from views_example import yml_feed

urlpatterns = [
    path("feed.xml", yml_feed, name="yml_feed"),
]
```

View отдаёт `HttpResponse` с `content_type="application/xml; charset=utf-8"`.
