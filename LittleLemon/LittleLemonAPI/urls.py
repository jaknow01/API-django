from django.urls import path
from .views import MenuItemsView, GroupManagementView, GroupDeliveryView, CartView, OrderView

urlpatterns = [
    path("menu-items", MenuItemsView.as_view(
        {
            'get': 'list',
            'post': 'create'
        }
    )),
    path("menu-items/<int:pk>", MenuItemsView.as_view(
        {
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy',
        }
    )),
    path('groups/manager/users', GroupManagementView.as_view(
        {
            'get': 'list',
            'post': 'create'
        }
    )),
    path('groups/manager/users/<int:pk>', GroupManagementView.as_view(
        {
            'delete': 'destroy'
        }
    )),
    path('groups/delivery-crew/users', GroupDeliveryView.as_view(
        {
            'get': 'list',
            'post': 'create'
        }
    )),
    path('groups/delivery-crew/users/<int:pk>', GroupDeliveryView.as_view(
        {
            'delete': 'destroy'
        }
    )),
    path('cart/menu-items', CartView.as_view(
        {
            'get': 'list',
            'post': 'create',
            'delete': 'destroy'
        }
    )),
    path('orders', OrderView.as_view(
        {
            'get': 'list',
            'post': 'create'
        }
    )),
    path('orders/<int:pk>', OrderView.as_view(
        {
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy',
        }
    ))
]