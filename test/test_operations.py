import unittest

from zoonomia.solution import BasisOperator, TerminalOperator, OperatorSet
from zoonomia.operations import (
    build_types_possibility_table, full, grow, ramped_half_and_half,
    mutate_subtree, mutate_node, crossover_subtree, tournament_select
)


class TestBuildTypesPossibilityTable(unittest.TestCase):

    def test_build_types_possibility_table_full(self):
        """

        """
        def add(a, b): return a + b

        basis_op_1 = BasisOperator(func=add, signature=(int, int), dtype=int)
        basis_op_2 = BasisOperator(
            func=add, signature=(float, float), dtype=float
        )
        basis_op_3 = BasisOperator(func=add, signature=(str, str), dtype=int)

        terminal_op_1 = TerminalOperator(source=xrange(666), dtype=int)
        terminal_op_2 = TerminalOperator(
            source=(float(i) for i in xrange(666)), dtype=float
        )
        terminal_op_3 = TerminalOperator(
            source=(str(i) for i in xrange(666)), dtype=str
        )

        basis_set = OperatorSet(operators=(basis_op_1, basis_op_2, basis_op_3))
        terminal_set = OperatorSet(
            operators=(terminal_op_1, terminal_op_2, terminal_op_3)
        )

        types_possibility_table = build_types_possibility_table(
            basis_set=basis_set,
            terminal_set=terminal_set,
            max_depth=2,
            grow_=False
        )

        self.assertSetEqual(
            types_possibility_table[0], set(o.dtype for o in terminal_set)
        )

        self.assertSetEqual(
            types_possibility_table[1], set(o.dtype for o in basis_set)
        )

    def test_build_types_possibility_table_grow(self):
        """

        """
        def add(a, b): return a + b

        basis_op_1 = BasisOperator(func=add, signature=(int, int), dtype=int)
        basis_op_2 = BasisOperator(
            func=add, signature=(float, float), dtype=float
        )
        basis_op_3 = BasisOperator(func=add, signature=(str, str), dtype=int)

        terminal_op_1 = TerminalOperator(source=xrange(666), dtype=int)
        terminal_op_2 = TerminalOperator(
            source=(float(i) for i in xrange(666)), dtype=float
        )
        terminal_op_3 = TerminalOperator(
            source=(str(i) for i in xrange(666)), dtype=str
        )

        basis_set = OperatorSet(operators=(basis_op_1, basis_op_2, basis_op_3))
        terminal_set = OperatorSet(
            operators=(terminal_op_1, terminal_op_2, terminal_op_3)
        )

        types_possibility_table = build_types_possibility_table(
            basis_set=basis_set,
            terminal_set=terminal_set,
            max_depth=2,
            grow_=True
        )

        self.assertSetEqual(
            types_possibility_table[0], set(o.dtype for o in terminal_set.union(basis_set))
        )

        self.assertSetEqual(
            types_possibility_table[1], set(o.dtype for o in basis_set.union(terminal_set))
        )


class TestFull(unittest.TestCase):

    def test_full(self):
        raise NotImplementedError()  # FIXME


class TestGrow(unittest.TestCase):

    def test_grow(self):
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
