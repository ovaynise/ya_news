from http import HTTPStatus
import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
def test_home_availability_for_anonymous_user(client, name):
    """
    Главная страница доступна анонимному пользователю.
    Страницы регистрации пользователей, входа в учётную запись и выхода из неё
    доступны анонимным пользователям.
    """
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_news_detail_availability_for_anonymous_user(client, news):
    """
    Страница отдельной новости доступна
    анонимному пользователю.
    """
    url = reverse('news:detail', kwargs={'pk': 1})
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_pages_availability_for_author(parametrized_client,
                                       name,
                                       news,
                                       comment,
                                       expected_status):
    """
    Страницы удаления и редактирования комментария
    доступны автору комментария. Авторизованный пользователь не может
    зайти на страницы редактирования или удаления чужих
    комментариев (возвращается ошибка 404).
    """
    url = reverse(name, args=(news.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, news_object',
    (
        ('news:edit', pytest.lazy_fixture('news')),
        ('news:delete', pytest.lazy_fixture('news')),
    ),
)
def test_redirects(client, name, news_object, comment):
    """
    При попытке перейти на страницу редактирования или удаления
    комментария анонимный пользователь перенаправляется на страницу
    авторизации.
    """
    login_url = reverse('users:login')
    if news_object is not None:
        url = reverse(name, args=(news_object.id,))
    else:
        url = reverse(name)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
