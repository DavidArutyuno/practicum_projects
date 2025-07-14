# 🎬 YaMDb - API сервиса отзывов на произведения

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-3.2-green.svg)](https://djangoproject.com)
[![DRF](https://img.shields.io/badge/DRF-3.12-red.svg)](https://www.django-rest-framework.org)

## 👨‍💻 Команда разработки

| Разработчик       | Email                          | Роль               | Когорта |
|-------------------|--------------------------------|--------------------|---------|
| Давид Арутюнов    | david.arutyuno@gmail.com       | Аутентификация     | #60     |
| Николай Дегтярев  | degtyarevkolya1996@yandex.ru   | Произведения       | #60     |
| Олег Ямолтдинов   | yamoltdinovoleg@yandex.com     | Отзывы и рейтинги  | #60     |

## 📖 Описание проекта

YaMDb - это API сервиса для сбора отзывов пользователей на различные произведения: книги, фильмы и музыку.

## 🗂 Структура проекта

```bash
yamdb/
├── api/                    # Основное приложение API
│   ├── __init__.py
│   ├── admin.py            # Админ-панель
│   ├── apps.py
│   ├── migrations/         # Миграции БД
│   ├── models.py           # Модели данных
│   ├── permissions.py      # Права доступа
│   ├── serializers.py      # Сериализаторы
│   ├── urls.py             # Маршруты API
│   ├── views.py            # Представления
│   └── tests/              # Тесты API
│
├── users/                  # Приложение пользователей
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py           # Кастомная модель User
│   ├── permissions.py
│   ├── serializers.py
│   ├── urls.py
│   ├── views.py
│   └── tests/
│
├── yamdb/                  # Ядро проекта
│   ├── __init__.py
│   ├── asgi.py             # ASGI-конфиг
│   ├── settings.py         # Настройки
│   ├── urls.py             # Главные URL
│   └── wsgi.py             # WSGI-конфиг
│
├── manage.py               # CLI-управление
└── requirements.txt        # Зависимости
```

**Ключевые компоненты:**

- `api/` - REST API для работы с отзывами и произведениями
- `users/` - Аутентификация и управление пользователями
- `yamdb/` - Основные настройки Django-проекта

Для навигации по коду используйте дерево файлов в GitHub или IDE.


**Ключевые возможности:**
- 📚 Категории и жанры произведений
- ⭐ Оценки и рейтинги произведений
- ✍️ Текстовые отзывы и комментарии
- 🔐 JWT-аутентификация
- 👨‍💻 Гибкая система ролей (админ, модератор, пользователь)

**Документация API:**  
[Redoc](http://127.0.0.1:8000/redoc/)

## 🚀 Быстрый старт

### Установка и запуск

```bash
# Клонирование репозитория
    git clone https://github.com/DavidArutyuno/api-yamdb
    cd api_yamdb

# Создание виртуального окружения
    python -m venv venv

# Активация окружения
# Windows:
    venv\Scripts\activate
# Linux/MacOS:
    source venv/bin/activate

# Установка зависимостей
    pip install -r requirements.txt

# Миграции
    python manage.py migrate

# Загрузка тестовых данных (опционально)
    python manage.py loaddata fixtures/*.json

# Запуск сервера
    python manage.py runserver
```

## Переменные окружения

### Создайте файл .env в корне проекта:
    
    SECRET_KEY=ваш_секретный_ключ
    DEBUG=True
    ALLOWED_HOSTS=localhost,127.0.0.1


## 🌐 Основные эндпоинты

| Метод       | Эндпоинт                          | Описание               
|-------------------|--------------------------------|--------------------|
| POST    | /api/v1/auth/signup/       | Регистрация нового пользователя     |
| POST  | /api/v1/auth/token/   | Получение JWT-токена       |
| GET   | /api/v1/titles/     | Список произведений  |
| POST  | /api/v1/reviews/   | Добавление отзыва       |
| GET   | /api/v1/users/me/     | Профиль текущего пользователя  |


## 🔒 Права доступа

| Роль       | Возможности                         |
|-------------------|------------------------------|
| Аноним    | Просмотр произведений, отзывов       |
| Пользователь    | Создание отзывов и комментариев|
| Модератор    | Управление любыми отзывами       |
| Администратор    | Полный доступ ко всем ресурсам|


## 📊 Примеры запросов

Регистрация пользователя:

    POST /api/v1/auth/signup/
    Content-Type: application/json

    {
    "email": "user@example.com",
    "username": "new_user"
    }

Получение токена:

    POST /api/v1/auth/token/
    Content-Type: application/json

    {
    "username": "new_user",
    "confirmation_code": "123456"
    }


## 📌 Особенности реализации

* Кастомная модель пользователя с расширенными полями

* Интеграция с Simple JWT для аутентификации

* Каскадное удаление связанных данных

* Фильтрация и поиск по всем ресурсам

* Пагинация и ограничение скорости запросов

## 🤝 Вклад в проект

Приветствуются pull request'ы. Для серьезных изменений, пожалуйста, откройте issue для обсуждения.