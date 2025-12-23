from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, viewsets
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404

from .models import MenuItem, Cart, Order, OrderItem
from .serializers import MenuItemSerializer, CartSerializer, OrderSerializer
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
    
    def create(self, request):
        serializer = CartSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def destroy(self, request):
        Cart.objects.filter(user=request.user).delete()
        return Response(
            {'message': 'deleted cart'},
            status=status.HTTP_200_OK
        )
    
class OrderView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user

        if user.groups.filter(name='manager').exists():
            orders = Order.objects.all()
        elif user.groups.filter(name='delivery').exists():
            orders = Order.objects.filter(delivery_crew=user)
        else:
            orders = Order.objects.filter(user=user)

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        if not request.user.groups.filter(name='customer').exists():
            return Response(
                {"error": "Only customers can create orders"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        cart = Cart.objects.filter(user=request.user)
        if not cart:
            return Response(
                {"message": "Cart is empty"},
                status=status.HTTP_404_NOT_FOUND
            )
        order = Order.objects.create(user=request.user)

        for item in cart:
            OrderItem.objects.create(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price
            )
        
        order.total = sum(item.price for item in order.order_items.all())

        cart.delete()
        serializer = OrderSerializer(order)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    
