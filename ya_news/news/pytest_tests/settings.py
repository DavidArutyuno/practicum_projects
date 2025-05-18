from django.conf import settings
from django.urls import reverse


# Пользователи
AUTHOR = 'Author'
NOT_AUTHOR = 'NotAuthor'

# Константы для объектов БД
NEWS_COUNT = settings.NEWS_COUNT_ON_HOME_PAGE
COMMENTS_COUNT = 10

COMMENT_TEXT = 'Tекст комментария'
NEW_COMMENT_TEXT = 'Обновлённый комментарий'

NEWS_TITLE = 'Заголовок новости'
NEWS_TEXT = 'Текст новости'

# Пространство имен для маршрутизации динамических страниц
NAMESPACE_NEWS_DETAIL = 'news:detail'
NAMESPACE_NEWS_EDIT = 'news:edit'
NAMESPACE_NEWS_DELETE = 'news:delete'

# Формирование URL для статичных страниц
URL_NEWS_HOME = reverse('news:home')
URL_USERS_LOGIN = reverse('users:login')
URL_USERS_LOGOUT = reverse('users:logout')
URL_USERS_SIGNUP = reverse('users:signup')

# Данные для тестов
FORM_DATA = {
    'title': f'Новый {NEWS_TITLE}',
    'text': f'Новый {NEWS_TEXT}'
}

COMMENT_DATA = {
    'text': COMMENT_TEXT
}
