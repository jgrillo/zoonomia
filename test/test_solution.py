import unittest

from zoonomia.solution import (
    verify_closure_property, BasisOperator, TerminalOperator, OperatorSet,
    Objective, Fitness, Solution
)


class TestVerifyClosureProperty(unittest.TestCase):

    def test_verify_closure_property(self):
        def add(left, right): return left + right

        int_basis = BasisOperator(func=add, signature=(int, int), dtype=int)
        float_basis = BasisOperator(
            func=add, signature=(float, float), dtype=float
        )

        int_terminal = TerminalOperator(source=xrange(666), dtype=int)
        float_terminal = TerminalOperator(
            source=(float(i) for i in xrange(666)), dtype=float
        )

        terminal_set = OperatorSet(operators=(int_terminal, float_terminal))

        result = verify_closure_property(

        )


class TestBasisOperator(unittest.TestCase):

    def test_basis_operator(self):
        raise NotImplementedError()  # FIXME


class TestTerminalOperator(unittest.TestCase):

    def test_terminal_operator(self):
        raise NotImplementedError()  # FIXME


class TestOperatorSet(unittest.TestCase):

    def test_operator_set(self):
        raise NotImplementedError()  # FIXME


class TestObjective(unittest.TestCase):

    def test_evaluate(self):
        raise NotImplementedError()  # FIXME


class TestFitness(unittest.TestCase):

    def test_equals(self):
        raise NotImplementedError()  # FIXME


class TestSolution(unittest.TestCase):

    def test_solution(self):
        raise NotImplementedError()  # FIXME
