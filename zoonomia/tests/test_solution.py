import unittest
import time
import logging
import pickle

from unittest import mock
from concurrent.futures import ThreadPoolExecutor
from zoonomia.tree import Node, Tree
from zoonomia.solution import Objective, Fitness, Solution
from zoonomia.types import Type
from zoonomia.lang import Symbol, Call, Operator, OperatorTable

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


def eval_func(s):
    LOG.info('Evaluating solution:\t{0}'.format(repr(s)))
    return 66.6


class TestObjective(unittest.TestCase):

    def test_equals_reflexive(self):
        """Test that an object equals itself."""
        weight = 42.0

        objective_1 = Objective(eval_func=eval_func, weight=weight)
        objective_2 = objective_1

        self.assertIs(objective_1, objective_2)
        self.assertEqual(objective_1, objective_2)

    def test_equals_symmetric(self):
        """Test that for objects :math:`\{x,y\}, x = y \iff y = x`."""
        weight = 42.0
        another_weight = 66.6

        objective_1 = Objective(eval_func=eval_func, weight=weight)
        objective_2 = Objective(eval_func=eval_func, weight=weight)
        another_objective = Objective(
            eval_func=eval_func, weight=another_weight
        )

        self.assertFalse(objective_1 is objective_2)

        self.assertEqual(objective_1, objective_2)
        self.assertEqual(objective_2, objective_1)

        self.assertFalse(objective_1 is another_objective)

        self.assertNotEqual(objective_1, another_objective)
        self.assertNotEqual(another_objective, objective_1)

    def test_equals_transitive(self):
        """Test that for objects :math:`\{x,y,z\}, x = y, y = z \iff x = z`."""
        weight = 42.0

        objective_1 = Objective(eval_func=eval_func, weight=weight)
        objective_2 = Objective(eval_func=eval_func, weight=weight)
        objective_3 = Objective(eval_func=eval_func, weight=weight)

        self.assertFalse(objective_1 is objective_2)
        self.assertFalse(objective_2 is objective_3)
        self.assertFalse(objective_1 is objective_3)

        self.assertEqual(objective_1, objective_2)
        self.assertEqual(objective_2, objective_3)
        self.assertEqual(objective_1, objective_3)

    def test_equals_consistent(self):
        """Test that repeated equals calls return the same value."""
        weight = 42.0
        another_weight = 66.6

        objective_1 = Objective(eval_func=eval_func, weight=weight)
        objective_2 = Objective(eval_func=eval_func, weight=weight)
        another_objective = Objective(
            eval_func=eval_func, weight=another_weight
        )

        self.assertFalse(objective_1 is objective_2)

        self.assertEqual(objective_1, objective_2)
        self.assertEqual(objective_1, objective_2)
        self.assertEqual(objective_1, objective_2)

        self.assertFalse(objective_1 is another_objective)

        self.assertNotEqual(objective_1, another_objective)
        self.assertNotEqual(objective_1, another_objective)
        self.assertNotEqual(objective_1, another_objective)

    def test_hash_consistent(self):
        """Test that repeated hash calls yield the same value."""
        weight = 42.0

        objective_1 = Objective(eval_func=eval_func, weight=weight)
        hash_1 = hash(objective_1)

        self.assertEqual(hash_1, hash(objective_1))
        self.assertEqual(hash_1, hash(objective_1))
        self.assertEqual(hash_1, hash(objective_1))

    def test_hash_equals(self):
        """Test that when two objects are equal their hashes are equal."""
        weight = 42.0

        objective_1 = Objective(eval_func=eval_func, weight=weight)
        objective_2 = Objective(eval_func=eval_func, weight=weight)

        self.assertEqual(hash(objective_1), hash(objective_2))
        self.assertEqual(objective_1, objective_2)

    def test_objective_pickle(self):
        """Test that an Objective instance can be pickled and unpickled using
        the 0 protocol and the -1 protocol.

        """
        weight = 42.0
        objective = Objective(eval_func=eval_func, weight=weight)

        pickled_objective = pickle.dumps(objective, -1)
        unpickled_objective = pickle.loads(pickled_objective)

        self.assertEqual(objective, unpickled_objective)
        self.assertEqual(hash(objective), hash(unpickled_objective))

        pickled_objective = pickle.dumps(objective, 0)
        unpickled_objective = pickle.loads(pickled_objective)

        self.assertEqual(objective, unpickled_objective)
        self.assertEqual(hash(objective), hash(unpickled_objective))

    def test_objective_evaluate(self):
        """Test that calling an Objective's *evaluate* method produces a
        Fitness object whose *score* attribute is equal to the *weight*
        parameter multiplied by the result of calling the *eval_func*.

        """
        int_type = Type(name='int')

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
        score = 66.6
        weight = 42.0

        objective = Objective(eval_func=eval_func, weight=weight)

        fitness = Fitness(score=score, objective=objective)

        self.assertIs(fitness.score, score)
        self.assertIs(fitness.objective, objective)

    def test_equals_reflexive(self):
        """Test that an object equals itself."""
        score = 66.6
        weight = 42.0

        objective = Objective(eval_func=eval_func, weight=weight)

        fitness_1 = Fitness(score=score, objective=objective)
        fitness_2 = fitness_1

        self.assertIs(fitness_1, fitness_2)
        self.assertEqual(fitness_1, fitness_2)

    def test_equals_symmetric(self):
        """Test that for objects :math:`\{x,y\}, x = y \iff y = x`."""
        score = 66.6
        weight = 42.0
        another_weight = 66.6

        objective_1 = Objective(eval_func=eval_func, weight=weight)
        another_objective = Objective(
            eval_func=eval_func, weight=another_weight
        )

        fitness_1 = Fitness(score=score, objective=objective_1)
        fitness_2 = Fitness(score=score, objective=objective_1)
        another_fitness = Fitness(score=score, objective=another_objective)

        self.assertFalse(fitness_1 is fitness_2)

        self.assertEqual(fitness_1, fitness_2)
        self.assertEqual(fitness_2, fitness_1)

        self.assertFalse(fitness_1 is another_fitness)

        self.assertNotEqual(fitness_1, another_fitness)
        self.assertNotEqual(another_fitness, fitness_1)

    def test_equals_transitive(self):
        """Test that for objects :math:`\{x,y,z\}, x = y, y = z \iff x = z`."""
        score = 66.6
        weight = 42.0

        objective_1 = Objective(eval_func=eval_func, weight=weight)

        fitness_1 = Fitness(score=score, objective=objective_1)
        fitness_2 = Fitness(score=score, objective=objective_1)
        fitness_3 = Fitness(score=score, objective=objective_1)

        self.assertFalse(fitness_1 is fitness_2)
        self.assertFalse(fitness_2 is fitness_3)
        self.assertFalse(fitness_1 is fitness_3)

        self.assertEqual(fitness_1, fitness_2)
        self.assertEqual(fitness_2, fitness_3)
        self.assertEqual(fitness_1, fitness_3)

    def test_equals_consistent(self):
        """Test that repeated equals calls return the same value."""
        score = 66.6
        weight = 42.0
        another_weight = 66.6

        objective_1 = Objective(eval_func=eval_func, weight=weight)
        another_objective = Objective(
            eval_func=eval_func, weight=another_weight
        )

        fitness_1 = Fitness(score=score, objective=objective_1)
        fitness_2 = Fitness(score=score, objective=objective_1)
        another_fitness = Fitness(score=score, objective=another_objective)

        self.assertFalse(fitness_1 is fitness_2)

        self.assertEqual(fitness_1, fitness_2)
        self.assertEqual(fitness_1, fitness_2)
        self.assertEqual(fitness_1, fitness_2)

        self.assertFalse(fitness_1 is another_fitness)

        self.assertNotEqual(fitness_1, another_fitness)
        self.assertNotEqual(fitness_1, another_fitness)
        self.assertNotEqual(fitness_1, another_fitness)

    def test_hash_consistent(self):
        """Test that repeated hash calls yield the same value."""
        score = 66.6
        weight = 42.0

        objective_1 = Objective(eval_func=eval_func, weight=weight)

        fitness_1 = Fitness(score=score, objective=objective_1)
        hash_1 = hash(fitness_1)

        self.assertEqual(hash_1, hash(fitness_1))
        self.assertEqual(hash_1, hash(fitness_1))
        self.assertEqual(hash_1, hash(fitness_1))

    def test_hash_equals(self):
        """Test that when two objects are equal their hashes are equal."""
        score = 66.6
        weight = 42.0

        objective_1 = Objective(eval_func=eval_func, weight=weight)

        fitness_1 = Fitness(score=score, objective=objective_1)
        fitness_2 = Fitness(score=score, objective=objective_1)

        self.assertFalse(fitness_1 is fitness_2)

        self.assertEqual(hash(fitness_1), hash(fitness_2))
        self.assertEqual(fitness_1, fitness_2)

    def test_fitness_pickle(self):
        """Test that a Fitness instance can be pickled and unpickled using the
        0 protocol and the -1 protocol.

        """
        weight = 42.0
        objective = Objective(eval_func=eval_func, weight=weight)
        fitness = Fitness(score=66.6, objective=objective)

        pickled_fitness = pickle.dumps(fitness, -1)
        unpickled_fitness = pickle.loads(pickled_fitness)

        self.assertEqual(fitness, unpickled_fitness)
        self.assertEqual(hash(fitness), hash(unpickled_fitness))

        pickled_fitness = pickle.dumps(fitness, 0)
        unpickled_fitness = pickle.loads(pickled_fitness)

        self.assertEqual(fitness, unpickled_fitness)
        self.assertEqual(hash(fitness), hash(unpickled_fitness))

    def test_fitness_gt(self):
        """Test that fitness_1 with score_1 > score_2 is greater than fitness_2
        with score_2.

        """
        objective = Objective(eval_func=eval_func, weight=42.0)

        fitness_1 = Fitness(score=66.7, objective=objective)
        fitness_2 = Fitness(score=66.6, objective=objective)

        self.assertGreater(fitness_1, fitness_2)

    def test_fitness_ge(self):
        """Test that fitness_1 with score_1 > score_2 is greater than or equal
        to fitness_2 with score_2 and that fitness_1 is greater than or equal
        to fitness_3 with score_3 == score_1.

        """
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
        objective = Objective(eval_func=eval_func, weight=42.0)

        fitness_1 = Fitness(score=66.6, objective=objective)
        fitness_2 = Fitness(score=66.7, objective=objective)

        self.assertLess(fitness_1, fitness_2)

    def test_fitness_le(self):
        """Test that fitness_1 with score_1 <= score_2 is less than or equal to
        fitness_2 with score_2 and that fitness_1 is greater than or equal to
        fitness_3 with score_3 == score_1.

        """
        objective = Objective(eval_func=eval_func, weight=42.0)

        fitness_1 = Fitness(score=66.6, objective=objective)
        fitness_2 = Fitness(score=66.7, objective=objective)
        fitness_3 = Fitness(score=66.6, objective=objective)

        self.assertLess(fitness_1.score, fitness_2.score)
        self.assertLessEqual(fitness_1, fitness_2)

        self.assertEqual(fitness_1.score, fitness_3.score)
        self.assertLessEqual(fitness_1, fitness_3)


class TestSolution(unittest.TestCase):

    def setUp(self):
        self.pool = ThreadPoolExecutor(max_workers=100)

    def tearDown(self):
        self.pool.shutdown()

    def futures_map(self, fn, iterable):
        return self.pool.map(fn, iterable)

    def test_equals_reflexive(self):
        """Test that an object equals itself."""
        int_type = Type(name='int')

        mock_eval_func = mock.Mock(return_value=66.6)

        objective = Objective(eval_func=mock_eval_func, weight=42.0)

        terminal_operator = Operator(
            symbol=Symbol(name='term', dtype=int_type)
        )

        root_1 = Node(operator=terminal_operator)

        tree_1 = Tree(root=root_1)

        solution_1 = Solution(
            tree=tree_1,
            objectives=(objective,),
            map_=self.futures_map
        )
        solution_2 = solution_1

        self.assertIs(solution_1, solution_2)
        self.assertEqual(solution_1, solution_2)

        mock_eval_func.assert_called_once_with(solution_1)

    def test_equals_symmetric(self):
        """Test that for objects :math:`\{x,y\}, x = y \iff y = x`."""
        int_type = Type(name='int')

        mock_eval_func = mock.Mock(return_value=66.6)

        objective = Objective(eval_func=mock_eval_func, weight=42.0)

        terminal_operator = Operator(
            symbol=Symbol(name='term', dtype=int_type)
        )
        another_terminal_operator = Operator(
            symbol=Symbol(name='another_term', dtype=int_type)
        )

        root_1 = Node(operator=terminal_operator)
        root_2 = Node(operator=terminal_operator)
        another_root = Node(operator=another_terminal_operator)

        tree_1 = Tree(root=root_1)
        tree_2 = Tree(root=root_2)
        another_tree = Tree(root=another_root)

        solution_1 = Solution(
            tree=tree_1,
            objectives=(objective,),
            map_=self.futures_map
        )
        solution_2 = Solution(
            tree=tree_2,
            objectives=(objective,),
            map_=self.futures_map
        )
        another_solution = Solution(
            tree=another_tree,
            objectives=(objective,),
            map_=self.futures_map
        )

        self.assertFalse(solution_1 is solution_2)

        self.assertEqual(solution_1, solution_2)
        self.assertEqual(solution_2, solution_1)

        self.assertFalse(solution_1 is another_solution)

        self.assertNotEqual(solution_1, another_solution)
        self.assertNotEqual(another_solution, solution_1)

        mock_eval_func.assert_has_calls(
                calls=(
                    mock.call(solution_1),
                    mock.call(solution_2),
                    mock.call(another_solution)
                )
        )

        self.assertEqual(mock_eval_func.call_count, 3)

    def test_equals_transitive(self):
        """Test that for objects :math:`\{x,y,z\}, x = y, y = z \iff x = z`."""
        int_type = Type(name='int')

        mock_eval_func = mock.Mock(return_value=66.6)

        objective = Objective(eval_func=mock_eval_func, weight=42.0)

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
            map_=self.futures_map
        )
        solution_2 = Solution(
            tree=tree_2,
            objectives=(objective,),
            map_=self.futures_map
        )
        solution_3 = Solution(
            tree=tree_2,
            objectives=(objective,),
            map_=self.futures_map
        )

        self.assertFalse(solution_1 is solution_2)
        self.assertFalse(solution_2 is solution_3)
        self.assertFalse(solution_1 is solution_3)

        self.assertEqual(solution_1, solution_2)
        self.assertEqual(solution_2, solution_3)
        self.assertEqual(solution_1, solution_3)

        mock_eval_func.assert_has_calls(
            calls=(
                mock.call(solution_1),
                mock.call(solution_2),
                mock.call(solution_3)
            )
        )

        self.assertEqual(mock_eval_func.call_count, 3)

    def test_equals_consistent(self):
        """Test that repeated equals calls return the same value."""
        int_type = Type(name='int')

        mock_eval_func = mock.Mock(return_value=66.6)

        objective = Objective(eval_func=mock_eval_func, weight=42.0)

        terminal_operator = Operator(
            symbol=Symbol(name='term', dtype=int_type)
        )
        another_terminal_operator = Operator(
            symbol=Symbol(name='another_term', dtype=int_type)
        )

        root_1 = Node(operator=terminal_operator)
        root_2 = Node(operator=terminal_operator)
        another_root = Node(operator=another_terminal_operator)

        tree_1 = Tree(root=root_1)
        tree_2 = Tree(root=root_2)
        another_tree = Tree(root=another_root)

        solution_1 = Solution(
            tree=tree_1,
            objectives=(objective,),
            map_=self.futures_map
        )
        solution_2 = Solution(
            tree=tree_2,
            objectives=(objective,),
            map_=self.futures_map
        )
        another_solution = Solution(
            tree=another_tree,
            objectives=(objective,),
            map_=self.futures_map
        )

        self.assertFalse(solution_1 is solution_2)
        self.assertFalse(solution_1 is another_solution)

        for _ in range(100):
            self.assertEqual(solution_1, solution_2)
            self.assertNotEqual(solution_1, another_solution)

        mock_eval_func.assert_has_calls(
                calls=(
                    mock.call(solution_1),
                    mock.call(solution_2),
                    mock.call(another_solution)
                )
        )

        self.assertEqual(mock_eval_func.call_count, 3)

    def test_hash_consistent(self):
        """Test that repeated hash calls yield the same value."""
        int_type = Type(name='int')

        mock_eval_func = mock.Mock(return_value=66.6)

        objective = Objective(eval_func=mock_eval_func, weight=42.0)

        terminal_operator = Operator(
            symbol=Symbol(name='term', dtype=int_type)
        )

        root_1 = Node(operator=terminal_operator)

        tree_1 = Tree(root=root_1)

        solution_1 = Solution(
            tree=tree_1,
            objectives=(objective,),
            map_=self.futures_map
        )
        hash_1 = hash(solution_1)

        for _ in range(100):
            self.assertEqual(hash_1, hash(solution_1))

        mock_eval_func.assert_called_once_with(solution_1)

    def test_hash_equals(self):
        """Test that when two objects are equal their hashes are equal."""
        int_type = Type(name='int')

        mock_eval_func = mock.Mock(return_value=66.6)

        objective = Objective(eval_func=mock_eval_func, weight=42.0)

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
            map_=self.futures_map
        )
        solution_2 = Solution(
            tree=tree_2,
            objectives=(objective,),
            map_=self.futures_map
        )

        self.assertEqual(hash(solution_1), hash(solution_2))
        self.assertEqual(solution_1, solution_2)

        mock_eval_func.assert_has_calls(
                calls=(
                    mock.call(solution_1),
                    mock.call(solution_2)
                )
        )

        self.assertEqual(mock_eval_func.call_count, 2)

    def test_solution_attributes(self):
        """Test that a Solution's *tree*, *objectives*, and *map* attributes
        refer to the data passed into the constructor.

        """
        int_type = Type(name='int')

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
            LOG.debug('Calling eval_func_1')
            time.sleep(0.01)  # eval_func_1 hopefully evaluated second
            return 66.6

        def eval_func_2(solution):
            LOG.debug('Calling eval_func_2')
            return 66.7

        objective_1 = Objective(eval_func=eval_func_1, weight=42.0)
        objective_2 = Objective(eval_func=eval_func_2, weight=42.0)

        terminal_operator = Operator(
            symbol=Symbol(name='term', dtype=int_type)
        )

        root = Node(operator=terminal_operator)

        tree = Tree(root=root)

        for _ in range(50):
            solution = Solution(
                tree=tree,
                objectives=(objective_1, objective_2),
                map_=self.futures_map
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

        mock_eval_func = mock.Mock(return_value=66.6)

        objective = Objective(eval_func=mock_eval_func, weight=42.0)

        terminal_operator = Operator(
            symbol=Symbol(name='term', dtype=int_type)
        )

        root = Node(operator=terminal_operator)

        tree = Tree(root=root)

        solution = Solution(
            tree=tree,
            objectives=(objective,),
            map_=self.futures_map
        )

        results = [
            self.pool.submit(lambda s: s.evaluate(), solution)
            for _ in range(100)
        ]

        previous_result = None
        for idx, res in enumerate(results):
            result = res.result()
            if idx > 0:
                self.assertEqual(result, previous_result)
            previous_result = result

        mock_eval_func.assert_called_once_with(solution)

    def test_solution_dominates(self):
        """Test that a Solution's *dominates* method returns True if the
        solution Pareto-dominates another solution, and False otherwise.

        """
        int_type = Type(name='int')

        mock_eval_func_1 = mock.Mock(side_effect=[66.7, 66.6, 66.6])
        mock_eval_func_2 = mock.Mock(side_effect=[66.6, 66.6, 66.6])
        mock_eval_func_3 = mock.Mock(side_effect=[66.6, 66.6, 66.6])

        objective_1 = Objective(eval_func=mock_eval_func_1, weight=42.0)
        objective_2 = Objective(eval_func=mock_eval_func_2, weight=42.0)
        objective_3 = Objective(eval_func=mock_eval_func_3, weight=42.0)

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

        mock_eval_func_1.assert_has_calls(
            calls=(mock.call(solution_1), mock.call(solution_2))
        )
        self.assertEqual(mock_eval_func_1.call_count, 3)

        mock_eval_func_2.assert_has_calls(
            calls=(mock.call(solution_1), mock.call(solution_2))
        )
        self.assertEqual(mock_eval_func_2.call_count, 3)

        mock_eval_func_3.assert_has_calls(
            calls=(mock.call(solution_1), mock.call(solution_2))
        )
        self.assertEqual(mock_eval_func_3.call_count, 3)

    def test_solution_len(self):
        """Test that a solution

        """
        int_type = Type(name='int')

        mock_eval_func = mock.Mock(return_value=66.6)

        objective = Objective(eval_func=mock_eval_func, weight=42.0)

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
            map_=self.futures_map
        )
        solution_2 = Solution(
            tree=tree_2,
            objectives=(objective,),
            map_=self.futures_map
        )

        for _ in range(100):
            self.assertEqual(2, len(solution_1))
            self.assertEqual(len(solution_1), len(solution_2))

        mock_eval_func.assert_not_called()

    def test_solution_pickle(self):
        """Test that a Solution instance can be pickled and unpickled using the
        0 protocol and the -1 protocol.

        """
        int_type = Type(name='int')

        objective = Objective(eval_func=eval_func, weight=42.0)

        terminal_operator = Operator(
            symbol=Symbol(name='term', dtype=int_type)
        )

        root = Node(operator=terminal_operator)
        tree = Tree(root=root)

        solution = Solution(
            tree=tree,
            objectives=(objective,),
            map_=map
        )

        pickled_solution = pickle.dumps(solution, -1)
        unpickled_solution = pickle.loads(pickled_solution)

        self.assertEqual(solution, unpickled_solution)
        self.assertEqual(hash(solution), hash(unpickled_solution))

        pickled_solution = pickle.dumps(solution, 0)
        unpickled_solution = pickle.loads(pickled_solution)

        self.assertEqual(solution, unpickled_solution)
        self.assertEqual(hash(solution), hash(unpickled_solution))

    def test_solution_gt(self):
        """Test that a Solution which dominates another solution and has equal
        objectives is greater than the other solution.

        """
        int_type = Type(name='int')

        mock_eval_func_1 = mock.Mock(side_effect=[66.7, 66.6, 66.6])
        mock_eval_func_2 = mock.Mock(side_effect=[66.6, 66.6, 66.6])

        objective_1 = Objective(eval_func=mock_eval_func_1, weight=42.0)
        objective_2 = Objective(eval_func=mock_eval_func_2, weight=42.0)

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

        for _ in range(100):
            self.assertGreater(solution_1, solution_2)
            self.assertFalse(solution_2 > solution_1)
            self.assertRaises(
                TypeError,
                lambda s1, s2: s1 > s2,
                solution_1,
                solution_3
            )

        mock_eval_func_1.assert_has_calls(
            calls=(
                mock.call(solution_1),
                mock.call(solution_2),
                mock.call(solution_3)
            )
        )
        self.assertEqual(mock_eval_func_1.call_count, 3)

        mock_eval_func_2.assert_has_calls(
            calls=(
                mock.call(solution_1),
                mock.call(solution_2),
                mock.call(solution_3)
            )
        )
        self.assertEqual(mock_eval_func_2.call_count, 3)

    def test_solution_lt(self):
        """Test that a solution which is dominated by another solution and has
        equal objectives is less than the other solution.

        """
        int_type = Type(name='int')

        mock_eval_func_1 = mock.Mock(side_effect=[66.6, 66.7, 66.7])
        mock_eval_func_2 = mock.Mock(side_effect=[66.6, 66.6, 66.6])

        objective_1 = Objective(eval_func=mock_eval_func_1, weight=42.0)
        objective_2 = Objective(eval_func=mock_eval_func_2, weight=42.0)

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

        for _ in range(100):
            self.assertLess(solution_1, solution_2)
            self.assertFalse(solution_2 < solution_1)
            self.assertRaises(
                TypeError,
                lambda s1, s2: s1 < s2,
                solution_1,
                solution_3
            )

        mock_eval_func_1.assert_has_calls(
            calls=(
                mock.call(solution_1),
                mock.call(solution_2),
                mock.call(solution_3)
            )
        )
        self.assertEqual(mock_eval_func_1.call_count, 3)

        mock_eval_func_2.assert_has_calls(
            calls=(
                mock.call(solution_1),
                mock.call(solution_2),
                mock.call(solution_3)
            )
        )
        self.assertEqual(mock_eval_func_2.call_count, 3)

    def test_solutions_sorted(self):
        """Test that a collection of solution instances behave nicely under the
        built-in *sorted* function.

        """
        int_type = Type(name='int')

        self.maxDiff = None

        mock_eval_func_1 = mock.Mock(side_effect=[66.6, 66.7, 66.7, 66.8])
        mock_eval_func_2 = mock.Mock(side_effect=[66.6, 66.6, 66.6, 66.6])

        objective_1 = Objective(eval_func=mock_eval_func_1, weight=42.0)
        objective_2 = Objective(eval_func=mock_eval_func_2, weight=42.0)

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
            LOG.info('checking solution %d', idx)
            self.assertIs(solution, expected[idx])
            LOG.info('verified solution %d', idx)

        mock_eval_func_1.assert_has_calls(
            calls=(
                mock.call(solution_1),
                mock.call(solution_2),
                mock.call(solution_3),
                mock.call(solution_4)
            )
        )
        self.assertEqual(mock_eval_func_1.call_count, 4)

        mock_eval_func_2.assert_has_calls(
            calls=(
                mock.call(solution_1),
                mock.call(solution_2),
                mock.call(solution_3),
                mock.call(solution_4)
            )
        )
        self.assertEqual(mock_eval_func_2.call_count, 4)
