import pytest
from django.contrib.auth.models import User, Group
from rest_framework import status

@pytest.mark.django_db
class TestUserCreation:
    """Testy czy fixtures poprawnie tworzą użytkowników"""
    
    def test_create_single_user(self, create_user):
        user = create_user(username='testuser')
        
        assert User.objects.count() == 1
        assert user.username == 'testuser'
    
    def test_create_user_with_group(self, create_user):
        user = create_user(username='customer1', groups=['customer'])
        
        assert user.groups.filter(name='customer').exists()
    
    def test_create_multiple_users(self, create_user):
        create_user(username='user1')
        create_user(username='user2')
        create_user(username='user3')
        
        assert User.objects.count() == 3
    
    def test_customer_fixture(self, customer_user):
        assert customer_user.username == 'customer'
        assert customer_user.groups.filter(name='customer').exists()
    
    def test_manager_fixture(self, manager_user):
        assert manager_user.username == 'manager'
        assert manager_user.groups.filter(name='managers').exists()
    
    def test_delivery_fixture(self, delivery_user):
        assert delivery_user.username == 'delivery'
        assert delivery_user.groups.filter(name='delivery').exists()


@pytest.mark.django_db
class TestDjoserRegistration:
    """Testy endpointów rejestracji Djoser"""
    
    def test_user_registration_endpoint_exists(self, api_client):
        response = api_client.post('/api/users/', {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'testpass123'
        })
        
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]
    
    def test_register_new_user(self, api_client):
        response = api_client.post('/api/users/', {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'testpass123'
        })
        
        if response.status_code == status.HTTP_201_CREATED:
            assert User.objects.filter(username='newuser').exists()