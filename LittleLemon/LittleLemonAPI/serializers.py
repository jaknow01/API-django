from rest_framework import serializers
from django.contrib.auth.models import User
from .models import MenuItem, Cart, Order, OrderItem


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'price']


class CartSerializer(serializers.ModelSerializer):
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'menuitem', 'quantity', 'unit_price', 'price']
        read_only_fields = ['user', 'unit_price', 'price']
    
    def create(self, validated_data):
        # Automatycznie pobierz cenę z MenuItem
        menuitem = validated_data['menuitem']
        quantity = validated_data['quantity']
        
        validated_data['unit_price'] = menuitem.price
        validated_data['price'] = menuitem.price * quantity
        validated_data['user'] = self.context['request'].user
        
        return super().create(validated_data)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'menuitem', 'quantity', 'unit_price', 'price']


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date', 'order_items']