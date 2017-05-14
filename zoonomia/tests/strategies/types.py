"""This module defines builders for `Hypothesis <https://hypothesis.works>`_
strategies sufficient for constructing objects found in :mod:`zoonomia.types` to
use in Hypothesis tests.

"""

import hypothesis.strategies as st

from zoonomia.types import Type, ParametrizedType, GenericType


def name_types(min_size=1, average_size=5):
    """Build a text strategy representing type names.

    :param min_size: Minimum string length.
    :type min_size: int

    :param average_size: Maximum string length.
    :type average_size: int

    :return: A text strategy.
    :rtype: hypothesis.strategies.SearchStrategy

    """
    return st.text(min_size=min_size, average_size=average_size)


def meta_types(min_size=1, average_size=5):
    """Build a text strategy representing type metadata.

    :param min_size: Minimum string length.
    :type min_size: int

    :param average_size: Maximum string length.
    :type min_size: int

    :return: A text strategy.
    :rtype: hypothesis.strategies.SearchStrategy

    """
    return st.text(min_size=min_size, average_size=average_size)


def types(name_ts, meta_ts):
    """Build a :class:`zoonomia.types.Type` strategy.

    :param name_ts: A text strategy representing type names.
    :type name_ts: hypothesis.strategies.SearchStrategy

    :param meta_ts: A text strategy representing type metadata.
    :type meta_ts: hypothesis.strategies.SearchStrategy

    :return: A types strategy.
    :rtype: hypothesis.strategies.SearchStrategy

    """
    return st.builds(Type, **{'name': name_ts, 'meta': meta_ts})


def default_types():
    return types(name_ts=name_types(), meta_ts=meta_types())


def distinct_types(distinct_ts):
    """Build a :class:`zoonomia.types.Type` strategy yielding two types per call
    where the two types are guaranteed to be distinct.

    :param distinct_ts:
        A :class:`zoonomia.types.Type` strategy from which distinct pairs of
        types will be drawn.

    :type distinct_ts: hypothesis.strategies.SearchStrategy

    :return:
        A fixed dictionary strategy yielding two distinct types under the keys
        'type1' and 'another_type'.

    :rtype: hypothesis.strategies.SearchStrategy

    """
    return st.fixed_dictionaries(
        {'type1': distinct_ts, 'another_type': distinct_ts}
    ).filter(lambda d: (
        d['type1'].name != d['another_type'].name
        and d['type1'].meta != d['another_type'].meta
    ))


def contained_types(contained_ts, min_size=0, max_size=5):
    """Build a strategy representing the contained types of a
    :class:`zoonomia.types.GenericType`.

    :param contained_ts:
        A strategy supplying :class:`zoonomia.types.Type` or
        :class:`zoonomia.type.GenericType` instances.

    :type contained_ts: hypothesis.strategies.SearchStrategy

    :param min_size: The minimum number of contained types.
    :type min_size: int

    :param max_size: The maximum number of contained types.
    :type max_size: int

    :return:
        A frozensets strategy representing the contained types of a generic
        type.

    :rtype: hypothesis.strategies.SearchStrategy

    """
    return st.frozensets(
        elements=contained_ts,
        min_size=min_size,
        max_size=max_size
    )


def generic_types(name_ts, meta_ts, contained_ts):
    """Build a :class:`zoonomia.types.GenericType` strategy.

    :param name_ts: A text strategy representing type names.
    :type name_ts: hypothesis.strategies.SearchStrategy

    :param meta_ts: A text strategy representing type metadata.
    :type meta_ts: hypothesis.strategies.SearchStrategy

    :param contained_ts:
        A strategy representing contained types. This strategy should
        emit `zoonomia.types.Type` instances.

    :type contained_ts: hypothesis.strategies.SearchStrategy

    :return: A strategy yielding generic types.
    :rtype: hypothesis.strategies.SearchStrategy

    """
    return st.recursive(
        base=st.builds(
            GenericType,
            **{
                'name': name_ts,
                'meta': meta_ts,
                'contained_types': contained_types(contained_ts)
            }
        ),
        extend=lambda children: st.builds(
            GenericType,
            **{
                'name': name_ts,
                'meta': meta_ts,
                'contained_types': contained_types(contained_ts | children)
            }
        ),
        max_leaves=3
    )


def default_generic_types():
    return generic_types(
        name_ts=name_types(),
        meta_ts=meta_types(),
        contained_ts=default_types()
    )


def distinct_generic_types(generic_ts):
    """Build a :class:`zoonomia.types.GenericType` strategy yielding two types
    per call where the two types are guaranteed to be distinct.

    :param generic_ts: A generic types strategy.
    :type generic_ts: hypothesis.strategies.SearchStrategy

    :return: A fixed dictionaries strategy yielding distinct generic types under
    the keys 'type1' and 'another_type'.

    :rtype: hypothesis.strategies.SearchStrategy

    """
    return st.fixed_dictionaries(
        {'type1': generic_ts, 'another_type': generic_ts}
    ).filter(lambda d: (
        d['type1'].name != d['another_type'].name
        and d['type1'].meta != d['another_type'].meta
        and d['type1'].contained_types != d['another_type'].contained_types
    ))


def parameter_types(parameter_ts, min_size=0, max_size=5):
    """Build a strategy of :class:`zoonomia.types.Type` and
    :class:`zoonomia.types.GenericType` instances which represent parameter
    types for :class:`zoonomia.types.ParametrizedType`.

    :param parameter_ts: A parameter types strategy.
    :type parameter_ts: hypothesis.strategies.SearchStrategy

    :param min_size: The minimum number of parameter types.
    :type min_size: int

    :param max_size: The maximum number of parameter types.
    :type max_size: int

    :return: A strategy containing tuples of parameter types.
    :rtype: hypothesis.strategies.SearchStrategy

    """
    return st.builds(
        tuple,
        st.lists(
            elements=parameter_ts,
            min_size=min_size,
            max_size=max_size
        )
    )


def default_parameter_types():
    return parameter_types(
        parameter_ts=generic_types(
            name_ts=name_types(),
            meta_ts=meta_types(),
            contained_ts=contained_types(
                contained_ts=types(
                    name_ts=name_types(), meta_ts=meta_types()
                )
            )
        ) | types(name_ts=name_types(), meta_ts=meta_types()))


def parametrized_types(name_ts, meta_ts, base_ts, parameter_ts):
    """Build a strategy of :class:`zoonomia.types.ParametrizedType` instances.

    :param name_ts: A text strategy representing type names.
    :type name_ts: hypothesis.strategies.SearchStrategy

    :param meta_ts: A text strategy representing type metadata.
    :type meta_ts: hypothesis.strategies.SearchStrategy

    :param base_ts:
        A strategy yielding :class:`zoonomia.types.Type` and
        :class:`zoonomia.types.GenericType` instances representing base types.

    :type base_ts: hypothesis.strategies.SearchStrategy

    :param parameter_ts:
        A strategy representing parameter types. This strategy should emit
        `zoonomia.types.GenericType` and `zoonomia.types.Type` instances.

    :type base_ts: hypothesis.strategies.SearchStrategy

    :return: A strategy of parametrized types.
    :rtype: hypothesis.strategies.SearchStrategy

    """
    return st.recursive(
        base=st.builds(
            ParametrizedType,
            **{
                'name': name_ts,
                'meta': meta_ts,
                'base_type': base_ts,
                'parameter_types': parameter_types(parameter_ts)
            }
        ),
        extend=lambda children: st.builds(
            ParametrizedType,
            **{
                'name': name_ts,
                'meta': meta_ts,
                'base_type': base_ts,
                'parameter_types': parameter_types(parameter_ts | children)
            }
        ),
        max_leaves=3
    )


def default_parametrized_types():
    return parametrized_types(
        name_ts=name_types(),
        meta_ts=meta_types(),
        base_ts=default_generic_types() | default_types(),
        parameter_ts=default_parameter_types()
    )


def distinct_parametrized_types(parametrized_ts):
    """Build a :class:`zoonomia.types.ParametrizedType` strategy yielding two
    types per call where the two types are guaranteed to be distinct.

    :param parametrized_ts: A strategy yielding parametrized types.
    :type parametrized_ts: hypothesis.strategies.SearchStrategy

    :return:
        A fixed dictionary strategy yielding two distinct parametrized types
        under the keys 'type1' and 'another_type'.

    :rtype: hypothesis.strategies.SearchStrategy

    """
    return st.fixed_dictionaries(
        {'type1': parametrized_ts, 'another_type': parametrized_ts}
    ).filter(lambda d: (
        d['type1'].name != d['another_type'].name
        and d['type1'].meta != d['another_type'].meta
        and d['type1'].base_type != d['another_type'].base_type
        and d['type1'].parameter_types != d['another_type'].parameter_types
    ))
