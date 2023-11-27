from http import HTTPStatus

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()

ADD_URL = reverse('notes:add')
SUCCESS_URL = reverse('notes:success')

FORM_DATA = {
    'title': 'Новый заголовок',
    'text': 'Новый текст',
    'slug': 'new-slug'
}


class NoteTestCase(TestCase):
    def assert_notes_count(self, count):
        self.assertEqual(Note.objects.count(), count)


class TestLogic(NoteTestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')

    def test_user_can_create_note(self):
        self.client.force_login(self.author)
        response = self.client.post(ADD_URL, FORM_DATA)
        self.assertRedirects(response, SUCCESS_URL)
        self.assert_notes_count(1)
        note = Note.objects.get()

        self.assertEqual(note.title, FORM_DATA['title'])
        self.assertEqual(note.text, FORM_DATA['text'])
        self.assertEqual(note.slug, FORM_DATA['slug'])
        self.assertEqual(note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        response = self.client.post(ADD_URL, FORM_DATA)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={ADD_URL}'
        self.assertRedirects(response, expected_url)
        self.assert_notes_count(0)

    def test_empty_slug(self):
        form_data = FORM_DATA.copy()
        form_data.pop('slug')
        self.client.force_login(self.author)
        response = self.client.post(ADD_URL, form_data)
        self.assertRedirects(response, SUCCESS_URL)

        self.assert_notes_count(1)
        note = Note.objects.get()
        expected_slug = slugify(form_data['title'])
        self.assertEqual(note.slug, expected_slug)


class TestNote(NoteTestCase):

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

    @property
    def edit_url(self):
        return reverse('notes:edit', args=(self.note.slug,))

    @property
    def delete_url(self):
        return reverse('notes:delete', args=(self.note.slug,))

    def test_not_unique_slug(self):
        FORM_DATA['slug'] = self.note.slug
        self.client.force_login(self.author)
        response = self.client.post(ADD_URL, FORM_DATA)
        self.assertFormError(
            response, 'form', 'slug', self.note.slug + WARNING)
        self.assert_notes_count(1)

    def test_author_can_edit_note(self):
        self.client.force_login(self.author)
        response = self.client.post(self.edit_url, data=FORM_DATA)
        self.assertRedirects(response, SUCCESS_URL)

        self.note.refresh_from_db()
        self.assertEqual(self.note.title, FORM_DATA['title'])
        self.assertEqual(self.note.text, FORM_DATA['text'])
        self.assertEqual(self.note.slug, FORM_DATA['slug'])

    def test_other_user_cant_edit_note(self):
        self.client.force_login(self.reader)
        response = self.client.post(self.edit_url, data=FORM_DATA)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        self.client.force_login(self.author)
        response = self.client.post(self.delete_url)
        self.assertRedirects(response, SUCCESS_URL)
        self.assert_notes_count(0)

    def test_other_user_cant_delete_note(self):
        self.client.force_login(self.reader)
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assert_notes_count(1)
