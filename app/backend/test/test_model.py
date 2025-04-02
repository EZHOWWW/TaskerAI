import unittest
from backend.task import Task
from backend.Model.model import TaskerModel


class TestAIModel(unittest.TestCase):
    m = TaskerModel()

    @unittest.skip
    def test_lvl_estimate(self):
        tsk_g_lvl = Task(text="Создать уникальный интернет магиз по продаже чая")
        tsk_l_lvl = Task(text="Сходить на пробежку")
        g_lvl = self.m.estimate_level(tsk_g_lvl, inplace=False)
        l_lvl = self.m.estimate_level(tsk_l_lvl, inplace=True)
        self.assertGreater(g_lvl, l_lvl)
        self.assertEqual(l_lvl, tsk_l_lvl.lvl)
        self.assertNotEqual(g_lvl, tsk_g_lvl.lvl)

    @unittest.skip
    def test_tags_estimate(self):
        tsk1 = Task(text="Выучить тему предел в математическом анализе")
        tsk2 = Task(text="Выучить тему множества в математике")
        tags1 = self.m.estimate_tags(tsk1)
        tags2 = self.m.estimate_tags(tsk2)
        self.assertNotEqual(tags1, tags2)
        print(tags1, tags2)
        self.assertTrue(not set(tags1).isdisjoint(tags2))  # множества пересекаются

        tags_count = 7
        tsk3 = Task(
            text="Разработать систему тренировок и сбалансированного питания для моих параметров тела"
        )
        tags3 = self.m.estimate_tags(tsk3, tags_count=tags_count)
        self.assertEqual(len(tags3), tags_count)

        tags_count = (0, 3)
        tags3 = self.m.estimate_tags(tsk3, tags_count=tags_count)
        self.assertTrue(tags_count[0] <= len(tags3) <= tags_count[1])

        ex_tags = ["Программирование", "IT"]
        tsk4 = Task(
            text="Разработать программу(запрограммировать) заметок для ведения и отслежования задачь"
        )
        tags4 = self.m.estimate_tags(tsk4, existent_tags=ex_tags)
        self.assertTrue(not set(ex_tags).isdisjoint(tags4))

    @unittest.skip
    def test_complexity_estimate(self):
        tsk_h = Task("Выучить 200 вопросов для экзамена на водительские права")
        tsk_e = Task("Сходить в кафе с друзьями")
        hc = self.m.estimate_complexity(tsk_h)
        ec = self.m.estimate_complexity(tsk_e)
        self.assertGreater(hc, ec)

        tsk1 = Task(
            "Выучить тему матрицы в линейной алгебре. Для меня это очень сложная задача"
        )
        tsk2 = Task(
            "Выучить тему теория групп в линейной алгебре. Для меня это очень простая тема"
        )
        c1 = self.m.estimate_complexity(tsk1)
        c2 = self.m.estimate_complexity(tsk2)
        self.assertGreater(c1, c2)

    def test_priority_estimate(self):
        task_g = Task("Доделать важный проект по работе, скоро дедлайн")
        task_l = Task("Научится готовить торт наполеон")
        pg = self.m.estimate_priority(task_g)
        pl = self.m.estimate_priority(task_l)
        self.assertGreater(pg, pl)

        self.assertEqual(task_g.priority, pg)


    def test_time_to_do_task_estimate(self):
        # TODO
        pass


if __name__ == "__main__":
    unittest.main()
