#   Copyright 2015-2017 Jesse C. Grillo
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import unittest
import pickle

import hypothesis.strategies as st

from hypothesis import given, settings, HealthCheck
from concurrent.futures import ThreadPoolExecutor

from zoonomia.types import Type, ParametrizedType
from zoonomia.lang import (
    Symbol, Call, Operator, OperatorTable
)

from zoonomia.tests.strategies.lang import (
    default_symbols, distinct_symbols, default_operators, distinct_operators,
    default_calls, distinct_calls, default_operator_tables,
    distinct_operator_tables
)


class TestSymbol(unittest.TestCase):
    BUFFER_SIZE = 8192 * 4
    SUPPRESSED_HEALTH_CHECKS = (HealthCheck.too_slow,)

    @given(
        st.shared(default_symbols(), key='test_symbol_equals_reflexive'),
        st.shared(default_symbols(), key='test_symbol_equals_reflexive')
    )
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_equals_reflexive(self, symbol1, symbol2):
        """Test that an object equals itself."""
        self.assertIs(symbol1, symbol2)
        self.assertEqual(symbol1, symbol2)

    @given(st.data())
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_equals_symmetric(self, data):
        """Test that for objects :math:`\{x,y\}, x = y \iff y = x`."""
        d = data.draw(distinct_symbols(symbol_ts=default_symbols()))
        symbol1 = d['symbol1']
        another_symbol = d['another_symbol']

        symbol2 = Symbol(name=symbol1.name, dtype=symbol1.dtype)

        self.assertEqual(symbol1, symbol2)
        self.assertEqual(symbol2, symbol1)

        self.assertNotEqual(symbol1, another_symbol)
        self.assertNotEqual(another_symbol, symbol1)

    @given(
        st.shared(default_symbols(), key='test_symbol_equals_transitive'),
        st.shared(default_symbols(), key='test_symbol_equals_transitive').map(
            lambda s: Symbol(name=s.name, dtype=s.dtype)
        ),
        st.shared(default_symbols(), key='test_symbol_equals_transitive').map(
            lambda s: Symbol(name=s.name, dtype=s.dtype)
        )
    )
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_equals_transitive(self, symbol1, symbol2, symbol3):
        """Test that for objects :math:`\{x,y,z\}, x = y, y = z \iff x = z`."""
        self.assertEqual(symbol1, symbol2)
        self.assertEqual(symbol2, symbol3)
        self.assertEqual(symbol1, symbol3)

    @given(st.data())
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_equals_consistent(self, data):
        """Test that repeated equals calls return the same value."""
        d = data.draw(distinct_symbols(symbol_ts=default_symbols()))
        symbol1 = d['symbol1']
        another_symbol = d['another_symbol']

        symbol2 = Symbol(name=symbol1.name, dtype=symbol1.dtype)

        self.assertEqual(symbol1, symbol2)
        self.assertEqual(symbol1, symbol2)
        self.assertEqual(symbol1, symbol2)

        self.assertNotEqual(symbol1, another_symbol)
        self.assertNotEqual(symbol1, another_symbol)
        self.assertNotEqual(symbol1, another_symbol)

    @given(default_symbols())
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_hash_consistent(self, symbol1):
        """Test that repeated hash calls yield the same value."""
        hash1 = hash(symbol1)

        self.assertEqual(hash1, hash(symbol1))
        self.assertEqual(hash1, hash(symbol1))
        self.assertEqual(hash1, hash(symbol1))

    @given(
        st.shared(default_symbols(), key='test_symbol_hash_equals'),
        st.shared(default_symbols(), key='test_symbol_hash_equals').map(
            lambda s: Symbol(name=s.name, dtype=s.dtype)
        )
    )
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_hash_equals(self, symbol1, symbol2):
        """Test that when two objects are equal their hashes are equal."""
        self.assertEqual(symbol1, symbol2)
        self.assertEqual(hash(symbol1), hash(symbol2))

    @given(default_symbols())
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_symbol_pickle(self, symbol1):
        """Test that a Symbol instance can be pickled and unpickled using the
        0 protocol and the -1 protocol.

        """
        pickled_symbol = pickle.dumps(symbol1, -1)
        unpickled_symbol = pickle.loads(pickled_symbol)

        self.assertEqual(symbol1, unpickled_symbol)
        self.assertEqual(hash(symbol1), hash(unpickled_symbol))

        pickled_symbol = pickle.dumps(symbol1, 0)
        unpickled_symbol = pickle.loads(pickled_symbol)

        self.assertEqual(symbol1, unpickled_symbol)
        self.assertEqual(hash(symbol1), hash(unpickled_symbol))


class TestCall(unittest.TestCase):
    BUFFER_SIZE = 8192 * 4
    SUPPRESSED_HEALTH_CHECKS = (HealthCheck.too_slow,)

    @given(
        st.shared(default_calls(), key='test_call_equals_reflexive'),
        st.shared(default_calls(), key='test_call_equals_reflexive')
    )
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_equals_reflexive(self, call1, call2):
        """Test that an object equals itself."""
        self.assertIs(call1, call2)
        self.assertEqual(call1, call2)

    @given(st.data())
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_equals_symmetric(self, data):
        """Test that for objects :math:`\{x,y\}, x = y \iff y = x`."""
        d = data.draw(distinct_calls(call_ts=default_calls()))
        call1 = d['call1']
        another_call = d['another_call']

        call2 = Call(
            target=call1.target, operator=call1.operator, args=call1.args
        )

        self.assertEqual(call1, call2)
        self.assertEqual(call2, call1)

        self.assertNotEqual(call1, another_call)
        self.assertNotEqual(another_call, call1)

    @given(
        st.shared(default_calls(), key='test_call_equals_transitive'),
        st.shared(default_calls(), key='test_call_equals_transitive').map(
            lambda c: Call(target=c.target, operator=c.operator, args=c.args)
        ),
        st.shared(default_calls(), key='test_call_equals_transitive').map(
            lambda c: Call(target=c.target, operator=c.operator, args=c.args)
        )
    )
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_equals_transitive(self, call1, call2, call3):
        """Test that for objects :math:`\{x,y,z\}, x = y, y = z \iff x = z`."""
        self.assertEqual(call1, call2)
        self.assertEqual(call2, call3)
        self.assertEqual(call1, call3)

    @given(st.data())
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_equals_consistent(self, data):
        """Test that repeated equals calls return the same value."""
        d = data.draw(distinct_calls(call_ts=default_calls()))
        call1 = d['call1']
        another_call = d['another_call']

        call2 = Call(
            target=call1.target, operator=call1.operator, args=call1.args
        )

        self.assertEqual(call1, call2)
        self.assertEqual(call1, call2)
        self.assertEqual(call1, call2)

        self.assertNotEqual(call1, another_call)
        self.assertNotEqual(call1, another_call)
        self.assertNotEqual(call1, another_call)

    @given(default_calls())
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_hash_consistent(self, call1):
        """Test that repeated hash calls yield the same value."""
        hash1 = hash(call1)

        self.assertEqual(hash1, hash(call1))
        self.assertEqual(hash1, hash(call1))
        self.assertEqual(hash1, hash(call1))

    @given(
        st.shared(default_calls(), key='test_call_hash_equals'),
        st.shared(default_calls(), key='test_call_hash_equals').map(
            lambda c: Call(target=c.target, operator=c.operator, args=c.args)
        )
    )
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_hash_equals(self, call1, call2):
        """Test that when two objects are equal their hashes are equal."""
        self.assertEqual(call1, call2)
        self.assertEqual(hash(call1), hash(call2))

    @given(default_calls())
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_call_pickle(self, call1):
        """Test that a Call instance can be pickled and unpickled using the
        0 protocol and the -1 protocol.

        """
        pickled_call = pickle.dumps(call1, -1)
        unpickled_call = pickle.loads(pickled_call)

        self.assertEqual(call1, unpickled_call)
        self.assertEqual(hash(call1), hash(unpickled_call))

        pickled_call = pickle.dumps(call1, 0)
        unpickled_call = pickle.loads(pickled_call)

        self.assertEqual(call1, unpickled_call)
        self.assertEqual(hash(call1), hash(unpickled_call))


class TestOperator(unittest.TestCase):
    BUFFER_SIZE = 8192 * 4
    SUPPRESSED_HEALTH_CHECKS = (HealthCheck.too_slow,)

    @given(
        st.shared(default_operators(), key='test_operator_equals_reflexive'),
        st.shared(default_operators(), key='test_operator_equals_reflexive')
    )
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_equals_reflexive(self, operator1, operator2):
        """Test that an object equals itself."""
        self.assertIs(operator1, operator2)
        self.assertEqual(operator1, operator2)

    @given(st.data())
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_equals_symmetric(self, data):
        """Test that for objects :math:`\{x,y\}, x = y \iff y = x`."""
        d = data.draw(distinct_operators(operator_ts=default_operators()))
        operator1 = d['operator1']
        another_operator = d['another_operator']

        operator2 = Operator(
            symbol=operator1.symbol, signature=operator1.signature
        )

        self.assertEqual(operator1, operator2)
        self.assertEqual(operator2, operator1)

        self.assertNotEqual(operator1, another_operator)
        self.assertNotEqual(another_operator, operator1)

    @given(
        st.shared(default_operators(), key='test_operator_equals_transitive'),
        st.shared(
            default_operators(), key='test_operator_equals_transitive'
        ).map(
            lambda o: Operator(symbol=o.symbol, signature=o.signature)
        ),
        st.shared(
            default_operators(), key='test_operator_equals_transitive'
        ).map(
            lambda o: Operator(symbol=o.symbol, signature=o.signature)
        )
    )
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_equals_transitive(self, operator1, operator2, operator3):
        """Test that for objects :math:`\{x,y,z\}, x = y, y = z \iff x = z`."""
        self.assertEqual(operator1, operator2)
        self.assertEqual(operator2, operator3)
        self.assertEqual(operator1, operator3)

    @given(st.data())
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_equals_consistent(self, data):
        """Test that repeated equals calls return the same value."""
        d = data.draw(distinct_operators(operator_ts=default_operators()))
        operator1 = d['operator1']
        another_operator = d['another_operator']

        operator2 = Operator(
            symbol=operator1.symbol, signature=operator1.signature
        )

        self.assertEqual(operator1, operator2)
        self.assertEqual(operator1, operator2)
        self.assertEqual(operator1, operator2)

        self.assertNotEqual(operator1, another_operator)
        self.assertNotEqual(operator1, another_operator)
        self.assertNotEqual(operator1, another_operator)

    @given(default_operators())
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_hash_consistent(self, operator1):
        """Test that repeated hash calls yield the same value."""
        hash1 = hash(operator1)

        self.assertEqual(hash1, hash(operator1))
        self.assertEqual(hash1, hash(operator1))
        self.assertEqual(hash1, hash(operator1))

    @given(
        st.shared(default_operators(), key='test_operator_hash_equals'),
        st.shared(default_operators(), key='test_operator_hash_equals').map(
            lambda o: Operator(symbol=o.symbol, signature=o.signature)
        )
    )
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_hash_equals(self, operator1, operator2):
        """Test that when two objects are equal their hashes are equal."""
        self.assertEqual(operator1, operator2)
        self.assertEqual(hash(operator1), hash(operator2))

    @given(default_operators())
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_operator_pickle(self, operator1):
        """Test that an Operator inctance can be pickled and unpickled using
        the 0 protocol and the -1 protocol.

        """
        pickled_operator = pickle.dumps(operator1, -1)
        unpickled_operator = pickle.loads(pickled_operator)

        self.assertEqual(operator1, unpickled_operator)
        self.assertEqual(hash(operator1), hash(unpickled_operator))

        pickled_operator = pickle.dumps(operator1, 0)
        unpickled_operator = pickle.loads(pickled_operator)

        self.assertEqual(operator1, unpickled_operator)
        self.assertEqual(hash(operator1), hash(unpickled_operator))

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

    @given(
        default_symbols(),
        st.builds(
            tuple,
            st.lists(elements=default_operators(), min_size=0, max_size=5)
        ),
        default_operators()
    )
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_operator_call_returns_expected_call_object(  # FIXME: bad data
        self, target1, args1, operator1
    ):
        """Test that calling a basis operator like a function produces the
        corresponding Call object.

        """
        self.assertEqual(
            Call(target=target1, operator=operator1, args=args1),
            operator1(target=target1, args=args1)
        )


class TestOperatorTable(unittest.TestCase):
    BUFFER_SIZE = 8192 * 4
    SUPPRESSED_HEALTH_CHECKS = (HealthCheck.too_slow,)

    @given(
        st.shared(default_operator_tables(), key='test_ot_equals_reflexive'),
        st.shared(default_operator_tables(), key='test_ot_equals_reflexive')
    )
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_equals_reflexive(self, table1, table2):
        """Test that an object equals itself."""
        self.assertIs(table1, table2)
        self.assertEqual(table1, table2)

    @given(st.data())
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_equals_symmetric(self, data):
        """Test that for objects :math:`\{x,y\}, x = y \iff y = x`."""
        d = data.draw(distinct_operator_tables(
            operator_tables_ts=default_operator_tables()
        ))
        table1 = d['table1']
        another_table = d['another_table']

        table2 = OperatorTable(operators=table1.operators)

        self.assertEqual(table1, table2)
        self.assertEqual(table2, table1)

        self.assertNotEqual(table1, another_table)
        self.assertNotEqual(another_table, table1)

    @given(
        st.shared(default_operator_tables(), key='test_ot_eq_transitive'),
        st.shared(default_operator_tables(), key='test_ot_eq_transitive').map(
            lambda t: OperatorTable(operators=t.operators)
        ),
        st.shared(default_operator_tables(), key='test_ot_eq_transitive').map(
            lambda t: OperatorTable(operators=t.operators)
        )
    )
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_equals_transitive(self, table1, table2, table3):
        """Test that for objects :math:`\{x,y,z\}, x = y, y = z \iff x = z`."""
        self.assertEqual(table1, table2)
        self.assertEqual(table2, table3)
        self.assertEqual(table1, table3)

    @given(st.data())
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_equals_consistent(self, data):
        """Test that repeated equals calls return the same value."""
        d = data.draw(distinct_operator_tables(
            operator_tables_ts=default_operator_tables()
        ))
        table1 = d['table1']
        another_table = d['another_table']

        table2 = OperatorTable(operators=table1.operators)

        self.assertEqual(table1, table2)
        self.assertEqual(table1, table2)
        self.assertEqual(table1, table2)

        self.assertNotEqual(table1, another_table)
        self.assertNotEqual(table1, another_table)
        self.assertNotEqual(table1, another_table)

    @given(default_operator_tables())
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_hash_consistent(self, table1):
        """Test that repeated hash calls yield the same value."""
        hash1 = hash(table1)

        self.assertEqual(hash1, hash(table1))
        self.assertEqual(hash1, hash(table1))
        self.assertEqual(hash1, hash(table1))

    @given(
        st.shared(default_operator_tables(), key='test_ot_hash_equals'),
        st.shared(default_operator_tables(), key='test_ot_hash_equals').map(
            lambda t: OperatorTable(operators=t.operators)
        )
    )
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_hash_equals(self, table1, table2):
        """Test that when two objects are equal their hashes are equal."""
        self.assertEqual(hash(table1), hash(table2))
        self.assertEqual(table1, table2)

    @given(default_operator_tables())
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_operator_table_pickle(self, table1):
        """Test that an OperatorTable instance can be pickled and unpickled using
        the 0 protocol and the -1 protocol.

        """
        pickled_operator_table = pickle.dumps(table1, -1)
        unpickled_operator_table = pickle.loads(pickled_operator_table)

        self.assertEqual(table1, unpickled_operator_table)
        self.assertEqual(hash(table1), hash(unpickled_operator_table))

        pickled_operator_table = pickle.dumps(table1, 0)
        unpickled_operator_table = pickle.loads(pickled_operator_table)

        self.assertEqual(table1, unpickled_operator_table)
        self.assertEqual(hash(table1), hash(unpickled_operator_table))

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
        collection_type = Type(
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
        which is not a Type or ParametrizedType is attempted.

        """
        int_type = Type(name='int')
        str_type = Type(name='str')
        list_type = Type(name='List')
        collection_type = Type(
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

        collection_type = Type(
            name='Collection',
            contained_types=frozenset((list_type, set_type))
        )

        number_type = Type(
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

        collection_type = Type(
            name='Collection',
            contained_types=frozenset((list_type, set_type))
        )
        number_type = Type(
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
                ) for _ in range(1000)
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
        number_type = Type(
            name='Number',
            contained_types=frozenset((int_type, float_type))
        )
        collection_type = Type(
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
        number_type = Type(
            name='Number',
            contained_types=frozenset((int_type, float_type))
        )
        collection_type = Type(
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
        a key which is not a Type or ParametrizedType.

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

    @given(default_operator_tables())
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_operator_table_iter(self, table1):
        """Test that an iterator over an OperatorTable yields the same items as
        an iterator over its *operators* attribute.

        """
        self.assertSequenceEqual(
            table1.operators, frozenset(iter(table1)), seq_type=frozenset
        )
