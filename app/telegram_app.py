# main.py
import uvicorn
import threading
from aiogram import Dispatcher
from fastapi import FastAPI
from typing import Optional

# Импорты микросервиса
from backend.Model.model_app import (
    app as model_app,
)  # Предполагается, что модель находится здесь


class Application:
    def __init__(self):
        self.tg_bot = None

    def run(self):
        # Запуск FastAPI сервера в отдельном потоке
        server_thread = threading.Thread(target=self.run_server, daemon=True)
        server_thread.start()

        # Запуск Telegram бота
        self.run_telegram_bot()

    def run_server(self):
        # uvicorn.run(model_app, host="0.0.0.0", port=8000)
        uvicorn.run("backend.Model.model_app:app")

    def run_telegram_bot(self):
        from frontend.bot import TelegramBot

        self.tg_bot = TelegramBot(model_url="http://localhost:8000")
        self.tg_bot.run()


if __name__ == "__main__":
    Application().run()

# import uvicorn

# if __name__ == "__main__":
#     uvicorn.run("backend.Model.model_app:app")
