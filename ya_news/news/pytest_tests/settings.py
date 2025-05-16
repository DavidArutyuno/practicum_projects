from django.conf import settings


# Пользователи
AUTHOR = 'Автор'
NOT_AUTHOR = 'Не автор'

# Константы для объектов БД
NEWS_COUNT = settings.NEWS_COUNT_ON_HOME_PAGE
COMMENTS_COUNT = 10

COMMENT_TEXT = 'Tекст комментария'
NEW_COMMENT_TEXT = 'Обновлённый комментарий'

NEWS_TITLE = 'Заголовок новости'
NEWS_TEXT = 'Текст новости'

# Пространство имен для маршрутизации
NEWS_HOME = 'news:home'
NEWS_DETAIL = 'news:detail'
NEWS_EDIT = 'news:edit'
NEWS_DELETE = 'news:delete'

USERS_LOGIN = 'users:login'
USERS_LOGOUT = 'users:logout'
USERS_SIGNUP = 'users:signup'
