import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User, Group

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user(db):
    def make_user(username='testuser', email='test@test.com', password='testpass123', groups=None):
        user = User.objects.create_user(username=username, email=email, password=password)
        
        if groups:
            for group_name in groups:
                group, _ = Group.objects.get_or_create(name=group_name)
                user.groups.add(group)
        
        return user
    return make_user

@pytest.fixture
def customer_user(create_user):
    return create_user(username='customer', groups=['customers'])

@pytest.fixture
def manager_user(create_user):
    return create_user(username='manager', groups=['managers'])

@pytest.fixture
def delivery_user(create_user):
    return create_user(username='delivery', groups=['delivery'])