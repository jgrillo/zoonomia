"""This module defines Zoonomia's type system. There are three main characters:

    1. *Type* -- the base type.
    2. *ParametrizedType* -- a parametrized generic type.
    3. *GenericType* -- a parameter-less generic type.

Some terminology:

    1. We say type A *contains* another type B if we can safely substitute
    values having type B in places expecting values of type A.
    2. We say type C is *more general than* type D if type D cannot contain
    type C.

*GenericType* is the most general kind of type. It subsumes *ParametrizedType*
and *Type*. Given this hierarchy of generics, we can construct a parametrized
*collection_of_numbers* generic like this:

.. code-block:: python
    int_type = Type(name='Int')

    float_type = Type(name='Float')

    number_type = GenericType(
        name='Number', contained_types=(int_type, float_type)
    )

    list_type = Type(name='List')

    set_type = Type(name='Set')

    collection_type = GenericType(
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

from threading import RLock


class Type(object):

    __slots__ = ('name', 'meta', '_hash', '_cache', '_lock')

    def __new__(cls, name, meta=None):
        """A Type instance represents a base type in Zoonomia's type system. A
        Type is distinguished from other Types by its name and metadata.

        :param name:
            The name of this type.

        :type name: str

        :param meta:
            Some (optional) metadata to associate with this type.

        :type meta: object

        """
        obj = super(Type, cls).__new__(cls)
        obj.name = name
        obj.meta = meta
        obj._hash = hash((obj.name, obj.meta))
        obj._cache = set()
        obj._lock = RLock()
        return obj

    def __getnewargs__(self):
        return self.name, self.meta

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        if isinstance(other, Type):
            return self.name == other.name and self.meta == other.meta
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __contains__(self, candidate):
        """Check whether this type can be resolved to the candidate type. This
        is similar to checking equality between this type and the candidate,
        but it's implemented for symmetry with GenericType and
        ParametrizedType.

        :param candidate:
            A candidate type.

        :type candidate: Type or GenericType or ParametrizedType

        :raise TypeError:
            if *candidate* is not a Type, GenericType, or ParametrizedType.

        :return:
            True if this type can be resolved to the candidate type, False
            otherwise.

        :rtype: bool

        """
        with self._lock:
            if candidate in self._cache:
                return True
            elif isinstance(candidate, Type):
                if self == candidate:
                    self._cache.add(candidate)
                    return True
            elif isinstance(candidate, (ParametrizedType, GenericType)):
                return False
            else:
                raise TypeError(
                    'candidate must be a Type, GenericType, '
                    'or ParametrizedType: {0}'.format(repr(candidate))
                )

    def __repr__(self):
        return 'Type(name={name}, meta={meta})'.format(
            name=repr(self.name), meta=repr(self.meta)
        )


class ParametrizedType(object):

    __slots__ = (
        'name', 'base_type', 'parameter_types', 'meta', '_hash', '_cache',
        '_lock'
    )

    def __new__(cls, name, base_type, parameter_types, meta=None):
        """A ParametrizedType is constructed with a name, a GenericType or Type
        *base_type*, a tuple[ParametrizedType|GenericType|Type]
        *parameter_types*, and (optionally) some metadata.

        :param name:
            The name of this type.

        :type name: str

        :param base_type:
            The base type of this generic.

        :type base_type: GenericType or Type

        :param parameter_types:
            The parameters of this generic.

        :type parameter_types: tuple[ParametrizedType|GenericType|Type]

        :param meta:
            Some (optional) metadata to associate with this type.

        :type meta: object

        """
        obj = super(ParametrizedType, cls).__new__(cls)
        obj.name = name
        obj.base_type = base_type
        obj.parameter_types = parameter_types
        obj.meta = meta
        obj._hash = hash(
            (obj.name, obj.base_type, obj.parameter_types, obj.meta)
        )
        obj._cache = set()
        obj._lock = RLock()
        return obj

    def __getnewargs__(self):
        return self.name, self.base_type, self.parameter_types, self.meta

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
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __contains__(self, candidate):
        """Check whether this type can be resolved to a type *candidate*.

        :param candidate:
            A candidate type.

        :type candidate: Type or GenericType or ParametrizedType

        :raise TypeError:
            if *candidate* is not a Type, GenericType, or ParametrizedType.

        :return:
            True if the candidate type belongs to this generic type (i.e. if
            this type can be resolved to the candidate type), False otherwise.

        :rtype: bool

        """
        with self._lock:
            if candidate in self._cache:
                return True
            elif isinstance(candidate, ParametrizedType):
                if candidate == self:
                    self._cache.add(candidate)
                    return True
                elif (
                    candidate.base_type in self.base_type and
                    len(candidate.parameter_types) == len(self.parameter_types)
                    and all(c in t for (c, t) in zip(
                        candidate.parameter_types, self.parameter_types
                    ))
                ):
                    self._cache.add(candidate)
                    return True
                else:
                    return False
            elif isinstance(candidate, (Type, GenericType)):
                return False
            else:
                raise TypeError(
                    'candidate must be a Type, GenericType, '
                    'or ParametrizedType: {0}'.format(repr(candidate))
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


class GenericType(object):

    __slots__ = ('name', 'contained_types', 'meta', '_hash', '_cache', '_lock')

    def __new__(cls, name, contained_types, meta=None):
        """A generic type is constructed with a name and a frozenset of
        *contained_types*. The *contained_types* represent the set of possible
        types to which this generic can be resolved.

        :param name:
            The name of this type.

        :type name: str

        :param contained_types:
            The set of possible types that this GenericType can be resolved to.
            This parameter is prohibited if either *base_type* or
            *parameter_types* is present.

        :type contained_types: frozenset(Type|GenericType)

        :param meta:
            Some (optional) metadata to associate with this type.

        :type meta: object

        """
        obj = super(GenericType, cls).__new__(cls)
        obj.name = name
        obj.contained_types = contained_types
        obj.meta = meta
        obj._hash = hash((obj.name, obj.contained_types, obj.meta))
        obj._cache = set()
        obj._lock = RLock()
        return obj

    def __getnewargs__(self):
        return self.name, self.contained_types, self.meta

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        if isinstance(other, GenericType):
            return (
                self.name == other.name and
                self.contained_types == other.contained_types and
                self.meta == other.meta
            )
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __contains__(self, candidate):
        """Check whether this type can be resolved to a type *candidate*.

        :param candidate:
            A candidate type.

        :type candidate: Type or GenericType or ParametrizedType

        :raise TypeError:
            if *candidate* is not a Type, GenericType, or ParametrizedType.

        :return:
            True if the candidate type belongs to this generic type (i.e. if
            this type can be resolved to the candidate type), False otherwise.

        :rtype: bool

        """
        with self._lock:
            if candidate in self._cache:
                return True
            elif isinstance(candidate, Type):
                if any(candidate in t for t in self.contained_types):
                    self._cache.add(candidate)
                    return True
            elif isinstance(candidate, ParametrizedType):
                if candidate.base_type in self:
                    self._cache.add(candidate)
                    return True
            elif isinstance(candidate, GenericType):
                if candidate == self:
                    self._cache.add(candidate)
                    return True
                else:
                    if any(candidate in t for t in self.contained_types):
                        self._cache.add(candidate)
                        return True
                    elif all(t in self for t in candidate.contained_types):
                        self._cache.add(candidate)
                        return True
                    else:
                        return False
            else:
                raise TypeError(
                    'candidate must be a Type, GenericType, or '
                    'ParametrizedType: {0}'.format(repr(candidate))
                )

    def __repr__(self):
        return (
            'GenericType(name={name}, contained_types={contained_types}, '
            'meta={meta})'
        ).format(
            name=repr(self.name),
            contained_types=repr(self.contained_types),
            meta=repr(self.meta)
        )
