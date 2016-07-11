import unittest
import mock

from concurrent.futures import ThreadPoolExecutor

from zoonomia.types import Type, GenericType, ParametrizedType
from zoonomia.lang import (
    Symbol, Call, Operator, OperatorSet
)


class TestSymbol(unittest.TestCase):

    def test_symbol_equals(self):
        """Test that two Symbols are equal if their hashes are equal."""
        symbol1 = Symbol(name='symbol', dtype=Type(name='type'))
        symbol2 = Symbol(name='symbol', dtype=Type(name='type'))

        self.assertEqual(hash(symbol1), hash(symbol2))
        self.assertEqual(symbol1, symbol2)
        self.assertEqual(symbol2, symbol1)

    def test_symbol_not_equals(self):
        """Test that two Symbols are unequal if their hashes are unequal."""
        symbol1 = Symbol(name='symbol1', dtype=Type(name='type1'))
        symbol2 = Symbol(name='symbol2', dtype=Type(name='type2'))

        self.assertNotEqual(hash(symbol1), hash(symbol2))
        self.assertNotEqual(symbol1, symbol2)
        self.assertNotEqual(symbol2, symbol1)


class TestCall(unittest.TestCase):

    def test_call_equals(self):
        """Test that two Calls are equal if their hashes are equal."""
        some_type = Type(name='some_type')

        symbol1 = Symbol(name='symbol', dtype=some_type)
        operator1 = Operator(symbol=symbol1)
        call1 = Call(
            target=Symbol(name='target', dtype=some_type),
            operator=operator1,
            args=()
        )

        symbol2 = Symbol(name='symbol', dtype=some_type)
        operator2 = Operator(symbol=symbol2)
        call2 = Call(
            target=Symbol(name='target', dtype=some_type),
            operator=operator2,
            args=()
        )

        self.assertEqual(hash(call1), hash(call2))
        self.assertEqual(call1, call2)
        self.assertEqual(call2, call1)

    def test_call_not_equals(self):
        """Test that two Calls are unequal if their hashes are unequal."""
        some_type = Type(name='some_type')

        symbol1 = Symbol(name='symbol1', dtype=some_type)
        operator1 = Operator(symbol=symbol1)
        call1 = Call(
            target=Symbol(name='target1', dtype=some_type),
            operator=operator1,
            args=()
        )

        symbol2 = Symbol(name='symbol2', dtype=some_type)
        operator2 = Operator(symbol=symbol2)
        call2 = Call(
            target=Symbol(name='target2', dtype=some_type),
            operator=operator2,
            args=()
        )

        self.assertNotEqual(hash(call1), hash(call2))
        self.assertNotEqual(call1, call2)
        self.assertNotEqual(call2, call1)


class TestOperator(unittest.TestCase):

    def test_basis_operator_attributes(self):
        """Test that a BasisOperator instance has attributes which are
        references to the data passed into the initializer.

        """
        int_type = Type(name='int')
        signature = (int_type, int_type)
        dtype = int_type

        basis_operator = Operator(
            symbol=Symbol(name='add', dtype=dtype), signature=signature
        )

        self.assertIs(basis_operator.symbol.name, 'add')
        self.assertIs(basis_operator.signature, signature)
        self.assertIs(basis_operator.dtype, dtype)

    def test_operator_hash(self):
        """Test that two Operators which are distinct yet refer to the same
        data have identical hashes.

        """
        int_type = Type(name='int')
        signature = (int_type, int_type)
        dtype = int_type

        basis_operator_1 = Operator(
            symbol=Symbol(name='add', dtype=dtype), signature=signature
        )

        basis_operator_2 = Operator(
            symbol=Symbol(name='add', dtype=dtype), signature=signature
        )

        self.assertEqual(hash(basis_operator_1), hash(basis_operator_2))

    def test_operator_equals(self):
        """Test that two Operators which are distinct yet refer to the same
        data are equal.

        """
        int_type = Type(name='int')
        signature = (int_type, int_type)
        dtype = int_type

        basis_operator_1 = Operator(
            symbol=Symbol(name='add', dtype=dtype), signature=signature
        )

        basis_operator_2 = Operator(
            symbol=Symbol(name='add', dtype=dtype), signature=signature
        )

        self.assertEqual(basis_operator_1, basis_operator_2)
        self.assertEqual(basis_operator_2, basis_operator_1)

    def test_operator_not_equals(self):
        """Test that two Operators which do not refer to the same data are
        unequal.

        """
        int_type = Type(name='int')
        float_type = Type(name='float')
        signature = (int_type, int_type)

        basis_operator_1 = Operator(
            symbol=Symbol(name='add', dtype=int_type), signature=signature
        )

        basis_operator_2 = Operator(
            symbol=Symbol(name='add', dtype=float_type), signature=signature
        )

        self.assertNotEqual(basis_operator_1, basis_operator_2)
        self.assertNotEqual(basis_operator_2, basis_operator_1)

    def test_operator_call_raises_when_target_present_and_args_absent(self):
        terminal_operator = Operator(
            symbol=Symbol(name='term_1', dtype=Type(name='int'))
        )
        self.assertRaises(TypeError, terminal_operator, {'target': 'target'})

    def test_operator_call_raises_when_target_absent_and_args_present(self):
        int_type = Type(name='int')
        basis_operator = Operator(
            symbol=Symbol(
                name='add', dtype=int_type), signature=(int_type, int_type)
        )
        self.assertRaises(
            TypeError, basis_operator, {'args': ('arg',)}
        )

    def test_operator_call_returns_expected_call_object(self):
        """Test that calling a basis operator like a function produces the
        corresponding Call object.

        """
        int_type = Type(name='int')
        signature = (int_type, int_type)
        dtype = int_type

        basis_operator = Operator(
            symbol=Symbol(name='add', dtype=dtype), signature=signature
        )

        terminal_operator_1 = Operator(
            symbol=Symbol(name='term_1', dtype=dtype)
        )
        terminal_operator_2 = Operator(
            symbol=Symbol(name='term_2', dtype=dtype)
        )
        call = Call(
            target=terminal_operator_1(),
            operator=basis_operator,
            args=(terminal_operator_2,)
        )
        target = Symbol(name='target', dtype=dtype)

        self.assertEqual(
            Call(
                target=target,
                operator=basis_operator,
                args=(terminal_operator_2(), call)
            ),
            basis_operator(
                target=target, args=(terminal_operator_2(), call)
            )
        )


class TestOperatorSet(unittest.TestCase):

    def test_operator_set_lookup(self):
        """Test that an OperatorSet acts legit wrt lookups by *dtype*."""
        int_type = Type(name='int')
        str_type = Type(name='str')

        basis_op_1 = Operator(
            symbol=Symbol(name='add', dtype=int_type),
            signature=(int_type, int_type)
        )
        basis_op_2 = Operator(
            symbol=Symbol(name='add', dtype=str_type),
            signature=(str_type, str_type)
        )

        terminal_op_1 = Operator(symbol=Symbol(name='term1', dtype=int_type))
        terminal_op_2 = Operator(symbol=Symbol(name='term2', dtype=str_type))

        basis_set = OperatorSet(operators=(basis_op_1, basis_op_2))
        terminal_set = OperatorSet(operators=(terminal_op_1, terminal_op_2))

        self.assertSetEqual({basis_op_1, basis_op_2}, basis_set.operators)

        self.assertSetEqual(basis_set[int_type], {basis_op_1})

        self.assertSetEqual(basis_set[str_type], {basis_op_2})

        self.assertSetEqual(
            {terminal_op_1, terminal_op_2}, terminal_set.operators
        )

        self.assertSetEqual(terminal_set[int_type], {terminal_op_1})
        self.assertSetEqual(terminal_set[str_type], {terminal_op_2})

    def test_operator_set_implicit_lookup(self):
        """Test that a lookup on an OperatorSet works when the OperatorSet
        isn't explicitly initialized with some type, yet one of its elements
        contains that type.

        """
        int_type = Type(name='Int')
        float_type = Type(name='Float')

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

        collection_of_numbers_type = ParametrizedType(
            name='Collection<Number>',
            base_type=collection_type,
            parameter_types=(number_type,)
        )

        # collection_of_numbers_type can be resolved to collection_type
        self.assertIn(collection_of_numbers_type, collection_type)

        terminal_operator_0 = Operator(
            symbol=Symbol(
                name='terminal_operator_0', dtype=collection_type
            ),
            signature=()
        )
        terminal_operator_1 = Operator(
            symbol=Symbol(
                name='terminal_operator_0', dtype=collection_of_numbers_type
            ),
            signature=()
        )
        operator_set = OperatorSet(operators=(terminal_operator_0,))

        with ThreadPoolExecutor(max_workers=100) as pool:
            futures = [
                pool.submit(
                    lambda: (
                        operator_set[terminal_operator_0.dtype],
                        operator_set[terminal_operator_1.dtype]
                    )
                ) for _ in xrange(1000)
            ]

            for fut in futures:
                result = fut.result()
                self.assertIs(terminal_operator_0, result[0])
                self.assertIs(terminal_operator_1, result[1])

    def test_operator_set_union(self):
        """Test that the union of two OperatorSets behaves as expected with
        respect to lookups by *dtype* and *signature*.

        """
        int_type = Type(name='int')
        str_type = Type(name='str')

        basis_op_1 = Operator(
            symbol=Symbol(name='add', dtype=int_type),
            signature=(int_type, int_type)
        )
        basis_op_2 = Operator(
            symbol=Symbol(name='add', dtype=str_type),
            signature=(str_type, str_type)
        )

        terminal_op_1 = Operator(symbol=Symbol(name='term1', dtype=int_type))
        terminal_op_2 = Operator(symbol=Symbol(name='term2', dtype=str_type))

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
            basis_union_terminal[int_type], terminal_union_basis[int_type]
        )

        self.assertSetEqual(
            basis_union_terminal[int_type], {basis_op_1, terminal_op_1}
        )

        self.assertSetEqual(
            basis_union_terminal[str_type], terminal_union_basis[str_type]
        )

        self.assertSetEqual(
            basis_union_terminal[str_type], {basis_op_2, terminal_op_2}
        )

    def test_operator_set_iter(self):
        """Test that an iterator over an OperatorSet yields the same items as
        an iterator over its *operators* attribute.

        """
        int_type = Type(name='int')

        basis_op_1 = Operator(
            symbol=Symbol(name='add', dtype=int_type),
            signature=(int_type, int_type)
        )

        terminal_op_1 = Operator(symbol=Symbol(name='term1', dtype=int_type))

        operator_set = OperatorSet(operators=(basis_op_1, terminal_op_1))

        self.assertItemsEqual(
            operator_set.operators, iter(operator_set)
        )
