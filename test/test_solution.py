import unittest

from zoonomia.solution import (
    verify_closure_property, Objective, Fitness, Solution
)


def test_verify_closure_property():
    verify_closure_property(None, None)  # FIXME


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
