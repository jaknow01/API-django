import pytest
from LittleLemonAPI.models import Cart


@pytest.fixture
def create_cart_item(db):
    """
    Fixture do tworzenia cart items
    Użycie: item = create_cart_item(user=user, menuitem=menu_item, quantity=2)
    """
    def make_cart_item(user, menuitem, quantity=1, unit_price=None, price=None):
        if unit_price is None:
            unit_price = menuitem.price
        if price is None:
            price = unit_price * quantity
        
        return Cart.objects.create(
            user=user,
            menuitem=menuitem,
            quantity=quantity,
            unit_price=unit_price,
            price=price
        )
    return make_cart_item


@pytest.fixture
def customer_cart(customer_user, menu_item, create_cart_item):
    """Koszyk z jednym produktem dla customer"""
    return create_cart_item(user=customer_user, menuitem=menu_item, quantity=2)


@pytest.fixture
def customer_cart_multiple_items(customer_user, multiple_menu_items, create_cart_item):
    """Koszyk z wieloma produktami dla customer"""
    cart_items = []
    for menu_item in multiple_menu_items:
        cart_items.append(
            create_cart_item(user=customer_user, menuitem=menu_item, quantity=1)
        )
    return cart_items
