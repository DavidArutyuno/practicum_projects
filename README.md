# api_yatube
api_yatube

**Автор проекта:**<br>
    *Давид Арутюнов*<br>
    *Студент факультета Бэкенд. Когорта № 59*<br>

**Электронная почта:**<br>
    *david.arutyuno@gmail.com*<br>


## Описание проекта

API для учебного проекта.

### Для взаимодействия с ресурсами доступны эндпоинты:

    api/v1/api-token-auth/ (POST): передаём логин и пароль, получаем токен.
    api/v1/posts/ (GET, POST): получаем список всех постов или создаём новый пост.
    api/v1/posts/{post_id}/ (GET, PUT, PATCH, DELETE): получаем, редактируем или удаляем пост с идентификатором{post_id}.
    api/v1/groups/ (GET): получаем список всех групп.
    api/v1/groups/{group_id}/ (GET): получаем информацию о группе с идентификатором {group_id}.
    api/v1/posts/{post_id}/comments/
      (GET): получаем список всех комментариев поста с  идентификатором post_id 
      (POST): создаём новый комментарий для поста с идентификатором {post_id}.
    api/v1/posts/{post_id}/comments/{comment_id}/ (GET, PUT, PATCH, DELETE): получаем, редактируем или удаляем комментарий с идентификатором {comment_id} в посте с  id=post_id


### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/DavidArutyuno/api-yatube.git
```

```
cd api_yatube
```

Cоздать и активировать виртуальное окружение:

```
python -m venv env
```

```
source env/Scripts/activate
```

```
python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```