import pytest

from datetime import datetime, timedelta

from django.urls import reverse
from django.utils import timezone

from news.models import News, Comment
from django.conf import settings

COMMENT_TEXT = 'Текст комментария'


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(title='Заголовок', text='Текст')
    return news


@pytest.fixture
def all_news():
    today = datetime.today()
    all_news = [
        News(title=f'News {i}', text=' Text', date=today - timedelta(days=i))
        for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)]
    News.objects.bulk_create(all_news)


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news, author=author, text=COMMENT_TEXT)
    return comment


@pytest.fixture
def few_comment(news, author):
    comments = []
    now = timezone.now()
    for i in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Text {i}'
        )
        comment.created = now + timedelta(days=i)
        comment.save()
        comments.append(comment)

    return comments


@pytest.fixture
def news_id_for_args(news):
    return news.id,


@pytest.fixture
def comment_id_for_args(comment):
    return comment.id,


@pytest.fixture
def detail_url(news_id_for_args):
    return reverse('news:detail', args=news_id_for_args)


@pytest.fixture
def edit_url(comment_id_for_args):
    return reverse('news:edit', args=comment_id_for_args)


@pytest.fixture
def delete_url(comment_id_for_args):
    return reverse('news:delete', args=comment_id_for_args)


@pytest.fixture
def url_to_comments(detail_url):
    return f'{detail_url}#comments'
