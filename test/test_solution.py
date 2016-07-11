import unittest
import time
import mock
import logging

from concurrent.futures import ThreadPoolExecutor
from zoonomia.tree import Node, Tree
from zoonomia.solution import Objective, Fitness, Solution
from zoonomia.types import Type
from zoonomia.lang import Symbol, Call, Operator, OperatorSet

logging.basicConfig()  # FIXME: wat
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

POOL = ThreadPoolExecutor(max_workers=100)


def futures_map(fn, iterable):
    return POOL.map(fn, iterable)


class TestObjective(unittest.TestCase):

    def test_objective_hash(self):
        """Test that two objectives which are identically distinct yet refer to
        the same data have equal hashes.

        """
        def eval_func(solution): return 66.6

        weight = 42.0

        objective_1 = Objective(eval_func=eval_func, weight=weight)
        objective_2 = Objective(eval_func=eval_func, weight=weight)

        self.assertIsNot(objective_1, objective_2)

        self.assertEqual(hash(objective_1), hash(objective_2))

    def test_objective_equals(self):
        """Test that two objectives which are identically distinct yet refer to
        the same data are equal.

        """
        def eval_func(solution): return 66.6

        weight = 42.0

        objective_1 = Objective(eval_func=eval_func, weight=weight)
        objective_2 = Objective(eval_func=eval_func, weight=weight)

        self.assertEqual(objective_1, objective_2)
        self.assertEqual(objective_2, objective_1)

    def test_objective_not_equals(self):
        """Test that two objectives which do not refer to the same data are
        unequal.

        """
        def eval_func(solution): return 66.6

        weight_1 = 42.0
        weight_2 = 43.0

        objective_1 = Objective(eval_func=eval_func, weight=weight_1)
        objective_2 = Objective(eval_func=eval_func, weight=weight_2)

        self.assertNotEqual(objective_1, objective_2)
        self.assertNotEqual(objective_2, objective_1)

    def test_evaluate(self):
        """Test that calling an Objective's *evaluate* method produces a
        Fitness object whose *score* attribute is equal to the *weight*
        parameter multiplied by the result of calling the *eval_func*.

        """
        int_type = Type(name='int')

        def eval_func(solution): return 66.6

        weight = 42.0

        objective = Objective(eval_func=eval_func, weight=weight)
        terminal_op = Operator(symbol=Symbol(name='term', dtype=int_type))
        root = Node(operator=terminal_op)

        solution = Solution(tree=Tree(root=root), objectives=(objective,))
        fitness = objective.evaluate(solution)

        self.assertEqual(fitness.score, weight * eval_func(solution))


class TestFitness(unittest.TestCase):

    def test_fitness_attributes(self):
        """Test that a Fitness object's *score* and *objective* attributes
        refer to the data passed into the constructor.

        """
        int_type = Type(name='int')

        def eval_func(solution): return 66.6

        weight = 42.0

        objective = Objective(eval_func=eval_func, weight=weight)
        terminal_op = Operator(symbol=Symbol(name='term', dtype=int_type))
        root = Node(operator=terminal_op)

        solution = Solution(tree=Tree(root=root), objectives=(objective,))

        score = weight * eval_func(solution)

        fitness = Fitness(score=score, objective=objective)

        self.assertIs(fitness.score, score)
        self.assertIs(fitness.objective, objective)

    def test_fitness_hash(self):
        """Test that two identically distinct Fitness objects which refer to
        the same data have equal hashes.

        """
        int_type = Type(name='int')

        def eval_func(solution): return 66.6

        weight = 42.0

        objective = Objective(eval_func=eval_func, weight=weight)
        terminal_op = Operator(symbol=Symbol(name='term', dtype=int_type))
        root = Node(operator=terminal_op)

        solution = Solution(tree=Tree(root=root), objectives=(objective,))

        score = weight * eval_func(solution)

        fitness_1 = Fitness(score=score, objective=objective)
        fitness_2 = Fitness(score=score, objective=objective)

        self.assertEqual(hash(fitness_1), hash(fitness_2))

    def test_fitness_equals(self):
        """Test that two identically distinct Fitness objects which refer to
        the same data are equal.

        """
        int_type = Type(name='int')

        def eval_func(solution): return 66.6

        weight = 42.0

        objective = Objective(eval_func=eval_func, weight=weight)
        terminal_op = Operator(symbol=Symbol(name='term', dtype=int_type))
        root = Node(operator=terminal_op)

        solution = Solution(tree=Tree(root=root), objectives=(objective,))

        score = weight * eval_func(solution)

        fitness_1 = Fitness(score=score, objective=objective)
        fitness_2 = Fitness(score=score, objective=objective)

        self.assertEqual(fitness_1, fitness_2)
        self.assertEqual(fitness_2, fitness_1)

    def test_fitness_not_equals(self):
        """Test that two Fitness objects which do not refer to the same data
        are unequal.

        """
        int_type = Type(name='int')

        def eval_func(solution): return 66.6

        weight = 42.0

        objective = Objective(eval_func=eval_func, weight=weight)
        terminal_op = Operator(symbol=Symbol(name='term', dtype=int_type))
        root = Node(operator=terminal_op)

        solution = Solution(tree=Tree(root=root), objectives=(objective,))

        score_1 = weight * eval_func(solution)
        score_2 = 666.666

        fitness_1 = Fitness(score=score_1, objective=objective)
        fitness_2 = Fitness(score=score_2, objective=objective)

        self.assertNotEqual(fitness_1, fitness_2)
        self.assertNotEqual(fitness_2, fitness_1)

    def test_fitness_gt(self):
        """Test that fitness_1 with score_1 > score_2 is greater than fitness_2
        with score_2.

        """
        def eval_func(solution): return 0.0  # only used for constructing objective

        objective = Objective(eval_func=eval_func, weight=42.0)

        fitness_1 = Fitness(score=66.7, objective=objective)
        fitness_2 = Fitness(score=66.6, objective=objective)

        self.assertGreater(fitness_1, fitness_2)

    def test_fitness_ge(self):
        """Test that fitness_1 with score_1 > score_2 is greater than or equal
        to fitness_2 with score_2 and that fitness_1 is greater than or equal
        to fitness_3 with score_3 == score_1.

        """
        def eval_func(solution): return 0.0  # only used for constructing objective

        objective = Objective(eval_func=eval_func, weight=42.0)

        fitness_1 = Fitness(score=66.7, objective=objective)
        fitness_2 = Fitness(score=66.6, objective=objective)
        fitness_3 = Fitness(score=66.7, objective=objective)

        self.assertGreater(fitness_1.score, fitness_2.score)
        self.assertGreaterEqual(fitness_1, fitness_2)

        self.assertEqual(fitness_1.score, fitness_3.score)
        self.assertGreaterEqual(fitness_1, fitness_3)

    def test_fitness_lt(self):
        """Test that fitness_1 with score_1 < score_2 is less than fitness_2
        with score_2.

        """
        def eval_func(solution): return 0.0  # only used for constructing objective

        objective = Objective(eval_func=eval_func, weight=42.0)

        fitness_1 = Fitness(score=66.6, objective=objective)
        fitness_2 = Fitness(score=66.7, objective=objective)

        self.assertLess(fitness_1, fitness_2)

    def test_fitness_le(self):
        """Test that fitness_1 with score_1 <= score_2 is less than or equal to
        fitness_2 with score_2 and that fitness_1 is greater than or equal to
        fitness_3 with score_3 == score_1.

        """
        def eval_func(solution): return 0.0  # only used for constructing objective

        objective = Objective(eval_func=eval_func, weight=42.0)

        fitness_1 = Fitness(score=66.6, objective=objective)
        fitness_2 = Fitness(score=66.7, objective=objective)
        fitness_3 = Fitness(score=66.6, objective=objective)

        self.assertLess(fitness_1.score, fitness_2.score)
        self.assertLessEqual(fitness_1, fitness_2)

        self.assertEqual(fitness_1.score, fitness_3.score)
        self.assertLessEqual(fitness_1, fitness_3)


class TestSolution(unittest.TestCase):

    def test_solution_attributes(self):
        """Test that a Solution's *tree*, *objectives*, and *map* attributes
        refer to the data passed into the constructor.

        """
        int_type = Type(name='int')

        def eval_func(solution): return 66.6

        objective = Objective(eval_func=eval_func, weight=42.0)

        terminal_operator = Operator(
            symbol=Symbol(name='term', dtype=int_type)
        )

        root = Node(operator=terminal_operator)

        tree = Tree(root=root)

        solution = Solution(tree=tree, objectives=(objective,))

        self.assertIs(solution.tree, tree)
        self.assertTupleEqual(solution.objectives, (objective,))
        self.assertIs(solution.map, map)

    def test_solution_evaluate_result(self):
        """Test that a Solution's *evaluate* method returns a tuple of Fitness
        objects with the correct fitness scores, having the same structure as
        the *objectives* parameter passed into the Solution's constructor.

        """
        int_type = Type(name='int')

        self.maxDiff = None

        def eval_func_1(solution):
            log.debug('Calling eval_func_1')
            time.sleep(0.01)  # eval_func_1 hopefully evaluated second
            return 66.6

        def eval_func_2(solution):
            log.debug('Calling eval_func_2')
            return 66.7

        objective_1 = Objective(eval_func=eval_func_1, weight=42.0)
        objective_2 = Objective(eval_func=eval_func_2, weight=42.0)

        terminal_operator = Operator(
            symbol=Symbol(name='term', dtype=int_type)
        )

        root = Node(operator=terminal_operator)

        tree = Tree(root=root)

        for _ in xrange(50):
            solution = Solution(
                tree=tree,
                objectives=(objective_1, objective_2),
                map_=futures_map
            )
            self.assertTupleEqual(
                solution.evaluate(),
                (
                    objective_1.evaluate(solution),
                    objective_2.evaluate(solution)
                )
            )

    def test_solution_evaluate_result_caching(self):
        """Test that a Solution's *evaluate* method caches results in a
        thread-safe manner.

        """
        int_type = Type(name='int')

        eval_func = mock.Mock(return_value=66.6)

        objective = Objective(eval_func=eval_func, weight=42.0)

        terminal_operator = Operator(
            symbol=Symbol(name='term', dtype=int_type)
        )

        root = Node(operator=terminal_operator)

        tree = Tree(root=root)

        solution = Solution(
            tree=tree,
            objectives=(objective,),
            map_=futures_map
        )

        results = [
            POOL.submit(lambda s: s.evaluate(), solution)
            for _ in xrange(100)
        ]

        previous_result = None
        for idx, res in enumerate(results):
            result = res.result()
            if idx > 0:
                self.assertEqual(result, previous_result)
            previous_result = result

        eval_func.assert_called_once_with(solution)

    def test_solution_dominates(self):
        """Test that a Solution's *dominates* method returns True if the
        solution Pareto-dominates another solution, and False otherwise.

        """
        int_type = Type(name='int')

        eval_func_1 = mock.Mock(side_effect=[66.7, 66.6, 66.6])
        eval_func_2 = mock.Mock(side_effect=[66.6, 66.6, 66.6])
        eval_func_3 = mock.Mock(side_effect=[66.6, 66.6, 66.6])

        objective_1 = Objective(eval_func=eval_func_1, weight=42.0)
        objective_2 = Objective(eval_func=eval_func_2, weight=42.0)
        objective_3 = Objective(eval_func=eval_func_3, weight=42.0)

        terminal_operator = Operator(
            symbol=Symbol(name='term', dtype=int_type)
        )

        root = Node(operator=terminal_operator)

        tree = Tree(root=root)

        solution_1 = Solution(
            tree=tree, objectives=(objective_1, objective_2, objective_3)
        )

        solution_2 = Solution(
            tree=tree, objectives=(objective_1, objective_2, objective_3)
        )

        solution_3 = Solution(
            tree=tree, objectives=(objective_1, objective_3, objective_2)
        )

        solution_1.evaluate()
        solution_2.evaluate()
        solution_3.evaluate()

        self.assertTrue(solution_1.dominates(solution_2))
        self.assertFalse(solution_2.dominates(solution_1))
        self.assertRaises(
            TypeError, solution_1.dominates, solution_3
        )

        eval_func_1.assert_has_calls(
            calls=(mock.call(solution_1), mock.call(solution_2))
        )
        self.assertEqual(eval_func_1.call_count, 3)

        eval_func_2.assert_has_calls(
            calls=(mock.call(solution_1), mock.call(solution_2))
        )
        self.assertEqual(eval_func_2.call_count, 3)

        eval_func_3.assert_has_calls(
            calls=(mock.call(solution_1), mock.call(solution_2))
        )
        self.assertEqual(eval_func_3.call_count, 3)

    def test_solution_hash(self):
        """Test that two identically-distinct Solution instances which refer to
        equivalent trees and equivalent objectives have the same hash value.

        """
        int_type = Type(name='int')

        eval_func = mock.Mock(return_value=66.6)

        objective = Objective(eval_func=eval_func, weight=42.0)

        terminal_operator = Operator(
            symbol=Symbol(name='term', dtype=int_type)
        )

        root_1 = Node(operator=terminal_operator)
        root_2 = Node(operator=terminal_operator)

        tree_1 = Tree(root=root_1)
        tree_2 = Tree(root=root_2)

        solution_1 = Solution(
            tree=tree_1,
            objectives=(objective,),
            map_=futures_map
        )
        solution_2 = Solution(
            tree=tree_2,
            objectives=(objective,),
            map_=futures_map
        )

        for _ in xrange(100):
            self.assertEqual(hash(solution_1), hash(solution_2))

        eval_func.assert_has_calls(
                calls=(mock.call(solution_1), mock.call(solution_2))
        )

        self.assertEqual(eval_func.call_count, 2)

    def test_solution_len(self):
        """Test that a solution

        """
        int_type = Type(name='int')

        eval_func = mock.Mock(return_value=66.6)

        objective = Objective(eval_func=eval_func, weight=42.0)

        basis_operator = Operator(
            symbol=Symbol(name='basis', dtype=int_type), signature=(int_type,)
        )
        terminal_operator = Operator(
            symbol=Symbol(name='term', dtype=int_type)
        )

        root_1 = Node(operator=basis_operator)
        root_2 = Node(operator=basis_operator)

        node_1 = Node(operator=terminal_operator)
        node_2 = Node(operator=terminal_operator)

        root_1.add_child(child=node_1, position=0)
        root_2.add_child(child=node_2, position=0)

        tree_1 = Tree(root=root_1)
        tree_2 = Tree(root=root_2)

        solution_1 = Solution(
            tree=tree_1,
            objectives=(objective,),
            map_=futures_map
        )
        solution_2 = Solution(
            tree=tree_2,
            objectives=(objective,),
            map_=futures_map
        )

        for _ in xrange(100):
            self.assertEqual(2, len(solution_1))
            self.assertEqual(len(solution_1), len(solution_2))

        eval_func.assert_not_called()

    def test_solution_equals(self):
        """Test that two identically distinct Solutions are equal if their
        hashes are equal.

        """
        int_type = Type(name='int')

        eval_func = mock.Mock(return_value=66.6)

        objective = Objective(eval_func=eval_func, weight=42.0)

        terminal_operator = Operator(
            symbol=Symbol(name='term', dtype=int_type)
        )

        root_1 = Node(operator=terminal_operator)
        root_2 = Node(operator=terminal_operator)

        tree_1 = Tree(root=root_1)
        tree_2 = Tree(root=root_2)

        solution_1 = Solution(
            tree=tree_1,
            objectives=(objective,),
            map_=futures_map
        )
        solution_2 = Solution(
            tree=tree_2,
            objectives=(objective,),
            map_=futures_map
        )

        for _ in xrange(100):
            self.assertEqual(solution_1, solution_2)
            self.assertEqual(solution_2, solution_1)

        eval_func.assert_has_calls(
                calls=(mock.call(solution_1), mock.call(solution_2))
        )

        self.assertEqual(eval_func.call_count, 2)

    def test_solution_not_equals(self):
        """Test that two solutions are not equal if their hashes are not equal.

        """
        int_type = Type(name='int')

        eval_func = mock.Mock(side_effect=[66.6, 66.7])

        objective = Objective(eval_func=eval_func, weight=42.0)

        terminal_operator = Operator(
            symbol=Symbol(name='term', dtype=int_type)
        )

        root_1 = Node(operator=terminal_operator)
        root_2 = Node(operator=terminal_operator)

        tree_1 = Tree(root=root_1)
        tree_2 = Tree(root=root_2)

        solution_1 = Solution(
            tree=tree_1,
            objectives=(objective,),
            map_=futures_map
        )
        solution_2 = Solution(
            tree=tree_2,
            objectives=(objective,),
            map_=futures_map
        )

        for _ in xrange(100):
            self.assertNotEqual(solution_1, solution_2)
            self.assertNotEqual(solution_2, solution_1)

        eval_func.assert_has_calls(
            calls=(mock.call(solution_1), mock.call(solution_2))
        )

        self.assertEqual(eval_func.call_count, 2)

    def test_solution_gt(self):
        """Test that a Solution which dominates another solution and has equal
        objectives is greater than the other solution.

        """
        int_type = Type(name='int')

        eval_func_1 = mock.Mock(side_effect=[66.7, 66.6, 66.6])
        eval_func_2 = mock.Mock(side_effect=[66.6, 66.6, 66.6])

        objective_1 = Objective(eval_func=eval_func_1, weight=42.0)
        objective_2 = Objective(eval_func=eval_func_2, weight=42.0)

        terminal_operator_1 = Operator(
            symbol=Symbol(name='term1', dtype=int_type)
        )
        terminal_operator_2 = Operator(
            symbol=Symbol(name='term2', dtype=int_type)
        )

        root_1 = Node(operator=terminal_operator_1)
        root_2 = Node(operator=terminal_operator_2)

        tree_1 = Tree(root=root_1)
        tree_2 = Tree(root=root_2)

        solution_1 = Solution(
            tree=tree_1,
            objectives=(objective_1, objective_2)
        )
        solution_2 = Solution(
            tree=tree_2,
            objectives=(objective_1, objective_2)
        )
        solution_3 = Solution(
            tree=tree_2,
            objectives=(objective_2, objective_1)
        )

        solution_1.evaluate()
        solution_2.evaluate()
        solution_3.evaluate()

        for _ in xrange(100):
            self.assertGreater(solution_1, solution_2)
            self.assertFalse(solution_2 > solution_1)
            self.assertRaises(
                TypeError,
                lambda s1, s2: s1 > s2,
                solution_1,
                solution_3
            )

        eval_func_1.assert_has_calls(
            calls=(
                mock.call(solution_1),
                mock.call(solution_2),
                mock.call(solution_3)
            )
        )
        self.assertEqual(eval_func_1.call_count, 3)

        eval_func_2.assert_has_calls(
            calls=(
                mock.call(solution_1),
                mock.call(solution_2),
                mock.call(solution_3)
            )
        )
        self.assertEqual(eval_func_2.call_count, 3)

    def test_solution_lt(self):
        """Test that a solution which is dominated by another solution and has
        equal objectives is less than the other solution.

        """
        int_type = Type(name='int')

        eval_func_1 = mock.Mock(side_effect=[66.6, 66.7, 66.7])
        eval_func_2 = mock.Mock(side_effect=[66.6, 66.6, 66.6])

        objective_1 = Objective(eval_func=eval_func_1, weight=42.0)
        objective_2 = Objective(eval_func=eval_func_2, weight=42.0)

        terminal_operator_1 = Operator(
            symbol=Symbol(name='term1', dtype=int_type)
        )
        terminal_operator_2 = Operator(
            symbol=Symbol(name='term2', dtype=int_type)
        )

        root_1 = Node(operator=terminal_operator_1)
        root_2 = Node(operator=terminal_operator_2)

        tree_1 = Tree(root=root_1)
        tree_2 = Tree(root=root_2)

        solution_1 = Solution(
            tree=tree_1,
            objectives=(objective_1, objective_2)
        )
        solution_2 = Solution(
            tree=tree_2,
            objectives=(objective_1, objective_2)
        )
        solution_3 = Solution(
            tree=tree_2,
            objectives=(objective_2, objective_1)
        )

        solution_1.evaluate()
        solution_2.evaluate()
        solution_3.evaluate()

        for _ in xrange(100):
            self.assertLess(solution_1, solution_2)
            self.assertFalse(solution_2 < solution_1)
            self.assertRaises(
                TypeError,
                lambda s1, s2: s1 < s2,
                solution_1,
                solution_3
            )

        eval_func_1.assert_has_calls(
            calls=(
                mock.call(solution_1),
                mock.call(solution_2),
                mock.call(solution_3)
            )
        )
        self.assertEqual(eval_func_1.call_count, 3)

        eval_func_2.assert_has_calls(
            calls=(
                mock.call(solution_1),
                mock.call(solution_2),
                mock.call(solution_3)
            )
        )
        self.assertEqual(eval_func_2.call_count, 3)

    def test_solutions_sorted(self):
        """Test that a collection of solution instances behave nicely under the
        built-in *sorted* function.

        """
        int_type = Type(name='int')

        self.maxDiff = None

        eval_func_1 = mock.Mock(side_effect=[66.6, 66.7, 66.7, 66.8])
        eval_func_2 = mock.Mock(side_effect=[66.6, 66.6, 66.6, 66.6])

        objective_1 = Objective(eval_func=eval_func_1, weight=42.0)
        objective_2 = Objective(eval_func=eval_func_2, weight=42.0)

        terminal_operator = Operator(
            symbol=Symbol(name='term', dtype=int_type)
        )

        root = Node(operator=terminal_operator)

        tree = Tree(root=root)

        solution_1 = Solution(
            tree=tree,
            objectives=(objective_1, objective_2)
        )
        solution_2 = Solution(
            tree=tree,
            objectives=(objective_1, objective_2)
        )
        solution_3 = Solution(
            tree=tree,
            objectives=(objective_1, objective_2)
        )
        solution_4 = Solution(
            tree=tree,
            objectives=(objective_1, objective_2)
        )

        solution_1.evaluate()
        solution_2.evaluate()
        solution_3.evaluate()
        solution_4.evaluate()

        # NOTE: if expected == [solution_1, solution_3, solution_2, solution_4]
        #       output matching this expected would also be correct. This test
        #       may break if (what appears to be) that implementation detail of
        #       sorted which doesn't re-arrange elements which don't dominate
        #       changes, or is implemented differently on other platforms, etc.
        expected = [solution_1, solution_2, solution_3, solution_4]
        candidate = sorted([solution_2, solution_1, solution_4, solution_3])

        for idx, solution in enumerate(candidate):
            log.info('checking solution %d', idx)
            self.assertIs(solution, expected[idx])
            log.info('verified solution %d', idx)

        eval_func_1.assert_has_calls(
            calls=(
                mock.call(solution_1),
                mock.call(solution_2),
                mock.call(solution_3),
                mock.call(solution_4)
            )
        )
        self.assertEqual(eval_func_1.call_count, 4)

        eval_func_2.assert_has_calls(
            calls=(
                mock.call(solution_1),
                mock.call(solution_2),
                mock.call(solution_3),
                mock.call(solution_4)
            )
        )
        self.assertEqual(eval_func_2.call_count, 4)
