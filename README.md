# Little Lemon Restaurant API Project

## Project Overview
This project involves building a RESTful API for the Little Lemon restaurant, focusing on user roles and functionalities for managers, customers, and delivery personnel. This is the final project from Meta's APIs course available on Coursera [link](https://www.coursera.org/learn/apis?specialization=meta-full-stack-developer).

## User Roles
- **Managers**
  - Can add, edit, and remove menu items.
  - Can update user roles to delivery personnel.
  - Can browse and filter orders by status.

- **Customers**
  - Can browse menu items and filter by categories and price ranges.
  - Can add menu items to their cart and place orders.
  - Can view their order status and total price.

- **Delivery Personnel**
  - Can browse assigned orders and mark them as delivered.

## API Endpoints
- **User Registration and Authentication**
  - Endpoints for user registration and authentication.
  - Token-based authentication required.

- **Menu Management**
  - Endpoints for managers to manage menu items.

- **Order Management**
  - Endpoints for customers to manage their orders and carts.
  - Cart must be emptied upon successful order creation.

- **Delivery Management**
  - Endpoints for managers to assign orders to delivery personnel.
  - Delivery personnel can update order statuses.

## Rate Limiting
- Implement throttling to limit API calls to five per minute.

## Development Tools
- **Framework**: Django with Django REST framework (DRF)
- **Testing Tool**: Insomnia, Pytest

## How to run
```
pip install uv
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## How to run tests
You can either use tools like Insomnia to send your own requests or check out pre-made tests in LittleLemon/tests
