import unittest
import mock
import time
import logging

from multiprocessing.pool import ThreadPool

from zoonomia.tree import Node, Tree
from zoonomia.solution import (
    verify_closure_property, BasisOperator, TerminalOperator, OperatorSet,
    Objective, Fitness, Solution
)

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class TestVerifyClosureProperty(unittest.TestCase):

    def test_verify_closure_property(self):
        """

        """
        def add(left, right): return left + right

        int_basis = BasisOperator(func=add, signature=(int, int), dtype=int)
        float_basis = BasisOperator(
            func=add, signature=(float, float), dtype=float
        )

        int_terminal = TerminalOperator(source=xrange(666), dtype=int)
        float_terminal = TerminalOperator(
            source=(float(i) for i in xrange(666)), dtype=float
        )

        basis_set = OperatorSet(operators=(int_basis, float_basis))
        terminal_set = OperatorSet(operators=(int_terminal, float_terminal))

        result = verify_closure_property(
            basis_set=basis_set, terminal_set=terminal_set
        )

        self.assertTrue(result)


class TestBasisOperator(unittest.TestCase):

    def test_basis_operator_attributes(self):
        """Test that a BasisOperator instance has attributes which are
        references to the data passed into the constructor.

        """
        def add(a, b): return a + b

        signature = (int, int)
        dtype = int

        basis_operator = BasisOperator(
            func=add, signature=signature, dtype=dtype
        )

        self.assertIs(basis_operator.func, add)
        self.assertIs(basis_operator.signature, signature)
        self.assertIs(basis_operator.dtype, dtype)

    def test_basis_operator_hash(self):
        """Test that two BasisOperators which are identically distinct yet
        refer to the same data have identical hashes.

        """
        def add(a, b): return a + b

        signature = (int, int)
        dtype = int

        basis_operator_1 = BasisOperator(
            func=add, signature=signature, dtype=dtype
        )

        basis_operator_2 = BasisOperator(
            func=add, signature=signature, dtype=dtype
        )

        self.assertEqual(hash(basis_operator_1), hash(basis_operator_2))

    def test_basis_operator_equals(self):
        """Test that two BasisOperators which are identically distinct yet
        refer to the same data are equal.

        """
        def add(a, b): return a + b

        signature = (int, int)
        dtype = int

        basis_operator_1 = BasisOperator(
            func=add, signature=signature, dtype=dtype
        )

        basis_operator_2 = BasisOperator(
            func=add, signature=signature, dtype=dtype
        )

        self.assertEqual(basis_operator_1, basis_operator_2)
        self.assertEqual(basis_operator_2, basis_operator_1)

    def test_basis_operator_not_equals(self):
        """Test that two BasisOperators which do not refer to the same data are
        unequal.

        """
        def add(a, b): return a + b

        signature = (int, int)
        dtype_1 = int
        dtype_2 = float

        basis_operator_1 = BasisOperator(
            func=add, signature=signature, dtype=dtype_1
        )

        basis_operator_2 = BasisOperator(
            func=add, signature=signature, dtype=dtype_2
        )

        self.assertNotEqual(basis_operator_1, basis_operator_2)
        self.assertNotEqual(basis_operator_2, basis_operator_1)

    def test_basis_operator_call(self):
        """Test that calling a basis operator like a function produces the same
        result as calling the basis operator's *func* attribute.

        """
        def add(a, b): return a + b

        signature = (int, int)
        dtype = int

        basis_operator = BasisOperator(
            func=add, signature=signature, dtype=dtype
        )

        self.assertEqual(add(6, 66), basis_operator(6, 66))


class TestTerminalOperator(unittest.TestCase):

    def test_terminal_operator_attributes(self):
        """Test that a TerminalOperator instance has attributes which are
        references to the data passed into its constructor.

        """
        source = xrange(666)
        dtype = int

        terminal_operator = TerminalOperator(source=source, dtype=dtype)

        self.assertIs(terminal_operator.source, source)
        self.assertIs(terminal_operator.dtype, dtype)

    def test_terminal_operator_hash(self):
        """Test that two TerminalOperators which are identically distinct yet
        refer to the same data have identical hashes.

        """
        source = xrange(666)
        dtype = int

        terminal_operator_1 = TerminalOperator(source=source, dtype=dtype)
        terminal_operator_2 = TerminalOperator(source=source, dtype=dtype)

        self.assertEqual(hash(terminal_operator_1), hash(terminal_operator_2))

    def test_terminal_operator_equals(self):
        """Test that two TerminalOperators which are identically distinct yet
        refer to the same data are equal.

        """
        source = xrange(666)
        dtype = int

        terminal_operator_1 = TerminalOperator(source=source, dtype=dtype)
        terminal_operator_2 = TerminalOperator(source=source, dtype=dtype)

        self.assertEqual(terminal_operator_1, terminal_operator_2)
        self.assertEqual(terminal_operator_2, terminal_operator_1)

    def test_terminal_operator_not_equals(self):
        """Test that two TerminalOperators which do not refer to the same data
        are unequal.

        """
        source = xrange(666)
        dtype_1 = int
        dtype_2 = float

        terminal_operator_1 = TerminalOperator(source=source, dtype=dtype_1)
        terminal_operator_2 = TerminalOperator(source=source, dtype=dtype_2)

        self.assertNotEqual(terminal_operator_1, terminal_operator_2)
        self.assertNotEqual(terminal_operator_2, terminal_operator_1)

    def test_terminal_operator_iter(self):
        """Test that an iterator over a TerminalOperator produces the same
        results as an iterator over its *source* attribute.

        """
        source = xrange(666)
        dtype = int

        terminal_operator = TerminalOperator(source=source, dtype=dtype)

        self.assertItemsEqual(
            iter(terminal_operator.source), iter(terminal_operator)
        )


class TestOperatorSet(unittest.TestCase):

    def test_operator_set_lookup(self):
        """Test that an OperatorSet behaves as expected with respect to lookups
        by *dtype* and *signature*.

        """
        def add(a, b): return a + b

        basis_op_1 = BasisOperator(func=add, signature=(int, int), dtype=int)
        basis_op_2 = BasisOperator(func=add, signature=(str, str), dtype=str)

        terminal_op_1 = TerminalOperator(source=xrange(666), dtype=int)
        terminal_op_2 = TerminalOperator(
            source=(str(i) for i in xrange(666)), dtype=str
        )

        basis_set = OperatorSet(operators=(basis_op_1, basis_op_2))
        terminal_set = OperatorSet(operators=(terminal_op_1, terminal_op_2))

        self.assertSetEqual({basis_op_1, basis_op_2}, basis_set.operators)

        self.assertSetEqual(basis_set[int], {basis_op_1})
        self.assertSetEqual(basis_set[(int, int)], {basis_op_1})

        self.assertSetEqual(basis_set[str], {basis_op_2})
        self.assertSetEqual(basis_set[(str, str)], {basis_op_2})

        self.assertSetEqual(
            {terminal_op_1, terminal_op_2}, terminal_set.operators
        )

        self.assertSetEqual(terminal_set[int], {terminal_op_1})
        self.assertSetEqual(terminal_set[str], {terminal_op_2})

    def test_operator_set_union(self):
        """Test that the union of two OperatorSets behaves as expected with
        respect to lookups by *dtype* and *signature*.

        """
        def add(a, b): return a + b

        basis_op_1 = BasisOperator(func=add, signature=(int, int), dtype=int)
        basis_op_2 = BasisOperator(func=add, signature=(str, str), dtype=str)

        terminal_op_1 = TerminalOperator(source=xrange(666), dtype=int)
        terminal_op_2 = TerminalOperator(
            source=(str(i) for i in xrange(666)), dtype=str
        )

        basis_set = OperatorSet(operators=(basis_op_1, basis_op_2))
        terminal_set = OperatorSet(operators=(terminal_op_1, terminal_op_2))

        basis_union_terminal = basis_set.union(terminal_set)
        terminal_union_basis = terminal_set.union(basis_set)

        self.assertSetEqual(
            basis_union_terminal.operators, terminal_union_basis.operators
        )

        self.assertSetEqual(
            {basis_op_1, basis_op_2, terminal_op_1, terminal_op_2},
            basis_union_terminal.operators
        )

        self.assertSetEqual(
            basis_union_terminal[int], terminal_union_basis[int]
        )

        self.assertSetEqual(
            basis_union_terminal[int], {basis_op_1, terminal_op_1}
        )

        self.assertSetEqual(
            basis_union_terminal[str], terminal_union_basis[str]
        )

        self.assertSetEqual(
            basis_union_terminal[str], {basis_op_2, terminal_op_2}
        )

        self.assertSetEqual(
            basis_union_terminal[(int, int)], terminal_union_basis[(int, int)]
        )

        self.assertSetEqual(
            basis_union_terminal[(int, int)], {basis_op_1}
        )

        self.assertSetEqual(
            basis_union_terminal[(str, str)], terminal_union_basis[(str, str)]
        )

        self.assertSetEqual(
            basis_union_terminal[(str, str)], {basis_op_2}
        )

    def test_operator_set_iter(self):
        """Test that an iterator over an OperatorSet yields the same items as
        an iterator over its *operators* attribute.

        """
        def add(a, b): return a + b

        basis_op_1 = BasisOperator(func=add, signature=(int, int), dtype=int)

        terminal_op_1 = TerminalOperator(source=xrange(666), dtype=int)

        operator_set = OperatorSet(operators=(basis_op_1, terminal_op_1))

        self.assertItemsEqual(
            operator_set.operators, iter(operator_set)
        )


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
        def eval_func(sol): return 66.6

        weight = 42.0

        objective = Objective(eval_func=eval_func, weight=weight)
        terminal_op = TerminalOperator(source=xrange(666), dtype=int)
        root = Node(operator=terminal_op)

        solution = Solution(tree=Tree(root=root), objectives=(objective,))
        fitness = objective.evaluate(solution)

        self.assertEqual(fitness.score, weight * eval_func(solution))


class TestFitness(unittest.TestCase):

    def test_fitness_attributes(self):
        """Test that a Fitness object's *score* and *objective* attributes
        refer to the data passed into the constructor.

        """
        def eval_func(sol): return 66.6

        weight = 42.0

        objective = Objective(eval_func=eval_func, weight=weight)
        terminal_op = TerminalOperator(source=xrange(666), dtype=int)
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
        def eval_func(sol): return 66.6

        weight = 42.0

        objective = Objective(eval_func=eval_func, weight=weight)
        terminal_op = TerminalOperator(source=xrange(666), dtype=int)
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
        def eval_func(sol): return 66.6

        weight = 42.0

        objective = Objective(eval_func=eval_func, weight=weight)
        terminal_op = TerminalOperator(source=xrange(666), dtype=int)
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
        def eval_func(sol): return 66.6

        weight = 42.0

        objective = Objective(eval_func=eval_func, weight=weight)
        terminal_op = TerminalOperator(source=xrange(666), dtype=int)
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
        def eval_func(sol): return 0.0  # only used for constructing objective

        objective = Objective(eval_func=eval_func, weight=42.0)

        fitness_1 = Fitness(score=66.7, objective=objective)
        fitness_2 = Fitness(score=66.6, objective=objective)

        self.assertGreater(fitness_1, fitness_2)

    def test_fitness_ge(self):
        """Test that fitness_1 with score_1 > score_2 is greater than or equal
        to fitness_2 with score_2 and that fitness_1 is greater than or equal
        to fitness_3 with score_3 == score_1.

        """
        def eval_func(sol): return 0.0  # only used for constructing objective

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
        def eval_func(sol): return 0.0  # only used for constructing objective

        objective = Objective(eval_func=eval_func, weight=42.0)

        fitness_1 = Fitness(score=66.6, objective=objective)
        fitness_2 = Fitness(score=66.7, objective=objective)

        self.assertLess(fitness_1, fitness_2)

    def test_fitness_le(self):
        """Test that fitness_1 with score_1 <= score_2 is less than or equal to
        fitness_2 with score_2 and that fitness_1 is greater than or equal to
        fitness_3 with score_3 == score_1.

        """
        def eval_func(sol): return 0.0  # only used for constructing objective

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
        def eval_func(sol): return 66.6

        objective = Objective(eval_func=eval_func, weight=42.0)

        terminal_operator = TerminalOperator(source=xrange(666), dtype=int)

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
        self.maxDiff = None

        pool = ThreadPool(processes=2)

        def eval_func_1(sol):
            log.debug('Calling eval_func_1')
            time.sleep(0.01)  # eval_func_1 hopefully evaluated second
            return 66.6

        def eval_func_2(sol):
            log.debug('Calling eval_func_2')
            return 66.7

        objective_1 = Objective(eval_func=eval_func_1, weight=42.0)
        objective_2 = Objective(eval_func=eval_func_2, weight=42.0)

        terminal_operator = TerminalOperator(source=xrange(666), dtype=int)

        root = Node(operator=terminal_operator)

        tree = Tree(root=root)

        for _ in xrange(50):
            solution = Solution(
                tree=tree,
                objectives=(objective_1, objective_2),
                map_=lambda f, s: pool.imap_unordered(
                    func=f, iterable=s, chunksize=2
                )
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
        pool = ThreadPool(processes=100)

        eval_func = mock.Mock(return_value=66.6)

        objective = Objective(eval_func=eval_func, weight=42.0)

        terminal_operator = TerminalOperator(source=xrange(666), dtype=int)

        root = Node(operator=terminal_operator)

        tree = Tree(root=root)

        solution = Solution(
            tree=tree, objectives=(objective,), map_=pool.imap_unordered
        )

        results = [
            pool.apply_async(lambda s: s.evaluate(), (solution,))
            for _ in xrange(100)
        ]

        previous_result = None
        for idx, res in enumerate(results):
            result = res.get()
            if idx > 0:
                self.assertEqual(result, previous_result)
            previous_result = result

        eval_func.assert_called_once_with(solution)

    def test_solution_dominates(self):
        """Test that a Solution's *dominates* method returns True if the
        solution Pareto-dominates another solution, and False otherwise.

        """
        eval_func_1 = mock.Mock(side_effect=[66.7, 66.6, 66.6])
        eval_func_2 = mock.Mock(side_effect=[66.6, 66.6, 66.6])
        eval_func_3 = mock.Mock(side_effect=[66.6, 66.6, 66.6])

        objective_1 = Objective(eval_func=eval_func_1, weight=42.0)
        objective_2 = Objective(eval_func=eval_func_2, weight=42.0)
        objective_3 = Objective(eval_func=eval_func_3, weight=42.0)

        terminal_operator = TerminalOperator(source=xrange(666), dtype=int)

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
        pool = ThreadPool(processes=2)

        eval_func = mock.Mock(return_value=66.6)

        objective = Objective(eval_func=eval_func, weight=42.0)

        terminal_operator = TerminalOperator(source=xrange(666), dtype=int)

        root_1 = Node(operator=terminal_operator)
        root_2 = Node(operator=terminal_operator)

        tree_1 = Tree(root=root_1)
        tree_2 = Tree(root=root_2)

        solution_1 = Solution(
                tree=tree_1, objectives=(objective,), map_=pool.imap_unordered
        )
        solution_2 = Solution(
                tree=tree_2, objectives=(objective,), map_=pool.imap_unordered
        )

        for _ in xrange(100):
            self.assertEqual(hash(solution_1), hash(solution_2))

        eval_func.assert_has_calls(
                calls=(mock.call(solution_1), mock.call(solution_2))
        )

        self.assertEqual(eval_func.call_count, 2)

    def test_solution_equals(self):
        """Test that two identically distinct Solutions are equal if their
        hashes are equal.

        """
        pool = ThreadPool(processes=2)

        eval_func = mock.Mock(return_value=66.6)

        objective = Objective(eval_func=eval_func, weight=42.0)

        terminal_operator = TerminalOperator(source=xrange(666), dtype=int)

        root_1 = Node(operator=terminal_operator)
        root_2 = Node(operator=terminal_operator)

        tree_1 = Tree(root=root_1)
        tree_2 = Tree(root=root_2)

        solution_1 = Solution(
                tree=tree_1, objectives=(objective,), map_=pool.imap_unordered
        )
        solution_2 = Solution(
                tree=tree_2, objectives=(objective,), map_=pool.imap_unordered
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
        pool = ThreadPool(processes=2)

        eval_func = mock.Mock(side_effect=[66.6, 66.7])

        objective = Objective(eval_func=eval_func, weight=42.0)

        terminal_operator = TerminalOperator(source=xrange(666), dtype=int)

        root_1 = Node(operator=terminal_operator)
        root_2 = Node(operator=terminal_operator)

        tree_1 = Tree(root=root_1)
        tree_2 = Tree(root=root_2)

        solution_1 = Solution(
                tree=tree_1, objectives=(objective,), map_=pool.imap_unordered
        )
        solution_2 = Solution(
                tree=tree_2, objectives=(objective,), map_=pool.imap_unordered
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
        eval_func_1 = mock.Mock(side_effect=[66.7, 66.6, 66.6])
        eval_func_2 = mock.Mock(side_effect=[66.6, 66.6, 66.6])

        objective_1 = Objective(eval_func=eval_func_1, weight=42.0)
        objective_2 = Objective(eval_func=eval_func_2, weight=42.0)

        terminal_operator_1 = TerminalOperator(source=xrange(666), dtype=int)
        terminal_operator_2 = TerminalOperator(source=xrange(666), dtype=int)

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
        eval_func_1 = mock.Mock(side_effect=[66.6, 66.7, 66.7])
        eval_func_2 = mock.Mock(side_effect=[66.6, 66.6, 66.6])

        objective_1 = Objective(eval_func=eval_func_1, weight=42.0)
        objective_2 = Objective(eval_func=eval_func_2, weight=42.0)

        terminal_operator_1 = TerminalOperator(source=xrange(666), dtype=int)
        terminal_operator_2 = TerminalOperator(source=xrange(666), dtype=int)

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
        self.maxDiff = None

        eval_func_1 = mock.Mock(side_effect=[66.6, 66.7, 66.7, 66.8])
        eval_func_2 = mock.Mock(side_effect=[66.6, 66.6, 66.6, 66.6])

        objective_1 = Objective(eval_func=eval_func_1, weight=42.0)
        objective_2 = Objective(eval_func=eval_func_2, weight=42.0)

        terminal_operator = TerminalOperator(source=xrange(666), dtype=int)

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
