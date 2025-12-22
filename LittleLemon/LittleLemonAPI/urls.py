from django.urls import path
from views import MenuItemView

urlpatterns = [
    path("menu-items/", MenuItemView.as_view()),
    path("menu-items/<int:pk>", MenuItemView.as_view())
]