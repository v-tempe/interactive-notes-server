from rest_framework import permissions

from notes.models import Collaborator


class IsOwnerOrCollaborator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # owner always has permission
        if obj.owner == request.user:
            return True

        # check if user is a collaborator
        collaborator = Collaborator.objects.filter(notebook=obj, user=request.user).first()
        if not collaborator:
            return False

        # if method is safe, then give permissions
        if request.method in permissions.SAFE_METHODS:
            return True

        # for changing need an editor role
        return collaborator.role == 'editor'
