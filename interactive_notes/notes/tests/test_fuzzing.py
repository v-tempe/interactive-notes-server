import random
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .factories import NotebookFactory, UserFactory, CollaboratorFactory


class FuzzingAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Основной пользователь (Владелец)
        self.owner = UserFactory.create()
        self.token_owner = self._get_token(self.owner)

        # Пользователь-соавтор
        self.collab_user = UserFactory.create()
        self.token_collab = self._get_token(self.collab_user)

        # Посторонний пользователь
        self.stranger = UserFactory.create()
        self.token_stranger = self._get_token(self.stranger)

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
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_owner}')
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

    def test_fuzz_permissions_collaborator_management(self):
        """Фаззинг прав доступа: проверка, что соавтор не может управлять другими соавторами"""
        notebook = NotebookFactory.create(owner=self.owner)
        CollaboratorFactory.create(notebook=notebook, user=self.collab_user, role='editor')

        # Создаем третьего пользователя, которого будем пытаться добавить/удалить
        target_user = UserFactory.create()

        url_list = f'/api/notebooks/{notebook.id}/collaborators/'

        # 1. Попытка соавтора добавить кого-то (должно быть 403)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_collab}')
        response = self.client.post(url_list, {'user': target_user.id, 'role': 'viewer'}, format='json')
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST],
                      f"Соавтор смог добавить участника! Status: {response.status_code}")

        # 2. Попытка постороннего удалить соавтора (должно быть 403 или 404)
        collaborator_obj = CollaboratorFactory.create(notebook=notebook, user=target_user)
        url_detail = f'/api/notebooks/{notebook.id}/collaborators/{collaborator_obj.id}/'

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_stranger}')
        response = self.client.delete(url_detail)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND],
                      f"Посторонний смог удалить соавтора! Status: {response.status_code}")

    def test_fuzz_invalid_ids_and_methods(self):
        """Проверяет реакцию на неверные ID и методы"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_owner}')

        # Случайные несуществующие ID
        random_id = random.randint(10000, 99999)
        url = f'/api/notebooks/{random_id}/'

        methods = ['get', 'put', 'patch', 'delete']
        for method in methods:
            func = getattr(self.client, method)
            response = func(url)
            # Должно быть 404, а не 500
            self.assertNotEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR,
                                f"Ошибка 500 при обращении к несуществующему ID через {method}")
