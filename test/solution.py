import unittest

from zoonomia.solution import Objective, Fitness, Solution


class TestObjective(unittest.TestCase):

    def test_evaluate(self):
        eval_func = lambda solution: 42.0
        weight = 6.66
        expected = eval_func(None) * weight
        solution = Solution(graph=None, objectives=None, map_=None)  # FIXME

        objective = Objective(eval_func=eval_func, weight=weight)
        self.assertEqual(objective.evaluate(solution=solution), expected)


class TestFitness(unittest.TestCase):

    def test_equals(self):
        score = 66.6
        objective = Objective(eval_func=lambda _: 42.0, weight=6.66)
        fitness1 = Fitness(score=score, objective=objective)
        fitness2 = Fitness(score=score, objective=objective)
        self.assertEqual(fitness1, fitness2)


class TestSolution(unittest.TestCase):
    pass
