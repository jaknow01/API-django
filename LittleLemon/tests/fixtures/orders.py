import pytest
from LittleLemonAPI.models import Order, OrderItem


@pytest.fixture
def create_order(db):
    """
    Fixture do tworzenia zamówień
    Użycie: order = create_order(user=user, status=False)
    """
    def make_order(user, delivery_crew=None, status=False, total=0):
        return Order.objects.create(
            user=user,
            delivery_crew=delivery_crew,
            status=status,
            total=total
        )
    return make_order


@pytest.fixture
def create_order_item(db):
    """
    Fixture do tworzenia order items
    Użycie: item = create_order_item(order=order, menuitem=menu_item, quantity=2)
    """
    def make_order_item(order, menuitem, quantity=1, unit_price=None, price=None):
        if unit_price is None:
            unit_price = menuitem.price
        if price is None:
            price = unit_price * quantity
        
        return OrderItem.objects.create(
            order=order,
            menuitem=menuitem,
            quantity=quantity,
            unit_price=unit_price,
            price=price
        )
    return make_order_item


@pytest.fixture
def customer_order(customer_user, create_order):
    """Pojedyncze zamówienie dla customer"""
    return create_order(user=customer_user, total=25.50)


@pytest.fixture
def customer_order_with_items(customer_user, create_order, create_order_item, multiple_menu_items):
    """Zamówienie z produktami dla customer"""
    order = create_order(user=customer_user, total=0)
    
    total = 0
    for menu_item in multiple_menu_items:
        create_order_item(order=order, menuitem=menu_item, quantity=1)
        total += menu_item.price
    
    order.total = total
    order.save()
    
    return order


@pytest.fixture
def delivery_order(delivery_user, create_order, customer_user):
    """Zamówienie przypisane do delivery crew"""
    return create_order(user=customer_user, delivery_crew=delivery_user, status=False, total=30.00)
