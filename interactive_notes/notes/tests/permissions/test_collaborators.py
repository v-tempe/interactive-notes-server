from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from ..factories import NotebookFactory, UserFactory, CollaboratorFactory


class PermissionTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = UserFactory.create()
        self.collab = UserFactory.create()
        self.stranger = UserFactory.create()

        self.notebook = NotebookFactory.create(owner=self.owner)
        self.collab_obj = CollaboratorFactory.create(notebook=self.notebook, user=self.collab, role='editor')

        self.token_owner = self._get_token(self.owner)
        self.token_collab = self._get_token(self.collab)
        self.token_stranger = self._get_token(self.stranger)

    def _get_token(self, user):
        response = self.client.post(
            '/api/auth/token/',
            {'username': user.username, 'password': 'defaultpassword'},
        )
        return response.data['access']

    def test_owner_can_manage_collaborators(self):
        """Владелец может добавлять соавторов"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_owner}')
        url = f'/api/notebooks/{self.notebook.id}/collaborators/'
        response = self.client.post(url, {'user': self.stranger.id, 'role': 'viewer'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_collaborator_cannot_add_others(self):
        """Соавтор НЕ может добавлять других людей"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_collab}')
        url = f'/api/notebooks/{self.notebook.id}/collaborators/'
        response = self.client.post(url, {'user': self.stranger.id, 'role': 'viewer'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_stranger_cannot_see_collaborators(self):
        """Посторонний не видит список соавторов"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_stranger}')
        url = f'/api/notebooks/{self.notebook.id}/collaborators/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        if response.status_code == 200:
            self.assertEqual(len(response.data), 0)

    def test_collaborator_cannot_delete_others(self):
        """Соавтор не может удалить другого соавтора"""
        another_collab = UserFactory.create()
        collab_to_delete = CollaboratorFactory.create(
            notebook=self.notebook,
            user=another_collab,
        )

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_collab}')
        url = f'/api/notebooks/{self.notebook.id}/collaborators/{collab_to_delete.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
