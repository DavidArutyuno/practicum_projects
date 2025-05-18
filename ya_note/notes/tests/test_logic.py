from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note
from notes.tests.settings import ClassTestMixin

User = get_user_model()


class TestNoteCreation(ClassTestMixin):
    """Тесты создания заметок в web приложении YaNote."""

    @classmethod
    def setUpTestData(cls):
        """
        Фикстуры для проверки логики web приложения YaNote.

        В пользу лучшей читаемости кода принято решение создать одну запись
        в БД и три набора словарей для передачи заметок под разные сценарии
        тестирования:
            cls.note - базовая исходная заметка (это запись (объект) в БД)
            cls.bad_note_with_error - заметка с уже существующим в БД слагом
            cls.correct_note - для проверки успешного добавления новой заметки
            cls.note_without_slug - для проверки, что в случае отсутствия
                слага он создается автоматически.
        """
        super().setUpTestData()

        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)

        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG,
            author=cls.author
        )

        cls.bad_note_with_error = {
            'title': cls.NOTE_TITLE + ' qwerty',
            'text': cls.NOTE_TEXT + ' qwerty',
            'slug': cls.NOTE_SLUG
        }

        cls.correct_note = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.NOTE_SLUG + '-2'
        }

        cls.note_without_slug = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT + ' qwerty'
        }

    def setUp(self):
        """Фиксируем количество записей в БД перед каждым тестом."""
        self.etalon_notes_count = Note.objects.count()

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        self.client.post(self.URL_NOTES_ADD, data=self.correct_note)
        self.assertEqual(Note.objects.count(), self.etalon_notes_count)

    def test_user_can_create_note(self):
        """
        Залогиненный пользователь может создать заметку.

        Проверяем:
            - вначале в БД не должно быть записи с передаваемым далее слагом.
                assertFalse возвращает False для запроса
                Note.objects.filter(slug=self.NOTE_SLUG + '-2').exists()
            - успешный редирект на страницу добавления заметки;
            - количество объектов в БД после добавления заметки, при этом
                исходное кол-во записей получаем в методе setUp();
            - содержимое добавленной записи получаем из БД запросом
                Note.objects.filter(slug=self.NOTE_SLUG + '-2').exists()
                assertTrue проверяет что такая запись есть
        """
        self.assertFalse(
            Note.objects.filter(slug=self.NOTE_SLUG + '-2').exists()
        )

        response = self.auth_client.post(
            self.URL_NOTES_ADD,
            data=self.correct_note
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.URL_NOTES_SUCCESS)
        self.assertEqual(
            Note.objects.count(), self.etalon_notes_count + 1
        )
        self.assertTrue(
            Note.objects.filter(slug=self.NOTE_SLUG + '-2').exists()
        )

    def test_user_cant_create_note_exists_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""

        response = self.auth_client.post(
            self.URL_NOTES_ADD, data=self.bad_note_with_error)
        form = response.context['form']
        self.assertFormError(
            form=form,
            field='slug',
            errors=self.bad_note_with_error['slug'] + WARNING
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
        self.assertFalse(
            Note.objects.filter(slug=self.NOTE_TRANSLIT_SLUGIFY).exists()
        )
        response = self.auth_client.post(
            self.URL_NOTES_ADD,
            data=self.note_without_slug
        )
        self.assertRedirects(response, self.URL_NOTES_SUCCESS)
        self.assertEqual(
            Note.objects.count(), self.etalon_notes_count + 1
        )
        self.assertTrue(
            Note.objects.filter(slug=self.NOTE_TRANSLIT_SLUGIFY).exists()
        )


class TestNoteEditDelete(ClassTestMixin):
    """Тесты функционала взаимодействия с заметками в web приложении YaNote."""

    @classmethod
    def setUpTestData(cls):
        """Фикстуры для проверки логики web приложения YaNote."""
        super().setUpTestData()
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=f'{cls.NOTE_SLUG}-{cls.author}',
            author=cls.author
        )

        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT
        }

    def setUp(self):
        """Фиксируем количество записей в БД перед каждым тестом."""
        self.etalon_notes_count = Note.objects.count()

    def test_author_can_delete_note(self):
        """
        Авторизованный пользователь-автор заметки
        может удалять свои заметки.
        """
        self.assertEqual(
            Note.objects.count(), self.etalon_notes_count
        )
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.URL_NOTES_SUCCESS)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), self.etalon_notes_count - 1)

    def test_user_cant_delete_note_of_another_user(self):
        """
        Авторизованный пользователь-читатель
        не может удалять чужие заметки.
        """
        self.assertEqual(Note.objects.count(), self.etalon_notes_count)

        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        self.assertEqual(Note.objects.count(), self.etalon_notes_count)

    def test_author_can_edit_note(self):
        """Пользователь может редактировать свои заметки."""
        response = self.author_client.post(
            self.edit_url,
            data=self.form_data
        )
        self.assertRedirects(response, self.URL_NOTES_SUCCESS)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        """Пользователь не может редактировать чужие заметки."""
        response = self.reader_client.post(
            self.edit_url,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
