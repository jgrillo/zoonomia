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

"""This module defines Zoonomia's type system. There are two main characters:

    1. *Type* -- a parameter-less generic type.
    2. *ParametrizedType* -- a parametrized generic type.

Some terminology:

    1. We say type A *contains* another type B if we can safely substitute
    values having type B in places expecting values of type A.
    2. We say a type D is *less general (more specific)* than type C if C
    *contains* D. We say type C is *more general than* type D if type D cannot
    contain type C.

*Type* is the most general kind of type. It subsumes *ParametrizedType*. Given
this hierarchy of generics, we can construct a parametrized
*collection_of_numbers* generic like this:

.. code-block:: python
    int_type = Type(name='Int')

    float_type = Type(name='Float')

    number_type = Type(
        name='Number', subtypes=(int_type, float_type)
    )

    list_type = Type(name='List')

    set_type = Type(name='Set')

    collection_type = Type(
        name='Collection', subtypes=frozenset((list_type, set_type))
    )

    collection_of_numbers_type = ParametrizedType(
        name='Collection<Number>',
        base_type=collection_type,
        parameters=(
            Parameter(dtype=number_type),
        )
    )

    collection_of_ints_type = ParametrizedType(
        name='Collection<Int>',
        base_type=collection_type,
        parameters=(
            Parameter(dtype=int_type),
        )
    )

In the above example, *Collection<Int>* is **not** contained by
*Collection<Number>* because Zoonomia's parametrized types are *invariant* by
default. However, both *Collection<Int>* and *Collection<Number>* are contained
by *Collection*. If a place expects values of type *Collection* we can safely
substitute values of type *Collection<Number>*, *Collection<Int>*, or
Collection<Float>. If a place expects values of type *Collection<Number>* we can
safely substitute values of type *Collection<Number>* only. However, Zoonomia
supports something like a declaration-site variance specifier:

.. code-block:: python
    covariant_collection_of_numbers = ParametrizedType(
        name='Collection<? extends Number>',
        base_type=collection_type,
        parameters=(
            Parameter(dtype=int_type, variance=Variance.COVARIANT)
        )
    )

    contravariant_collection_of_numbers = ParametrizedType(
        name='Collection<? super Number>',
        base_type=collection_type,
        parameters=(
            Parameter(dtype=int_type, variance=Variance.CONTRAVARIANT)
        )
    )

Now we have the happy circumstance that *Collection<? extends Number>* contains
*Collection<Number>*, *Collection<Float>*, and *Collection<Int>*. Moreover,
*Collection<? super Number>* contains nothing at all.

Zoonomia's tree mutation operators maintain the following invariant:

    Functions (i.e. `Func<T, R>`) must be *contravariant* in their inputs and
    *covariant* in their outputs. That is, a function of type *Func<T, R>* can
    be safely replaced with another function which accepts a more general type
    than *T* and emits a more specific type than *R*. In Java we would write
    `Function<? super T, ? extends R>` (if you are a Java programmer you may
    have seen this rule written as the acronym PECS: "Producer Extends Consumer
    Super").

Zoonomia will check that this function type invariant is maintained when each
node is inserted into a tree. Therefore you should be able to make Zoonomia's
type system play nicely with your target language, whatever that language may
be.

"""

from enum import Enum
from functools import lru_cache

TYPE_CACHE_SIZE = 16  # FIXME: tune


class TypeCheckError(Exception):
    """This exception is raised by code which uses types in this module if
    that code expects types to check and they fail to do so.

    """
    pass


class Type(object):
    __slots__ = ('name', 'subtypes', 'meta', '_hash')

    def __init__(self, name, subtypes=frozenset(), meta=None):
        """A generic type is constructed with a name and a frozenset of
        *subtypes*. The *subtypes* represent the set of possible types to which
        this generic can be safely resolved.

        :param name:
            The name of this type.

        :type name: str

        :param subtypes:
            The set of possible types that this Type can be resolved to.

        :type subtypes: frozenset(Type)

        :param meta:
            Some (optional) metadata to associate with this type.

        :type meta: object

        """
        self.name = name
        self.subtypes = subtypes
        self.meta = meta
        self._hash = hash(
            ('Type', self.name, self.subtypes, self.meta)
        )

    def __getstate__(self):
        return {
            'name': self.name,
            'subtypes': self.subtypes,
            'meta': self.meta
        }

    def __setstate__(self, state):
        self.__init__(state['name'], state['subtypes'], state['meta'])

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        if isinstance(other, Type):
            return (
                self.name == other.name and
                self.subtypes == other.subtypes and
                self.meta == other.meta
            )
        else:
            return NotImplemented

    @lru_cache(maxsize=TYPE_CACHE_SIZE, typed=True)
    def __contains__(self, candidate):
        """Check whether this type can be resolved to a type *candidate*.

        :param candidate:
            A candidate type.

        :type candidate: Type | ParametrizedType

        :raise TypeError: if *candidate* is not a Type or ParametrizedType.

        :return:
            True if the candidate type belongs to this generic type (i.e. if
            this type can be resolved to the candidate type), False otherwise.

        :rtype: bool

        """
        if isinstance(candidate, ParametrizedType):
            if candidate.base_type in self:
                return True
            else:
                return False
        elif isinstance(candidate, Type):
            if candidate == self:
                return True
            else:
                if any(candidate in t for t in self.subtypes):
                    return True
                elif (
                    len(candidate.subtypes) > 0 and all(
                        t in self for t in candidate.subtypes
                    )
                ):
                    return True
                else:
                    return False
        else:
            raise TypeError(
                'candidate must be a Type or ParametrizedType: {0}'.format(
                    repr(candidate)
                )
            )

    def __repr__(self):
        return 'Type(name={name}, subtypes={subtypes}, meta={meta})'.format(
            name=repr(self.name),
            subtypes=repr(self.subtypes),
            meta=repr(self.meta)
        )


class Variance(Enum):
    COVARIANT = 'COVARIANT'
    INVARIANT = 'INVARIANT'
    CONTRAVARIANT = 'CONTRAVARIANT'


class Parameter(object):
    __slots__ = ('dtype', 'variance', '_hash')

    def __init__(self, dtype, variance=Variance.INVARIANT):
        """A Parameter is constructed with a *dtype* and a *variance*.
        Parameters are invariant by default.

        :param dtype: The type of this parameter.
        :type dtype: Type | ParametrizedType

        :param variance: The variance of this parameter.
        :type variance: Variance

        """
        self.dtype = dtype
        self.variance = variance
        self._hash = hash((self.dtype, self.variance))

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        return self.dtype == other.type and self.variance == other.variance

    def __repr__(self):
        return 'Parameter(type={type}, variance={variance})'.format(
            type=self.dtype, variance=self.variance
        )


class ParametrizedType(object):
    __slots__ = (
        'name', 'base_type', 'parameters', 'meta', '_hash'
    )

    def __init__(self, name, base_type, parameters, meta=None):
        """A ParametrizedType is constructed with a *name*, a *base_type*, one
        or more *parameters*, and (optionally) some *metadata*.

        :param name: The name of this type.
        :type name: str

        :param base_type: The base type of this generic.
        :type base_type: Type

        :param parameters: The parameters of this generic.
        :type parameters: tuple[Parameter]

        :param meta: Some (optional) metadata to associate with this type.
        :type meta: object
        
        :raises TypeError: if :param:`parameter_types` has length < 1.

        """
        self.name = name
        self.base_type = base_type

        if len(parameters) < 1:
            raise TypeError(
                'Cannot construct a ParametrizedType with empty parameter_types'
            )

        self.parameters = parameters
        self.meta = meta
        self._hash = hash((
            'ParametrizedType',
            self.name,
            self.base_type,
            self.parameters,
            self.meta
        ))

    def __getstate__(self):
        return {
            'name': self.name,
            'base_type': self.base_type,
            'parameter_types': self.parameters,
            'meta': self.meta
        }

    def __setstate__(self, state):
        self.__init__(
            state['name'],
            state['base_type'],
            state['parameter_types'],
            state['meta']
        )

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        if isinstance(other, ParametrizedType):
            return (
                self.name == other.name and
                self.base_type == other.base_type and
                self.parameters == other.parameters and
                self.meta == other.meta
            )
        else:
            return NotImplemented

    @lru_cache(maxsize=TYPE_CACHE_SIZE, typed=True)
    def __contains__(self, candidate):  # FIXME: deal with variance
        """Check whether this type can be resolved to a type *candidate*.

        :param candidate: A candidate type.
        :type candidate: Type | ParametrizedType

        :raise TypeError: if *candidate* is not a Type or ParametrizedType.

        :return:
            True if the candidate type belongs to this generic type (i.e. if
            this type can be resolved to the candidate type), False otherwise.

        :rtype: bool

        """
        if isinstance(candidate, ParametrizedType):
            if candidate == self:
                return True
            elif (
                candidate.base_type in self.base_type and
                len(candidate.parameters) == len(self.parameters)
                and len(candidate.parameters) > 0
            ):
                if all(c in t for c, t in zip(
                    candidate.parameters, self.parameters
                )):
                    return True
                else:
                    return False
            else:
                return False
        elif isinstance(candidate, Type):
            return False
        else:
            raise TypeError(
                'candidate must be a Type or ParametrizedType: {0}'.format(
                    repr(candidate)
                )
            )

    def __repr__(self):
        return (
            'ParametrizedType(name={name}, base_type={base_type}, '
            'parameter_types={parameter_types}, meta={meta})'
        ).format(
            name=repr(self.name),
            base_type=repr(self.base_type),
            parameter_types=repr(self.parameters),
            meta=repr(self.meta)
        )
