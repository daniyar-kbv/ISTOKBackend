from rest_framework.permissions import IsAuthenticated, BasePermission, AllowAny

import constants

class OwnerPermission(BasePermission):
    message = 'You must be logged in or the owner of the order to update/delete.'

    def has_permission(self, request, view):
        if view.action not in ['list', 'retrieve']:
            return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.is_staff:
            return True
        if view.action in ['update', 'partial_update', 'destroy']:
            return request.user == obj.user
        return True


class IsClient(BasePermission):
    message = 'You must be logged in or the owner of the order to update/delete.'

    def has_permission(self, request, view):
        if view.action not in ['list', 'retrieve']:
            return request.user.is_authenticated and request.user.role == constants.ROLE_CLIENT
        return True


class IsMerchant(BasePermission):
    message = 'You must be logged in or the owner of the order to update/delete.'

    def has_permission(self, request, view):
        if view.action not in ['list', 'retrieve']:
            return request.user.is_authenticated and request.user.role == constants.ROLE_MERCHANT
        return True
