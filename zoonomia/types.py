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
    2. We say type C is *more general than* type D if type D cannot contain
    type C.

*Type* is the most general kind of type. It subsumes *ParametrizedType*. Given
this hierarchy of generics, we can construct a parametrized
*collection_of_numbers* generic like this:

.. code-block:: python
    int_type = Type(name='Int')

    float_type = Type(name='Float')

    number_type = Type(
        name='Number', contained_types=(int_type, float_type)
    )

    list_type = Type(name='List')

    set_type = Type(name='Set')

    collection_type = Type(
        name='Collection', contained_types=frozenset((list_type, set_type))
    )

    collection_of_numbers_type = ParametrizedType(
        name='Collection<Number>',
        base_type=collection_type,
        parameter_types=(number_type,)
    )

    collection_of_ints_type = ParametrizedType(
        name='Collection<Int>',
        base_type=collection_type,
        parameter_types=(int_type,)
    )

In the above example, *Collection<Int>* is contained by *Collection<Number>*
because *Number* is a more general parameter type than *Int*. Both
*Collection<Int>* and *Collection<Number>* are contained by *Collection*. If a
place expects values of type *Collection* we can safely substitute values of
type *Collection<Number>*, or even values of type *Collection<Int>*!

"""

from functools import lru_cache

TYPE_CACHE_SIZE = 16  # FIXME: tune


class TypeCheckError(Exception):
    """This exception is raised by code which uses types in this module if
    that code expects types to check and they fail to do so.

    """
    pass


class Type(object):
    __slots__ = ('name', 'contained_types', 'meta', '_hash')

    def __init__(self, name, contained_types=frozenset(), meta=None):
        """A generic type is constructed with a name and a frozenset of
        *contained_types*. The *contained_types* represent the set of possible
        types to which this generic can be resolved.

        :param name:
            The name of this type.

        :type name: str

        :param contained_types:
            The set of possible types that this Type can be resolved to. There
            must be at least one contained type.

        :type contained_types: frozenset(Type)

        :param meta:
            Some (optional) metadata to associate with this type.

        :type meta: object

        """
        self.name = name
        self.contained_types = contained_types
        self.meta = meta
        self._hash = hash(
            ('Type', self.name, self.contained_types, self.meta)
        )

    def __getstate__(self):
        return {
            'name': self.name,
            'contained_types': self.contained_types,
            'meta': self.meta
        }

    def __setstate__(self, state):
        self.__init__(state['name'], state['contained_types'], state['meta'])

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        if isinstance(other, Type):
            return (
                self.name == other.name and
                self.contained_types == other.contained_types and
                self.meta == other.meta
            )
        else:
            return NotImplemented

    def __ne__(self, other):
        return not self.__eq__(other)

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
                if any(candidate in t for t in self.contained_types):
                    return True
                elif (
                    len(candidate.contained_types) > 0 and all(
                        t in self for t in candidate.contained_types
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
        return (
            'Type(name={name}, contained_types={contained_types}, meta={meta})'
        ).format(
            name=repr(self.name),
            contained_types=repr(self.contained_types),
            meta=repr(self.meta)
        )


class ParametrizedType(object):

    __slots__ = ('name', 'base_type', 'parameter_types', 'meta', '_hash')

    def __init__(self, name, base_type, parameter_types, meta=None):
        """A ParametrizedType is constructed with a *name*, a Type *base_type*,
        a tuple[ParametrizedType|Type] *parameter_types*, and (optionally) some
        *metadata*.

        :param name:
            The name of this type.

        :type name: str

        :param base_type:
            The base type of this generic.

        :type base_type: Type

        :param parameter_types:
            The parameters of this generic.

        :type parameter_types: tuple[ParametrizedType|Type]

        :param meta:
            Some (optional) metadata to associate with this type.

        :type meta: object
        
        :raises TypeError: if :param:`parameter_types` has length < 1.

        """
        self.name = name
        self.base_type = base_type

        if len(parameter_types) < 1:
            raise TypeError(
                'Cannot construct a ParametrizedType with empty parameter_types'
            )

        self.parameter_types = parameter_types
        self.meta = meta
        self._hash = hash((
            'ParametrizedType',
            self.name,
            self.base_type,
            self.parameter_types,
            self.meta
        ))

    def __getstate__(self):
        return {
            'name': self.name,
            'base_type': self.base_type,
            'parameter_types': self.parameter_types,
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
                self.parameter_types == other.parameter_types and
                self.meta == other.meta
            )
        else:
            return NotImplemented

    def __ne__(self, other):
        return not self.__eq__(other)

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
            if candidate == self:
                return True
            elif (
                candidate.base_type in self.base_type and
                len(candidate.parameter_types) == len(self.parameter_types)
                and len(candidate.parameter_types) > 0
            ):
                if all(c in t for c, t in zip(
                    candidate.parameter_types, self.parameter_types
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
            parameter_types=repr(self.parameter_types),
            meta=repr(self.meta)
        )
