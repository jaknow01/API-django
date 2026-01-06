import pytest
from rest_framework import status
from rest_framework.authtoken.models import Token
from LittleLemonAPI.models import Cart


@pytest.mark.django_db
class TestCartCustomer:
    """Testy endpointów koszyka dla Customer"""
    
    def test_customer_can_view_own_cart(self, api_client, customer_user, customer_cart):
        """Customer może pobierać swój koszyk - GET /api/cart/menu-items -> 200"""
        token = Token.objects.create(user=customer_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.get('/api/cart/menu-items')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['quantity'] == 2
    
    def test_customer_can_view_cart_with_multiple_items(self, api_client, customer_user, customer_cart_multiple_items):
        """Customer może pobierać koszyk z wieloma produktami - GET /api/cart/menu-items -> 200"""
        token = Token.objects.create(user=customer_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.get('/api/cart/menu-items')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3
    
    def test_customer_sees_only_own_cart_items(self, api_client, customer_user, create_user, menu_item, create_cart_item):
        """Customer widzi tylko swoje produkty w koszyku, nie innych użytkowników"""
        other_customer = create_user(username='othercustomer', groups=['customers'])
        
        # Dodaj produkty do koszyka customera
        create_cart_item(user=customer_user, menuitem=menu_item, quantity=1)
        
        # Dodaj produkty do koszyka innego customera
        create_cart_item(user=other_customer, menuitem=menu_item, quantity=5)
        
        token = Token.objects.create(user=customer_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.get('/api/cart/menu-items')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['quantity'] == 1  # tylko swoje
    
    def test_customer_can_add_item_to_cart(self, api_client, customer_user, menu_item):
        """Customer może dodawać produkty do koszyka - POST /api/cart/menu-items -> 201"""
        token = Token.objects.create(user=customer_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.post('/api/cart/menu-items', {
            'menuitem': menu_item.id,
            'quantity': 3
        })
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Cart.objects.filter(user=customer_user, menuitem=menu_item).exists()
        
        cart_item = Cart.objects.get(user=customer_user, menuitem=menu_item)
        assert cart_item.quantity == 3
        assert float(cart_item.unit_price) == float(menu_item.price)
        assert float(cart_item.price) == float(menu_item.price) * 3
    
    def test_customer_cart_automatically_sets_user(self, api_client, customer_user, menu_item):
        """POST automatycznie ustawia authenticated user jako właściciela cart item"""
        token = Token.objects.create(user=customer_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        # Nie wysyłamy user_id w payloadzie
        response = api_client.post('/api/cart/menu-items', {
            'menuitem': menu_item.id,
            'quantity': 1
        })
        
        assert response.status_code == status.HTTP_201_CREATED
        
        cart_item = Cart.objects.get(menuitem=menu_item)
        assert cart_item.user == customer_user  # Automatycznie ustawione
    
    def test_customer_can_delete_all_cart_items(self, api_client, customer_user, customer_cart_multiple_items):
        """Customer może usunąć wszystkie produkty ze swojego koszyka - DELETE /api/cart/menu-items -> 200"""
        token = Token.objects.create(user=customer_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        # Przed usunięciem: 3 produkty w koszyku
        assert Cart.objects.filter(user=customer_user).count() == 3
        
        response = api_client.delete('/api/cart/menu-items')
        
        assert response.status_code == status.HTTP_200_OK
        # Po usunięciu: 0 produktów
        assert Cart.objects.filter(user=customer_user).count() == 0
    
    def test_customer_delete_only_own_cart_items(self, api_client, customer_user, create_user, menu_item, create_cart_item):
        """DELETE usuwa tylko produkty zalogowanego użytkownika, nie innych"""
        other_customer = create_user(username='othercustomer', groups=['customers'])
        
        # Dodaj produkty do obu koszyków
        create_cart_item(user=customer_user, menuitem=menu_item, quantity=1)
        create_cart_item(user=other_customer, menuitem=menu_item, quantity=5)
        
        token = Token.objects.create(user=customer_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.delete('/api/cart/menu-items')
        
        assert response.status_code == status.HTTP_200_OK
        # Koszyk customera pusty
        assert Cart.objects.filter(user=customer_user).count() == 0
        # Koszyk innego customera niezmieniony
        assert Cart.objects.filter(user=other_customer).count() == 1
    
    def test_customer_can_view_empty_cart(self, api_client, customer_user):
        """Customer może pobierać pusty koszyk - GET /api/cart/menu-items -> 200"""
        token = Token.objects.create(user=customer_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.get('/api/cart/menu-items')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0


@pytest.mark.django_db
class TestCartManager:
    """Testy endpointów koszyka dla Manager (brak dostępu)"""
    
    def test_manager_cannot_view_cart(self, api_client, manager_user):
        """Manager NIE może pobierać koszyka - GET /api/cart/menu-items -> 403"""
        token = Token.objects.create(user=manager_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.get('/api/cart/menu-items')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_manager_cannot_add_to_cart(self, api_client, manager_user, menu_item):
        """Manager NIE może dodawać do koszyka - POST /api/cart/menu-items -> 403"""
        token = Token.objects.create(user=manager_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.post('/api/cart/menu-items', {
            'menuitem': menu_item.id,
            'quantity': 1
        })
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_manager_cannot_delete_cart(self, api_client, manager_user):
        """Manager NIE może usuwać koszyka - DELETE /api/cart/menu-items -> 403"""
        token = Token.objects.create(user=manager_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.delete('/api/cart/menu-items')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCartDeliveryCrew:
    """Testy endpointów koszyka dla Delivery Crew (brak dostępu)"""
    
    def test_delivery_cannot_view_cart(self, api_client, delivery_user):
        """Delivery crew NIE może pobierać koszyka - GET /api/cart/menu-items -> 403"""
        token = Token.objects.create(user=delivery_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.get('/api/cart/menu-items')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delivery_cannot_add_to_cart(self, api_client, delivery_user, menu_item):
        """Delivery crew NIE może dodawać do koszyka - POST /api/cart/menu-items -> 403"""
        token = Token.objects.create(user=delivery_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.post('/api/cart/menu-items', {
            'menuitem': menu_item.id,
            'quantity': 1
        })
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delivery_cannot_delete_cart(self, api_client, delivery_user):
        """Delivery crew NIE może usuwać koszyka - DELETE /api/cart/menu-items -> 403"""
        token = Token.objects.create(user=delivery_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.delete('/api/cart/menu-items')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCartUnauthenticated:
    """Testy endpointów koszyka dla niezalogowanych użytkowników"""
    
    def test_unauthenticated_cannot_view_cart(self, api_client):
        """Niezalogowany NIE może pobierać koszyka - GET /api/cart/menu-items -> 401"""
        response = api_client.get('/api/cart/menu-items')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_unauthenticated_cannot_add_to_cart(self, api_client, menu_item):
        """Niezalogowany NIE może dodawać do koszyka - POST /api/cart/menu-items -> 401"""
        response = api_client.post('/api/cart/menu-items', {
            'menuitem': menu_item.id,
            'quantity': 1
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_unauthenticated_cannot_delete_cart(self, api_client):
        """Niezalogowany NIE może usuwać koszyka - DELETE /api/cart/menu-items -> 401"""
        response = api_client.delete('/api/cart/menu-items')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
