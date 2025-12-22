from rest_framework import serializers
from models import MenuItem

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model=User
#         fields=["id", "name", "surname"]

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'price']