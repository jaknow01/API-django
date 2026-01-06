from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, viewsets
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404

from .models import MenuItem, Cart, Order, OrderItem, Category
from .serializers import MenuItemSerializer, CartSerializer, OrderSerializer, CategorySerializer
from .permissions import MenuItemPermission, ManagementPermission, CustomerPermission


# Create your views here.
class MenuItemsView(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all().order_by("id")
    serializer_class = MenuItemSerializer
    permission_classes = [MenuItemPermission]
    ordering_fields = ['price']
    filterset_fields = ['category']

class CategoryView(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [MenuItemPermission]

class GroupManagementView(viewsets.ViewSet):
    permission_classes = [ManagementPermission]

    def list(self, request):
        managers = User.objects.filter(groups__name='managers')
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
        serializer = CartSerializer(items, many=True)
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
    
class OrderView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='managers').exists():
            return Order.objects.all()
        elif user.groups.filter(name='delivery').exists():
            return Order.objects.filter(delivery_crew=user)
        else:
            return Order.objects.filter(user=user)
        
    def update(self, request, *args, **kwargs):
        if kwargs.get("partial"):
            return super().update(request, *args, **kwargs)

        if not request.user.groups.filter(name='managers').exists():
            return Response(
                {"error": "Only managers can update orders"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        print(f"User: {request.user.username}")
        print(f"Groups: {list(request.user.groups.values_list('name', flat=True))}")
        print(request.user.groups.filter(name='delivery').exists())
        print(set(request.data.keys()) != {'status'})
        print(set(request.data.keys()))

        if request.user.groups.filter(name='managers').exists():
            return super().partial_update(request, *args, **kwargs)
        
        elif request.user.groups.filter(name='delivery').exists():
            if set(request.data.keys()) != {'status'}:
                return Response(
                    {"error": "Delivery crew can only update status"},
                    status = status.HTTP_403_FORBIDDEN
                )
    
            order_status = request.data.get("status")
            if order_status not in [0, 1, True, False]:
                return Response(
                    {"error": "Status must be 0, 1, true, or false"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return super().partial_update(request, *args, **kwargs)
        
        else:
            return Response(
                {'error': 'Customers cant update orders'},
                status=status.HTTP_403_FORBIDDEN
            )

    def destroy(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='managers').exists():
            return Response(
                {"error": "Only managers can delete orders"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)
    
    def create(self, request):
        if not request.user.groups.filter(name='customer').exists():
            return Response(
                {"error": "Only customers can create orders"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        cart = Cart.objects.filter(user=request.user)
        if not cart.exists():
            return Response(
                {"message": "Cart is empty"},
                status=status.HTTP_400_BAD_REQUEST
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
        order.save()

        cart.delete()
        serializer = OrderSerializer(order)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

        
    
