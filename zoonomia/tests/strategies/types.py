#   Copyright 2015-2018 Jesse C. Grillo
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

"""This module defines builders for `Hypothesis <https://hypothesis.works>`_
strategies sufficient for constructing objects found in :mod:`zoonomia.types` to
use in Hypothesis tests.

"""

import hypothesis.strategies as st

from zoonomia.types import Type, Parameter, Variance, ParametrizedType


def names(min_size=1, average_size=5):
    """Build a text strategy representing type names.

    :param min_size: Minimum string length.
    :type min_size: int

    :param average_size: Maximum string length.
    :type average_size: int

    :return: A text strategy.
    :rtype: hypothesis.strategies.SearchStrategy

    """
    return st.text(min_size=min_size, average_size=average_size)


def metas(min_size=1, average_size=5):
    """Build a text strategy representing type metadata.

    :param min_size: Minimum string length.
    :type min_size: int

    :param average_size: Maximum string length.
    :type min_size: int

    :return: A text strategy.
    :rtype: hypothesis.strategies.SearchStrategy

    """
    return st.text(min_size=min_size, average_size=average_size)


def subtypes(types_strategy, min_size=0, max_size=5):
    """Build a strategy representing the subtypes of a
    :class:`zoonomia.types.Type`.

    :param types_strategy:
        A strategy supplying :class:`zoonomia.types.Type` instances

    :type types_strategy: hypothesis.strategies.SearchStrategy

    :param min_size: The minimum number of subtypes.
    :type min_size: int

    :param max_size: The maximum number of subtypes.
    :type max_size: int

    :return: A frozensets strategy representing the subtypes of a generic type.

    :rtype: hypothesis.strategies.SearchStrategy

    """
    return st.frozensets(
        elements=types_strategy,
        min_size=min_size,
        max_size=max_size
    )


def types(names_strategy, metas_strategy):
    """Build a :class:`zoonomia.types.Type` strategy.

    :param names_strategy: A text strategy representing type names.
    :type names_strategy: hypothesis.strategies.SearchStrategy

    :param metas_strategy: A text strategy representing type metadata.
    :type metas_strategy: hypothesis.strategies.SearchStrategy

    :return: A strategy yielding generic types.
    :rtype: hypothesis.strategies.SearchStrategy

    """
    return st.recursive(
        base=st.builds(
            Type,
            **{
                'name': names_strategy,
                'meta': metas_strategy,
            }
        ),
        extend=lambda children: st.builds(
            Type,
            **{
                'name': names_strategy,
                'meta': metas_strategy,
                'subtypes': subtypes(children)
            }
        ),
        max_leaves=5
    )


def default_types():
    return types(
        names_strategy=names(),
        metas_strategy=metas()
    )


def distinct_types(types_strategy):
    """Build a :class:`zoonomia.types.Type` strategy yielding two types
    per call where the two types are guaranteed to be distinct.

    :param types_strategy: A generic types strategy.
    :type types_strategy: hypothesis.strategies.SearchStrategy

    :return: A fixed dictionaries strategy yielding distinct generic types under
    the keys 'type1' and 'another_type'.

    :rtype: hypothesis.strategies.SearchStrategy

    """
    return st.fixed_dictionaries(
        {'type1': types_strategy, 'another_type': types_strategy}
    ).filter(lambda d: (
        d['type1'].name != d['another_type'].name
        and d['type1'].meta != d['another_type'].meta
        and d['type1'].subtypes != d['another_type'].subtypes
    ))


def parameters(types_strategy, variances_strategy, min_size=1, max_size=5):
    """Build a strategy of :class:`zoonomia.types.Parameter` for
    :class:`zoonomia.types.ParametrizedType`.

    :param types_strategy: A strategy of parameter types.
    :type types_strategy: hypothesis.strategies.SearchStrategy

    :param variances_strategy: A strategy of variances
    :type variances_strategy: hypothesis.strategies.SearchStrategy

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
            elements=st.builds(
                Parameter,
                **{
                    'dtype': types_strategy,
                    'variance': variances_strategy
                }
            ),
            min_size=min_size,
            max_size=max_size
        )
    )


def default_parameters():
    return parameters(
        types_strategy=default_types(),
        variances_strategy=st.sampled_from(
            (Variance.CONTRAVARIANT, Variance.COVARIANT, Variance.INVARIANT)
        )
    )


def distinct_parameters(parameters_strategy):
    """Build a :class:`zoonomia.types.Parameter` strategy yielding two
    parameters per call where the two parameters are guaranteed to be distinct.

    :param parameters_strategy: A strategy which yields parameters.
    :type parameters_strategy: hypothesis.strategies.SearchStrategy

    :return: A fixed dictionaries strategy yielding distinct parameters under
    the keys 'parameter1' and 'another_parameter'.

    :rtype: hypothesis.strategies.SearchStrategy

    """
    return st.fixed_dictionaries(
        {
            'parameter1': parameters_strategy,
            'another_parameter': parameters_strategy
        }
    ).filter(lambda d: (
        d['parameter1'].dtype != d['another_parameter'].dtype
        and d['parameter1'].variance != d['another_parameter'].variance
    ))


def parametrized_types(
    names_strategy,
    metas_strategy,
    base_types_strategy,
    parameter_types_strategy,
    variances_strategy
):
    """Build a strategy of :class:`zoonomia.types.ParametrizedType` instances.

    :param names_strategy: A text strategy representing type names.
    :type names_strategy: hypothesis.strategies.SearchStrategy

    :param metas_strategy: A text strategy representing type metadata.
    :type metas_strategy: hypothesis.strategies.SearchStrategy

    :param base_types_strategy:
        A strategy yielding :class:`zoonomia.types.Type` instances representing
        base types.

    :type base_types_strategy: hypothesis.strategies.SearchStrategy

    :param parameter_types_strategy:
        A strategy yielding :class:`zoonomia.types.Type` instances representing
        parameter types.

    :type parameter_types_strategy: hypothesis.strategies.SearchStrategy

    :param variances_strategy:
        A strategy of :class:`zoonomia.types.Parameter` instances.

    :type variances_strategy: hypothesis.strategies.SearchStrategy

    :return: A strategy of parametrized types.
    :rtype: hypothesis.strategies.SearchStrategy

    """
    return st.recursive(
        base=st.builds(
            ParametrizedType,
            **{
                'name': names_strategy,
                'meta': metas_strategy,
                'base_type': base_types_strategy,
                'parameters': parameters(
                    types_strategy=parameter_types_strategy,
                    variances_strategy=variances_strategy
                )
            }
        ),
        extend=lambda children: st.builds(
            ParametrizedType,
            **{
                'name': names_strategy,
                'meta': metas_strategy,
                'base_type': base_types_strategy,
                'parameters': parameters(
                    types_strategy=parameter_types_strategy | children,
                    variances_strategy=variances_strategy
                )
            }
        ),
        max_leaves=5
    )


def default_parametrized_types():
    return parametrized_types(
        names_strategy=names(),
        metas_strategy=metas(),
        base_types_strategy=default_types(),
        parameter_types_strategy=default_parameters(),
        variances_strategy=st.sampled_from(
            (Variance.CONTRAVARIANT, Variance.COVARIANT, Variance.INVARIANT)
        )
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
        and d['type1'].parameters != d['another_type'].parameters
    ))
