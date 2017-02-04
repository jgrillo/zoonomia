import unittest
import pickle

from concurrent.futures import ThreadPoolExecutor

from zoonomia.types import Type, GenericType, ParametrizedType
from zoonomia.lang import (
    Symbol, Call, Operator, OperatorTable
)


class TestSymbol(unittest.TestCase):

    def test_equals_reflexive(self):
        """Test that an object equals itself."""
        symbol1 = Symbol(name='symbol', dtype=Type(name='type'))
        symbol2 = symbol1

        self.assertIs(symbol1, symbol2)
        self.assertEqual(symbol1, symbol2)

    def test_equals_symmetric(self):
        """Test that for objects :math:`\{x,y\}, x = y \iff y = x`."""
        symbol1 = Symbol(name='symbol', dtype=Type(name='name'))
        symbol2 = Symbol(name='symbol', dtype=Type(name='name'))
        another_symbol = Symbol(name='another_symbol', dtype=Type(name='name'))

        self.assertFalse(symbol1 is symbol2)

        self.assertEqual(symbol1, symbol2)
        self.assertEqual(symbol2, symbol1)

        self.assertFalse(symbol1 is another_symbol)

        self.assertNotEqual(symbol1, another_symbol)
        self.assertNotEqual(another_symbol, symbol1)

    def test_equals_transitive(self):
        """Test that for objects :math:`\{x,y,z\}, x = y, y = z \iff x = z`."""
        symbol1 = Symbol(name='symbol', dtype=Type(name='type'))
        symbol2 = Symbol(name='symbol', dtype=Type(name='type'))
        symbol3 = Symbol(name='symbol', dtype=Type(name='type'))

        self.assertFalse(symbol1 is symbol2)
        self.assertFalse(symbol2 is symbol3)
        self.assertFalse(symbol1 is symbol3)

        self.assertEqual(symbol1, symbol2)
        self.assertEqual(symbol2, symbol3)
        self.assertEqual(symbol1, symbol3)

    def test_equals_consistent(self):
        """Test that repeated equals calls return the same value."""
        symbol1 = Symbol(name='symbol', dtype=Type(name='type'))
        symbol2 = Symbol(name='symbol', dtype=Type(name='type'))
        another_symbol = Symbol(name='another_symbol', dtype=Type(name='name'))

        self.assertFalse(symbol1 is symbol2)

        self.assertEqual(symbol1, symbol2)
        self.assertEqual(symbol1, symbol2)
        self.assertEqual(symbol1, symbol2)

        self.assertFalse(symbol1 is another_symbol)

        self.assertNotEqual(symbol1, another_symbol)
        self.assertNotEqual(symbol1, another_symbol)
        self.assertNotEqual(symbol1, another_symbol)

    def test_hash_consistent(self):
        """Test that repeated hash calls yield the same value."""
        symbol1 = Symbol(name='symbol', dtype=Type(name='type'))
        hash1 = hash(symbol1)

        self.assertEqual(hash1, hash(symbol1))
        self.assertEqual(hash1, hash(symbol1))
        self.assertEqual(hash1, hash(symbol1))

    def test_hash_equals(self):
        """Test that when two objects are equal their hashes are equal."""
        symbol1 = Symbol(name='symbol', dtype=Type(name='type'))
        symbol2 = Symbol(name='symbol', dtype=Type(name='type'))

        self.assertEqual(symbol1, symbol2)
        self.assertEqual(hash(symbol1), hash(symbol2))

    def test_symbol_pickle(self):
        """Test that a Symbol instance can be pickled and unpickled using the
        default protocol.

        """
        symbol = Symbol(name='symbol', dtype=Type(name='type'))

        pickled_symbol = pickle.dumps(symbol)
        unpickled_symbol = pickle.loads(pickled_symbol)

        self.assertEqual(symbol, unpickled_symbol)


class TestCall(unittest.TestCase):

    def test_equals_reflexive(self):
        """Test that an object equals itself."""
        some_type = Type(name='some_type')

        symbol1 = Symbol(name='symbol', dtype=some_type)
        target1 = Symbol(name='target', dtype=some_type)
        operator1 = Operator(symbol=symbol1)
        call1 = Call(
            target=target1,
            operator=operator1,
            args=()
        )
        call2 = call1

        self.assertIs(call1, call2)
        self.assertEqual(call1, call2)

    def test_equals_symmetric(self):
        """Test that for objects :math:`\{x,y\}, x = y \iff y = x`."""
        some_type = Type(name='some_type')

        symbol1 = Symbol(name='symbol', dtype=some_type)
        target1 = Symbol(name='target', dtype=some_type)
        operator1 = Operator(symbol=symbol1)
        call1 = Call(
            target=target1,
            operator=operator1,
            args=()
        )

        symbol2 = Symbol(name='symbol', dtype=some_type)
        target2 = Symbol(name='target', dtype=some_type)
        operator2 = Operator(symbol=symbol2)
        call2 = Call(
            target=target2,
            operator=operator2,
            args=()
        )

        another_symbol = Symbol(name='another_symbol', dtype=some_type)
        another_target = Symbol(name='another_target', dtype=some_type)
        another_operator = Operator(symbol=another_symbol)
        another_call = Call(
            target=another_target,
            operator=another_operator,
            args=()
        )

        self.assertFalse(call1 is call2)

        self.assertEqual(call1, call2)
        self.assertEqual(call2, call1)

        self.assertFalse(call1 is another_call)

        self.assertNotEqual(call1, another_call)
        self.assertNotEqual(another_call, call1)

    def test_equals_transitive(self):
        """Test that for objects :math:`\{x,y,z\}, x = y, y = z \iff x = z`."""
        some_type = Type(name='some_type')

        symbol1 = Symbol(name='symbol', dtype=some_type)
        target1 = Symbol(name='target', dtype=some_type)
        operator1 = Operator(symbol=symbol1)
        call1 = Call(
            target=target1,
            operator=operator1,
            args=()
        )

        symbol2 = Symbol(name='symbol', dtype=some_type)
        target2 = Symbol(name='target', dtype=some_type)
        operator2 = Operator(symbol=symbol2)
        call2 = Call(
            target=target2,
            operator=operator2,
            args=()
        )

        symbol3 = Symbol(name='symbol', dtype=some_type)
        target3 = Symbol(name='target', dtype=some_type)
        operator3 = Operator(symbol=symbol3)
        call3 = Call(
            target=target3,
            operator=operator3,
            args=()
        )

        self.assertFalse(call1 is call2)
        self.assertFalse(call2 is call3)
        self.assertFalse(call1 is call3)

        self.assertEqual(call1, call2)
        self.assertEqual(call2, call3)
        self.assertEqual(call1, call3)

    def test_equals_consistent(self):
        """Test that repeated equals calls return the same value."""
        some_type = Type(name='some_type')

        symbol1 = Symbol(name='symbol', dtype=some_type)
        target1 = Symbol(name='target', dtype=some_type)
        operator1 = Operator(symbol=symbol1)
        call1 = Call(
            target=target1,
            operator=operator1,
            args=()
        )

        symbol2 = Symbol(name='symbol', dtype=some_type)
        target2 = Symbol(name='target', dtype=some_type)
        operator2 = Operator(symbol=symbol2)
        call2 = Call(
            target=target2,
            operator=operator2,
            args=()
        )

        another_symbol = Symbol(name='another_symbol', dtype=some_type)
        another_target = Symbol(name='another_target', dtype=some_type)
        another_operator = Operator(symbol=another_symbol)
        another_call = Call(
            target=another_target,
            operator=another_operator,
            args=()
        )

        self.assertFalse(call1 is call2)

        self.assertEqual(call1, call2)
        self.assertEqual(call1, call2)
        self.assertEqual(call1, call2)

        self.assertFalse(call1 is another_call)

        self.assertNotEqual(call1, another_call)
        self.assertNotEqual(call1, another_call)
        self.assertNotEqual(call1, another_call)

    def test_hash_consistent(self):
        """Test that repeated hash calls yield the same value."""
        some_type = Type(name='some_type')

        symbol1 = Symbol(name='symbol', dtype=some_type)
        target1 = Symbol(name='target', dtype=some_type)
        operator1 = Operator(symbol=symbol1)
        call1 = Call(
            target=target1,
            operator=operator1,
            args=()
        )

        hash1 = hash(call1)

        self.assertEqual(hash1, hash(call1))
        self.assertEqual(hash1, hash(call1))
        self.assertEqual(hash1, hash(call1))

    def test_hash_equals(self):
        """Test that when two objects are equal their hashes are equal."""
        some_type = Type(name='some_type')

        symbol1 = Symbol(name='symbol', dtype=some_type)
        target1 = Symbol(name='target', dtype=some_type)
        operator1 = Operator(symbol=symbol1)
        call1 = Call(
            target=target1,
            operator=operator1,
            args=()
        )

        symbol2 = Symbol(name='symbol', dtype=some_type)
        target2 = Symbol(name='target', dtype=some_type)
        operator2 = Operator(symbol=symbol2)
        call2 = Call(
            target=target2,
            operator=operator2,
            args=()
        )

        self.assertEqual(call1, call2)
        self.assertEqual(hash(call1), hash(call2))

    def test_call_pickle(self):
        """Test that a Call instance can be pickled and unpickled using the
        default protocol.

        """
        some_type = Type(name='some_type')

        symbol = Symbol(name='symbol', dtype=some_type)
        operator = Operator(symbol=symbol)
        call = Call(
            target=Symbol(name='target', dtype=some_type),
            operator=operator,
            args=()
        )

        pickled_call = pickle.dumps(call)
        unpickled_call = pickle.loads(pickled_call)

        self.assertEqual(call, unpickled_call)


class TestOperator(unittest.TestCase):

    def test_equals_reflexive(self):
        """Test that an object equals itself."""
        int_type = Type(name='int')
        signature = (int_type, int_type)
        dtype = int_type

        basis_operator_1 = Operator(
            symbol=Symbol(name='add', dtype=dtype), signature=signature
        )

        basis_operator_2 = basis_operator_1

        self.assertIs(basis_operator_1, basis_operator_2)
        self.assertEqual(basis_operator_1, basis_operator_2)

    def test_equals_symmetric(self):
        """Test that for objects :math:`\{x,y\}, x = y \iff y = x`."""
        int_type = Type(name='int')
        signature = (int_type, int_type)
        dtype = int_type

        basis_operator_1 = Operator(
            symbol=Symbol(name='add', dtype=dtype), signature=signature
        )

        basis_operator_2 = Operator(
            symbol=Symbol(name='add', dtype=dtype), signature=signature
        )

        another_basis_operator = Operator(
            symbol=Symbol(name='another_add', dtype=dtype), signature=signature
        )

        self.assertFalse(basis_operator_1 is basis_operator_2)

        self.assertEqual(basis_operator_1, basis_operator_2)
        self.assertEqual(basis_operator_2, basis_operator_1)

        self.assertFalse(basis_operator_1 is another_basis_operator)

        self.assertNotEqual(basis_operator_1, another_basis_operator)
        self.assertNotEqual(another_basis_operator, basis_operator_1)

    def test_equals_transitive(self):
        """Test that for objects :math:`\{x,y,z\}, x = y, y = z \iff x = z`."""
        int_type = Type(name='int')
        signature = (int_type, int_type)
        dtype = int_type

        basis_operator_1 = Operator(
            symbol=Symbol(name='add', dtype=dtype), signature=signature
        )

        basis_operator_2 = Operator(
            symbol=Symbol(name='add', dtype=dtype), signature=signature
        )

        basis_operator_3 = Operator(
            symbol=Symbol(name='add', dtype=dtype), signature=signature
        )

        self.assertFalse(basis_operator_1 is basis_operator_2)
        self.assertFalse(basis_operator_2 is basis_operator_3)
        self.assertFalse(basis_operator_1 is basis_operator_3)

        self.assertEqual(basis_operator_1, basis_operator_2)
        self.assertEqual(basis_operator_2, basis_operator_3)
        self.assertEqual(basis_operator_1, basis_operator_3)

    def test_equals_consistent(self):
        """Test that repeated equals calls return the same value."""
        int_type = Type(name='int')
        signature = (int_type, int_type)
        dtype = int_type

        basis_operator_1 = Operator(
            symbol=Symbol(name='add', dtype=dtype), signature=signature
        )

        basis_operator_2 = Operator(
            symbol=Symbol(name='add', dtype=dtype), signature=signature
        )

        another_basis_operator = Operator(
            symbol=Symbol(name='another_add', dtype=dtype), signature=signature
        )

        self.assertFalse(basis_operator_1 is basis_operator_2)

        self.assertEqual(basis_operator_1, basis_operator_2)
        self.assertEqual(basis_operator_1, basis_operator_2)
        self.assertEqual(basis_operator_1, basis_operator_2)

        self.assertFalse(basis_operator_1 is another_basis_operator)

        self.assertNotEqual(basis_operator_1, another_basis_operator)
        self.assertNotEqual(basis_operator_1, another_basis_operator)
        self.assertNotEqual(basis_operator_1, another_basis_operator)

    def test_hash_consistent(self):
        """Test that repeated hash calls yield the same value."""
        int_type = Type(name='int')
        signature = (int_type, int_type)
        dtype = int_type

        basis_operator_1 = Operator(
            symbol=Symbol(name='add', dtype=dtype), signature=signature
        )

        hash1 = hash(basis_operator_1)

        self.assertEqual(hash1, hash(basis_operator_1))
        self.assertEqual(hash1, hash(basis_operator_1))
        self.assertEqual(hash1, hash(basis_operator_1))

    def test_hash_equals(self):
        """Test that when two objects are equal their hashes are equal."""
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
        self.assertEqual(hash(basis_operator_1), hash(basis_operator_2))

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

    def test_operator_pickle(self):
        """Test that an Operator inctance can be pickled and unpickled using
        the default protocol.

        """
        int_type = Type(name='int')
        signature = (int_type, int_type)
        dtype = int_type

        basis_operator = Operator(
            symbol=Symbol(name='add', dtype=dtype), signature=signature
        )

        pickled_operator = pickle.dumps(basis_operator)
        unpickled_operator = pickle.loads(pickled_operator)

        self.assertEqual(basis_operator, unpickled_operator)

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


class TestOperatorTable(unittest.TestCase):

    def test_equals_reflexive(self):
        """Test that an object equals itself."""
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

        operator_table_1 = OperatorTable(
            operators=(basis_op_1, basis_op_2, terminal_op_1, terminal_op_2)
        )
        operator_table_2 = operator_table_1

        self.assertIs(operator_table_1, operator_table_2)
        self.assertEqual(operator_table_1, operator_table_2)

    def test_equals_symmetric(self):
        """Test that for objects :math:`\{x,y\}, x = y \iff y = x`."""
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

        operator_table_1 = OperatorTable(
            operators=(basis_op_1, basis_op_2, terminal_op_1, terminal_op_2)
        )
        operator_table_2 = OperatorTable(
            operators=(basis_op_1, basis_op_2, terminal_op_1, terminal_op_2)
        )
        another_operator_table = OperatorTable(
            operators=(basis_op_1, terminal_op_1)
        )

        self.assertFalse(operator_table_1 is operator_table_2)

        self.assertEqual(operator_table_1, operator_table_2)
        self.assertEqual(operator_table_2, operator_table_1)

        self.assertFalse(operator_table_1 is another_operator_table)

        self.assertNotEqual(operator_table_1, another_operator_table)
        self.assertNotEqual(another_operator_table, operator_table_1)

    def test_equals_transitive(self):
        """Test that for objects :math:`\{x,y,z\}, x = y, y = z \iff x = z`."""
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

        operator_table_1 = OperatorTable(
            operators=(basis_op_1, basis_op_2, terminal_op_1, terminal_op_2)
        )
        operator_table_2 = OperatorTable(
            operators=(basis_op_1, basis_op_2, terminal_op_1, terminal_op_2)
        )
        operator_table_3 = OperatorTable(
            operators=(basis_op_1, basis_op_2, terminal_op_1, terminal_op_2)
        )

        self.assertFalse(operator_table_1 is operator_table_2)
        self.assertFalse(operator_table_2 is operator_table_3)
        self.assertFalse(operator_table_1 is operator_table_3)

        self.assertEqual(operator_table_1, operator_table_2)
        self.assertEqual(operator_table_2, operator_table_3)
        self.assertEqual(operator_table_1, operator_table_3)

    def test_equals_consistent(self):
        """Test that repeated equals calls return the same value."""
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

        operator_table_1 = OperatorTable(
            operators=(basis_op_1, basis_op_2, terminal_op_1, terminal_op_2)
        )
        operator_table_2 = OperatorTable(
            operators=(basis_op_1, basis_op_2, terminal_op_1, terminal_op_2)
        )
        another_operator_table = OperatorTable(
            operators=(basis_op_1, terminal_op_1)
        )

        self.assertFalse(operator_table_1 is operator_table_2)

        self.assertEqual(operator_table_1, operator_table_2)
        self.assertEqual(operator_table_1, operator_table_2)
        self.assertEqual(operator_table_1, operator_table_2)

        self.assertFalse(operator_table_1 is another_operator_table)

        self.assertNotEqual(operator_table_1, another_operator_table)
        self.assertNotEqual(operator_table_1, another_operator_table)
        self.assertNotEqual(operator_table_1, another_operator_table)

    def test_hash_consistent(self):
        """Test that repeated hash calls yield the same value."""
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

        operator_table_1 = OperatorTable(
            operators=(basis_op_1, basis_op_2, terminal_op_1, terminal_op_2)
        )
        hash1 = hash(operator_table_1)

        self.assertEqual(hash1, hash(operator_table_1))
        self.assertEqual(hash1, hash(operator_table_1))
        self.assertEqual(hash1, hash(operator_table_1))

    def test_hash_equals(self):
        """Test that when two objects are equal their hashes are equal."""
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

        operator_table_1 = OperatorTable(
            operators=(basis_op_1, basis_op_2, terminal_op_1, terminal_op_2)
        )
        operator_table_2 = OperatorTable(
            operators=(basis_op_1, basis_op_2, terminal_op_1, terminal_op_2)
        )

        self.assertEqual(hash(operator_table_1), hash(operator_table_2))
        self.assertEqual(operator_table_1, operator_table_2)

    def test_operator_table_pickle(self):
        """Test that an OperatorTable instance can be pickled and unpickled using
        the default protocol.

        """
        int_type = Type(name='int')
        str_type = Type(name='str')

        basis_op = Operator(
            symbol=Symbol(name='add', dtype=int_type),
            signature=(int_type, str_type)
        )
        terminal_op = Operator(symbol=Symbol(name='term', dtype=int_type))

        operator_table = OperatorTable(operators=(basis_op, terminal_op))

        pickled_operator_table = pickle.dumps(operator_table)
        unpickled_operator_table = pickle.loads(pickled_operator_table)

        self.assertEqual(operator_table, unpickled_operator_table)

    def test_operator_table_lookup(self):
        """Test that an OperatorTable acts legit wrt lookups by *dtype*."""
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

        basis_operators = OperatorTable(operators=(basis_op_1, basis_op_2))
        terminal_operators = OperatorTable(
            operators=(terminal_op_1, terminal_op_2)
        )

        self.assertSetEqual(
            {basis_op_1, basis_op_2}, basis_operators.operators
        )

        self.assertSetEqual(basis_operators[int_type], {basis_op_1})

        self.assertSetEqual(basis_operators[str_type], {basis_op_2})

        self.assertSetEqual(
            {terminal_op_1, terminal_op_2}, terminal_operators.operators
        )

        self.assertSetEqual(terminal_operators[int_type], {terminal_op_1})
        self.assertSetEqual(terminal_operators[str_type], {terminal_op_2})

    def test_operator_table_lookup_raises_KeyError_when_target_absent(self):
        """Test that an OperatorTable raises KeyError when attempting to lookup
        a *dtype* for which no operators exist in the OperatorTable whose
        *dtype* can be resolved to the given *dtype*.

        """
        int_type = Type(name='int')
        str_type = Type(name='str')
        list_type = Type(name='List')
        collection_type = GenericType(
            name='Collection', contained_types=frozenset((list_type,))
        )

        op_1 = Operator(
            symbol=Symbol(name='add', dtype=int_type),
            signature=(int_type, int_type)
        )
        op_2 = Operator(
            symbol=Symbol(name='add', dtype=str_type),
            signature=(str_type, str_type)
        )

        operators = OperatorTable(operators=(op_1, op_2))

        self.assertRaises(KeyError, lambda: operators[collection_type])

    def test_operator_table_lookup_raises_TypeError_when_improper_type(self):
        """Test that an OperatorTable raises TypeError when lookup by a key
        which is not a Type, GenericType, or ParametrizedType is attempted.

        """
        int_type = Type(name='int')
        str_type = Type(name='str')
        list_type = Type(name='List')
        collection_type = GenericType(
            name='Collection', contained_types=frozenset((list_type,))
        )
        collection_of_ints_type = ParametrizedType(
            name='Collection<int>',
            base_type=collection_type,
            parameter_types=(int_type,)
        )

        op_1 = Operator(
            symbol=Symbol(name='add', dtype=int_type),
            signature=(int_type, int_type)
        )
        op_2 = Operator(
            symbol=Symbol(name='add', dtype=str_type),
            signature=(str_type, str_type)
        )

        operators = OperatorTable(operators=(op_1, op_2))

        self.assertRaises(KeyError, lambda: operators[collection_type])
        self.assertRaises(KeyError, lambda: operators[collection_of_ints_type])
        self.assertRaises(TypeError, lambda: operators[1])

    def test_operator_table_lookup_multiple_matches(self):
        """Test that a lookup on an OperatorTable produces the set of all
        operators such that the lookup type can be resolved to each operator's
        return type.

        """
        int_type = Type(name='Int')
        float_type = Type(name='Float')
        string_type = Type(name='String')

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

        collection_of_floats_type = ParametrizedType(
            name='Collection<Float>',
            base_type=collection_type,
            parameter_types=(float_type,)
        )

        collection_of_strings_type = ParametrizedType(
            name='Collection<String>',
            base_type=collection_type,
            parameter_types=(string_type,)
        )

        # collection_of_numbers_type and collection_of_floats_type can be
        # resolved to collection_type, as can collection_of_strings_type
        self.assertIn(collection_of_numbers_type, collection_type)
        self.assertIn(collection_of_floats_type, collection_type)
        self.assertIn(collection_of_strings_type, collection_type)
        # collection_of_floats_type can be resolved to
        # collection_of_numbers_type, but collection_of_strings can't
        self.assertIn(collection_of_floats_type, collection_of_numbers_type)
        self.assertNotIn(
            collection_of_strings_type, collection_of_numbers_type
        )

        terminal_operator_0 = Operator(
            symbol=Symbol(
                name='terminal_operator_0', dtype=collection_type
            ),
            signature=()
        )
        terminal_operator_1 = Operator(
            symbol=Symbol(
                name='terminal_operator_1', dtype=collection_of_numbers_type
            ),
            signature=()
        )
        terminal_operator_2 = Operator(
            symbol=Symbol(
                name='terminal_operator_2', dtype=collection_of_floats_type
            ),
            signature=()
        )
        terminal_operator_3 = Operator(
            symbol=Symbol(
                name='terminal_operator_3', dtype=collection_of_strings_type
            )
        )

        operator_table = OperatorTable(
            operators=(
                terminal_operator_0, terminal_operator_1, terminal_operator_2,
                terminal_operator_3
            )
        )

        self.assertSetEqual(
            frozenset(
                (
                    terminal_operator_0, terminal_operator_1,
                    terminal_operator_2, terminal_operator_3
                )
            ),
            operator_table[collection_type]
        )

        self.assertSetEqual(
            frozenset((terminal_operator_1, terminal_operator_2)),
            operator_table[collection_of_numbers_type]
        )

        self.assertSetEqual(
            frozenset((terminal_operator_2,)),
            operator_table[collection_of_floats_type]
        )

        self.assertSetEqual(
            frozenset((terminal_operator_3,)),
            operator_table[collection_of_strings_type]
        )

    def test_operator_table_implicit_lookup(self):
        """Test that a lookup on an OperatorTable works when the OperatorTable
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

        terminal_operator_1 = Operator(
            symbol=Symbol(
                name='terminal_operator_1', dtype=collection_of_numbers_type
            ),
            signature=()
        )
        operator_table = OperatorTable(operators=(terminal_operator_1,))

        with ThreadPoolExecutor(max_workers=100) as pool:
            futures = [
                pool.submit(
                    lambda: (
                        operator_table[collection_type],
                        operator_table[terminal_operator_1.dtype]
                    )
                ) for _ in xrange(1000)
            ]

            for fut in futures:
                result = fut.result()
                self.assertIn(terminal_operator_1, result[0])
                self.assertIn(terminal_operator_1, result[1])

    def test_operator_table_contains(self):
        """Test that an OperatorTable contains operators whose return types can
        be resolved to the given key type.

        """
        int_type = Type(name='Int')
        float_type = Type(name='Float')
        list_type = Type(name='List')
        number_type = GenericType(
            name='Number',
            contained_types=frozenset((int_type, float_type))
        )
        collection_type = GenericType(
            name='Collection', contained_types=frozenset((list_type,))
        )
        collection_of_numbers_type = ParametrizedType(
            name='Collection<Number>',
            base_type=collection_type,
            parameter_types=(number_type,)
        )

        op_1 = Operator(
            symbol=Symbol(name='add', dtype=float_type),
            signature=(int_type, float_type)
        )
        op_2 = Operator(
            symbol=Symbol(name='add', dtype=collection_type),
            signature=(collection_type, collection_type)
        )

        operators = OperatorTable(operators=(op_1, op_2))

        self.assertIn(collection_type, operators)
        self.assertIn(float_type, operators)
        self.assertNotIn(collection_of_numbers_type, operators)

    def test_operator_table_implicit_contains(self):
        """Test that an OperatorTable contains operators whose return types can
        be resolved to the given key type, even when none of the operators has
        that explicit return type.

        """
        int_type = Type(name='Int')
        float_type = Type(name='Float')
        list_type = Type(name='List')
        number_type = GenericType(
            name='Number',
            contained_types=frozenset((int_type, float_type))
        )
        collection_type = GenericType(
            name='Collection', contained_types=frozenset((list_type,))
        )
        collection_of_numbers_type = ParametrizedType(
            name='Collection<Number>',
            base_type=collection_type,
            parameter_types=(number_type,)
        )

        op_1 = Operator(
            symbol=Symbol(name='add', dtype=float_type),
            signature=(int_type, float_type)
        )
        op_2 = Operator(
            symbol=Symbol(name='add', dtype=collection_of_numbers_type),
            signature=(collection_type, collection_type)
        )

        operators = OperatorTable(operators=(op_1, op_2))

        self.assertIn(number_type, operators)
        self.assertIn(collection_type, operators)

    def test_operator_table_contains_raises_TypeError_when_improper_key(self):
        """Test that OperatorTable raises TypeError when testing containment of
        a key which is not a Type, GenericType, or ParametrizedType.

        """
        int_type = Type(name='Int')
        float_type = Type(name='Float')

        op_1 = Operator(
            symbol=Symbol(name='add', dtype=float_type),
            signature=(float_type, float_type)
        )
        op_2 = Operator(
            symbol=Symbol(name='add', dtype=int_type),
            signature=(int_type, int_type)
        )

        operators = OperatorTable(operators=(op_1, op_2))

        self.assertRaises(TypeError, lambda: 1 in operators)

    def test_operator_table_union(self):
        """Test that the union of two OperatorTables behaves as expected with
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

        basis_operators = OperatorTable(operators=(basis_op_1, basis_op_2))
        terminal_operators = OperatorTable(
            operators=(terminal_op_1, terminal_op_2)
        )

        basis_union_terminal = basis_operators.union(terminal_operators)
        terminal_union_basis = terminal_operators.union(basis_operators)

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

    def test_operator_table_iter(self):
        """Test that an iterator over an OperatorTable yields the same items as
        an iterator over its *operators* attribute.

        """
        int_type = Type(name='int')

        basis_op_1 = Operator(
            symbol=Symbol(name='add', dtype=int_type),
            signature=(int_type, int_type)
        )

        terminal_op_1 = Operator(symbol=Symbol(name='term1', dtype=int_type))

        operator_table = OperatorTable(operators=(basis_op_1, terminal_op_1))

        self.assertItemsEqual(
            operator_table.operators, iter(operator_table)
        )
