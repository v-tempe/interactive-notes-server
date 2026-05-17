from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Notebook, Collaborator
from .permissions import IsOwnerOrCollaborator
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
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        notebook_id = self.kwargs['notebook_pk']
        return Collaborator.objects.filter(notebook_id=notebook_id)

    def perform_create(self, serializer):
        notebook_id = self.kwargs['notebook_pk']
        notebook = Notebook.objects.get(id=notebook_id)

        # only owner is allowed to add collaborators
        if notebook.owner != self.request.user:
            raise permissions.PermissionDenied("Только владелец может добавлять соавторов.")

        serializer.save(notebook=notebook)
