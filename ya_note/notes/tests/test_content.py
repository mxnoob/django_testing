from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.reader = User.objects.create(username='Reader')

        cls.note = Note.objects.create(
            title='Test',
            text='test text',
            slug='test_slug',
            author=cls.author
        )

    def test_authorized_client_has_notes(self):
        self.client.force_login(self.author)
        response = self.client.get(self.LIST_URL)
        self.assertIn('object_list', response.context)

    def test_notes_list_for_different_users(self):
        note_clients = (
            (self.author, True),
            (self.reader, False),
        )
        for user, note_in_list in note_clients:
            self.client.force_login(user)
            response = self.client.get(self.LIST_URL)
            with self.subTest():
                self.assertEqual(
                    self.note in response.context['object_list'], note_in_list)

    def test_add_and_edit_note_has_form(self):
        self.client.force_login(self.author)
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
