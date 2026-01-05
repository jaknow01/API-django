import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User, Group

pytest_plugins = [
    'tests.fixtures.users',
    'tests.fixtures.menu_items',
]
