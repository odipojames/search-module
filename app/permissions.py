from rest_framework.permissions import BasePermission


class IsApplicant(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "normal"


class IsRegistrar(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "is_registrar"


class IsRegistrarInCharge(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "is_registrar_in_charge"
