from rest_framework import permissions

from notes.models import Collaborator


class IsOwnerOrCollaborator(permissions.BasePermission):
    """
    Разрешение для объектов Notebook.
    Владелец имеет полные права.
    Соавторы имеют права на чтение (GET, HEAD, OPTIONS).
    Редакторы (editor) имеют права на изменение самого конспекта (PUT, PATCH).
    """

    def has_object_permission(self, request, view, obj):
        # owner always has permission
        if obj.owner == request.user:
            return True

        # check if user is a collaborator
        try:
            collaborator = Collaborator.objects.get(notebook=obj, user=request.user)
        except Collaborator.DoesNotExist:
            return False

        # if method is safe, then give permissions to any collaborator
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.method == 'DELETE':
            return False

        # for changing notebook content need an editor role
        return collaborator.role == 'editor'


class IsOwner(permissions.BasePermission):
    """
    Разрешение для управления соавторами (Collaborator).
    Только владелец ноутбука может добавлять, изменять или удалять соавторов.
    Читать список соавторов могут владелец и сами соавторы.
    """

    def has_permission(self, request, view):
        # check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        notebook = obj.notebook

        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return notebook.owner == request.user

        if request.method in permissions.SAFE_METHODS:
            return notebook.owner == request.user or \
                    obj.user == request.user

        return False
