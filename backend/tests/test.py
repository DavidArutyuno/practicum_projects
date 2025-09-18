from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from users.models import Subscription


class UsersAPITestCase(TestCase):
    """Тесты API пользователей."""

    def setUp(self):
        """Настройка тестовых данных."""
        User = get_user_model()
        self.user = User.objects.create_user(
            username='auth_user',
            email='auth@mail.com',
            password='testpassphrase123'
        )
        self.other_user = User.objects.create_user(
            username='other_user',
            email='other@mail.com',
            password='testpassphrase123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_exists(self):
        """Проверка доступности списка пользователей."""
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_user_profile_exists(self):
        """Проверка доступности профиля пользователя."""
        response = self.client.get(f'/api/users/{self.other_user.id}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_current_user_endpoint(self):
        """Проверка endpoint текущего пользователя."""
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.data['username'], 'auth_user')

    def test_subscribe_to_user(self):
        """Проверка подписки на пользователя."""
        response = self.client.post(
            f'/api/users/{self.other_user.id}/subscribe/'
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertTrue(
            Subscription.objects.filter(
                user=self.user,
                author=self.other_user
            ).exists()
        )

    def test_unsubscribe_from_user(self):
        """Проверка отписки от пользователя."""
        # Сначала подписываемся
        Subscription.objects.create(user=self.user, author=self.other_user)

        # Затем отписываемся
        response = self.client.delete(
            f'/api/users/{self.other_user.id}/subscribe/'
        )
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
        self.assertFalse(
            Subscription.objects.filter(
                user=self.user,
                author=self.other_user
            ).exists()
        )

    def test_subscriptions_list(self):
        """Проверка списка подписок."""
        Subscription.objects.create(user=self.user, author=self.other_user)

        response = self.client.get('/api/users/subscriptions/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_cannot_subscribe_to_self(self):
        """Проверка что нельзя подписаться на себя."""
        response = self.client.post(f'/api/users/{self.user.id}/subscribe/')
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_user_registration(self):
        """Проверка регистрации нового пользователя."""
        data = {
            'username': 'new_user',
            'email': 'new@mail.com',
            'password': 'newtestpassphrase123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post('/api/users/', data)
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertEqual(response.data['username'], 'new_user')

    def test_anonymous_access_to_users(self):
        """Проверка доступа анонимных пользователей к списку пользователей."""
        self.client.logout()
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_anonymous_no_access_to_me(self):
        """Проверка что анонимы не могут получить данные о себе."""
        self.client.logout()
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
