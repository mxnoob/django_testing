from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        author = User.objects.create(username='Author')
        reader = User.objects.create(username='Reader')

        cls.author_client = cls.client_class()
        cls.reader_client = cls.client_class()

        cls.author_client.force_login(author)
        cls.reader_client.force_login(reader)

        cls.note = Note.objects.create(
            title='Test',
            text='test text',
            slug='test_slug',
            author=author
        )

    def test_notes_list_for_different_users(self):
        """Пользователи видят только свои заметки."""
        note_clients = (
            (self.author_client, True),
            (self.reader_client, False),
        )
        for client, note_in_list in note_clients:
            response = client.get(self.LIST_URL)
            with self.subTest():
                self.assertIn('object_list', response.context)
                self.assertIs(
                    self.note in response.context['object_list'],
                    note_in_list
                )

    def test_add_and_edit_note_has_form(self):
        """Проверка формы добавления и редактирования заметки."""
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
