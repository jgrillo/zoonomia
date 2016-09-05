import unittest
import pickle

from concurrent.futures import ThreadPoolExecutor

from zoonomia.types import Type, GenericType, ParametrizedType
from zoonomia.lang import (
    Symbol, Call, Operator, OperatorTable
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

    def test_symbol_pickle(self):
        """Test that a Symbol instance can be pickled and unpickled using the
        default protocol.

        """
        symbol = Symbol(name='symbol', dtype=Type(name='type'))

        pickled_symbol = pickle.dumps(symbol)
        unpickled_symbol = pickle.loads(pickled_symbol)

        self.assertEqual(symbol, unpickled_symbol)


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

    def test_operator_table_equals(self):
        """Test that two OperatorSets with equal hashes are equal."""
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
        self.assertEqual(operator_table_2, operator_table_1)

    def test_operator_table_not_equals(self):
        """Test that two OperatorSets with unequal hashes are not equal."""
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
            operators=(basis_op_1, basis_op_2, terminal_op_1)
        )
        operator_table_2 = OperatorTable(
            operators=(basis_op_1, basis_op_2, terminal_op_2)
        )

        self.assertNotEqual(hash(operator_table_1), hash(operator_table_2))
        self.assertNotEqual(operator_table_1, operator_table_2)
        self.assertNotEqual(operator_table_2, operator_table_1)

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
