from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    """Тесты создания заметок в web приложении YaNote."""

    # Текст заметки понадобится в нескольких местах кода,
    # поэтому запишем его в атрибуты класса.
    NOTE_TITLE = 'Заголовок'
    NOTE_TEXT = 'Это текст заметки для теста'
    NOTE_SLUG = 'slug1'
    NOTE_TRANSLIT_SLUGIFY = slugify(NOTE_TITLE)

    @classmethod
    def setUpTestData(cls):
        """Фикстуры для проверки логики web приложения YaNote."""
        # Адрес страницы с новостью.
        cls.url = reverse('notes:add', args=None)
        cls.url_success = reverse('notes:success', args=None)

        # Создаём пользователя и клиент, логинимся в клиенте.
        cls.user = User.objects.create(username='David')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)

        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug='slug2',
            author=cls.user
        )

        # Данные для POST-запроса при создании комментария.
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.NOTE_SLUG
        }

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        self.client.post(self.url, data=self.form_data)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.url_success)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 2)
        note = Note.objects.last()
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.slug, self.NOTE_SLUG)
        self.assertEqual(note.author, self.user)

    def test_user_cant_create_note_exists_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        bad_note_with_error = {
            'title': self.NOTE_TITLE,
            'text': self.NOTE_TEXT,
            'slug': 'slug2'
        }
        response = self.auth_client.post(self.url, data=bad_note_with_error)
        form = response.context['form']
        self.assertFormError(
            form=form,
            field='slug',
            errors=bad_note_with_error['slug'] + WARNING
        )
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_can_create_auto_insert_slug_if_empty(self):
        """
        Автозаполнение поля slug.

        Если при создании заметки не заполнен slug,
        то он формируется автоматически,
        с помощью функции pytils.translit.slugify.
        """
        note_without_slug = {
            'title': self.NOTE_TITLE,
            'text': self.NOTE_TEXT
        }

        response = self.auth_client.post(self.url, data=note_without_slug)
        self.assertRedirects(response, self.url_success)
        note = Note.objects.last()
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.slug, self.NOTE_TRANSLIT_SLUGIFY)
        self.assertEqual(note.author, self.user)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 2)


class TestNoteEditDelete(TestCase):
    """Тесты функционала взаимодействия с заметками в web приложении YaNote."""

    NOTE_TITLE = 'Заголовок'
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TEXT = 'Обновлённая заметка'
    NOTE_SLUG = 'slug'

    @classmethod
    def setUpTestData(cls):
        """Фикстуры для проверки логики web приложения YaNote."""
        cls.user_1 = User.objects.create(username='David')
        cls.auth_client_1 = Client()
        cls.auth_client_1.force_login(cls.user_1)

        cls.note_1 = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=f'{cls.NOTE_SLUG}_{cls.user_1}',
            author=cls.user_1
        )

        cls.user_2 = User.objects.create(username='Petrovich')
        cls.auth_client_2 = Client()
        cls.auth_client_2.force_login(cls.user_2)

        cls.url_success = reverse('notes:success', args=None)
        cls.edit_url_1 = reverse('notes:edit', args=(cls.note_1.slug,))
        cls.delete_url_1 = reverse('notes:delete', args=(cls.note_1.slug,))

        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT
        }

    def test_author_can_delete_note(self):
        """Пользователь может удалять свои заметки."""
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        response = self.auth_client_1.delete(self.delete_url_1)
        self.assertRedirects(response, self.url_success)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        """Пользователь не может удалять чужие заметки."""
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

        response = self.auth_client_2.delete(self.delete_url_1)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        """Пользователь может редактировать свои заметки."""
        response = self.auth_client_1.post(
            self.edit_url_1,
            data=self.form_data
        )
        self.assertRedirects(response, self.url_success)
        self.note_1.refresh_from_db()
        self.assertEqual(self.note_1.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        """Пользователь не может редактировать чужие заметки."""
        response = self.auth_client_2.post(
            self.edit_url_1,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note_1.refresh_from_db()
        self.assertEqual(self.note_1.text, self.NOTE_TEXT)
