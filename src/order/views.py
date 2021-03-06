import datetime, json
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from main.utils import TYPE_OF_ORDER_DICT, ORDER_INV_TO_CUSTOMER, ORDER_CUSTOMER_TO_INV, \
    ORDER_GUIDION_TO_INV, ORDER_INV_TO_GUIDION
from order.models import Order, Product

from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from serializers import OrderSerializer, ProductSerializer


@csrf_exempt
def adjust_order(request, **kwargs):
    now = datetime.datetime.now()
    html = "test - {now}".format(now=now)
    retour_defect = False
    type = 'Regular'
    order_id = kwargs.get('order_id', None)
    batch_size = kwargs.get('batch_size', None)
    if batch_size:
        batch_size = int(batch_size)

    if order_id is None or batch_size is None:
        body = json.loads(request.body)
        if 'order_id' in body:
            order_id = body['order_id']
        if 'batch_size' in body:
            batch_size = body['batch_size']
        if 'type' in body:
            type = body['type']
        if 'date' in body:
            date = body['date']
        if 'product_id' in body:
            product_id = body['product_id']

    if batch_size is None:
        return HttpResponseBadRequest('Bad Request')

    try:
        batch_size = int(batch_size)
    except:
        return HttpResponseBadRequest('Bad Request')

    update_or_add = None
    if TYPE_OF_ORDER_DICT[type] == ORDER_INV_TO_CUSTOMER or TYPE_OF_ORDER_DICT[type] == ORDER_INV_TO_GUIDION:
        update_or_add = 'remove'

    if TYPE_OF_ORDER_DICT[type] == ORDER_GUIDION_TO_INV or TYPE_OF_ORDER_DICT[type] == ORDER_CUSTOMER_TO_INV:
        update_or_add = 'add'

    # Updating quantity of product
    try:
        product = Product.objects.get(pk=product_id)

        order = Order(product=product)
        order.quantity = batch_size
        order.type = type
        order.order_date = date
        order.save()

        if update_or_add == 'add':
            product.quantity += order.quantity
        if update_or_add == 'remove':
            product.quantity -= order.quantity
        product.save()

    except Product.DoesNotExist:
        return HttpResponseNotFound('Product Not Found')

    html = order.pk

    return HttpResponse(html)


class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows orders to be viewed or edited.
    """
    queryset = Order.objects.all().order_by('-modified')
    serializer_class = OrderSerializer

    def get_queryset(self):
        qs = super(OrderViewSet, self).get_queryset()
        date_start = datetime.datetime.strftime(datetime.datetime.today(), '%Y-%m-%d')
        if 'date_start' in self.request.QUERY_PARAMS:
            date_start = self.request.QUERY_PARAMS['date_start']
            date_start = datetime.datetime.strptime(date_start, '%d-%m-%Y')

        qs = qs.filter(created__gte=date_start)
        return qs


class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows products to be viewed or edited.
    """
    queryset = Product.objects.all().order_by('name')
    serializer_class = ProductSerializer
