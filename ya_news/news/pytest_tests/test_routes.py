from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('comment_id_for_args')),
        ('users:signup', None),
        ('users:login', None),
        ('users:logout', None),
    )
)
def test_pages_availability(name, args, client):
    """Проверка доступности страниц любому пользователя."""
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    "parametrized_client, expected_status",
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
    )
)
@pytest.mark.parametrize(
    'name', ('news:edit', 'news:delete')
)
def test_availability_for_comment_edit_and_delete(
    parametrized_client, expected_status, name, comment_id_for_args
):
    """Проверка доступности редактирования и удаления комментария"""
    url = reverse(name, args=comment_id_for_args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name', ('news:edit', 'news:delete')
)
def test_redirect_for_anonymous_client(client, name, comment_id_for_args):
    """Проверка редиректа для анонимного пользователя"""
    login_url = reverse('users:login')
    url = reverse(name, args=comment_id_for_args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
