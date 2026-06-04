# 🧑‍💻 Практикум-проекты Давида Арутюнова

[![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2-green?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-24.0-blue?logo=docker&logoColor=white)](https://www.docker.com/)

Добро пожаловать в мое портфолио учебных проектов!  
Здесь собраны работы, выполненные в процессе обучения веб-разработке (Яндекс.Практикум).  
Проекты сгруппированы по направлениям, чтобы вам было удобно оценить мой стек и подход к решению задач.

---

## 📂 Структура портфолио

- **[🌐 Веб-приложения на Django](#-веб-приложения-на-django)** — полноценные сайты с админкой, авторизацией, пагинацией.
- **[🔌 API и бэкенд-сервисы](#-api-и-бэкенд-сервисы)** — REST API на DRF и FastAPI, асинхронные эндпоинты.
- **[🕷️ Парсинг и сбор данных](#️-парсинг-и-сбор-данных)** — Beautiful Soup, Scrapy, работа с PEP.
- **[🤖 Телеграм-боты](#-телеграм-боты)** — асинхронные боты для проверки домашек и уведомлений.
- **[🐳 DevOps и инфраструктура](#-devops-и-инфраструктура)** — Docker, GitHub Actions, деплой на сервер.
- **[🧠 Алгоритмы и игры](#-алгоритмы-и-игры)** — классические задачи, игра «Змейка».
- **[📊 Интеграции с Google Sheets](#-интеграции-с-google-sheets)** — работа с таблицами и отчетность.

---

### 🌐 Веб-приложения на Django

| Проект | Описание | Стек |
|--------|----------|------|
| **[foodgram](https://github.com/DavidArutyuno/practicum_projects/tree/main/foodgram)** | «Продуктовый помощник»: сайт с рецептами, подписками, списком покупок и скачиванием PDF. | Django, DRF, PostgreSQL, Docker, Nginx, GitHub Actions |
| **[kittygram_final](https://github.com/DavidArutyuno/practicum_projects/tree/main/kittygram_final)** | Социальная сеть для обмена фото котиков с возможностью комментариев и лайков. | Django, DRF, PostgreSQL, Docker |
| **[django-sprint4](https://github.com/DavidArutyuno/practicum_projects/tree/main/django-sprint4)** | Блог-платформа с постами, группами, комментариями и пагинацией. | Django, SQLite |
| **[django-sprint3](https://github.com/DavidArutyuno/practicum_projects/tree/main/django-sprint3)** | Расширенный блог: кастомные фильтры, теги, кэширование. | Django, PostgreSQL |
| **[django-sprint1](https://github.com/DavidArutyuno/practicum_projects/tree/main/django-sprint1)** | Первый Django-проект: статичные страницы и базовая маршрутизация. | Django |

---

### 🔌 API и бэкенд-сервисы

| Проект | Описание | Стек |
|--------|----------|------|
| **[api-final-yatube](https://github.com/DavidArutyuno/practicum_projects/tree/main/api-final-yatube)** | Полноценный REST API для соцсети Yatube (посты, группы, комментарии, подписки). JWT-авторизация. | DRF, JWT, PostgreSQL |
| **[api-yatube](https://github.com/DavidArutyuno/practicum_projects/tree/main/api-yatube)** | Базовый API для Yatube с правами доступа. | DRF, SQLite |
| **[api-yamdb](https://github.com/DavidArutyuno/practicum_projects/tree/main/api-yamdb)** | API для сбора отзывов на произведения (игры, фильмы, книги). Роли (Admin, Moderator, User). | DRF, Django Filters, JWT |
| **[async-yacut](https://github.com/DavidArutyuno/practicum_projects/tree/main/async-yacut)** | Асинхронный сервис сокращения ссылок на FastAPI + Redis. | FastAPI, Redis, async SQLAlchemy |

---

### 🕷️ Парсинг и сбор данных

| Проект | Описание | Стек |
|--------|----------|------|
| **[scrapy_parser_pep](https://github.com/DavidArutyuno/practicum_projects/tree/main/scrapy_parser_pep)** | Scrapy-паук для сбора статусов PEP с python.org. Результат — CSV с числовой статистикой. | Scrapy, CSV |
| **[bs4_parser_pep](https://github.com/DavidArutyuno/practicum_projects/tree/main/bs4_parser_pep)** | Аналогичный парсер PEP, но на Beautiful Soup с аргументами командной строки. | Beautiful Soup, argparse, requests |

---

### 🤖 Телеграм-боты

| Проект | Описание | Стек |
|--------|----------|------|
| **[homework-bot](https://github.com/DavidArutyuno/practicum_projects/tree/main/homework-bot)** | Бот, который раз в 10 минут проверяет статус домашки в Яндекс.Практикуме и присылает уведомления. | python-telegram-bot, logging, API-интеграция |

---

### 🐳 DevOps и инфраструктура

| Проект | Описание | Стек |
|--------|----------|------|
| **[infra_sprint1](https://github.com/DavidArutyuno/practicum_projects/tree/main/infra_sprint1)** | Контейнеризация Django-приложения: Dockerfile, docker-compose для Nginx + PostgreSQL. | Docker, Nginx, Gunicorn, PostgreSQL |
| **[django-testing](https://github.com/DavidArutyuno/practicum_projects/tree/main/django-testing)** | Покрытие Django-проекта тестами (unit, integration). Настройка CI через GitHub Actions. | Pytest, unittest, coverage, GitHub Actions |

---

### 🧠 Алгоритмы и игры

| Проект | Описание | Стек |
|--------|----------|------|
| **[the_snake](https://github.com/DavidArutyuno/practicum_projects/tree/main/the_snake)** | Классическая игра «Змейка» на чистом Python с использованием `curses`. | Python, curses |
| *(другие алгоритмические задачи в папках `django-sprint*`)* | Реализации сортировок, структур данных, рекурсии. | Python |

---

### 📊 Интеграции с Google Sheets

| Проект | Описание | Стек |
|--------|----------|------|
| **[QRkot-spreadsheets](https://github.com/DavidArutyuno/practicum_projects/tree/main/QRkot-spreadsheets)** | Отчеты о пожертвованиях в Google Sheets + QR-коды. | Google API (Sheets), QR Code, FastAPI |

---

## 🎯 Что еще можно улучшить для работодателя (мои планы)

- [ ] Добавить в каждый проект отдельный `README.md` с инструкцией по запуску и скриншотами.
- [ ] Написать тесты для всех проектов (где их еще нет).
- [ ] Документировать API через Swagger/ReDoc (там, где еще не сделано).
- [ ] Привести код к единому стилю (black/isort) и добавить pre-commit хуки.

---

## 📫 Как со мной связаться

- **GitHub:** [DavidArutyuno](https://github.com/DavidArutyuno)
- **Telegram:** [@ArDavidVl]
- **Email:** arutyunov-dv@ya.ru

---

⭐ Если вам понравились проекты — поставьте звезду репозиторию.  
Буду рад конструктивным замечаниям и предложениям о сотрудничестве!
