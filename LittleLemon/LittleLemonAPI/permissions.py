from rest_framework.permissions import BasePermission

class MenuItemPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method == "GET":
            return True
        
        return (
            request.user and
            request.user.is_authenticated and
            request.user.groups.filter(name="managers").exists()
        )
class ManagementPermission(BasePermission):
    def has_permission(self, request, view):
        return (
            request.is_authenticated and
            request.user.groups.filter(name="managers").exists()
        )
    
class CustomerPermission(BasePermission):
    def has_permission(self, request, view):
        return (
            request.is_authenticated and
            request.user.groups.filter(name="customers").exists()
        )