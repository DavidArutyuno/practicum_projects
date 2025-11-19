# 🖥️ Проект парсинга PEP на scrapy

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Scrapy](https://img.shields.io/badge/Scrapy-2.8+-orange.svg)](https://scrapy.org)

**Автор:** Давид Арутюнов  
**Почта:** [david.arutyuno@gmail.com](mailto:david.arutyuno@gmail.com)  
**Когорта:** Бэкенд-60, Яндекс.Практикум  

## 🔍 Описание проекта

Проект представляет собой парсер документов PEP (Python Enhancement Proposals), написанный на фреймворке Scrapy.<br>
Парсер собирает данные с официального сайта PEP и сохраняет их в двух форматах:<br>

1. **Список всех PEP** - файл `pep_дата_время.csv` с номерами, названиями и статусами документов
2. **Сводка по статусам** - файл `status_summary_дата_время.csv` с количеством PEP в каждом статусе

Собранные данные сохраняются в директорию `results/` в корне проекта.

## 🛠 Быстрый старт

1. Клонируйте репозиторий на свой компьютер.

    ```bash
    git clone https://github.com/DavidArutyuno/scrapy_parser_pep
    cd pep_parse
    ```

2. Настройте окружение

    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    venv\Scripts\activate     # Windows
    ```

3. Обновите менеджер пакетов pip

    ```bash
    python -m pip install --upgrade pip
    ```

4. Установите зависимости из файла requirements.txt.

    ```bash
    pip install -r requirements.txt
    ```

5. Запустите парсер для сбора данных о PEP:

    ```bash
    scrapy crawl pep
    ```

## 📁 Структура проекта

pep_parse/<br>
├── pep_parse/<br>
│ ├── spiders/<br>
│ │ ├── init.py<br>
│ │ └── pep_spider.py # Основной паук для парсинга PEP<br>
│ ├── init.py<br>
│ ├── items.py # Модели данных<br>
│ ├── pipelines.py # Pipeline для обработки данных<br>
│ └── settings.py # Настройки Scrapy<br>
├── results/ # Директория с результатами (создается автоматически)<br>
│ ├── pep_2024-01-20T12-30-45.csv<br>
│ └── status_summary_2024-01-20_12-30-45.csv<br>
├── requirements.txt<br>
└── README.md<br>


### Запуск с подробным логированием
```bash
scrapy crawl pep --loglevel=INFO
```


### Сохранение результатов в разных форматах
```bash
# В JSON (только список PEP)
scrapy crawl pep -o peps.json

# В CSV (только список PEP)
scrapy crawl pep -o peps.csv
```


### 🔧 Технические особенности

* Фреймворк: Scrapy 2.8+

* Селекторы: CSS-селекторы для точного извлечения данных

* Обработка данных: Кастомный Pipeline для генерации сводки

* Экспорт: Автоматическое сохранение через Scrapy Feeds

* Кодировка: UTF-8 для корректного отображения символов

### 📝 Примечания

* Парсер собирает данные только из секции index-by-category на сайте PEP

* Для каждого PEP извлекается номер, название и текущий статус

* Сводка автоматически подсчитывает общее количество документов

* Все файлы сохраняются с timestamp в названии для избежания конфликтов