from rest_framework.permissions import IsAuthenticated, BasePermission, AllowAny
from users.models import MerchantPhone

import constants


class OwnerPermission(BasePermission):
    message = 'Вы должны быть создателем обьекта что бы его изменять'

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
    message = 'Вы должны быть клиентом'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == constants.ROLE_CLIENT


class IsMerchant(BasePermission):
    message = 'Вы должны быть специалистом'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == constants.ROLE_MERCHANT


class HasPhone(BasePermission):
    message = 'У вас нет подтвержденного номера телефона'

    def has_permission(self, request, view):
        return request.user.is_authenticated and \
               MerchantPhone.objects.filter(user=request.user, is_valid=True).count() > 0
