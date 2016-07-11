import unittest
import random
import mock

from zoonomia.lang import Symbol, Operator, OperatorSet
from zoonomia.types import Type, GenericType, ParametrizedType
from zoonomia.operations import (
    full, grow, ramped_half_and_half, mutate_subtree, mutate_node,
    crossover_subtree, tournament_select
)
from zoonomia.tree import Tree, Node
from zoonomia.solution import Solution, Objective


class TestFull(unittest.TestCase):

    def test_full_max_depth_1(self):
        """Test that the full tree generation strategy returns a type-safe
        depth zero tree for max_depth=1.

        """
        int_type = Type(name='Int')
        float_type = Type(name='Float')
        str_type = Type(name='Str')

        list_type = Type(name='List')
        set_type = Type(name='Set')

        collection_type = GenericType(
            name='Collection',
            contained_types=frozenset((list_type, set_type))
        )

        number_type = GenericType(
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

        rng = random.Random()
        rng.choice = mock.Mock(return_value=terminal_0)

        basis_set = OperatorSet(operators=(basis_0,))
        terminal_set = OperatorSet(operators=(terminal_0, terminal_1))

        root = Node(operator=terminal_0)

        objective = Objective(eval_func=lambda s: 666, weight=0.666)

        expected_tree = Tree(root=root)
        expected_solution = Solution(
            tree=expected_tree, objectives=(objective,)
        )

        self.assertEqual(
            full(
                max_depth=1,
                basis_set=basis_set,
                terminal_set=terminal_set,
                dtype=collection_type,
                objectives=(objective,),
                rng=rng
            ),
            expected_solution
        )

    def test_full_max_depth_2(self):
        """Test that the full tree generation strategy returns a type-safe
        depth one tree for max_depth=2.

        """
        int_type = Type(name='Int')
        float_type = Type(name='Float')
        str_type = Type(name='Str')

        list_type = Type(name='List')
        set_type = Type(name='Set')

        collection_type = GenericType(
            name='Collection',
            contained_types=frozenset((list_type, set_type))
        )

        number_type = GenericType(
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

        rng = random.Random()
        rng.choice = mock.Mock(side_effect=[basis_0, terminal_0, terminal_1])

        basis_set = OperatorSet(operators=(basis_0,))
        terminal_set = OperatorSet(operators=(terminal_0, terminal_1))

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
                basis_set=basis_set,
                terminal_set=terminal_set,
                dtype=collection_type,
                objectives=(objective,),
                rng=rng
            ),
            expected_solution
        )


class TestGrow(unittest.TestCase):

    def test_grow_max_depth_1(self):
        raise NotImplementedError()  # FIXME

    def test_grow_max_depth_2(self):
        raise NotImplementedError()  # FIXME


class TestRampedHalfAndHalf(unittest.TestCase):

    def test_ramped_half_and_half(self):
        raise NotImplementedError()  # FIXME


class TestMutateSubtree(unittest.TestCase):

    def test_mutate_subtree(self):
        mutate_subtree(None)  # FIXME


class TestMutateNode(unittest.TestCase):

    def test_mutate_node(self):
        mutate_node(None)  # FIXME


class TestCrossoverSubtree(unittest.TestCase):

    def test_crossover_subtree(self):
        crossover_subtree(None, None)  # FIXME


class TestTournamentSelect(unittest.TestCase):

    def test_tournament_select(self):
        raise NotImplementedError()  # FIXME
