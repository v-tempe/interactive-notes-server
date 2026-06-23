from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User


class UserRegistrationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/api/auth/register/'

    def test_register_new_user_successfully(self):
        """Успешная регистрация нового пользователя"""
        data = {
            'username': 'testuser',
            'password': 'StrongPassword123!',
            'email': 'test@example.com'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_register_duplicate_username(self):
        """Попытка зарегистрироваться с уже занятым именем"""
        User.objects.create_user(username='existinguser', password='password')
        data = {
            'username': 'existinguser',
            'password': 'AnotherPassword123!',
            'email': 'new@example.com'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_without_password(self):
        """Регистрация без указания пароля должна быть запрещена"""
        data = {
            'username': 'nopassuser',
            'email': 'nopass@example.com'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_with_weak_password(self):
        """Проверка валидации сложности пароля (минимум 8 символов)"""
        data = {
            'username': 'weakpassuser',
            'password': '123',
            'email': 'weak@example.com'
        }
        response = self.client.post(self.url, data, format='json')
        # Django валидаторы должны отклонить такой пароль
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_with_invalid_email(self):
        """Регистрация с некорректным форматом email"""
        data = {
            'username': 'bademailuser',
            'password': 'StrongPassword123!',
            'email': 'not-an-email'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
