import re

import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(all_news, client):
    """Проверка количества новостей на главной странице"""
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_new_order(all_news, client):
    """
    Проверка сортировки новостей
    на главной странице от самой свежей к самой старой.
    """
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert sorted_dates == all_dates


@pytest.mark.django_db
def test_comments_order(few_comment, client, detail_url):
    """Проверка сортировки комментариев по дате"""
    response = client.get(detail_url)
    assert 'news' in response.context

    news = response.context['news']
    all_comments = news.comment_set.all().order_by('created')
    sorted_comments = (
        comment.text for comment in all_comments
    )
    comment_pattern = re.compile(r'[\s\S]+?'.join(sorted_comments))
    page_content = response.content.decode('utf-8')
    assert re.search(comment_pattern, page_content)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, expected_result',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('author_client'), True),
    )
)
def test_client_has_form(parametrized_client, expected_result, detail_url):
    """Проверка наличия формы в контексте для авторизованного пользователя"""
    response = parametrized_client.get(detail_url)
    assert ('form' in response.context) is expected_result
    if expected_result:
        assert isinstance(response.context['form'], CommentForm)
