from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestCreateNote(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')

        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.add_url = reverse('notes:add')
        cls.success_url = reverse('notes:success')

        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def test_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку."""
        self.author_client.post(self.add_url, self.form_data)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()

        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        self.client.post(self.add_url, self.form_data)
        self.assertEqual(Note.objects.count(), 0)

    def test_empty_slug(self):
        """Автоматическая генерация slug при его отсутствии."""
        self.form_data.pop('slug')
        self.author_client.post(self.add_url, self.form_data)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(note.slug, expected_slug)

    def test_not_unique_slug(self):
        """Проверка создания заметки с одинаковым slug."""
        self.author_client.post(self.add_url, self.form_data)
        response = self.author_client.post(self.add_url, self.form_data)
        self.assertFormError(
            response, 'form', 'slug', self.form_data['slug'] + WARNING)
        self.assertEqual(Note.objects.count(), 1)


class TestEditOrDeleteNote(TestCase):
    NOTE_TITLE = 'Test'
    NOTE_TEXT = 'test text'
    NOTE_SLUG = 'test_slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.reader = User.objects.create(username='Reader')

        cls.author_client = Client()
        cls.reader_client = Client()

        cls.author_client.force_login(cls.author)
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG,
            author=cls.author
        )

        cls.success_url = reverse('notes:success')
        cls.edit_url = reverse('notes:edit', args=(cls.NOTE_SLUG,))
        cls.delete_url = reverse('notes:delete', args=(cls.NOTE_SLUG,))

        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def test_author_can_edit_note(self):
        """Автор может редактировать свою заметку."""
        self.author_client.post(self.edit_url, data=self.form_data)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        """Другой пользователь не может редактировать заметку."""
        self.reader_client.post(self.edit_url, data=self.form_data)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.text, self.NOTE_TEXT)
        self.assertEqual(self.note.slug, self.NOTE_SLUG)

    def test_author_can_delete_note(self):
        """Автор может удалять свою заметку."""
        self.author_client.post(self.delete_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        """Другой пользователь не может удалять заметку."""
        self.reader_client.post(self.delete_url)
        self.assertEqual(Note.objects.count(), 1)
