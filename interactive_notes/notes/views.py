from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from .models import Notebook, Collaborator
from .permissions import IsOwnerOrCollaborator, IsOwner
from .serializers import NotebookSerializer, CollaboratorSerializer


class NotebookViewSet(viewsets.ModelViewSet):
    serializer_class = NotebookSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrCollaborator]

    def get_queryset(self):
        user = self.request.user
        # return objects when user is author or collaborator
        owned = Notebook.objects.filter(owner=user)
        collaborated_ids = Collaborator.objects.filter(user=user).values_list('notebook_id', flat=True)
        collaborated = Notebook.objects.filter(id__in=collaborated_ids)
        return (owned | collaborated).distinct()

    def perform_create(self, serializer):
        # when created, current user become an author
        serializer.save(owner=self.request.user)


class CollaboratorViewSet(viewsets.ModelViewSet):
    serializer_class = CollaboratorSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    lookup_field = 'id'
    lookup_url_kwarg = 'collaborator_pk'

    def get_queryset(self):
        notebook_id = self.kwargs['notebook_pk']
        # only author and collaborators can see list of collaborators

        try:
            notebook = Notebook.objects.get(id=notebook_id)
        except Notebook.DoesNotExist:
            return Collaborator.objects.none()

        if notebook.owner == self.request.user:
            return Collaborator.objects.filter(notebook_id=notebook_id)

        if Collaborator.objects.filter(notebook=notebook, user=self.request.user).exists():
            return Collaborator.objects.filter(notebook_id=notebook_id)

        raise PermissionDenied("Только владелец и соавторы имеют доступ к списку соавторов.")

    def perform_create(self, serializer):
        notebook_id = self.kwargs['notebook_pk']
        try:
            notebook = Notebook.objects.get(id=notebook_id)
        except Notebook.DoesNotExist:
            raise PermissionDenied("Конспект не найден.")

        # only owner is allowed to add collaborators
        if notebook.owner != self.request.user:
            raise PermissionDenied("Только владелец может добавлять соавторов.")

        # author cannot add himself as collaborator
        if serializer.validated_data['user'] == self.request.user:
            raise ValidationError(
                "Владелец конспекта уже имеет полный доступ и не может быть добавлен как соавтор."
            )

        # collaborator cannot add himself again
        if Collaborator.objects.filter(notebook=notebook, user=serializer.validated_data['user']).exists():
            raise ValidationError("Этот пользователь уже является соавтором.")

        serializer.save(notebook=notebook)
