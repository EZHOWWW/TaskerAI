from pprint import pprint
from backend.task import Task, DateTimeTask
import typing as tp
from datetime import datetime
from backend.model.deep_seek_model import DeepSeekModel
from pprint import pprint
from numpy import clip


class TaskerModel:
    # TODO agetns for other parameter
    def __init__(self):
        self.model = DeepSeekModel()
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

        user_prompt = f"""
            Декомпозируй задачу на {count if count != -1 else "необходимое количество"} подзадач: {tsk.text}
            Верни JSON с полем subtasks (массив объектов), где каждый объект содержит:
            - text (текст подзадачи)
            - complexity (0.0-1.0)
            - priority (0.0-1.0)
            - lvl (целое число, текущий уровень + 1)
            """

        try:
            response = self.promt(self._system_promt, user_prompt)
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
        user_prompt = f"""
            Определи оптимальное количество подзадач для декомпозиции задачи: {tsk.text}
            Например у задачи: Написать статью на тему ИИ, такие подзадачи:
                {"subtasks": [{"text": "Определить тему для статьи"},
                            {"text": "Провести исследования и анализ"},
                            {"text": "Определить структуру статьи"},
                            {"text": "Написать текст статьи"},
                            {"text": "Опубликоваться"}] } 
                        => 5 подзадачь.
                        => Ответ: {"count_subtasks": 5}
            У задачи "Сходить в магазин"
                        => 0 подзадачь.
                        => Ответ: {"count_subtasks": 0}
            Декомпозиция идет только на один уровень, не нужно декомпозировать подзадачи.
            Верни JSON с полем count_subtasks (целое число) 
            Ответ: {"count_subtasks": количество подзадач}
            """

        try:
            response = self.promt(self._system_promt, user_prompt)
            data = self._parse_json(response)
            return int(data.get("count", 3)), data.get("rationale", "")
        except:
            return 3, "Не удалось определить количество"

    def estimate_all_parameters(self, task: Task) -> Task:
        """Оценка всех параметров последовательно"""
        print("start")
        self.estimate_complexity(task)
        print("comp")
        pprint(task)
        self.estimate_priority(task)
        print("prior")
        pprint(task)
        self.estimate_level(task)
        print("lvl")
        pprint(task)
        self.estimate_tags(task)
        print("tags")
        pprint(task)
        self.estimate_datetime(task)
        print("date")
        return task

    def estimate_complexity(self, task: Task, inplace: bool = True) -> float:
        user_prompt = f"""
            Оцени сложность задачи от 0.0 (простая) до 1.0 (очень сложная).
            Например задача: "Разработать программу(запрограммировать) заметок для ведения и отслежования задачь" - 0.9,
                а задача: побриться новой бритвой - 0.0.
            Если в задаче пользователь явно указал что для него это задача сложная или легкая учти его мнение.
            Ответ - только число c максимальной точностью до 3ех знаков после запятой.
            Задача: {task.text}
            Ответ в формате: {{"complexity": 0.5}}"""
        try:
            response = self.promt(self._system_promt, user_prompt)
            data = self._parse_json(response)
            c = float(clip(float(data.get("complexity", 0.0)), 0.0, 1.0))
            if inplace:
                task.complexity = c
            return c
        except:
            return 0.0

    def estimate_priority(self, task: Task, inplace: bool = True) -> float:
        user_prompt = f"""
            Определи приоритет задачи от 0.0 (низкий) до 1.0 (критический). 
            Например задача: Срочно выучить билеты, потому что завтра экзамен, имеет приоритет 1.0, 
                а задача продолжить обучение игры на гитаре имеет прироритет 0.2
            Если в задаче пользователь явно указал что для него это задача важная или второстипенная учти его мнение.
            Ответ - только число c максимальной точностью до 3ех знаков после запятой.
            Задача: {task.text}
            Ответ в формате: {{"priority": 0.7}}"""

        try:
            response = self.promt(self._system_promt, user_prompt)
            data = self._parse_json(response)
            p = float(clip(float(data.get("priority", 0.0)), 0.0, 1.0))
            if inplace:
                task.priority = p
            return p
        except:
            return 0.0

    def estimate_level(self, task: Task, inplace: bool = True) -> int:
        user_prompt = f"""
            Определи уровень вложенности задачи(lvl) (0 - минимальная, {task.MAX_LVL} - максимальная). 
            Более абстрактные, многофакторные и сложные задачи имеют больший lvl, а более конекретные и легкие - меньший. 
            Если расматривать из дерево подзадачь этой задачи то высота токого дерева и lvl корневой вершины = lvl этой задачи,  
                а lvl листьев в этом дереве = 0 
            Ответ - только целое число от 0, до {task.MAX_LVL} включительно. 
            Например задача: Создать интернет магазин имеет lvl = {task.MAX_LVL} (потому что предпологает очень много этапов для выполнения), 
                a задача: сходить в магазин рядом с домом, lvl = 0 (потому что задача тривиальная).
            Задача: {task.text}
            Ответ в формате: {{"lvl": 2}}"""
        try:
            response = self.promt(self._system_promt, user_prompt)
            data = self._parse_json(response)
            lvl = int(clip(data.get("lvl", 0), 0, task.MAX_LVL, dtype=int))
            if inplace:
                task.lvl = lvl
            return lvl
        except:
            # log to not possible to get lvl
            return 0

    def estimate_tags(
        self,
        task: Task,
        tags_count: int | tuple[int] = (0, 5),
        existent_tags: list = [],
        inplace=True,
    ) -> list[str]:
        """
        tags_count : если int то количество тэгов, если tuple то диапозон
        """
        user_prompt = f"""
            Извлеки ключевые теги из задачи 
                {f"(от {tags_count[0]} до {tags_count[1]})" if isinstance(tags_count, tuple) and len(tags_count) == 2 else f"{tags_count} штук"}. 
            Теги это ключевые слова и ассоциации из этой задачей. Теги должны быть короткие и конкретные
            Постарайся не придумывать новые тэги, если они уже есть в списке существующих: {existent_tags if len(existent_tags) != 0 else ("список пуст")}, 
                но если теги не совподают то придумай новые.
            Например у задания: Выучить тему линейные пространства в линейной алгебре, будут такие теги: ['Учеба', 'Математика', 'Линейная алгебра'].
            Ответ - только массив строк правильного размера.
            Задача: {task.text}
            Ответ в формате: {{"tags": ["разработка", "оптимизация"]}}"""

        try:
            response = self.promt(self._system_promt, user_prompt)
            data = self._parse_json(response)
            max_count = (
                tags_count[1]
                if isinstance(tags_count, tuple) and len(tags_count) == 2
                else tags_count
            )
            task.tags = list(set(data.get("tags", [])))[:max_count]
            return task.tags
        except:
            return []

    def estimate_datetime(self, task: Task, inplace: bool = True) -> DateTimeTask:
        user_prompt = f"""
            Предположи временные параметры для задачи в ISO формате. Определи сколько времени нужно на выполнение этой задачи.
            Задача: {task.text}
            Ответ в формате: {{
                "deadline": "2024-05-25T18:00:00"
            }}"""

        try:
            response = self.promt(self._system_promt, user_prompt)
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

    def promt(self, system_promt: str, user_prompt: str) -> str:
        return self.model.generate(system_promt, user_prompt)
