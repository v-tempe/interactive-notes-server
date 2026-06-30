import random
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from notes.tests.factories import NotebookFactory, UserFactory


class NotebookFuzzingTestCase(TestCase):
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

    def get_random_payload(self):
        payloads = [
            {"title": None},
            {"title": 12345},
            {"title": True},
            {"title": "'; DROP TABLE notes_notebook; --"},
            {"title": "<script>alert('xss')</script>"},
            {"sections": "string_instead_of_list"},
            {"unknown_key": "value"},
            {"title": "A" * 50000},  # Экстремально длинная строка
        ]
        return random.choice(payloads)

    def test_fuzz_create_notebook_stability(self):
        """Устойчивость создания конспекта к случайным данным"""
        url = '/api/notebooks/'
        errors_500 = 0
        for _ in range(30):
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
            "Обнаружены критические ошибки сервера (500) при фаззинге создания!",
        )

    def test_fuzz_invalid_ids(self):
        """Реакция на несуществующие ID конспектов"""
        random_id = random.randint(999999, 9999999)
        url = f'/api/notebooks/{random_id}/'
        methods = ['get', 'put', 'patch', 'delete']

        for method in methods:
            func = getattr(self.client, method)
            response = func(url)
            self.assertNotEqual(
                response.status_code,
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"Ошибка 500 при обращении к несуществующему ID через {method}",
            )
