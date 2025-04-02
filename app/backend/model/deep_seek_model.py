from backend.model.imodel import LLModel
from dotenv import load_dotenv
import requests
import json
import os


class DeepSeekModel(LLModel):
    def __init__(self):
        load_dotenv()
        self._API_KEY = os.getenv(
            "DEEPSEEK_API_KEY"
        )  # внутри скобок свой апи ключ отсюда https://openrouter.ai/settings/keys
        self._MODEL = "deepseek/deepseek-chat:free"

    def generate(self, system_promt: str, user_promt: str, *args, **kwargs) -> str:
        headers = {
            "Authorization": f"Bearer {self._API_KEY}",
            "Content-Type": "application/json",
        }
        data = {
            "model": self._MODEL,
            "messages": [
                {"role": "system", "content": system_promt},
                {"role": "user", "content": user_promt},
            ],
            "stream": False,
        }
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=json.dumps(data),
        )
        res = response.json()["choices"][0]["message"]["content"]
        print(res)
        return res


from pprint import pprint

if __name__ == "__main__":
    m = DeepSeekModel()
    print(m.generate("Ты помошник в решении задач", "Расскажи о себе"))
