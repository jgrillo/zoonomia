"""This module defines builders for `Hypothesis <https://hypothesis.works>`_
strategies sufficient for constructing objects found in :mod:`zoonomia.lang` to
use in Hypothesis tests.

"""

import hypothesis.strategies as st

from zoonomia.lang import Symbol, Call, Operator, OperatorTable

from zoonomia.tests.strategies.types import (
    name_types, default_types, default_generic_types, default_parametrized_types
)


def symbols(name_ts, dtype_ts):
    """Build a :class:`zoonomia.lang.Symbol` strategy.

    :param name_ts: A text strategy representing type names.
    :type name_ts: hypothesis.strategies.SearchStrategy

    :param dtype_ts:
        A strategy of :class:`zoonomia.types.Type`,
        :class:`zoonomia.types.GenericType`, and
        :class:`zoonomia.types.ParametrizedType` instances.

    :type dtype_ts: hypothesis.strategies.SearchStrategy

    :return: A symbol strategy.
    :rtype: hypothesis.strategies.SearchStrategy

    """
    return st.builds(Symbol, **{'name': name_ts, 'dtype': dtype_ts})


def default_symbols():
    """Build a :class:`zoonomia.lang.Symbol` strategy using defaults defined in
    :mod:`zoonomia.tests.strategies.types`.

    :return: A symbol strategy.
    :rtype: hypothesis.strategies.SearchStrategy

    """
    return symbols(
        name_ts=name_types(),
        dtype_ts=(
            default_types() | default_generic_types()
            | default_parametrized_types()
        )
    )


def distinct_symbols(symbol_ts):
    """Build a :class:`zoonomia.lang.Symbol` strategy yielding two symbols per
    call where the two symbols are guaranteed to be distinct.

    :param symbol_ts: A strategy of symbols.
    :type symbol_ts: hypothesis.strategies.SearchStrategy

    :return:
        A fixed dictionary strategy yielding two distinct symbols under the keys
        'symbol1' and 'another_symbol'.

    :rtype: hypothesis.strategies.SearchStrategy

    """
    return st.fixed_dictionaries(
        {'symbol1': symbol_ts, 'another_symbol': symbol_ts}
    ).filter(lambda d: (
        d['symbol1'].name != d['another_symbol'].name
        and d['symbol1'].dtype != d['another_symbol'].dtype
    ))


def signatures(parameter_ts, min_size=0, max_size=5):
    """Build a strategy of tuples of :class:`zoonomia.types.Type`,
    :class:`zoonomia.types.GenericType`, and
    :class:`zoonomia.types.ParametrizedType` instances.

    :param parameter_ts:
        A strategy of :class:`zoonomia.types.Type`,
        :class:`zoonomia.types.GenericType`, and
        :class:`zoonomia.types.ParametrizedType` instances.

    :type parameter_ts: hypothesis.strategies.SearchStrategy

    :param min_size: Minimum signature length.
    :type min_size: int

    :param max_size: Maximum signature length.
    :type max_size: int

    :return: A signatures strategy.
    :rtype: hypothesis.strategies.SearchStrategy

    """
    return st.builds(
        tuple,
        st.lists(
            elements=parameter_ts, min_size=min_size, max_size=max_size
        )
    )


def default_signatures():
    """Build a signatures strategy using defaults from
    :mod:`zoonomia.tests.strategies.types`.

    :return: A signatures strategy.
    :rtype: hypothesis.strategies.SearchStrategy

    """
    return signatures(
        parameter_ts=(
            default_types() | default_generic_types()
            | default_parametrized_types()
        )
    )


def operators(symbol_ts, signature_ts):
    """Build an :class:`zoonomia.lang.Operator` strategy.

    :param symbol_ts: A symbols strategy.
    :type symbol_ts: hypothesis.strategies.SearchStrategy

    :param signature_ts: A signatures strategy.
    :type signature_ts: hypothesis.strategies.SearchStrategy

    :return: An operator strategy.
    :rtype: hypothesis.strategies.SearchStrategy

    """
    return st.builds(
        Operator, **{'symbol': symbol_ts, 'signature': signature_ts}
    )


def default_operators():
    """Build an operator strategy using defaults defined by
    :func:`default_symbols` and :func:`default_signatures`.

    :return: An operator strategy.
    :rtype: hypothesis.strategies.SearchStrategy

    """
    return operators(
        symbol_ts=default_symbols(), signature_ts=default_signatures()
    )


def distinct_operators(operator_ts):
    """Build a :class:`zoonomia.lang.Operator` strategy yielding two operators
    per call where the two operators are guaranteed to be distinct.

    :param operator_ts: An operator strategy.
    :type operator_ts: hypothesis.strategies.SearchStrategy

    :return:
        A fixed dictionary strategy yielding two distinct symbols under the keys
        'operator1' and 'another_operator'.

    :rtype: hypothesis.strategies.SearchStrategy

    """
    return st.fixed_dictionaries(
        {'operator1': operator_ts, 'another_operator': operator_ts}
    ).filter(lambda d: (
        d['operator1'].symbol != d['another_operator'].symbol
        and d['operator1'].signature != d['another_operator'].signature
    ))


def call_args(symbol_ts, min_size=0, max_size=5):
    """Build a strategy of tuples of :class:`zoonomia.lang.Symbol` instances
    representing arguments to a :class:`zoonomia.lang.Call`.

    :param symbol_ts: A symbols strategy.
    :type symbol_ts: hypothesis.strategies.SearchStrategy

    :param min_size: Minimum number of args.
    :type min_size: int

    :param max_size: Maximum number of args.
    :type max_size: int

    :return: An args strategy.
    :rtype: hypothesis.strategies.SearchStrategy

    """
    return st.builds(
        tuple,
        st.lists(
            elements=symbol_ts, min_size=min_size, max_size=max_size
        )
    )


def default_call_args():
    """Build an args strategy using defaults defined in :func:`default_symbols`.

    :return: An args strategy.
    :rtype: hypothesis.strategies.SearchStrategy

    """
    return call_args(symbol_ts=default_symbols())


def calls(target_ts, operator_ts, args_ts):
    """Build a :class:`zoonomia.lang.Call` strategy.

    :param target_ts: A symbols strategy.
    :type target_ts: hypothesis.strategies.SearchStrategy

    :param operator_ts: An operators strategy.
    :type operator_ts: hypothesis.strategies.SearchStrategy

    :param args_ts: An args strategy.
    :type args_ts: hypothesis.strategies.SearchStrategy

    :return: A calls strategy.
    :rtype: hypothesis.strategies.SearchStrategy

    """
    return st.builds(  # apparently py.test doesn't like 'target' keyword here
        Call, *(target_ts, operator_ts, args_ts)  # so we use *args instead.
    )


def default_calls():
    """Build a calls strategy using defaults defined in :func:`default_symbols`,
    :func:`default_operators`, and :func:`default_call_args`.

    :return: A calls strategy.
    :rtype: hypothesis.strategies.SearchStrategy

    """
    return calls(
        target_ts=default_symbols(),
        operator_ts=default_operators(),
        args_ts=default_call_args()
    )


def distinct_calls(call_ts):
    """Build a :class:`zoonomia.lang.Call` strategy yielding two calls per emit
    where the two calls are guaranteed to be distinct.

    :param call_ts: A calls strategy.
    :type call_ts: hypothesis.strategies.SearchStrategy

    :return:
        A fixed dictionary strategy yielding two distinct calls under the keys
        'call1' and 'another_call'.

    :rtype: hypothesis.strategies.SearchStrategy

    """
    return st.fixed_dictionaries(
        {'call1': call_ts, 'another_call': call_ts}
    ).filter(lambda d: (
        d['call1'].target != d['another_call'].target
        and d['call1'].operator != d['another_call'].operator
        and d['call1'].args != d['another_call'].args
    ))


def operator_tables(operator_ts, min_size=0, max_size=5):
    """Build a :class:`zoonomia.lang.OperatorTable` strategy.

    :param operator_ts: An operators strategy.
    :type operator_ts: hypothesis.strategies.SearchStrategy

    :param min_size: Minimum number of operators.
    :type min_size: int

    :param max_size: Maximum number of operators.
    :type max_size: int

    :return: An operator table strategy.
    :rtype: hypothesis.strategies.SearchStrategy

    """
    return st.builds(
        OperatorTable,
        **{
            'operators': st.lists(
                elements=operator_ts, min_size=min_size, max_size=max_size
            )
        }
    )


def default_operator_tables():
    """Build an operator table strategy using defaults defined in
    :func:`default_operators`.

    :return: An operator table strategy.
    :rtype: hypothesis.strategies.SearchStrategy

    """
    return operator_tables(operator_ts=default_operators())


def distinct_operator_tables(operator_tables_ts):
    """Build a :class:`zoonomia.lang.OperatorTable` strategy yielding two
    operator tables per call where the two tables are guaranteed to be distinct.

    :param operator_tables_ts: An operator table strategy.
    :type operator_tables_ts: hypothesis.strategies.SearchStrategy

    :return:
        A fixed dictionary strategy yielding two distinct operator tables under
        the keys 'table1' and 'another_table'.

    :rtype: hypothesis.strategies.SearchStrategy

    """
    return st.fixed_dictionaries(
        {'table1': operator_tables_ts, 'another_table': operator_tables_ts}
    ).filter(lambda d: (
        d['table1'].operators != d['another_table'].operators
    ))
