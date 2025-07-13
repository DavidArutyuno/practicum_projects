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