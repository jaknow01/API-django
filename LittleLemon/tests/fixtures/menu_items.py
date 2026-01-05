import pytest
from LittleLemonAPI.models import MenuItem


@pytest.fixture
def create_menu_item(db):
    """
    Fixture do tworzenia menu items
    Użycie: item = create_menu_item(name='Pizza', price=15.99)
    """
    def make_menu_item(name='Test Item', price=9.99):
        return MenuItem.objects.create(
            name=name,
            price=price
        )
    return make_menu_item


@pytest.fixture
def menu_item(create_menu_item):
    """Pojedynczy testowy menu item"""
    return create_menu_item(name='Pasta', price=12.50)


@pytest.fixture
def multiple_menu_items(create_menu_item):
    """Lista testowych menu items"""
    return [
        create_menu_item(name='Pizza Margherita', price=15.99),
        create_menu_item(name='Caesar Salad', price=8.50),
        create_menu_item(name='Tiramisu', price=6.99),
    ]
