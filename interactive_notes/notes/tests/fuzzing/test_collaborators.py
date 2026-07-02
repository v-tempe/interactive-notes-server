from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from ..factories import UserFactory, NotebookFactory


class CollaboratorFuzzingTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Создаем владельца и постороннего пользователя
        self.owner = UserFactory.create()
        self.stranger = UserFactory.create()

        self.notebook = NotebookFactory.create(owner=self.owner)

        self.token_owner = self._get_token(self.owner)
        self.token_stranger = self._get_token(self.stranger)

    def _get_token(self, user):
        url = '/api/auth/token/'
        response = self.client.post(url, {'username': user.username, 'password': 'defaultpassword'})
        return response.data['access']

    def get_invalid_collaborator_payloads(self):
        """Генерирует некорректные данные для добавления соавтора"""
        return [
            {},  # Пустое тело
            {"user": "not_an_id"},  # Строка вместо ID
            {"user": -1},  # Отрицательный ID
            {"user": 9999999},  # Несуществующий ID пользователя
            {"role": "superadmin"},  # Несуществующая роль
            {"role": 123},  # Число вместо строки роли
            {"user": None, "role": None},  # Null значения
            {"extra_field": "value"},  # Лишние поля
        ]

    def test_fuzz_add_collaborator_stability(self):
        """Проверяет устойчивость эндпоинта добавления соавторов к некорректным данным"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_owner}')
        url = f'/api/notebooks/{self.notebook.id}/collaborators/'
        errors_500 = 0

        for payload in self.get_invalid_collaborator_payloads():
            try:
                response = self.client.post(url, payload, format='json')
                # Нас интересуют только критические ошибки сервера
                if response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
                    errors_500 += 1
                    print(f"CRITICAL: 500 error for payload: {payload}")
            except Exception as e:
                errors_500 += 1
                print(f"EXCEPTION: {e} for payload: {payload}")

        self.assertEqual(errors_500, 0, "API вернул 500 ошибку при фаззинге соавторов!")

    def test_fuzz_unauthorized_collaborator_access(self):
        """Фаззинг прав доступа: попытка постороннего добавить соавтора"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_stranger}')
        url = f'/api/notebooks/{self.notebook.id}/collaborators/'

        # Даже с валидными данными посторонний должен получать отказ
        target_user = UserFactory.create()
        response = self.client.post(url, {'user': target_user.id, 'role': 'viewer'}, format='json')

        # Ожидаем 403 или 404, но не 500
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])
