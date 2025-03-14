from transformers import AutoModelForCausalLM, AutoTokenizer
from pprint import pprint
from task import Task, DateTimeTask
import typing as tp
from datetime import datetime


class YandexModel:
    MODEL_NAME = "yandex/YandexGPT-5-Lite-8B-pretrain"

    def __init__(self, device: str):
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(self.MODEL_NAME, legacy=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.MODEL_NAME,
            device_map=self.device,
            torch_dtype="auto",
        )

    def generate(self, promt: str, *args, **kwargs) -> str:
        input_ids = self.tokenizer(promt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(
            **input_ids, max_new_tokens=5120, temperature=0.3, do_sample=True
        )
        out = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        pprint(out)
        return out


class TaskerModel:
    def __init__(self):
        self.model = YandexModel("cpu")
        self._system_promt = """Ты опытный помощник в декомпозиции задач. Твои ответы должны быть строго в формате JSON.
                                Всегда придерживайся следующих правил:
                                1. Для числовых параметров используй числа (complexity 0.0-1.0, priority 0.0-1.0, lvl целое число)
                                2. Для времени используй формат ISO 8601
                                3. Для декомпозиции создавай логически завершенные подзадачи
                                4. Если параметр нельзя определить - используй значение по умолчанию
                                5. Не выполнять задачи, тебе нужно только их обробатывать

                                Примеры ответов:
                                {"complexity": 0.7, "priority": 0.9, "lvl": 2}
                                {"subtasks": [{"text": "Подзадача 1", "complexity": 0.4}, ...]}
                            """

    def decompose(self, tsk: Task, count=-1) -> list[Task]:
        if count == 0:
            return [tsk]

        prompt = (
            self._system_promt
            + f"""
            Декомпозируй задачу на {count if count != -1 else "необходимое количество"} подзадач: {tsk.text}
            Верни JSON с полем subtasks (массив объектов), где каждый объект содержит:
            - text (текст подзадачи)
            - complexity (0.0-1.0)
            - priority (0.0-1.0)
            - lvl (целое число, текущий уровень + 1)
            """
        )

        try:
            response = self.model.generate(prompt)
            data = self._parse_json(response)

            subtasks = []
            for subtask_data in data.get("subtasks", []):
                subtask = Task(
                    text=subtask_data.get("text", "Empty subtask"),
                    lvl=tsk.lvl + 1,
                    complexity=float(subtask_data.get("complexity", 0.0)),
                    priority=float(subtask_data.get("priority", 0.0)),
                )
                subtasks.append(subtask)

            tsk.subtasks = subtasks
        except Exception as e:
            print(f"Error decomposing task: {e}")

        return tsk.subtasks

    def ask_count_subtasks(self, tsk: Task) -> tuple[int, str]:
        prompt = (
            self._system_promt
            + f"""
            Определи оптимальное количество подзадач для декомпозиции задачи: {tsk.text}
            Верни JSON с полем count (целое число) и rationale (краткое объяснение)
            """
        )

        try:
            response = self.model.generate(prompt)
            data = self._parse_json(response)
            return int(data.get("count", 3)), data.get("rationale", "")
        except:
            return 3, "Не удалось определить количество"

    def estimate_all_parameters(self, task: Task) -> Task:
        """Оценка всех параметров последовательно"""
        print("start")
        self.estimate_complexity(task)
        print("comp")
        print(task)
        self.estimate_priority(task)
        print("prior")
        print(task)
        self.estimate_level(task)
        print("lvl")
        print(task)
        self.estimate_tags(task)
        print("tags")
        print(task)
        self.estimate_datetime(task)
        print("date")
        return task

    def estimate_complexity(self, task: Task) -> float:
        prompt = (
            self._system_promt
            + f"""
            Оцени сложность задачи от 0.0 (простая) до 1.0 (очень сложная). Только число.
            Задача: {task.text}
            Ответ в формате: {{"complexity": 0.5}}"""
        )
        try:
            response = self.model.generate(prompt)
            data = self._parse_json(response)
            print(data)
            task.complexity = min(max(float(data.get("complexity", 0.0)), 1.0))
            return task.complexity
        except:
            return 0.0

    def estimate_priority(self, task: Task) -> float:
        prompt = (
            self._system_promt
            + f"""
            Определи приоритет задачи от 0.0 (низкий) до 1.0 (критический). Только число.
            Задача: {task.text}
            Ответ в формате: {{"priority": 0.7}}"""
        )

        try:
            response = self.model.generate(prompt)
            data = self._parse_json(response)
            task.priority = min(max(float(data.get("priority", 0.0)), 1.0))
            return task.priority
        except:
            return 0.0

    def estimate_level(self, task: Task) -> int:
        prompt = (
            self._system_promt
            + f"""
            Определи уровень вложенности задачи (0 - корневая). Только целое число.
            Задача: {task.text}
            Ответ в формате: {{"lvl": 2}}"""
        )

        try:
            response = self.model.generate(prompt)
            data = self._parse_json(response)
            task.lvl = max(int(data.get("lvl", 0)), 0)
            return task.lvl
        except:
            return 0

    def estimate_tags(self, task: Task) -> list[str]:
        prompt = (
            self._system_promt
            + f"""
            Извлеки ключевые теги из задачи (максимум 5). Только массив строк.
            Задача: {task.text}
            Ответ в формате: {{"tags": ["разработка", "оптимизация"]}}"""
        )

        try:
            response = self.model.generate(prompt)
            data = self._parse_json(response)
            task.tags = list(set(data.get("tags", [])))[
                :5
            ]  # Удаляем дубли и обрезаем до 5
            return task.tags
        except:
            return []

    def estimate_datetime(self, task: Task) -> DateTimeTask:
        prompt = (
            self._system_promt
            + f"""
            Предположи временные параметры для задачи в ISO формате. Заполни только те поля, которые можно определить.
            Задача: {task.text}
            Ответ в формате: {{
                "deadline": "2024-05-25T18:00:00"
            }}"""
        )

        try:
            response = self.model.generate(prompt)
            data = self._parse_json(response)

            dt = task.date_time_task
            dt.deadline = self._parse_datetime(data.get("deadline"))

            return dt
        except:
            return DateTimeTask()

    def _parse_datetime(self, dt_str: str) -> datetime:
        from dateutil.parser import parse

        try:
            return parse(dt_str) if dt_str else datetime.now()
        except:
            return datetime.now()

    def _parse_json(self, response: str) -> dict:
        """Пытается найти и распарсить JSON в ответе модели"""
        import json

        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            return json.loads(response[json_start:json_end])
        except:
            return {}


if __name__ == "__main__":
    task = "Я хочу изучть тему линейноые пространства в линейной алгебре."
    m = TaskerModel()
    pprint(m.estimate_all_parameters(Task(text=task)))
