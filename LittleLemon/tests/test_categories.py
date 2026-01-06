import pytest
from rest_framework import status
from LittleLemonAPI.models import Category


@pytest.mark.django_db
class TestCategoriesCustomer:
    """Test suite for category endpoints as a customer"""
    
    def test_customer_can_list_categories(self, api_client, customer_user):
        """Customers can view all categories"""
        # Create some categories
        Category.objects.create(slug="appetizers", title="Appetizers")
        Category.objects.create(slug="mains", title="Main Courses")
        Category.objects.create(slug="desserts", title="Desserts")
        
        api_client.force_authenticate(user=customer_user)
        response = api_client.get("/api/categories")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3
    
    def test_customer_can_get_single_category(self, api_client, customer_user):
        """Customers can view a single category"""
        category = Category.objects.create(slug="appetizers", title="Appetizers")
        
        api_client.force_authenticate(user=customer_user)
        response = api_client.get(f"/api/categories/{category.id}")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == "Appetizers"
    
    def test_customer_cannot_create_category(self, api_client, customer_user):
        """Customers cannot create categories"""
        api_client.force_authenticate(user=customer_user)
        response = api_client.post("/api/categories", {
            'slug': 'drinks',
            'title': 'Drinks'
        })
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCategoriesUnauthenticated:
    """Test suite for category endpoints as unauthenticated user"""
    
    def test_unauthenticated_can_list_categories(self, api_client):
        """Unauthenticated users can view all categories"""
        Category.objects.create(slug="appetizers", title="Appetizers")
        Category.objects.create(slug="mains", title="Main Courses")
        
        response = api_client.get("/api/categories")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
    
    def test_unauthenticated_can_get_single_category(self, api_client):
        """Unauthenticated users can view a single category"""
        category = Category.objects.create(slug="appetizers", title="Appetizers")
        
        response = api_client.get(f"/api/categories/{category.id}")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == "Appetizers"
    
    def test_unauthenticated_cannot_create_category(self, api_client):
        """Unauthenticated users cannot create categories"""
        response = api_client.post("/api/categories", {
            'slug': 'drinks',
            'title': 'Drinks'
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestCategoriesManager:
    """Test suite for category endpoints as a manager"""
    
    def test_manager_can_list_categories(self, api_client, manager_user):
        """Managers can view all categories"""
        Category.objects.create(slug="appetizers", title="Appetizers")
        Category.objects.create(slug="mains", title="Main Courses")
        
        api_client.force_authenticate(user=manager_user)
        response = api_client.get("/api/categories")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
    
    def test_manager_can_create_category(self, api_client, manager_user):
        """Managers can create categories"""
        api_client.force_authenticate(user=manager_user)
        response = api_client.post("/api/categories", {
            'slug': 'drinks',
            'title': 'Drinks'
        })
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'Drinks'
        assert Category.objects.filter(slug='drinks').exists()
    
    def test_manager_can_update_category(self, api_client, manager_user):
        """Managers can update categories"""
        category = Category.objects.create(slug="appetizers", title="Appetizers")
        
        api_client.force_authenticate(user=manager_user)
        response = api_client.put(f"/api/categories/{category.id}", {
            'slug': 'starters',
            'title': 'Starters'
        })
        
        assert response.status_code == status.HTTP_200_OK
        category.refresh_from_db()
        assert category.title == 'Starters'
    
    def test_manager_can_delete_category(self, api_client, manager_user):
        """Managers can delete categories"""
        category = Category.objects.create(slug="appetizers", title="Appetizers")
        
        api_client.force_authenticate(user=manager_user)
        response = api_client.delete(f"/api/categories/{category.id}")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Category.objects.filter(id=category.id).exists()


@pytest.mark.django_db
class TestCategoriesDeliveryCrew:
    """Test suite for category endpoints as delivery crew"""
    
    def test_delivery_can_list_categories(self, api_client, delivery_user):
        """Delivery crew can view all categories"""
        Category.objects.create(slug="appetizers", title="Appetizers")
        
        api_client.force_authenticate(user=delivery_user)
        response = api_client.get("/api/categories")
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_delivery_cannot_create_category(self, api_client, delivery_user):
        """Delivery crew cannot create categories"""
        api_client.force_authenticate(user=delivery_user)
        response = api_client.post("/api/categories", {
            'slug': 'drinks',
            'title': 'Drinks'
        })
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
