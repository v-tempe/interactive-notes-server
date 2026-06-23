from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from ..factories import NotebookFactory, UserFactory, CollaboratorFactory


class RoleValidationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = UserFactory.create()
        self.token = self._get_token(self.owner)
        self.notebook = NotebookFactory.create(owner=self.owner)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def _get_token(self, user):
        response = self.client.post(
            '/api/auth/token/',
            {'username': user.username, 'password': 'defaultpassword'},
        )
        return response.data['access']

    def test_invalid_role_rejected(self):
        """Сервер отвергает несуществующие роли"""
        user = UserFactory.create()
        url = f'/api/notebooks/{self.notebook.id}/collaborators/'
        response = self.client.post(url, {'user': user.id, 'role': 'superadmin'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_owner_cannot_add_self(self):
        """Владелец не может добавить сам себя как соавтора"""
        url = f'/api/notebooks/{self.notebook.id}/collaborators/'
        response = self.client.post(url, {'user': self.owner.id, 'role': 'editor'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_collaborator_rejected(self):
        """Нельзя добавить одного и того же пользователя дважды"""
        user = UserFactory.create()
        url = f'/api/notebooks/{self.notebook.id}/collaborators/'

        # Первое добавление
        self.client.post(url, {'user': user.id, 'role': 'viewer'}, format='json')

        # Второе добавление
        response = self.client.post(url, {'user': user.id, 'role': 'editor'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
