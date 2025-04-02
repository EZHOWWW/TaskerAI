
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import List
import peewee as pw
from playhouse.shortcuts import model_to_dict

# Инициализация базы данных
db = pw.SqliteDatabase('tasks.db')
NOW = datetime.now()


# Определение моделей Peewee
class BaseModel(pw.Model):
    class Meta:
        database = db


class Tag(BaseModel):
    name = pw.CharField(unique=True)


class Task(BaseModel):
    text = pw.TextField(default="Empty task")
    lvl = pw.IntegerField(default=0)
    max_lvl = pw.IntegerField(default=25)
    complexity = pw.FloatField(default=0.0)
    priority = pw.FloatField(default=0.0)
    date_set_task = pw.DateTimeField(default=NOW)
    date_start_task = pw.DateTimeField(default=NOW)
    time_to_do_task = pw.DateTimeField(default=NOW)
    deadline = pw.DateTimeField(default=NOW)


class TaskTag(BaseModel):
    task = pw.ForeignKeyField(Task)
    tag = pw.ForeignKeyField(Tag)


class Subtask(BaseModel):
    parent = pw.ForeignKeyField(Task, backref="subtasks")
    child = pw.ForeignKeyField(Task)


db.connect()
db.create_tables([Task, Tag, TaskTag, Subtask], safe=True)


# Dataclasses
@dataclass
class DateTimeTask:
    date_set_task: datetime = NOW
    date_start_task: datetime = NOW
    time_to_do_task: datetime = NOW
    deadline: datetime = NOW


@dataclass
class TaskData:
    text: str = "Empty task"
    lvl: int = 0
    MAX_LVL: int = 25
    tags: List[str] = field(default_factory=list)
    complexity: float = 0.0
    priority: float = 0.0
    date_time_task: DateTimeTask = field(default_factory=DateTimeTask)
    subtasks: List["TaskData"] = field(default_factory=list)


class DatabaseManager:
    def add_task(self, task_data: TaskData, parent_task=None):
        # Конвертируем dataclass в словарь
        task_dict = asdict(task_data)
        date_time = task_dict.pop("date_time_task")
        tags = task_dict.pop("tags")
        subtasks = task_dict.pop("subtasks")

        # Создаем основную задачу
        with db.atomic():
            # Сохраняем временные метки
            task_dict.update(date_time)
            task = Task.create(**task_dict)

            # Добавляем теги
            if tags:
                Tag.insert_many(
                    [{"name": tag} for tag in tags]
                ).on_conflict_ignore().execute()
                tags_obj = Tag.select().where(Tag.name.in_(tags))
                TaskTag.insert_many(
                    [{"task": task, "tag": tag} for tag in tags_obj]
                ).execute()

            # Добавляем подзадачи
            for subtask in subtasks:
                subtask_obj = self.add_task(subtask, parent_task=task)
                Subtask.create(parent=task, child=subtask_obj)

            # Связь с родительской задачей
            if parent_task:
                Subtask.create(parent=parent_task, child=task)

            return task

    def _task_query(self):
        return (
            Task.select(
                Task,
                pw.fn.group_concat(Tag.name).alias("tags"),
                pw.fn.group_concat(Subtask.child).alias("subtasks"),
            )
            .left_outer_join(TaskTag)
            .left_outer_join(Tag)
            .left_outer_join(Subtask, on=Subtask.parent)
            .group_by(Task.id)
        )

    def _convert_to_dataclass(self, task_model):
        task_dict = model_to_dict(task_model)
        task_dict["tags"] = task_model.tags.split(",") if task_model.tags else []
        task_dict["subtasks"] = [
            self._convert_to_dataclass(sub)
            for sub in Task.select()
            .join(Subtask, on=Subtask.child)
            .where(Subtask.parent == task_model)
        ]

        # Преобразование DateTime полей
        date_time = DateTimeTask(
            date_set_task=task_model.date_set_task,
            date_start_task=task_model.date_start_task,
            time_to_do_task=task_model.time_to_do_task,
            deadline=task_model.deadline,
        )
        return TaskData(
            **{**task_dict, "date_time_task": date_time}, MAX_LVL=task_model.max_lvl
        )

    def get_tasks_by_deadline(self, deadline: datetime):
        query = self._task_query().where(Task.deadline == deadline)
        return [self._convert_to_dataclass(task) for task in query]

    def get_tasks_by_tags(self, tags: List[str]):
        query = self._task_query().join(TaskTag).join(Tag).where(Tag.name.in_(tags))
        return [self._convert_to_dataclass(task) for task in query.distinct()]

    def get_tasks_by_complexity(self, complexity: float):
        query = self._task_query().where(Task.complexity == complexity)
        return [self._convert_to_dataclass(task) for task in query]

    def get_tasks_by_priority(self, priority: float):
        query = self._task_query().where(Task.priority == priority)
        return [self._convert_to_dataclass(task) for task in query]