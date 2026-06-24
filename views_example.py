from datetime import datetime

from django.http import HttpResponse

from feed_task import CATEGORIES, PRODUCTS, build_yml


def yml_feed(request):
    xml_bytes = build_yml(PRODUCTS, CATEGORIES, datetime.now())
    return HttpResponse(xml_bytes, content_type="application/xml; charset=utf-8")
