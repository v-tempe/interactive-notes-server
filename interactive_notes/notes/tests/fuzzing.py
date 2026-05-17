import random
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .factories import NotebookFactory, UserFactory


class FuzzingAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Создаем пользователя и получаем токен
        self.user = UserFactory.create()
        url = '/api/auth/token/'
        response = self.client.post(url, {'username': self.user.username, 'password': 'defaultpassword'})
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def get_random_payload(self):
        """Генерирует случайные полезные нагрузки для фаззинга"""
        payloads = [
            {},  # Пустое тело
            {"title": 12345},  # Неверный тип данных
            {"title": None},  # Null значение
            {"title": "'; DROP TABLE notes_notebook; --"},  # SQL Injection attempt
            {"title": "<script>alert('xss')</script>"},  # XSS attempt
            {"sections": "not a list"},  # Неверный тип для вложенного объекта
            {"sections": [{"title": 123}]},  # Неверный тип внутри списка
            {"unknown_field": "value"},  # Лишние поля
            {"title": "A" * 10000},  # Очень длинная строка
        ]
        return random.choice(payloads)

    def test_fuzz_create_notebook(self):
        """Тестирует устойчивость endpoint создания конспекта к некорректным данным"""
        url = '/api/notebooks/'
        errors_found = 0

        for _ in range(20):
            payload = self.get_random_payload()
            try:
                response = self.client.post(url, payload, format='json')

                if response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
                    errors_found += 1
                    print(f"CRITICAL ERROR: Status 500 for payload: {payload}")
                    print(f"Response: {response.data}")

            except Exception as e:
                errors_found += 1
                print(f"EXCEPTION: {e} for payload: {payload}")

        self.assertEqual(errors_found, 0, "API вернул 500 ошибку на некорректные данные!")

    def test_fuzz_invalid_methods(self):
        """Проверяет реакцию на неверные HTTP методы"""
        notebook = NotebookFactory.create(owner=self.user)
        url = f'/api/notebooks/{notebook.id}/'

        response = self.client.get(url)

        response = self.client.post(url, {"title": "New"}, format='json')
        self.assertIn(response.status_code, [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_404_NOT_FOUND])