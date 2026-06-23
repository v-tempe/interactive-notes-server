import random
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .factories import NotebookFactory, UserFactory


class FuzzingAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory.create()
        self.token = self._get_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def _get_token(self, user):
        url = '/api/auth/token/'
        response = self.client.post(url, {'username': user.username, 'password': 'defaultpassword'})
        return response.data['access']

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
            {"title": ""},  # Пустая строка
            {"title": True},  # Булево значение
        ]
        return random.choice(payloads)

    def test_fuzz_create_notebook_stability(self):
        """Тестирует устойчивость endpoint создания конспекта к некорректным данным"""
        url = '/api/notebooks/'
        errors_500 = 0

        for _ in range(20):
            payload = self.get_random_payload()
            try:
                response = self.client.post(url, payload, format='json')

                if response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
                    errors_500 += 1
            except Exception:
                errors_500 += 1

        self.assertEqual(
            errors_500,
            0,
            "API вернул 500 ошибку на некорректные данные при создании!",
        )

    def test_fuzz_invalid_ids(self):
        """Проверка реакции на несуществующие ID"""
        random_id = random.randint(999999, 9999999)
        url = f'/api/notebooks/{random_id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
