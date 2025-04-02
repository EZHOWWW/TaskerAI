from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from dotenv import load_dotenv
import os
import logging
import asyncio
import aiohttp
import json


class TelegramBot:
    def __init__(self, model_url: str):
        load_dotenv()
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.bot = Bot(token=self.token)
        self.dp = Dispatcher()
        self.model_url = model_url
        self._register_handlers()

    def _register_handlers(self):
        self.dp.message.register(self._start, Command("start"))
        # self.dp.message.register(self._echo, F.text)
        self.dp.message.register(self._promt_to_model, Command("promt"))

    async def _start(self, message: types.Message):
        await message.answer("👋 Привет! Я простой бот. Просто напиши мне что-нибудь")

    async def _echo(self, message: types.Message):
        await message.answer(f"🤖 Вы написали: {message.text}")

    async def _promt_to_model(self, message: types.Message):
        system_promt = """
                    Ты умный помощник для планирования задач. 
                    Помоги пользователю разбить задачу на подзадачи, 
                    определить приоритеты и сроки выполнения. """
        user_prompt = message.text
        async with aiohttp.ClientSession() as session:
            payload = {"system_promt": system_promt, "user_promt": user_prompt}

            headers = {"accept": "application/json", "Content-Type": "application/json"}

            async with session.get(
                "http://127.0.0.1:8000/model/promt",
                headers=headers,
                data=json.dumps(payload),
            ) as response:
                # Проверяем статус ответа
                if response.status == 200:
                    # Парсим JSON ответ
                    result = await response.json()
                    await message.reply(str(result))
                else:
                    error = await response.text()
                    await message.reply(f"❌ Ошибка {response.status}: {error}")

        # try:
        #     async with aiohttp.ClientSession() as session:
        #         # Отправляем GET-запрос к микросервису
        #         async with session.get(
        #             self.model_url + "/model/promt",
        #             params={
        #                 "system_promt": "hollo",
        #                 "user_promt": "hello",
        #             },
        #         ) as response:
        #             if response.status == 200:
        #                 result = await response.text()
        #                 await message.reply(result)
        #             else:
        #                 error = await response.text()
        #                 await message.reply(f"❌ Ошибка {response.status}: {error}")

        # except aiohttp.ClientConnectorError:
        #     await message.reply("⚠️ Сервер модели недоступен!")
        # except Exception as e:
        #     await message.reply(f"⚠️ Произошла ошибка: {str(e)}")

    async def _start_polling(self):
        await self.dp.start_polling(self.bot)

    def run(self):
        logging.basicConfig(level=logging.INFO)
        asyncio.run(self._start_polling())


if __name__ == "__main__":
    bot = TelegramBot()
    bot.run()
