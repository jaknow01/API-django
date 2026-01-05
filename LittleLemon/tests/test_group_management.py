import pytest
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestManagerGroupManagement:
    """Testy zarządzania grupą managers przez Manager"""
    
    def test_manager_can_list_managers(self, api_client, manager_user, create_user):
        """Manager może pobierać listę managerów - GET /api/groups/manager/users -> 200"""
        # Utwórz dodatkowych managerów
        create_user(username='manager2', groups=['managers'])
        create_user(username='manager3', groups=['managers'])
        
        token = Token.objects.create(user=manager_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.get('/api/groups/manager/users')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3  # manager_user + 2 nowych
    
    def test_manager_can_assign_user_to_managers(self, api_client, manager_user, create_user):
        """Manager może dodać użytkownika do grupy managers - POST /api/groups/manager/users -> 201"""
        new_user = create_user(username='newmanager')
        
        token = Token.objects.create(user=manager_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.post('/api/groups/manager/users', {
            'username': 'newmanager'
        })
        
        assert response.status_code == status.HTTP_201_CREATED
        assert new_user.groups.filter(name='managers').exists()
    
    def test_manager_can_remove_user_from_managers(self, api_client, manager_user, create_user):
        """Manager może usunąć użytkownika z grupy managers - DELETE /api/groups/manager/users/{id} -> 200"""
        user_to_remove = create_user(username='removemanager', groups=['managers'])
        
        token = Token.objects.create(user=manager_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.delete(f'/api/groups/manager/users/{user_to_remove.id}')
        
        assert response.status_code == status.HTTP_200_OK
        assert not user_to_remove.groups.filter(name='managers').exists()
    
    def test_manager_delete_nonexistent_user_returns_404(self, api_client, manager_user):
        """Manager dostaje 404 przy usuwaniu nieistniejącego użytkownika - DELETE -> 404"""
        token = Token.objects.create(user=manager_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.delete('/api/groups/manager/users/99999')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_manager_assign_nonexistent_user_returns_404(self, api_client, manager_user):
        """Manager dostaje 404 przy dodawaniu nieistniejącego użytkownika - POST -> 404"""
        token = Token.objects.create(user=manager_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.post('/api/groups/manager/users', {
            'username': 'nonexistentuser'
        })
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestDeliveryCrewGroupManagement:
    """Testy zarządzania grupą delivery crew przez Manager"""
    
    def test_manager_can_list_delivery_crew(self, api_client, manager_user, create_user):
        """Manager może pobierać listę delivery crew - GET /api/groups/delivery-crew/users -> 200"""
        create_user(username='delivery1', groups=['delivery'])
        create_user(username='delivery2', groups=['delivery'])
        
        token = Token.objects.create(user=manager_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.get('/api/groups/delivery-crew/users')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
    
    def test_manager_can_assign_user_to_delivery_crew(self, api_client, manager_user, create_user):
        """Manager może dodać użytkownika do delivery crew - POST /api/groups/delivery-crew/users -> 201"""
        new_user = create_user(username='newdelivery')
        
        token = Token.objects.create(user=manager_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.post('/api/groups/delivery-crew/users', {
            'username': 'newdelivery'
        })
        
        assert response.status_code == status.HTTP_201_CREATED
        assert new_user.groups.filter(name='delivery').exists()
    
    def test_manager_can_remove_user_from_delivery_crew(self, api_client, manager_user, create_user):
        """Manager może usunąć użytkownika z delivery crew - DELETE /api/groups/delivery-crew/users/{id} -> 200"""
        user_to_remove = create_user(username='removedelivery', groups=['delivery'])
        
        token = Token.objects.create(user=manager_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.delete(f'/api/groups/delivery-crew/users/{user_to_remove.id}')
        
        assert response.status_code == status.HTTP_200_OK
        assert not user_to_remove.groups.filter(name='delivery').exists()
    
    def test_manager_delete_nonexistent_delivery_returns_404(self, api_client, manager_user):
        """Manager dostaje 404 przy usuwaniu nieistniejącego delivery - DELETE -> 404"""
        token = Token.objects.create(user=manager_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.delete('/api/groups/delivery-crew/users/99999')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_manager_assign_nonexistent_delivery_returns_404(self, api_client, manager_user):
        """Manager dostaje 404 przy dodawaniu nieistniejącego delivery - POST -> 404"""
        token = Token.objects.create(user=manager_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.post('/api/groups/delivery-crew/users', {
            'username': 'nonexistentuser'
        })
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestGroupManagementCustomer:
    """Testy zarządzania grupami przez Customer (brak dostępu)"""
    
    def test_customer_cannot_list_managers(self, api_client, customer_user):
        """Customer NIE może pobierać listy managerów - GET -> 403"""
        token = Token.objects.create(user=customer_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.get('/api/groups/manager/users')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_customer_cannot_assign_to_managers(self, api_client, customer_user, create_user):
        """Customer NIE może dodawać do grupy managers - POST -> 403"""
        new_user = create_user(username='newuser')
        
        token = Token.objects.create(user=customer_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.post('/api/groups/manager/users', {
            'username': 'newuser'
        })
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_customer_cannot_remove_from_managers(self, api_client, customer_user, manager_user):
        """Customer NIE może usuwać z grupy managers - DELETE -> 403"""
        token = Token.objects.create(user=customer_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.delete(f'/api/groups/manager/users/{manager_user.id}')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_customer_cannot_list_delivery_crew(self, api_client, customer_user):
        """Customer NIE może pobierać listy delivery crew - GET -> 403"""
        token = Token.objects.create(user=customer_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.get('/api/groups/delivery-crew/users')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_customer_cannot_assign_to_delivery_crew(self, api_client, customer_user, create_user):
        """Customer NIE może dodawać do delivery crew - POST -> 403"""
        new_user = create_user(username='newuser')
        
        token = Token.objects.create(user=customer_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.post('/api/groups/delivery-crew/users', {
            'username': 'newuser'
        })
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_customer_cannot_remove_from_delivery_crew(self, api_client, customer_user, delivery_user):
        """Customer NIE może usuwać z delivery crew - DELETE -> 403"""
        token = Token.objects.create(user=customer_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.delete(f'/api/groups/delivery-crew/users/{delivery_user.id}')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestGroupManagementDeliveryCrew:
    """Testy zarządzania grupami przez Delivery Crew (brak dostępu)"""
    
    def test_delivery_cannot_list_managers(self, api_client, delivery_user):
        """Delivery crew NIE może pobierać listy managerów - GET -> 403"""
        token = Token.objects.create(user=delivery_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.get('/api/groups/manager/users')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delivery_cannot_assign_to_managers(self, api_client, delivery_user, create_user):
        """Delivery crew NIE może dodawać do grupy managers - POST -> 403"""
        new_user = create_user(username='newuser')
        
        token = Token.objects.create(user=delivery_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.post('/api/groups/manager/users', {
            'username': 'newuser'
        })
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delivery_cannot_remove_from_managers(self, api_client, delivery_user, manager_user):
        """Delivery crew NIE może usuwać z grupy managers - DELETE -> 403"""
        token = Token.objects.create(user=delivery_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.delete(f'/api/groups/manager/users/{manager_user.id}')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delivery_cannot_list_delivery_crew(self, api_client, delivery_user):
        """Delivery crew NIE może pobierać listy delivery crew - GET -> 403"""
        token = Token.objects.create(user=delivery_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.get('/api/groups/delivery-crew/users')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delivery_cannot_assign_to_delivery_crew(self, api_client, delivery_user, create_user):
        """Delivery crew NIE może dodawać do delivery crew - POST -> 403"""
        new_user = create_user(username='newuser')
        
        token = Token.objects.create(user=delivery_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.post('/api/groups/delivery-crew/users', {
            'username': 'newuser'
        })
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delivery_cannot_remove_from_delivery_crew(self, api_client, delivery_user, create_user):
        """Delivery crew NIE może usuwać z delivery crew - DELETE -> 403"""
        other_delivery = create_user(username='otherdelivery', groups=['delivery'])
        
        token = Token.objects.create(user=delivery_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.delete(f'/api/groups/delivery-crew/users/{other_delivery.id}')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestGroupManagementUnauthenticated:
    """Testy zarządzania grupami przez niezalogowanych użytkowników"""
    
    def test_unauthenticated_cannot_list_managers(self, api_client):
        """Niezalogowany NIE może pobierać listy managerów - GET -> 401"""
        response = api_client.get('/api/groups/manager/users')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_unauthenticated_cannot_assign_to_managers(self, api_client):
        """Niezalogowany NIE może dodawać do grupy managers - POST -> 401"""
        response = api_client.post('/api/groups/manager/users', {
            'username': 'someuser'
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_unauthenticated_cannot_remove_from_managers(self, api_client):
        """Niezalogowany NIE może usuwać z grupy managers - DELETE -> 401"""
        response = api_client.delete('/api/groups/manager/users/1')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_unauthenticated_cannot_list_delivery_crew(self, api_client):
        """Niezalogowany NIE może pobierać listy delivery crew - GET -> 401"""
        response = api_client.get('/api/groups/delivery-crew/users')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_unauthenticated_cannot_assign_to_delivery_crew(self, api_client):
        """Niezalogowany NIE może dodawać do delivery crew - POST -> 401"""
        response = api_client.post('/api/groups/delivery-crew/users', {
            'username': 'someuser'
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_unauthenticated_cannot_remove_from_delivery_crew(self, api_client):
        """Niezalogowany NIE może usuwać z delivery crew - DELETE -> 401"""
        response = api_client.delete('/api/groups/delivery-crew/users/1')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
