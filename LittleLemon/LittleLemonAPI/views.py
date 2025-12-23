from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404

from .models import MenuItem, Cart, Order
from .serializers import MenuItemSerializer, CartSerializer
from .permissions import MenuItemPermission, ManagementPermission, CustomerPermission


# Create your views here.
class MenuItemsView(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [MenuItemPermission]


class GroupManagementView(viewsets.ViewSet):
    permission_classes = [ManagementPermission]

    def list(self, request):
        managers = User.objects.filter(groups__name='manager')
        return Response([{"id": u.id, "username": u.username, "email": u.email} for u in managers])
    
    def create(self, request):
        username = request.data.get('username')
        user = get_object_or_404(User, username=username)
        group = get_object_or_404(Group, name="managers")
        user.groups.add(group)

        return Response(
            {
                'message': f'Added {username} to the group of managers'
            },
            status=status.HTTP_201_CREATED
        )

    def destroy(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        group = get_object_or_404(Group, name="managers")
        user.groups.remove(group)

        return Response(
            {
                'messages': f"User with id {pk} has been deleted from the managers group"
            },
            status=status.HTTP_200_OK
        )
    
class GroupDeliveryView(viewsets.ViewSet):
    permission_classes = [ManagementPermission]

    def list(self, request):
        delivery_crew = User.objects.filter(groups__name='delivery')
        return Response([{"id": u.id, "username": u.username, "email": u.email} for u in delivery_crew])
    
    def create(self, request):
        username = request.data.get('username')
        user = get_object_or_404(User, username=username)
        group = get_object_or_404(Group, name="delivery")
        user.groups.add(group)

        return Response(
            {
                'message': f'Added {username} to the group of delivery'
            },
            status=status.HTTP_201_CREATED
        )
    
    def destroy(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        group = get_object_or_404(Group, name="delivery")
        user.groups.remove(group)

        return Response(
            {
                'messages': f"User with id {pk} has been deleted from the delivery group"
            },
            status=status.HTTP_200_OK
        )
    
class CartView(viewsets.ViewSet):
    permission_classes = [CustomerPermission]

    def list(self, request):
        items = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(items)
        return Response(serializer.data)