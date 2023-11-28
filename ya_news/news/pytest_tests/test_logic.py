import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, detail_url, form_data):
    """Анонимный пользователь не может создать комментарий."""
    client.post(detail_url, data=form_data)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
        author_client, detail_url, author, news, form_data
):
    """Авторизованный пользователь может создать комментарий."""
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.parametrize(
    'bad_word', BAD_WORDS
)
def test_user_cant_use_bad_words(admin_client, detail_url, bad_word):
    """Пользователь не может использовать запрещенные слова."""
    bad_words_data = {'text': f'Какой-то текст, {bad_word}, еще текст'}
    response = admin_client.post(detail_url, data=bad_words_data)
    assertFormError(response, form='form', field='text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(author_client, delete_url, url_to_comments):
    """Автор может удалить свои комментарии."""
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(admin_client, delete_url):
    """Пользователь не может удалить комментарий другого пользователя."""
    admin_client.delete(delete_url)
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_author_can_edit_comment(
        comment, author_client, edit_url, url_to_comments, form_data
):
    """Автор может редактировать свои комментарии."""
    response = author_client.post(edit_url, form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
        comment, admin_client, edit_url, form_data
):
    """Пользователь не может редактировать комментарий другого пользователя."""
    admin_client.post(edit_url, form_data)
    comment_text = comment.text
    comment.refresh_from_db()
    assert comment.text == comment_text
