# 🖥️ Проект парсинга pep

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4.9+-blue.svg)](https://beautiful-soup-4.readthedocs.io/en/latest/#)

**Автор:** Давид Арутюнов  
**Почта:** [david.arutyuno@gmail.com](mailto:david.arutyuno@gmail.com)  
**Когорта:** Бэкенд-60, Яндекс.Практикум  


## 🔍 Описание проекта

Проект состоит из трех парсеров, собирающих данные с официального сайта Python.<br>
Собранные данные сохраняются:<br>
1. csv файлы скачиваются в директорию: src\results
2. zip архивы скачиваются в директорию: src\downloads
3. работа парсера логируется в директорию: src\logs

## 🛠 Быстрый старт

1. Клонируйте репозиторий bs4_parser_pep на свой компьютер.

    [git clone https://github.com/DavidArutyuno/bs4_parser_pep](https://github.com/DavidArutyuno/bs4_parser_pep)

2. Настройте окружение

    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    venv\Scripts\activate    # Windows
    ```

3. Обновите менеджер пакетов pip

    ```bash
    python -m pip install --upgrade pip
    ```


4. Установите зависимости из файла requirements.txt.

    ```bash
    pip install -r requirements
    ```

5. Запустите проект в нужном режиме работы парсера:

    * Спарсить и сохранить данные в csv файл со страницы [What’s new in Python](https://docs.python.org/3/whatsnew/3.14.html):

        ```bash
        python main.py whats_new --output file
        ```

    * Спарсить и сохранить данные в csv файл [со списком документации Python](https://docs.python.org/3/):

        ```bash
        python main.py latest_versions --output file
        ```
    * [Скачать документацию](https://docs.python.org/3/download.html) по новой версии Python в zip файле :

        ```bash
        python main.py download --output file
        ```

    * Спарсить и сохранить данные в csv файл по статусам  [документов PEP](https://peps.python.org/)

        ```bash
        python main.py pep --output file
        ```

    
