import string

from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from pytils.translit import slugify

User = get_user_model()


class ClassTestMixin(TestCase):
    """Класс миксин для тестов."""

    NOTE_TITLE = 'Заголовок'
    NOTE_TEXT = 'Текст'
    NEW_NOTE_TEXT = 'Обновлённый текст'
    NOTE_SLUG = 'note-slug-1'
    NOTE_TRANSLIT_SLUGIFY = slugify(NOTE_TITLE)

    AUTHOR = 'Author'
    READER = 'Reader'
    COUNT_NOTES = 5

    NAMESPACE_NOTES_ADD = 'notes:add'
    NAMESPACE_NOTES_EDIT = 'notes:edit'

    URL_NOTES_HOME = reverse('notes:home')
    URL_USERS_LOGIN = reverse('users:login')
    URL_USERS_LOGOUT = reverse('users:logout')
    URL_USERS_SIGNUP = reverse('users:signup')

    URL_NOTES_LIST = reverse('notes:list')
    URL_NOTES_SUCCESS = reverse('notes:success')
    URL_NOTES_ADD = reverse('notes:add')

    URL_NOTES_DETAIL = reverse('notes:detail', kwargs={'slug': NOTE_SLUG})
    URL_NOTES_EDIT = reverse('notes:edit', kwargs={'slug': NOTE_SLUG})
    URL_NOTES_DELETE = reverse('notes:delete', kwargs={'slug': NOTE_SLUG})

    REDIRECT_TEMPLATE = string.Template(
        URL_USERS_LOGIN + '?next=$url'
    )

    @classmethod
    def setUpTestData(cls):
        """Фикстуры для тестирования."""
        cls.author = User.objects.create(username=cls.AUTHOR)
        cls.reader = User.objects.create(username=cls.READER)
