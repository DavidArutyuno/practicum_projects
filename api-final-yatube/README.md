# api_final
api final

**Автор проекта:**<br>
    *Давид Арутюнов*<br>
    *Студент факультета Бэкенд. Когорта № 59*<br>

**Электронная почта:**<br>
    *david.arutyuno@gmail.com*<br>


### <ins>Описание проекта</ins>

API для учебного проекта.

Документация api-проекта доступна по адресу:
[http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/).


### <ins>Как запустить проект</ins>

1. Клонировать репозиторий и перейти в него в командной строке:

    ```
    git clone https://github.com/DavidArutyuno/api-yatube.git
    ```

    ```
    cd api_yatube
    ```

2. Cоздать и активировать виртуальное окружение:

    ```
    python -m venv env
    ```

    ```
    source env/Scripts/activate
    ```

    ```
    python -m pip install --upgrade pip
    ```

3. Установить зависимости из файла requirements.txt:

    ```
    pip install -r requirements.txt
    ```

4. Выполнить миграции:

    ```
    python manage.py migrate
    ```

4. Запустить проект:

    ```
    python manage.py runserver
    ```