import pytest
from rest_framework import status
from rest_framework.authtoken.models import Token
from LittleLemonAPI.models import Order, OrderItem, Cart


@pytest.mark.django_db
class TestOrdersCustomer:
    """Testy endpointów zamówień dla Customer"""
    
    def test_customer_can_list_own_orders(self, api_client, customer_user, customer_order):
        """Customer może pobierać listę swoich zamówień - GET /api/orders -> 200"""
        token = Token.objects.create(user=customer_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.get('/api/orders')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
    
    def test_customer_sees_only_own_orders(self, api_client, customer_user, create_user, create_order):
        """Customer widzi tylko swoje zamówienia, nie innych użytkowników"""
        other_customer = create_user(username='othercustomer', groups=['customers'])
        
        # Zamówienia customer_user
        create_order(user=customer_user, total=10.00)
        create_order(user=customer_user, total=20.00)
        
        # Zamówienia innego customera
        create_order(user=other_customer, total=50.00)
        
        token = Token.objects.create(user=customer_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.get('/api/orders')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2  # tylko swoje
    
    def test_customer_can_get_own_order_details(self, api_client, customer_user, customer_order_with_items):
        """Customer może pobierać szczegóły swojego zamówienia - GET /api/orders/{id} -> 200"""
        token = Token.objects.create(user=customer_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.get(f'/api/orders/{customer_order_with_items.id}')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == customer_order_with_items.id
        assert 'order_items' in response.data
    
    def test_customer_cannot_get_other_user_order(self, api_client, customer_user, create_user, create_order):
        """Customer NIE może pobierać cudzych zamówień - GET /api/orders/{id} -> 404"""
        other_customer = create_user(username='othercustomer', groups=['customers'])
        other_order = create_order(user=other_customer, total=30.00)
        
        token = Token.objects.create(user=customer_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.get(f'/api/orders/{other_order.id}')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_customer_can_create_order_from_cart(self, api_client, customer_user, customer_cart_multiple_items):
        """Customer może tworzyć zamówienie z koszyka - POST /api/orders -> 201"""
        token = Token.objects.create(user=customer_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        # Przed: 3 produkty w koszyku, 0 zamówień
        assert Cart.objects.filter(user=customer_user).count() == 3
        assert Order.objects.filter(user=customer_user).count() == 0
        
        response = api_client.post('/api/orders', {})
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Po: 0 produktów w koszyku, 1 zamówienie
        assert Cart.objects.filter(user=customer_user).count() == 0
        assert Order.objects.filter(user=customer_user).count() == 1
        
        # Sprawdź czy order items zostały utworzone
        order = Order.objects.get(user=customer_user)
        assert order.order_items.count() == 3
    
    def test_customer_order_calculates_total_price(self, api_client, customer_user, customer_cart_multiple_items):
        """POST /api/orders oblicza całkowitą cenę zamówienia"""
        token = Token.objects.create(user=customer_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        # Oblicz oczekiwaną sumę z koszyka
        expected_total = sum(item.price for item in customer_cart_multiple_items)
        
        response = api_client.post('/api/orders', {})
        
        assert response.status_code == status.HTTP_201_CREATED
        
        order = Order.objects.get(user=customer_user)
        assert float(order.total) == float(expected_total)
    
    def test_customer_cannot_create_order_with_empty_cart(self, api_client, customer_user):
        """Customer NIE może utworzyć zamówienia z pustym koszykiem - POST /api/orders -> 400"""
        token = Token.objects.create(user=customer_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.post('/api/orders', {})
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_customer_cannot_update_order(self, api_client, customer_user, customer_order):
        """Customer NIE może aktualizować zamówienia - PUT /api/orders/{id} -> 403"""
        token = Token.objects.create(user=customer_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.put(f'/api/orders/{customer_order.id}', {
            'status': True
        })
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_customer_cannot_partial_update_order(self, api_client, customer_user, customer_order):
        """Customer NIE może częściowo aktualizować zamówienia - PATCH /api/orders/{id} -> 403"""
        token = Token.objects.create(user=customer_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.patch(f'/api/orders/{customer_order.id}', {
            'status': True
        })
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_customer_cannot_delete_order(self, api_client, customer_user, customer_order):
        """Customer NIE może usuwać zamówienia - DELETE /api/orders/{id} -> 403"""
        token = Token.objects.create(user=customer_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.delete(f'/api/orders/{customer_order.id}')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Order.objects.filter(id=customer_order.id).exists()


@pytest.mark.django_db
class TestOrdersManager:
    """Testy endpointów zamówień dla Manager"""
    
    def test_manager_can_list_all_orders(self, api_client, manager_user, create_user, create_order):
        """Manager może pobierać wszystkie zamówienia - GET /api/orders -> 200"""
        customer1 = create_user(username='customer1', groups=['customers'])
        customer2 = create_user(username='customer2', groups=['customers'])
        
        create_order(user=customer1, total=10.00)
        create_order(user=customer1, total=20.00)
        create_order(user=customer2, total=30.00)
        
        token = Token.objects.create(user=manager_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.get('/api/orders')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3  # wszystkie zamówienia
    
    def test_manager_can_get_any_order_details(self, api_client, manager_user, create_user, customer_order_with_items):
        """Manager może pobierać szczegóły dowolnego zamówienia - GET /api/orders/{id} -> 200"""
        token = Token.objects.create(user=manager_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.get(f'/api/orders/{customer_order_with_items.id}')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == customer_order_with_items.id
    
    def test_manager_can_update_order_status(self, api_client, manager_user, customer_order):
        """Manager może aktualizować status zamówienia - PATCH /api/orders/{id} -> 200"""
        token = Token.objects.create(user=manager_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.patch(f'/api/orders/{customer_order.id}', {
            'status': True
        })
        
        assert response.status_code == status.HTTP_200_OK
        
        customer_order.refresh_from_db()
        assert customer_order.status == True
    
    def test_manager_can_assign_delivery_crew(self, api_client, manager_user, customer_order, delivery_user):
        """Manager może przypisać delivery crew do zamówienia - PATCH /api/orders/{id} -> 200"""
        token = Token.objects.create(user=manager_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.patch(f'/api/orders/{customer_order.id}', {
            'delivery_crew': delivery_user.id
        })
        
        assert response.status_code == status.HTTP_200_OK
        
        customer_order.refresh_from_db()
        assert customer_order.delivery_crew == delivery_user
    
    def test_manager_can_set_order_out_for_delivery(self, api_client, manager_user, customer_order, delivery_user):
        """Manager może ustawić zamówienie jako 'out for delivery' (delivery_crew + status=0)"""
        token = Token.objects.create(user=manager_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.patch(f'/api/orders/{customer_order.id}', {
            'delivery_crew': delivery_user.id,
            'status': False
        })
        
        assert response.status_code == status.HTTP_200_OK
        
        customer_order.refresh_from_db()
        assert customer_order.delivery_crew == delivery_user
        assert customer_order.status == False  # out for delivery
    
    def test_manager_can_set_order_delivered(self, api_client, manager_user, customer_order, delivery_user):
        """Manager może ustawić zamówienie jako 'delivered' (delivery_crew + status=1)"""
        token = Token.objects.create(user=manager_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.patch(f'/api/orders/{customer_order.id}', {
            'delivery_crew': delivery_user.id,
            'status': True
        })
        
        assert response.status_code == status.HTTP_200_OK
        
        customer_order.refresh_from_db()
        assert customer_order.delivery_crew == delivery_user
        assert customer_order.status == True  # delivered
    
    def test_manager_can_delete_order(self, api_client, manager_user, customer_order):
        """Manager może usuwać zamówienia - DELETE /api/orders/{id} -> 204"""
        token = Token.objects.create(user=manager_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        order_id = customer_order.id
        
        response = api_client.delete(f'/api/orders/{order_id}')
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Order.objects.filter(id=order_id).exists()


@pytest.mark.django_db
class TestOrdersDeliveryCrew:
    """Testy endpointów zamówień dla Delivery Crew"""
    
    def test_delivery_can_list_assigned_orders(self, api_client, delivery_user, create_user, create_order):
        """Delivery crew może pobierać tylko przypisane zamówienia - GET /api/orders -> 200"""
        other_delivery = create_user(username='otherdelivery', groups=['delivery'])
        customer = create_user(username='customer1', groups=['customers'])
        
        # Zamówienia przypisane do delivery_user
        create_order(user=customer, delivery_crew=delivery_user, total=10.00)
        create_order(user=customer, delivery_crew=delivery_user, total=20.00)
        
        # Zamówienia przypisane do innego delivery
        create_order(user=customer, delivery_crew=other_delivery, total=30.00)
        
        # Zamówienia bez przypisania
        create_order(user=customer, total=40.00)
        
        token = Token.objects.create(user=delivery_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.get('/api/orders')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2  # tylko swoje
    
    def test_delivery_can_get_assigned_order_details(self, api_client, delivery_user, delivery_order):
        """Delivery crew może pobierać szczegóły przypisanego zamówienia - GET /api/orders/{id} -> 200"""
        token = Token.objects.create(user=delivery_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.get(f'/api/orders/{delivery_order.id}')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == delivery_order.id
    
    def test_delivery_cannot_get_unassigned_order(self, api_client, delivery_user, create_user, create_order):
        """Delivery crew NIE może pobierać niepripisanych zamówień - GET /api/orders/{id} -> 404"""
        customer = create_user(username='customer1', groups=['customers'])
        unassigned_order = create_order(user=customer, total=30.00)
        
        token = Token.objects.create(user=delivery_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.get(f'/api/orders/{unassigned_order.id}')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delivery_can_update_order_status(self, api_client, delivery_user, delivery_order):
        """Delivery crew może aktualizować status zamówienia - PATCH /api/orders/{id} -> 200"""
        token = Token.objects.create(user=delivery_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.patch(f'/api/orders/{delivery_order.id}', {
            'status': True,
        },
            format = "json"
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        delivery_order.refresh_from_db()
        assert delivery_order.status == True
    
    def test_delivery_cannot_update_delivery_crew(self, api_client, delivery_user, delivery_order, create_user):
        """Delivery crew NIE może zmieniać delivery_crew - PATCH /api/orders/{id} -> 403"""
        other_delivery = create_user(username='otherdelivery', groups=['delivery'])
        
        token = Token.objects.create(user=delivery_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.patch(f'/api/orders/{delivery_order.id}', {
            'delivery_crew': other_delivery.id
        })
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delivery_cannot_update_user(self, api_client, delivery_user, delivery_order, create_user):
        """Delivery crew NIE może zmieniać użytkownika zamówienia - PATCH /api/orders/{id} -> 403"""
        other_customer = create_user(username='othercustomer', groups=['customers'])
        
        token = Token.objects.create(user=delivery_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.patch(f'/api/orders/{delivery_order.id}', {
            'user': other_customer.id
        })
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delivery_cannot_update_total(self, api_client, delivery_user, delivery_order):
        """Delivery crew NIE może zmieniać total zamówienia - PATCH /api/orders/{id} -> 403"""
        token = Token.objects.create(user=delivery_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.patch(f'/api/orders/{delivery_order.id}', {
            'total': 999.99
        })
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delivery_cannot_delete_order(self, api_client, delivery_user, delivery_order):
        """Delivery crew NIE może usuwać zamówień - DELETE /api/orders/{id} -> 403"""
        token = Token.objects.create(user=delivery_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = api_client.delete(f'/api/orders/{delivery_order.id}')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Order.objects.filter(id=delivery_order.id).exists()


@pytest.mark.django_db
class TestOrdersUnauthenticated:
    """Testy endpointów zamówień dla niezalogowanych użytkowników"""
    
    def test_unauthenticated_cannot_list_orders(self, api_client):
        """Niezalogowany NIE może pobierać listy zamówień - GET /api/orders -> 401"""
        response = api_client.get('/api/orders')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_unauthenticated_cannot_get_order_details(self, api_client, customer_order):
        """Niezalogowany NIE może pobierać szczegółów zamówienia - GET /api/orders/{id} -> 401"""
        response = api_client.get(f'/api/orders/{customer_order.id}')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_unauthenticated_cannot_create_order(self, api_client):
        """Niezalogowany NIE może tworzyć zamówienia - POST /api/orders -> 401"""
        response = api_client.post('/api/orders', {})
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_unauthenticated_cannot_update_order(self, api_client, customer_order):
        """Niezalogowany NIE może aktualizować zamówienia - PATCH /api/orders/{id} -> 401"""
        response = api_client.patch(f'/api/orders/{customer_order.id}', {
            'status': True
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_unauthenticated_cannot_delete_order(self, api_client, customer_order):
        """Niezalogowany NIE może usuwać zamówienia - DELETE /api/orders/{id} -> 401"""
        response = api_client.delete(f'/api/orders/{customer_order.id}')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
