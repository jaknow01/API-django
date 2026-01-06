import pytest
from rest_framework import status
from LittleLemonAPI.models import Category, MenuItem


@pytest.mark.django_db
class TestMenuItemFiltering:
    """Test suite for filtering menu items by category"""
    
    def test_filter_menu_items_by_category(self, api_client):
        """Users can filter menu items by category"""
        # Create categories
        appetizers = Category.objects.create(slug="appetizers", title="Appetizers")
        mains = Category.objects.create(slug="mains", title="Main Courses")
        
        # Create menu items
        MenuItem.objects.create(name="Spring Rolls", price=8.99, category=appetizers)
        MenuItem.objects.create(name="Garlic Bread", price=5.99, category=appetizers)
        MenuItem.objects.create(name="Steak", price=25.99, category=mains)
        MenuItem.objects.create(name="Pasta", price=15.99, category=mains)
        
        # Filter by appetizers
        response = api_client.get(f"/api/menu-items?category={appetizers.id}")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        assert all(item['name'] in ['Spring Rolls', 'Garlic Bread'] for item in response.data['results'])
    
    def test_filter_menu_items_by_another_category(self, api_client):
        """Users can filter menu items by different category"""
        appetizers = Category.objects.create(slug="appetizers", title="Appetizers")
        mains = Category.objects.create(slug="mains", title="Main Courses")
        
        MenuItem.objects.create(name="Spring Rolls", price=8.99, category=appetizers)
        MenuItem.objects.create(name="Steak", price=25.99, category=mains)
        MenuItem.objects.create(name="Pasta", price=15.99, category=mains)
        
        # Filter by mains
        response = api_client.get(f"/api/menu-items?category={mains.id}")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        assert all(item['name'] in ['Steak', 'Pasta'] for item in response.data['results'])
    
    def test_filter_with_no_results(self, api_client):
        """Filtering by category with no items returns empty list"""
        appetizers = Category.objects.create(slug="appetizers", title="Appetizers")
        empty_category = Category.objects.create(slug="desserts", title="Desserts")
        
        MenuItem.objects.create(name="Spring Rolls", price=8.99, category=appetizers)
        
        response = api_client.get(f"/api/menu-items?category={empty_category.id}")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 0


@pytest.mark.django_db
class TestMenuItemOrdering:
    """Test suite for ordering/sorting menu items by price"""
    
    def test_order_menu_items_by_price_ascending(self, api_client):
        """Users can sort menu items by price (low to high)"""
        MenuItem.objects.create(name="Expensive Dish", price=45.99)
        MenuItem.objects.create(name="Cheap Dish", price=5.99)
        MenuItem.objects.create(name="Medium Dish", price=15.99)
        
        response = api_client.get("/api/menu-items?ordering=price")
        
        assert response.status_code == status.HTTP_200_OK
        prices = [float(item['price']) for item in response.data['results']]
        assert prices == sorted(prices)  # Check ascending order
        assert prices[0] == 5.99
        assert prices[-1] == 45.99
    
    def test_order_menu_items_by_price_descending(self, api_client):
        """Users can sort menu items by price (high to low)"""
        MenuItem.objects.create(name="Expensive Dish", price=45.99)
        MenuItem.objects.create(name="Cheap Dish", price=5.99)
        MenuItem.objects.create(name="Medium Dish", price=15.99)
        
        response = api_client.get("/api/menu-items?ordering=-price")
        
        assert response.status_code == status.HTTP_200_OK
        prices = [float(item['price']) for item in response.data['results']]
        assert prices == sorted(prices, reverse=True)  # Check descending order
        assert prices[0] == 45.99
        assert prices[-1] == 5.99


@pytest.mark.django_db
class TestMenuItemFilteringAndOrdering:
    """Test suite for combining filtering and ordering"""
    
    def test_filter_and_order_menu_items(self, api_client):
        """Users can filter by category and order by price simultaneously"""
        appetizers = Category.objects.create(slug="appetizers", title="Appetizers")
        mains = Category.objects.create(slug="mains", title="Main Courses")
        
        MenuItem.objects.create(name="Expensive Appetizer", price=12.99, category=appetizers)
        MenuItem.objects.create(name="Cheap Appetizer", price=4.99, category=appetizers)
        MenuItem.objects.create(name="Steak", price=25.99, category=mains)
        
        response = api_client.get(f"/api/menu-items?category={appetizers.id}&ordering=price")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        prices = [float(item['price']) for item in response.data['results']]
        assert prices == [4.99, 12.99]  # Filtered appetizers, sorted by price
    
    def test_authenticated_user_can_filter_and_order(self, api_client, customer_user):
        """Authenticated users can filter and order menu items"""
        category = Category.objects.create(slug="appetizers", title="Appetizers")
        MenuItem.objects.create(name="Item A", price=10.99, category=category)
        MenuItem.objects.create(name="Item B", price=5.99, category=category)
        
        api_client.force_authenticate(user=customer_user)
        response = api_client.get(f"/api/menu-items?category={category.id}&ordering=price")
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2


@pytest.mark.django_db
class TestMenuItemPagination:
    """Test suite for pagination of menu items"""
    
    def test_menu_items_are_paginated(self, api_client):
        """Menu items are paginated with default page size"""
        # Create more items than the page size (10)
        for i in range(15):
            MenuItem.objects.create(name=f"Item {i}", price=10.00 + i)
        
        response = api_client.get("/api/menu-items")
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
        assert response.data['count'] == 15
        assert len(response.data['results']) == 10  # Default page size
    
    def test_pagination_with_filtering(self, api_client):
        """Pagination works with filtering"""
        category = Category.objects.create(slug="appetizers", title="Appetizers")
        
        # Create 12 items in the category
        for i in range(12):
            MenuItem.objects.create(name=f"Appetizer {i}", price=5.00 + i, category=category)
        
        response = api_client.get(f"/api/menu-items?category={category.id}")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 12
        assert len(response.data['results']) == 10
        assert response.data['next'] is not None
    
    def test_pagination_with_ordering(self, api_client):
        """Pagination works with ordering"""
        # Create 12 items
        for i in range(12):
            MenuItem.objects.create(name=f"Item {i}", price=10.00 + i)
        
        response = api_client.get("/api/menu-items?ordering=-price")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 12
        assert len(response.data['results']) == 10
        
        # Verify ordering is maintained
        prices = [float(item['price']) for item in response.data['results']]
        assert prices == sorted(prices, reverse=True)
