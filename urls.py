"""Пример подключения YML-фида в маршруты Django.

Включите этот модуль в корневой urls.py проекта, например:

    from django.urls import include, path

    urlpatterns = [
        path("", include("urls")),
    ]
"""

from django.urls import path

from views_example import yml_feed

urlpatterns = [
    path("feed.xml", yml_feed, name="yml_feed"),
]
