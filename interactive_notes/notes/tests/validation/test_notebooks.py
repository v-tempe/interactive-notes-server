from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from notes.tests.factories import NotebookFactory, UserFactory


class NotebookValidationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory.create()
        self.token = self._get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def _get_token(self, user):
        response = self.client.post(
            '/api/auth/token/',
            {'username': user.username, 'password': 'defaultpassword'},
        )
        return response.data['access']

    def test_create_notebook_without_title(self):
        """Нельзя создать конспект без названия"""
        url = '/api/notebooks/'
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_notebook_with_empty_title(self):
        """Нельзя создать конспект с пустым названием"""
        url = '/api/notebooks/'
        response = self.client.post(url, {'title': ''}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_notebook_with_long_title(self):
        """Проверка ограничения длины названия (max_length=255)"""
        notebook = NotebookFactory.create(owner=self.user)
        url = f'/api/notebooks/{notebook.id}/'
        long_title = "A" * 256
        response = self.client.patch(url, {'title': long_title}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
