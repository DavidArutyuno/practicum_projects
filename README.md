# Homework Bot 🤖

[![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)](https://python.org)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?logo=telegram)](https://core.telegram.org/bots)
[![SQLite](https://img.shields.io/badge/SQLite-DB-lightgrey?logo=sqlite)](https://sqlite.org)

**Автор:** Давид Арутюнов  
**Почта:** [david.arutyuno@gmail.com](mailto:david.arutyuno@gmail.com)  
**Когорта:** Бэкенд-60, Яндекс.Практикум  

## 🚀 Технологии
- **Python 3.9+**
- **Telegram Bot API** (`python-telegram-bot`)
- **SQLite 3** (хранение истории статусов)
- **Requests** (HTTP-запросы к API)
- **Logging** (цветное логирование)
- **Dotenv** (управление переменными окружения)

## 🔍 Описание
Умный бот-ассистент для трекинга статусов домашних работ. Умеет:

✅ Автоматически проверять статус каждые 10 минут  
✅ Присылать уведомления в Telegram об изменениях  
✅ Хранить историю статусов в SQLite  
✅ Показывать актуальный статус по запросу  
✅ Логировать все события с цветовой разметкой  

## 🛠 Быстрый старт

```bash
        # 1. Клонируйте репозиторий
        git clone https://github.com/DavidArutyuno/homework-bot.git
        cd homework-bot

        # 2. Настройте окружение
        python -m venv venv
        source venv/bin/activate  # Linux/Mac
        venv\Scripts\activate    # Windows

        # 3. Установите зависимости
        pip install -r requirements.txt

        # 4. Настройте переменные окружения
        cp .env.example .env
        # Заполните .env своими данными

        # 5. Запустите бота
        python homework.py
```

⚙️ Функциональные клавиши

    /status - Проверить текущий статус

    Проверить сейчас 🔄 - Принудительный запрос к API

    История статусов 📜 - Последние 5 записей

📝 Логирование

Бот использует многоуровневое логирование:

    INFO - Успешные операции

    WARNING - Незначительные проблемы

    ERROR - Критические сбои

Логи выводятся в консоль с цветовой маркировкой.

