from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from notes.tests.factories import NotebookFactory, UserFactory, CollaboratorFactory


class NotebookPermissionTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = UserFactory.create()
        self.collab = UserFactory.create()
        self.stranger = UserFactory.create()

        self.notebook = NotebookFactory.create(owner=self.owner)
        # Добавляем соавтора с ролью редактора
        CollaboratorFactory.create(notebook=self.notebook, user=self.collab, role='editor')

        self.token_owner = self._get_token(self.owner)
        self.token_collab = self._get_token(self.collab)
        self.token_stranger = self._get_token(self.stranger)

    def _get_token(self, user):
        response = self.client.post(
            '/api/auth/token/',
            {'username': user.username, 'password': 'defaultpassword'},
        )
        return response.data['access']

    def test_owner_can_delete_notebook(self):
        """Владелец может удалить свой конспект"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_owner}')
        url = f'/api/notebooks/{self.notebook.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_collaborator_cannot_delete_notebook(self):
        """Соавтор (даже editor) не может удалить конспект"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_collab}')
        url = f'/api/notebooks/{self.notebook.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_stranger_cannot_access_notebook(self):
        """Посторонний пользователь не видит чужой конспект"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_stranger}')
        url = f'/api/notebooks/{self.notebook.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_collaborator_can_update_content(self):
        """Соавтор с ролью editor может изменять название конспекта"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_collab}')
        url = f'/api/notebooks/{self.notebook.id}/'
        response = self.client.patch(url, {'title': 'Новое название'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
