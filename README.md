# TaskerAI
Task manager with AI support. Front is tg bot.

# Настройка окружения

- Создать виртуальное окружение
  ```bash
  python -m venv
  ```
  Или с помощью uv:
  ```bash
  uv venv
  ```
- Активировать виртуальное окружение
  + На Linux
    ```bash
    source venv/bin/activate
    ```
  + На Windows
    ```bash
    source venv/Scripts/activate
    ```
- Установить зависимости:
  ```bash
  pip install requirements.txt
  ```
  Или с помощью uv:
  ```bash
  uv sync
  ```
  
- Создать файл .env и проставить свои токены телеграм бота и deepseek api, как в файле '.env_example'

# Запуск

  ```bash
  cd app
  python __main__.py
  ```
  Или с помощью uv:
  ```bash
  uv run app
  ```
