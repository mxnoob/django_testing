from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.reader = User.objects.create(username='Reader')

        cls.author_client = Client()
        cls.reader_client = Client()

        cls.author_client.force_login(cls.author)
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title='Test',
            text='test text',
            slug='test_slug',
            author=cls.author
        )

    def test_pages_availability(self):
        """Проверка доступности страниц любому пользователя."""
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )

        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_authorized_client(self):
        """Проверка страниц для авторизованного пользователя."""
        urls = (
            'notes:list',
            'notes:success',
            'notes:add',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        """Анонимный пользователь перенаправляется на страницу логина."""
        login_url = reverse('users:login')
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name, args=args):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_availability_for_note_detail_edit_and_delete(self):
        """
        Проверка доступности для детального просмотра,
        редактирования и удаления заметки.
        """
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND)
        )
        for client, status in users_statuses:
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)
