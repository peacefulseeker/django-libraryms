import pytest
from django.contrib.admin.sites import AdminSite
from django.http import HttpRequest
from mixer.backend.django import mixer

from apps.books.admin.deleted_order import DeletedOrderAdmin, HistoricalOrder
from apps.books.models import Order


@pytest.mark.django_db
def test_deleted_order_admin_get_queryset():
    orders = mixer.cycle(3).blend(Order)

    historical_orders = HistoricalOrder.objects.all()
    deleted_orders = HistoricalOrder.objects.filter(history_type="-")

    assert historical_orders.count() == 3
    assert deleted_orders.count() == 0

    orders[0].delete()

    assert historical_orders.count() == 4
    assert deleted_orders.count() == 1

    admin = DeletedOrderAdmin(HistoricalOrder, AdminSite)
    queryset = admin.get_queryset(HttpRequest())

    assert queryset.count() == 1
    assert queryset.first().pk == deleted_orders.first().pk

    orders[1].delete()

    assert queryset.count() == 2
    assert queryset[1].pk == deleted_orders[1].pk
