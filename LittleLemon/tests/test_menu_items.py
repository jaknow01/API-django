import pytest
from rest_framework import status
from rest_framework.authtoken.models import Token
from LittleLemonAPI.models import MenuItem


@pytest.mark.django_db
class TestMenuItemsCustomer:
    """Testy endpointów menu-items dla Customer"""
    
    def test_customer_can_list_menu_items(self, api_client, customer_user, multiple_menu_items):
        """Customer może pobierać listę menu items - GET /api/menu-items -> 200"""
        token = Token.objects.create(user=customer_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.get('/api/menu-items')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3
    
    def test_customer_can_get_single_menu_item(self, api_client, customer_user, menu_item):
        """Customer może pobierać pojedynczy menu item - GET /api/menu-items/{id} -> 200"""
        token = Token.objects.create(user=customer_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.get(f'/api/menu-items/{menu_item.id}')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == menu_item.name
        assert float(response.data['price']) == float(menu_item.price)
    
    def test_customer_cannot_create_menu_item(self, api_client, customer_user):
        """Customer NIE może tworzyć menu items - POST /api/menu-items -> 403"""
        token = Token.objects.create(user=customer_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.post('/api/menu-items', {
            'name': 'New Pizza',
            'price': 20.00
        })
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_customer_cannot_update_menu_item(self, api_client, customer_user, menu_item):
        """Customer NIE może aktualizować menu items - PUT /api/menu-items/{id} -> 403"""
        token = Token.objects.create(user=customer_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.put(f'/api/menu-items/{menu_item.id}', {
            'name': 'Updated Pizza',
            'price': 25.00
        })
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_customer_cannot_partial_update_menu_item(self, api_client, customer_user, menu_item):
        """Customer NIE może częściowo aktualizować menu items - PATCH /api/menu-items/{id} -> 403"""
        token = Token.objects.create(user=customer_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.patch(f'/api/menu-items/{menu_item.id}', {
            'price': 30.00
        })
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_customer_cannot_delete_menu_item(self, api_client, customer_user, menu_item):
        """Customer NIE może usuwać menu items - DELETE /api/menu-items/{id} -> 403"""
        token = Token.objects.create(user=customer_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.delete(f'/api/menu-items/{menu_item.id}')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert MenuItem.objects.filter(id=menu_item.id).exists()


@pytest.mark.django_db
class TestMenuItemsDeliveryCrew:
    """Testy endpointów menu-items dla Delivery Crew"""
    
    def test_delivery_can_list_menu_items(self, api_client, delivery_user, multiple_menu_items):
        """Delivery crew może pobierać listę menu items - GET /api/menu-items -> 200"""
        token = Token.objects.create(user=delivery_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.get('/api/menu-items')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3
    
    def test_delivery_can_get_single_menu_item(self, api_client, delivery_user, menu_item):
        """Delivery crew może pobierać pojedynczy menu item - GET /api/menu-items/{id} -> 200"""
        token = Token.objects.create(user=delivery_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.get(f'/api/menu-items/{menu_item.id}')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == menu_item.name
    
    def test_delivery_cannot_create_menu_item(self, api_client, delivery_user):
        """Delivery crew NIE może tworzyć menu items - POST /api/menu-items -> 403"""
        token = Token.objects.create(user=delivery_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.post('/api/menu-items', {
            'name': 'New Pizza',
            'price': 20.00
        })
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delivery_cannot_update_menu_item(self, api_client, delivery_user, menu_item):
        """Delivery crew NIE może aktualizować menu items - PUT /api/menu-items/{id} -> 403"""
        token = Token.objects.create(user=delivery_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.put(f'/api/menu-items/{menu_item.id}', {
            'name': 'Updated Pizza',
            'price': 25.00
        })
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delivery_cannot_partial_update_menu_item(self, api_client, delivery_user, menu_item):
        """Delivery crew NIE może częściowo aktualizować menu items - PATCH /api/menu-items/{id} -> 403"""
        token = Token.objects.create(user=delivery_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.patch(f'/api/menu-items/{menu_item.id}', {
            'price': 30.00
        })
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delivery_cannot_delete_menu_item(self, api_client, delivery_user, menu_item):
        """Delivery crew NIE może usuwać menu items - DELETE /api/menu-items/{id} -> 403"""
        token = Token.objects.create(user=delivery_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.delete(f'/api/menu-items/{menu_item.id}')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert MenuItem.objects.filter(id=menu_item.id).exists()


@pytest.mark.django_db
class TestMenuItemsManager:
    """Testy endpointów menu-items dla Manager"""
    
    def test_manager_can_list_menu_items(self, api_client, manager_user, multiple_menu_items):
        """Manager może pobierać listę menu items - GET /api/menu-items -> 200"""
        token = Token.objects.create(user=manager_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.get('/api/menu-items')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3
    
    def test_manager_can_get_single_menu_item(self, api_client, manager_user, menu_item):
        """Manager może pobierać pojedynczy menu item - GET /api/menu-items/{id} -> 200"""
        token = Token.objects.create(user=manager_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.get(f'/api/menu-items/{menu_item.id}')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == menu_item.name
    
    def test_manager_can_create_menu_item(self, api_client, manager_user):
        """Manager może tworzyć menu items - POST /api/menu-items -> 201"""
        token = Token.objects.create(user=manager_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.post('/api/menu-items', {
            'name': 'New Pizza',
            'price': 20.00
        })
        
        assert response.status_code == status.HTTP_201_CREATED
        assert MenuItem.objects.filter(name='New Pizza').exists()
        assert response.data['name'] == 'New Pizza'
        assert float(response.data['price']) == 20.00
    
    def test_manager_can_update_menu_item(self, api_client, manager_user, menu_item):
        """Manager może aktualizować menu items - PUT /api/menu-items/{id} -> 200"""
        token = Token.objects.create(user=manager_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.put(f'/api/menu-items/{menu_item.id}', {
            'name': 'Updated Pasta',
            'price': 25.00
        })
        
        assert response.status_code == status.HTTP_200_OK
        
        menu_item.refresh_from_db()
        assert menu_item.name == 'Updated Pasta'
        assert float(menu_item.price) == 25.00
    
    def test_manager_can_partial_update_menu_item(self, api_client, manager_user, menu_item):
        """Manager może częściowo aktualizować menu items - PATCH /api/menu-items/{id} -> 200"""
        token = Token.objects.create(user=manager_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        original_name = menu_item.name
        
        response = api_client.patch(f'/api/menu-items/{menu_item.id}', {
            'price': 30.00
        })
        
        assert response.status_code == status.HTTP_200_OK
        
        menu_item.refresh_from_db()
        assert menu_item.name == original_name  # nazwa nie zmieniona
        assert float(menu_item.price) == 30.00  # cena zmieniona
    
    def test_manager_can_delete_menu_item(self, api_client, manager_user, menu_item):
        """Manager może usuwać menu items - DELETE /api/menu-items/{id} -> 204"""
        token = Token.objects.create(user=manager_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        item_id = menu_item.id
        
        response = api_client.delete(f'/api/menu-items/{item_id}')
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not MenuItem.objects.filter(id=item_id).exists()


@pytest.mark.django_db
class TestMenuItemsUnauthenticated:
    """Testy endpointów menu-items dla niezalogowanych użytkowników"""
    
    def test_unauthenticated_cannot_list_menu_items(self, api_client, multiple_menu_items):
        """Niezalogowany użytkownik NIE może pobierać listy - GET /api/menu-items -> 401"""
        response = api_client.get('/api/menu-items')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_unauthenticated_cannot_get_single_menu_item(self, api_client, menu_item):
        """Niezalogowany użytkownik NIE może pobierać pojedynczego item - GET /api/menu-items/{id} -> 401"""
        response = api_client.get(f'/api/menu-items/{menu_item.id}')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_unauthenticated_cannot_create_menu_item(self, api_client):
        """Niezalogowany użytkownik NIE może tworzyć - POST /api/menu-items -> 401"""
        response = api_client.post('/api/menu-items', {
            'name': 'New Pizza',
            'price': 20.00
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
