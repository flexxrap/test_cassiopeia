from datetime import datetime

from django.http import HttpResponse

from feed_task import CATEGORIES, PRODUCTS, build_yml


def yml_feed(request):
    """Отдаёт товарный YML-фид для Яндекс Директа."""
    xml = build_yml(PRODUCTS, CATEGORIES, datetime.now())
    return HttpResponse(xml, content_type="application/xml; charset=utf-8")
