import pytest
from LittleLemonAPI.models import MenuItem, Category


@pytest.fixture
def create_category(db):
    """
    Fixture do tworzenia kategorii
    Użycie: category = create_category(title='Desserts', slug='desserts')
    """
    def make_category(title='Test Category', slug='test-category'):
        return Category.objects.create(
            title=title,
            slug=slug
        )
    return make_category


@pytest.fixture
def test_category(create_category):
    """Pojedyncza testowa kategoria"""
    return create_category(title='Main Course', slug='main-course')


@pytest.fixture
def create_menu_item(db, test_category):
    """
    Fixture do tworzenia menu items
    Użycie: item = create_menu_item(name='Pizza', price=15.99)
    """
    def make_menu_item(name='Test Item', price=9.99, featured=False, category=None):
        if category is None:
            category = test_category
        return MenuItem.objects.create(
            name=name,
            price=price,
            featured=featured,
            category=category
        )
    return make_menu_item


@pytest.fixture
def menu_item(create_menu_item):
    """Pojedynczy testowy menu item"""
    return create_menu_item(name='Pasta', price=12.50)


@pytest.fixture
def multiple_menu_items(create_menu_item, create_category):
    """Lista testowych menu items"""
    dessert_category = create_category(title='Desserts', slug='desserts')
    salad_category = create_category(title='Salads', slug='salads')
    
    return [
        create_menu_item(name='Pizza Margherita', price=15.99, featured=True),
        create_menu_item(name='Caesar Salad', price=8.50, category=salad_category),
        create_menu_item(name='Tiramisu', price=6.99, category=dessert_category),
    ]
