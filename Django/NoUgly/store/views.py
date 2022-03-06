from __future__ import barry_as_FLUFL
from email import header
from math import prod
from tkinter.tix import Tree
from typing import Optional
from wsgiref import headers
from .serializers import *
from rest_framework import permissions, viewsets, status
from accounts.permissions import IsUserOrReadOnly
from .pagination import CartProuductNumberPagination, ProductPageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import F


class ProductKindViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product_kind.objects.all()
    serializer_class = ProductKindSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsUserOrReadOnly]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = ProductPageNumberPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    search_fields = ['name']
    filterset_fields = ['kind']
    ordering_fields = ['hitcount']
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsUserOrReadOnly]

    @action(detail=False, methods=['GET'])
    def random(self, request, *args, **kwargs):
        pr = []
        count = 0
        while True:
            if count == 4:
                break
            num = Product.get_random3()
            if num not in pr:
                pr.append(num)
                count += 1
        serializer = self.get_serializer(pr, many=True)
        return Response(serializer.data, status=200)

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.hitcount = F('hitcount') + 1
        obj.save(update_fields=['hitcount', ])
        obj.refresh_from_db()
        serializer = self.get_serializer(obj)
        return Response(serializer.data, status=200)


class CartProuductViewSet(viewsets.ModelViewSet):
    queryset = Cart_product.objects.all()
    serializer_class = CartProuductSerializer
    pagination_class = CartProuductNumberPagination

    permission_classes = [
        permissions.IsAuthenticated, IsUserOrReadOnly]

    # 장바구니 전체삭제 구현

    @ action(detail=False, methods=['DELETE'])
    def allDelete(self, request, *args, **kwargs):
        if request.method == 'DELETE':
            queryset = self.get_queryset().delete()
        return Response(queryset)

    def get_queryset(self):
        user = self.request.user
        queryset = Cart_product.objects.filter(uIDX=user)

        return queryset

    def create(self, request, *args, **kwargs):
        serializer: CartProuductSerializer = self.get_serializer(
            data=request.data)
        serializer.is_valid(raise_exception=True)
        fIDX = serializer.validated_data['fIDX']
        cart_product: Optional[Cart_product] = self.get_queryset().filter(
            fIDX=fIDX).first()

        if cart_product is not None:
            cart_product.quantity = F('quantity') + \
                serializer.validated_data["quantity"]
            cart_product.save()
            cart_product.refresh_from_db()
            return Response(self.get_serializer(cart_product, many=False).data, status=status.HTTP_200_OK)
        else:
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    permission_classes = [
        permissions.IsAuthenticated, IsUserOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        # qu = Cart_product.objects.filter(uIDX=user)
        # qu.delete()
        queryset = Order.objects.filter(uIDX=user)

        return queryset

    def create(self, request, *args, **kwargs):
        many = isinstance(request.data, list)
        print("many : ", many)
        if not many:
            serializer = self.get_serializer(data=request.data, many=many)
            print("시리얼라이저 단일존재 :", serializer)
            serializer.is_valid(raise_exception=True)
            user = self.request.user
            serializer.save(uIDX_id=user.id)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, headers=headers, status=status.HTTP_201_CREATED)
        else:
            serializer = self.get_serializer(data=request.data, many=many)
            print("시리얼라이저 복수존재 :", serializer)
            serializer.is_valid(raise_exception=True)
            user = self.request.user
            serializer.save(uIDX_id=user.id)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, headers=headers, status=status.HTTP_201_CREATED)
