import unittest
import random

from unittest import mock
from hypothesis import given
from hypothesis.strategies import integers, text, builds

from zoonomia.lang import Symbol, Operator, OperatorTable
from zoonomia.types import Type, ParametrizedType
from zoonomia.operations import (
    full, grow, ramped_half_and_half, mutate_subtree, mutate_interior_node,
    mutate_leaf_node, crossover_subtree, tournament_select,
    _random_depth_counts
)
from zoonomia.tree import Tree, Node
from zoonomia.solution import Solution, Objective


class TestFull(unittest.TestCase):

    @mock.patch('random.Random')
    def test_full_max_depth_1(self, MockRandom):
        """Test that the full tree generation strategy returns a type-safe
        depth zero tree for max_depth=1.

        """
        int_type = Type(name='Int')
        float_type = Type(name='Float')
        str_type = Type(name='Str')

        list_type = Type(name='List')
        set_type = Type(name='Set')

        collection_type = Type(
            name='Collection',
            contained_types=frozenset((list_type, set_type))
        )

        number_type = Type(
            name='Number',
            contained_types=frozenset((int_type, float_type))
        )

        collection_of_numbers = ParametrizedType(
            name='Collection<Number>',
            base_type=collection_type,
            parameter_types=(number_type,)
        )

        collection_of_floats = ParametrizedType(
            name='Collection<Float>',
            base_type=collection_type,
            parameter_types=(float_type,)
        )

        basis_0 = Operator(
            symbol=Symbol(name='basis_0', dtype=collection_type),
            signature=(collection_of_numbers, str_type)
        )

        terminal_0 = Operator(
            symbol=Symbol(name='terminal_0', dtype=str_type),
            signature=()
        )

        terminal_1 = Operator(
            symbol=Symbol(name='terminal_1', dtype=collection_of_floats),
            signature=()
        )

        basis_operators = OperatorTable(operators=(basis_0,))
        terminal_operators = OperatorTable(operators=(terminal_0, terminal_1))

        root = Node(operator=terminal_1)

        objective = Objective(eval_func=lambda s: 666, weight=0.666)

        expected_tree = Tree(root=root)
        expected_solution = Solution(
            tree=expected_tree, objectives=(objective,)
        )

        rng = MockRandom.return_value
        rng.choice = mock.MagicMock(return_value=terminal_1)

        self.assertEqual(
            full(
                max_depth=1,
                basis_operators=basis_operators,
                terminal_operators=terminal_operators,
                dtype=collection_type,
                objectives=(objective,),
                rng=rng
            ),
            expected_solution
        )

        rng.choice.assert_called_once_with(
            tuple(terminal_operators[collection_type])
        )

    @mock.patch('random.Random')
    def test_full_max_depth_2(self, MockRandom):
        """Test that the full tree generation strategy returns a type-safe
        depth one tree for max_depth=2.

        """
        int_type = Type(name='Int')
        float_type = Type(name='Float')
        str_type = Type(name='Str')

        list_type = Type(name='List')
        set_type = Type(name='Set')

        collection_type = Type(
            name='Collection',
            contained_types=frozenset((list_type, set_type))
        )

        number_type = Type(
            name='Number',
            contained_types=frozenset((int_type, float_type))
        )

        collection_of_numbers = ParametrizedType(
            name='Collection<Number>',
            base_type=collection_type,
            parameter_types=(number_type,)
        )

        collection_of_floats = ParametrizedType(
            name='Collection<Float>',
            base_type=collection_type,
            parameter_types=(float_type,)
        )

        basis_0 = Operator(
            symbol=Symbol(name='basis_0', dtype=collection_type),
            signature=(collection_of_numbers, str_type)
        )

        terminal_0 = Operator(
            symbol=Symbol(name='terminal_0', dtype=str_type),
            signature=()
        )

        terminal_1 = Operator(
            symbol=Symbol(name='terminal_1', dtype=collection_of_floats),
            signature=()
        )

        rng = MockRandom.return_value
        rng.choice = mock.Mock(side_effect=[basis_0, terminal_1, terminal_0])

        basis_operators = OperatorTable(operators=(basis_0,))
        terminal_operators = OperatorTable(operators=(terminal_0, terminal_1))

        root = Node(operator=basis_0)
        root.add_child(child=Node(operator=terminal_1), position=0)
        root.add_child(child=Node(operator=terminal_0), position=1)

        objective = Objective(eval_func=lambda s: 666, weight=0.666)

        expected_tree = Tree(root=root)
        expected_solution = Solution(
            tree=expected_tree, objectives=(objective,)
        )

        self.assertEqual(
            full(
                max_depth=2,
                basis_operators=basis_operators,
                terminal_operators=terminal_operators,
                dtype=collection_type,
                objectives=(objective,),
                rng=rng
            ),
            expected_solution
        )

        rng.choice.assert_has_calls(
            [
                mock.call(tuple(basis_operators[collection_type])),
                mock.call(tuple(terminal_operators[collection_of_numbers])),
                mock.call(tuple(terminal_operators[str_type]))
            ],
            any_order=False
        )
        self.assertEqual(3, rng.choice.call_count)


class TestGrow(unittest.TestCase):

    @mock.patch('random.Random')
    def test_grow_max_depth_1(self, MockRandom):
        int_type = Type(name='Int')
        float_type = Type(name='Float')
        str_type = Type(name='Str')

        list_type = Type(name='List')
        set_type = Type(name='Set')

        collection_type = Type(
            name='Collection',
            contained_types=frozenset((list_type, set_type))
        )

        number_type = Type(
            name='Number',
            contained_types=frozenset((int_type, float_type))
        )

        collection_of_numbers = ParametrizedType(
            name='Collection<Number>',
            base_type=collection_type,
            parameter_types=(number_type,)
        )

        collection_of_floats = ParametrizedType(
            name='Collection<Float>',
            base_type=collection_type,
            parameter_types=(float_type,)
        )

        basis_0 = Operator(
            symbol=Symbol(name='basis_0', dtype=collection_type),
            signature=(collection_of_numbers, str_type)
        )

        terminal_0 = Operator(
            symbol=Symbol(name='terminal_0', dtype=str_type),
            signature=()
        )

        terminal_1 = Operator(
            symbol=Symbol(name='terminal_1', dtype=collection_of_floats),
            signature=()
        )

        basis_operators = OperatorTable(operators=(basis_0,))
        terminal_operators = OperatorTable(operators=(terminal_0, terminal_1))

        root = Node(operator=terminal_1)

        objective = Objective(eval_func=lambda s: 666, weight=0.666)

        expected_tree = Tree(root=root)
        expected_solution = Solution(
            tree=expected_tree, objectives=(objective,)
        )

        rng = MockRandom.return_value
        rng.choice = mock.MagicMock(return_value=terminal_1)

        self.assertEqual(
            grow(
                max_depth=1,
                basis_operators=basis_operators,
                terminal_operators=terminal_operators,
                dtype=collection_type,
                objectives=(objective,),
                rng=rng
            ),
            expected_solution
        )

        rng.choice.assert_called_once_with(
            tuple(terminal_operators[collection_type])
        )

    @mock.patch('random.Random')
    def test_grow_max_depth_2(self, MockRandom):
        int_type = Type(name='Int')
        float_type = Type(name='Float')
        str_type = Type(name='Str')

        list_type = Type(name='List')
        set_type = Type(name='Set')

        collection_type = Type(
            name='Collection',
            contained_types=frozenset((list_type, set_type))
        )

        number_type = Type(
            name='Number',
            contained_types=frozenset((int_type, float_type))
        )

        collection_of_numbers = ParametrizedType(
            name='Collection<Number>',
            base_type=collection_type,
            parameter_types=(number_type,)
        )

        collection_of_floats = ParametrizedType(
            name='Collection<Float>',
            base_type=collection_type,
            parameter_types=(float_type,)
        )

        basis_0 = Operator(
            symbol=Symbol(name='basis_0', dtype=collection_type),
            signature=(collection_of_numbers, str_type)
        )

        terminal_0 = Operator(
            symbol=Symbol(name='terminal_0', dtype=str_type),
            signature=()
        )

        terminal_1 = Operator(
            symbol=Symbol(name='terminal_1', dtype=collection_of_floats),
            signature=()
        )

        rng = MockRandom.return_value
        rng.choice = mock.Mock(side_effect=[basis_0, terminal_1, terminal_0])

        basis_operators = OperatorTable(operators=(basis_0,))
        terminal_operators = OperatorTable(operators=(terminal_0, terminal_1))

        root = Node(operator=basis_0)
        root.add_child(child=Node(operator=terminal_1), position=0)
        root.add_child(child=Node(operator=terminal_0), position=1)

        objective = Objective(eval_func=lambda s: 666, weight=0.666)

        expected_tree = Tree(root=root)
        expected_solution = Solution(
            tree=expected_tree, objectives=(objective,)
        )

        self.assertEqual(
            grow(
                max_depth=2,
                basis_operators=basis_operators,
                terminal_operators=terminal_operators,
                dtype=collection_type,
                objectives=(objective,),
                rng=rng
            ),
            expected_solution
        )

        rng.choice.assert_has_calls(
            [
                mock.call(tuple(
                    terminal_operators.union(basis_operators)[collection_type]
                )),
                mock.call(tuple(terminal_operators[collection_of_numbers])),
                mock.call(tuple(terminal_operators[str_type]))
            ],
            any_order=False
        )
        self.assertEqual(3, rng.choice.call_count)


class TestRampedHalfAndHalf(unittest.TestCase):

    def test_random_depth_counts_normalized(self):
        """Test that _random_depth_counts returns a histogram s.t. the total
        number of depths is equal to the population_size parameter.

        """
        max_depth = 666
        population_size = 66666
        depth_counts = _random_depth_counts(
            max_depth=max_depth,
            population_size=population_size,
            rng=random.Random()
        )

        self.assertEqual(
            sum(depth_counts[k] for k in depth_counts.keys()),
            population_size
        )

    def test_random_depth_counts_dimensions(self):
        """Test that _random_depth_counts returns a histogram s.t. the range of
        depth counts equals the max_depth parameter, and the interval of that
        range is [1, max_depth].

        """
        max_depth = 666
        population_size = 66666
        depth_counts = _random_depth_counts(
            max_depth=max_depth,
            population_size=population_size,
            rng=random.Random()
        )

        self.assertEqual(len(depth_counts.keys()), max_depth)
        self.assertEqual(tuple(sorted(depth_counts.keys()))[0], 1)
        self.assertEqual(tuple(sorted(depth_counts.keys()))[-1], max_depth)

    def test_random_depth_counts_depth_1(self):
        """Test that random_depth_counts returns a histogram {n: 1} when
        max_depth is 1.

        """
        max_depth = 1
        population_size = 1
        depth_counts = _random_depth_counts(
            max_depth=max_depth,
            population_size=population_size,
            rng=random.Random()
        )

        self.assertEqual({1: population_size}, depth_counts)

    @mock.patch('random.Random')
    def test_random_depth_counts(self, MockRandom):
        """Test that _random_depth_counts returns a histogram of depth counts
        having the expected distribution.

        """
        max_depth = 3
        population_size = 9
        rng = MockRandom.return_value
        rng.choice = mock.Mock(side_effect=[1, 2, 3, 1, 2, 3, 1, 2, 3])

        counts = _random_depth_counts(
            max_depth=max_depth,
            population_size=population_size,
            rng=rng
        )

        for k in counts:
            self.assertEqual(counts[k], 3)

    @mock.patch('random.Random')
    def test_ramped_half_and_half_max_depth_1_same_as_full(self, MockRandom):
        """Test that ramped_half_and_half produces an identical population to
        full when max_depth is 1.

        """
        int_type = Type(name='Int')
        float_type = Type(name='Float')
        str_type = Type(name='Str')

        list_type = Type(name='List')
        set_type = Type(name='Set')

        collection_type = Type(
            name='Collection',
            contained_types=frozenset((list_type, set_type))
        )

        number_type = Type(
            name='Number',
            contained_types=frozenset((int_type, float_type))
        )

        collection_of_numbers = ParametrizedType(
            name='Collection<Number>',
            base_type=collection_type,
            parameter_types=(number_type,)
        )

        collection_of_floats = ParametrizedType(
            name='Collection<Float>',
            base_type=collection_type,
            parameter_types=(float_type,)
        )

        basis_0 = Operator(
            symbol=Symbol(name='basis_0', dtype=collection_type),
            signature=(collection_of_numbers, str_type)
        )

        terminal_0 = Operator(
            symbol=Symbol(name='terminal_0', dtype=str_type),
            signature=()
        )

        terminal_1 = Operator(
            symbol=Symbol(name='terminal_1', dtype=collection_of_floats),
            signature=()
        )

        basis_operators = OperatorTable(operators=(basis_0,))
        terminal_operators = OperatorTable(operators=(terminal_0, terminal_1))

        root = Node(operator=terminal_1)

        objective = Objective(eval_func=lambda s: 666, weight=0.666)

        expected_tree = Tree(root=root)
        expected_solution = Solution(
            tree=expected_tree, objectives=(objective,)
        )

        rng = MockRandom.return_value
        rng.choice = mock.MagicMock(side_effect=[terminal_1, 1, terminal_1])

        full_solution = full(
            max_depth=1,
            basis_operators=basis_operators,
            terminal_operators=terminal_operators,
            dtype=collection_type,
            objectives=(objective,),
            rng=rng
        )

        ramped_half_and_half_solution = ramped_half_and_half(
            max_depth=1,
            population_size=1,
            basis_operators=basis_operators,
            terminal_operators=terminal_operators,
            dtype=collection_type,
            objectives=(objective,),
            rng=rng
        )

        self.assertEqual(1, len(ramped_half_and_half_solution))

        self.assertEqual(full_solution, expected_solution)
        self.assertSetEqual(
            frozenset((full_solution,)),
            ramped_half_and_half_solution
        )

        rng.choice.assert_has_calls(
            calls=(
                mock.call(tuple(terminal_operators[collection_type])),
                mock.call([1]),  # _random_depth_counts
                mock.call(tuple(terminal_operators[collection_type]))
            ),
            any_order=False
        )
        self.assertEqual(3, rng.choice.call_count)

    @mock.patch('random.Random')
    def test_ramped_half_and_half_max_depth_1_same_as_grow(self, MockRandom):
        """Test that ramped_half_and_half produces an identical population to
        grow when max_depth is 1.

        """
        int_type = Type(name='Int')
        float_type = Type(name='Float')
        str_type = Type(name='Str')

        list_type = Type(name='List')
        set_type = Type(name='Set')

        collection_type = Type(
            name='Collection',
            contained_types=frozenset((list_type, set_type))
        )

        number_type = Type(
            name='Number',
            contained_types=frozenset((int_type, float_type))
        )

        collection_of_numbers = ParametrizedType(
            name='Collection<Number>',
            base_type=collection_type,
            parameter_types=(number_type,)
        )

        collection_of_floats = ParametrizedType(
            name='Collection<Float>',
            base_type=collection_type,
            parameter_types=(float_type,)
        )

        basis_0 = Operator(
            symbol=Symbol(name='basis_0', dtype=collection_type),
            signature=(collection_of_numbers, str_type)
        )

        terminal_0 = Operator(
            symbol=Symbol(name='terminal_0', dtype=str_type),
            signature=()
        )

        terminal_1 = Operator(
            symbol=Symbol(name='terminal_1', dtype=collection_of_floats),
            signature=()
        )

        basis_operators = OperatorTable(operators=(basis_0,))
        terminal_operators = OperatorTable(operators=(terminal_0, terminal_1))

        root = Node(operator=terminal_1)

        objective = Objective(eval_func=lambda s: 666, weight=0.666)

        expected_tree = Tree(root=root)
        expected_solution = Solution(
            tree=expected_tree, objectives=(objective,)
        )

        rng = MockRandom.return_value
        rng.choice = mock.MagicMock(side_effect=[terminal_1, 1, terminal_1])

        grow_solution = grow(
            max_depth=1,
            basis_operators=basis_operators,
            terminal_operators=terminal_operators,
            dtype=collection_type,
            objectives=(objective,),
            rng=rng
        )

        ramped_half_and_half_solution = ramped_half_and_half(
            max_depth=1,
            population_size=1,
            basis_operators=basis_operators,
            terminal_operators=terminal_operators,
            dtype=collection_type,
            objectives=(objective,),
            rng=rng
        )

        self.assertEqual(1, len(ramped_half_and_half_solution))

        self.assertEqual(grow_solution, expected_solution)
        self.assertSetEqual(
            frozenset((grow_solution,)),
            ramped_half_and_half_solution
        )

        rng.choice.assert_has_calls(
            calls=(
                mock.call(tuple(terminal_operators[collection_type])),
                mock.call([1]),  # _random_depth_counts
                mock.call(tuple(terminal_operators[collection_type]))
            ),
            any_order=False
        )
        self.assertEqual(3, rng.choice.call_count)

    @mock.patch('random.Random')
    def test_ramped_half_and_half_max_depth_3(self, MockRandom):
        """Test that ramped_half_and_half produces the expected population."""
        int_type = Type(name='Int')
        float_type = Type(name='Float')
        str_type = Type(name='Str')

        list_type = Type(name='List')
        set_type = Type(name='Set')

        collection_type = Type(
            name='Collection',
            contained_types=frozenset((list_type, set_type))
        )

        number_type = Type(
            name='Number',
            contained_types=frozenset((int_type, float_type))
        )

        collection_of_numbers = ParametrizedType(
            name='Collection<Number>',
            base_type=collection_type,
            parameter_types=(number_type,)
        )

        collection_of_floats = ParametrizedType(
            name='Collection<Float>',
            base_type=collection_type,
            parameter_types=(float_type,)
        )

        basis_0 = Operator(
            symbol=Symbol(name='basis_0', dtype=collection_type),
            signature=(collection_of_numbers, str_type)
        )

        terminal_0 = Operator(
            symbol=Symbol(name='terminal_0', dtype=str_type),
            signature=()
        )

        terminal_1 = Operator(
            symbol=Symbol(name='terminal_1', dtype=collection_of_floats),
            signature=()
        )

        mock_rng = MockRandom.return_value
        mock_rng.choice = mock.Mock(
            side_effect=[
                2,
                basis_0,
                terminal_1,
                terminal_0
            ]
        )
        mock_rng.getrandbits = mock.Mock(
            side_effect=[True, False, True]
        )

        basis_operators = OperatorTable(operators=(basis_0,))
        terminal_operators = OperatorTable(operators=(terminal_0, terminal_1))

        root = Node(operator=basis_0)
        root.add_child(child=Node(operator=terminal_1), position=0)
        root.add_child(child=Node(operator=terminal_0), position=1)

        objective = Objective(eval_func=lambda s: 666, weight=0.666)

        expected_tree = Tree(root=root)
        expected_solution = Solution(
            tree=expected_tree, objectives=(objective,)
        )

        self.assertSetEqual(
            frozenset((expected_solution,)),
            ramped_half_and_half(
                max_depth=3,
                population_size=1,
                basis_operators=basis_operators,
                terminal_operators=terminal_operators,
                dtype=collection_type,
                objectives=(objective,),
                rng=mock_rng
            )
        )

        expected_depth_counts = {1: 1, 2: 1, 3: 1}

        mock_rng.choice.assert_has_calls(
            [
                mock.call(expected_depth_counts.keys()),
                mock.call(tuple(basis_operators[collection_type])),
                mock.call(tuple(terminal_operators[collection_of_floats])),
                mock.call(tuple(terminal_operators[str_type]))
            ],
            any_order=False
        )
        self.assertEqual(4, mock_rng.choice.call_count)

        mock_rng.getrandbits.assert_has_calls([mock.call(1)], any_order=False)
        self.assertEqual(1, mock_rng.getrandbits.call_count)


class TestMutateSubtree(unittest.TestCase):

    def test_mutate_subtree(self):
        self.fail()  # FIXME


class TestMutateNode(unittest.TestCase):

    def test_mutate_node(self):
        self.fail()  # FIXME


class TestCrossoverSubtree(unittest.TestCase):

    def test_crossover_subtree(self):
        self.fail()  # FIXME


class TestTournamentSelect(unittest.TestCase):

    def test_tournament_select(self):
        self.fail()  # FIXME
