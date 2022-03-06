
import datetime
from .models import *
from rest_framework import serializers


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'


class ProductNamePriceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['fIDX', 'name', 'price', 'image']


class ProductKindSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product_kind
        fields = '__all__'


class CartProuductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart_product
        exclude = ['created_at', 'updated_at']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['fIDX'] = ProductNamePriceSerializer(
            instance.fIDX).data
        return response


class OrderListSerializer(serializers.ListSerializer):

    def create(self, validated_data):
        orders = [Order(**item) for item in validated_data]
        return Order.objects.bulk_create(orders, ignore_conflicts=True)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
    # def update(self, instance, validated_data):
    #     # Maps for id->instance and id->data item.
    #     order_mapping = {order.order_id: order for order in instance}
    #     data_mapping = {item['order_id']: item for item in validated_data}

    #     # Perform creations and updates.
    #     ret = []
    #     for order_id, data in data_mapping.items():
    #         order = order_mapping.get(order_id, None)
    #         if order is None:
    #             ret.append(self.child.create(data))
    #         else:
    #             ret.append(self.child.update(order, data))

    #     # Perform deletions.
    #     for order_id, order in order_mapping.items():
    #         if order_id not in data_mapping:
    #             order.delete()

    #     return ret


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['order_id', 'count', 'price', 'destination', 'fIDX']
        list_serializer_class = OrderListSerializer

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['fIDX'] = ProductNamePriceSerializer(
            instance.fIDX).data
        return response
