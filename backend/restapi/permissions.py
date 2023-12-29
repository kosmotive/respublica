from rest_framework import permissions


class ProcessPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.owner.player == request.user
