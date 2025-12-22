from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from models import MenuItem
from serializers import MenuItemSerializer

# Create your views here.
class MenuItemView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def post(self, request):
        return Response(data={"info":"This method is not allowed"}, status=status.HTTP_403_FORBIDDEN)
    
    def put(self, request):
        return Response(data={"info":"This method is not allowed"}, status=status.HTTP_403_FORBIDDEN)

    def patch(self, request):
        return Response(data={"info":"This method is not allowed"}, status=status.HTTP_403_FORBIDDEN)
    
    def delete(self, request):
        return Response(data={"info":"This method is not allowed"}, status=status.HTTP_403_FORBIDDEN)
