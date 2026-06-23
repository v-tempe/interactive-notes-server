from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User


class JWTAuthTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='authuser',
            password='SecurePass123!',
        )
        self.token_url = '/api/auth/token/'

    def test_obtain_token_with_valid_credentials(self):
        """Получение токена при верных данных"""
        data = {
            'username': 'authuser',
            'password': 'SecurePass123!'
        }
        response = self.client.post(self.token_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_obtain_token_with_invalid_password(self):
        """Попытка получить токен с неверным паролем"""
        data = {
            'username': 'authuser',
            'password': 'WrongPassword'
        }
        response = self.client.post(self.token_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_obtain_token_for_non_existent_user(self):
        """Попытка получить токен для несуществующего пользователя"""
        data = {
            'username': 'ghostuser',
            'password': 'SomePassword'
        }
        response = self.client.post(self.token_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_protected_endpoint_without_token(self):
        """Попытка доступа к защищенному эндпоинту без токена"""
        response = self.client.get('/api/notebooks/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
