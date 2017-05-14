import pickle
import unittest

import hypothesis.strategies as st

from hypothesis import given

from zoonomia.types import Type, ParametrizedType, GenericType

from zoonomia.tests.strategies.types import (
    distinct_types, distinct_parametrized_types, distinct_generic_types,
    default_types, default_generic_types, default_parametrized_types
)


class TestType(unittest.TestCase):

    @given(
        st.shared(default_types(), key='test_type_equals_reflexive'),
        st.shared(default_types(), key='test_type_equals_reflexive')
    )
    def test_equals_reflexive(self, type1, type2):
        self.assertIs(type1, type2)
        self.assertEqual(type1, type2)

    @given(st.data())
    def test_equals_symmetric(self, data):
        """Test that for objects :math:`\{x,y\}, x = y \iff y = x`."""
        d = data.draw(distinct_types(distinct_ts=default_types()))
        type1 = d['type1']
        another_type = d['another_type']

        type2 = Type(type1.name, type1.meta)

        self.assertEqual(type1, type2)
        self.assertEqual(type2, type1)

        self.assertNotEqual(type1, another_type)
        self.assertNotEqual(another_type, type1)

    @given(
        st.shared(default_types(), key='test_type_eq_transitive'),
        st.shared(default_types(), key='test_type_eq_transitive').map(
            lambda t: Type(t.name, t.meta)
        ),
        st.shared(default_types(), key='test_type_eq_transitive').map(
            lambda t: Type(t.name, t.meta)
        )
    )
    def test_equals_transitive(self, type1, type2, type3):
        """Test that for objects :math:`\{x,y,z\}, x = y, y = z \iff x = z`."""
        self.assertEqual(type1, type2)
        self.assertEqual(type2, type3)
        self.assertEqual(type1, type3)

    @given(st.data())
    def test_equals_consistent(self, data):
        """Test that repeated equals calls return the same value."""
        d = data.draw(distinct_types(distinct_ts=default_types()))
        type1 = d['type1']
        another_type = d['another_type']

        type2 = Type(type1.name, type1.meta)

        self.assertEqual(type1, type2)
        self.assertEqual(type1, type2)
        self.assertEqual(type1, type2)

        self.assertNotEqual(type1, another_type)
        self.assertNotEqual(type1, another_type)
        self.assertNotEqual(type1, another_type)

    @given(default_types())
    def test_hash_consistent(self, type1):
        """Test that repeated hash calls yield the same value."""
        hash1 = hash(type1)

        self.assertEqual(hash1, hash(type1))
        self.assertEqual(hash1, hash(type1))
        self.assertEqual(hash1, hash(type1))

    @given(
        st.shared(default_types(), key='test_type_hash_equals'),
        st.shared(default_types(), key='test_type_hash_equals').map(
            lambda t: Type(t.name, t.meta)
        )
    )
    def test_hash_equals(self, type1, type2):
        """Test that when two objects are equal their hashes are equal."""
        self.assertEqual(hash(type1), hash(type2))
        self.assertEqual(type1, type2)

    @given(default_types())
    def test_type_pickle(self, type1):
        """Test that a Type instance can be pickled and unpickled using the
        default protocol.

        """
        pickled_type = pickle.dumps(type1, -1)
        unpickled_type = pickle.loads(pickled_type)

        self.assertEqual(type1, unpickled_type)

    @given(
        st.shared(default_types(), key='test_type_contains_1'),
        st.shared(default_types(), key='test_type_contains_1').map(
            lambda t: Type(t.name, t.meta)
        )
    )
    def test_type_contains__returns_True_when_types_equal(self, type1, type2):
        """Test that a Type contains another Type when the Types are equal."""
        self.assertEqual(type1, type2)
        self.assertIn(type1, type2)
        self.assertIn(type2, type1)

    @given(st.data())
    def test_type_contains__returns_False_when_types_not_equal(self, data):
        """Test that a Type does not contain another Type when the Types are
        not equal.

        """
        d = data.draw(distinct_types(distinct_ts=default_types()))
        type1 = d['type1']
        another_type = d['another_type']

        self.assertNotEqual(type1, another_type)
        self.assertNotIn(type1, another_type)
        self.assertNotIn(another_type, type1)

    @given(default_parametrized_types(), default_types())
    def test_type_contains__returns_False_when_ParametrizedType(
        self, ptype1, type1
    ):
        """Test that a Type does not contain a ParametrizedType."""
        self.assertNotIn(ptype1, type1)

    @given(default_generic_types(), default_types())
    def test_type_contains__returns_False_when_GenericType(self, gtype1, type1):
        """Test that a Type does not contain a GenericType."""
        self.assertNotIn(gtype1, type1)

    @given(
        default_types(),
        st.text() | st.integers() | st.none() | st.booleans() | st.floats()
    )
    def test_type_contains__raises_TypeError(self, type1, junk):
        """Test that a Type does not implement __contains__ for arbitrary
        candidates.

        """
        self.assertRaises(TypeError, type1.__contains__, (junk,))


class TestParametrizedType(unittest.TestCase):

    @given(
        st.shared(default_parametrized_types(), key='test_pt_eq_reflexive'),
        st.shared(default_parametrized_types(), key='test_pt_eq_reflexive')
    )
    def test_equals_reflexive(self, ptype1, ptype2):
        """Test that an object equals itself."""
        self.assertIs(ptype1, ptype2)
        self.assertEqual(ptype1, ptype2)

    @given(st.data())
    def test_equals_symmetric(self, data):
        """Test that for objects :math:`\{x,y\}, x = y \iff y = x`."""
        d = data.draw(distinct_parametrized_types(
            parametrized_ts=default_parametrized_types()
        ))
        ptype1 = d['type1']
        another_ptype = d['another_type']

        ptype2 = ParametrizedType(
            name=ptype1.name,
            meta=ptype1.meta,
            base_type=ptype1.base_type,
            parameter_types=ptype1.parameter_types
        )

        self.assertEqual(ptype1, ptype2)
        self.assertEqual(ptype2, ptype1)

        self.assertNotEqual(ptype1, another_ptype)
        self.assertNotEqual(another_ptype, ptype1)

    @given(
        st.shared(default_parametrized_types(), key='test_pt_eq_transitive'),
        st.shared(
            default_parametrized_types(), key='test_pt_eq_transitive'
        ).map(lambda t: ParametrizedType(
            name=t.name,
            meta=t.meta,
            base_type=t.base_type,
            parameter_types=t.parameter_types
        )),
        st.shared(
            default_parametrized_types(), key='test_pt_eq_transitive'
        ).map(lambda t: ParametrizedType(
            name=t.name,
            meta=t.meta,
            base_type=t.base_type,
            parameter_types=t.parameter_types
        ))
    )
    def test_equals_transitive(self, ptype1, ptype2, ptype3):
        """Test that for objects :math:`\{x,y,z\}, x = y, y = z \iff x = z`."""
        self.assertEqual(ptype1, ptype2)
        self.assertEqual(ptype2, ptype3)
        self.assertEqual(ptype1, ptype3)

    @given(st.data())
    def test_equals_consistent(self, data):
        """Test that repeated equals calls return the same value."""
        d = data.draw(distinct_parametrized_types(
            parametrized_ts=default_parametrized_types()
        ))
        ptype1 = d['type1']
        another_ptype = d['another_type']

        ptype2 = ParametrizedType(
            name=ptype1.name,
            meta=ptype1.meta,
            base_type=ptype1.base_type,
            parameter_types=ptype1.parameter_types
        )

        self.assertEqual(ptype1, ptype2)
        self.assertEqual(ptype1, ptype2)
        self.assertEqual(ptype1, ptype2)

        self.assertNotEqual(ptype1, another_ptype)
        self.assertNotEqual(ptype1, another_ptype)
        self.assertNotEqual(ptype1, another_ptype)

    @given(default_parametrized_types())
    def test_hash_consistent(self, ptype1):
        """Test that repeated hash calls yield the same value."""
        hash1 = hash(ptype1)

        self.assertEqual(hash1, hash(ptype1))
        self.assertEqual(hash1, hash(ptype1))
        self.assertEqual(hash1, hash(ptype1))

    @given(
        st.shared(default_parametrized_types(), key='test_pt_hash_equals'),
        st.shared(
            default_parametrized_types(), key='test_pt_hash_equals'
        ).map(lambda t: ParametrizedType(
            name=t.name,
            meta=t.meta,
            base_type=t.base_type,
            parameter_types=t.parameter_types
        ))
    )
    def test_hash_equals(self, ptype1, ptype2):
        """Test that when two objects are equal their hashes are equal."""
        self.assertEqual(ptype1, ptype2)
        self.assertEqual(hash(ptype1), hash(ptype2))

    @given(default_parametrized_types())
    def test_parametrized_type_pickle(self, ptype1):
        """Test that a ParametrizedType instance can be pickled and unpickled
        using the default protocol.

        """
        pickled_parametrized_type = pickle.dumps(ptype1, -1)
        unpickled_parametrized_type = pickle.loads(pickled_parametrized_type)

        self.assertEqual(ptype1, unpickled_parametrized_type)

    @given(
        st.shared(default_parametrized_types(), key='test_pt_contains1'),
        st.shared(
            default_parametrized_types(), key='test_pt_contains1'
        ).map(lambda t: ParametrizedType(
            name=t.name,
            meta=t.meta,
            base_type=t.base_type,
            parameter_types=t.parameter_types
        ))
    )
    def test_parametrized_type_contains_when_equal(self, ptype1, ptype2):
        """Test that a ParametrizedType contains another ParametrizedType when
        the two types are equal.

        """
        self.assertEqual(ptype1, ptype2)
        self.assertIn(ptype1, ptype2)
        self.assertIn(ptype2, ptype1)

    @given(st.data())
    def test_parametrized_type_not_contains_when_ptypes_ne(self, data):
        """Test that a ParametrizedType does not contain another
        ParametrizedType *candidate* when the two parametrized types are
        unequal.

        """
        d = data.draw(distinct_parametrized_types(
            parametrized_ts=default_parametrized_types()
        ))
        ptype1 = d['type1']
        another_ptype = d['another_type']

        self.assertNotIn(ptype1, another_ptype)
        self.assertNotIn(another_ptype, ptype1)

    def test_parametrized_type_contains_when_all_parameter_types_in_1(self):
        """Test that a ParametrizedType contains another ParametrizedType
        *candidate* when all of *candidate's* parameter types are contained in
        *self's* parameter types and the base types are equal.

        """
        base_type_1 = Type(name='base', meta='base')
        base_type_2 = Type(name='base', meta='base')

        self.assertEqual(base_type_1, base_type_2)

        parameter_type_1 = Type(name='parameter1', meta='meta')
        parameter_type_2 = Type(name='parameter2', meta='meta')

        parametrized_type_1 = ParametrizedType(
            name='ParametrizedType1',
            base_type=base_type_1,
            parameter_types=(parameter_type_1, parameter_type_2),
            meta='meta'
        )
        parametrized_type_2 = ParametrizedType(
            name='ParametrizedType2',
            base_type=base_type_2,
            parameter_types=(parameter_type_1, parameter_type_2),
            meta='meta'
        )

        self.assertNotEqual(parametrized_type_1, parametrized_type_2)
        self.assertNotEqual(parametrized_type_2, parametrized_type_1)

        self.assertIn(parametrized_type_1, parametrized_type_2)
        self.assertIn(parametrized_type_2, parametrized_type_1)

    def test_parametrized_type_not_contains_when_not_all_parameter_types_in_1(
        self
    ):
        """Test that a ParametrizedType does not contain another
        ParametrizedType *candidate* when some of *candidate's* parameter types
        are not contained in *self's* parameter types and the base types are
        equal.

        """
        base_type_1 = Type(name='base', meta='base')
        base_type_2 = Type(name='base', meta='base')

        self.assertEqual(base_type_1, base_type_2)

        parameter_type_1 = Type(name='parameter1', meta='meta')
        parameter_type_2 = Type(name='parameter2', meta='meta')
        parameter_type_3 = Type(name='parameter3', meta='meta')

        parametrized_type_1 = ParametrizedType(
            name='ParametrizedType1',
            base_type=base_type_1,
            parameter_types=(parameter_type_1, parameter_type_2),
            meta='meta'
        )
        parametrized_type_2 = ParametrizedType(
            name='ParametrizedType2',
            base_type=base_type_2,
            parameter_types=(parameter_type_1, parameter_type_3),
            meta='meta'
        )

        self.assertNotEqual(parametrized_type_1, parametrized_type_2)
        self.assertNotEqual(parametrized_type_2, parametrized_type_1)

        self.assertNotIn(parametrized_type_1, parametrized_type_2)
        self.assertNotIn(parametrized_type_2, parametrized_type_1)

    def test_parametrized_type_contains_when_all_parameter_types_in_2(self):
        """Test that a ParametrizedType contains another ParametrizedType
        *candidate* when all of *candidate's* parameter types are contained in
        *self's* parameter types and the base types are equal.

        """
        base_type_1 = Type(name='base', meta='base')
        base_type_2 = Type(name='base', meta='base')

        self.assertEqual(base_type_1, base_type_2)

        parameter_contained_type_1 = Type(
            name='ContainedType1',
            meta='meta'
        )
        parameter_contained_type_2 = Type(
            name='ContainedType2',
            meta='meta'
        )
        parameter_contained_type_3 = Type(
            name='ContainedType3',
            meta='meta'
        )

        parameter_generic_1 = GenericType(
            name='ParameterType1',
            contained_types=frozenset(
                (parameter_contained_type_1, parameter_contained_type_2)
            ),
            meta='meta'
        )
        parameter_generic_2 = GenericType(
            name='ParameterType1',
            contained_types=frozenset(
                (parameter_contained_type_1, parameter_contained_type_3)
            ),
            meta='meta'
        )

        generic_parametrized_type = ParametrizedType(
            name='ParametrizedType1',
            base_type=base_type_1,
            parameter_types=(parameter_generic_1, parameter_generic_2),
            meta='meta'
        )
        parametrized_type = ParametrizedType(
            name='ParametrizedType2',
            base_type=base_type_1,
            parameter_types=(
                parameter_contained_type_1, parameter_contained_type_3
            ),
            meta='meta'
        )

        self.assertIn(parametrized_type, generic_parametrized_type)
        self.assertNotIn(generic_parametrized_type, parametrized_type)

    def test_parametrized_type_not_contains_when_not_all_parameter_types_in_2(
        self
    ):
        """Test that a ParametrizedType does not contain another
        ParametrizedType *candidate* when some of *candidate's* parameter types
        are not contained in *self's* parameter types and the base types are
        equal.

        """
        base_type_1 = Type(name='base', meta='base')
        base_type_2 = Type(name='base', meta='base')

        self.assertEqual(base_type_1, base_type_2)

        parameter_contained_type_1 = Type(
            name='ContainedType1',
            meta='meta'
        )
        parameter_contained_type_2 = Type(
            name='ContainedType2',
            meta='meta'
        )
        parameter_contained_type_3 = Type(
            name='ContainedType3',
            meta='meta'
        )

        parameter_generic_1 = GenericType(
            name='ParameterType1',
            contained_types=frozenset(
                (parameter_contained_type_1, parameter_contained_type_2)
            ),
            meta='meta'
        )
        parameter_generic_2 = GenericType(
            name='ParameterType1',
            contained_types=frozenset(
                (parameter_contained_type_1, parameter_contained_type_3)
            ),
            meta='meta'
        )

        generic_parametrized_type = ParametrizedType(
            name='ParametrizedType1',
            base_type=base_type_1,
            parameter_types=(parameter_generic_1, parameter_generic_2),
            meta='meta'
        )
        parametrized_type = ParametrizedType(
            name='ParametrizedType2',
            base_type=base_type_1,
            parameter_types=(
                parameter_contained_type_1, parameter_contained_type_2
            ),
            meta='meta'
        )

        self.assertNotIn(parametrized_type, generic_parametrized_type)
        self.assertNotIn(generic_parametrized_type, parametrized_type)

    def test_parametrized_type_contains_with_one_generic_parameter(self):
        """Test that a ParametrizedType p0 contains another ParametrizedType p1
        when p0.base_type is a Type which is contained in p1.base_type, a
        GenericType.

        """
        int_type = Type(name='Int')
        float_type = Type(name='Float')

        list_type = Type(name='List')
        set_type = Type(name='Set')

        number_type = GenericType(
            name='Number',
            contained_types=frozenset((int_type, float_type))
        )
        collection_type = GenericType(
            name='Collection',
            contained_types=frozenset((list_type, set_type))
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

        self.assertIn(collection_of_ints_type, collection_of_numbers_type)

    def test_parametrized_type_not_contains_with_one_generic_parameter(self):
        """Test that a ParametrizedType p0 does not contain another
        ParametrizedType p1 when p0.base_type is a Type which is not contained
        in p1.base_type, a GenericType.

        """
        int_type = Type(name='Int')
        float_type = Type(name='Float')
        str_type = Type(name='Str')

        list_type = Type(name='List')
        set_type = Type(name='Set')

        number_type = GenericType(
            name='Number',
            contained_types=frozenset((int_type, float_type))
        )
        collection_type = GenericType(
            name='Collection',
            contained_types=frozenset((list_type, set_type))
        )

        collection_of_numbers_type = ParametrizedType(
            name='Collection<Number>',
            base_type=collection_type,
            parameter_types=(number_type,)
        )

        collection_of_strs_type = ParametrizedType(
            name='Collection<Str>',
            base_type=collection_type,
            parameter_types=(str_type,)
        )

        self.assertNotIn(collection_of_strs_type, collection_of_numbers_type)

    def test_parametrized_type_contains_with_two_generic_parameters(self):
        """Test that a ParametrizedType p0 contains another ParametrizedType p1
        when p0.base_type is a GenericType which is contained in p1.base_type,
        a GenericType.

        """
        int_type = Type(name='Int')
        float_type = Type(name='Float')

        list_type = Type(name='List')
        set_type = Type(name='Set')

        number_type = GenericType(
            name='Number',
            contained_types=frozenset((int_type, float_type))
        )
        integer_type = GenericType(
            name='Integer',
            contained_types=frozenset((int_type,))
        )
        collection_type = GenericType(
            name='Collection',
            contained_types=frozenset((list_type, set_type))
        )

        collection_of_numbers_type = ParametrizedType(
            name='Collection<Number>',
            base_type=collection_type,
            parameter_types=(number_type,)
        )

        collection_of_integers_type = ParametrizedType(
            name='Collection<Integer>',
            base_type=collection_type,
            parameter_types=(integer_type,)
        )

        self.assertIn(integer_type, number_type)
        self.assertIn(collection_of_integers_type, collection_of_numbers_type)

    def test_parametrized_type_not_contains_with_two_generic_parameters(self):
        """Test that a ParametrizedType p0 does not contain another
        ParametrizedType p1 when p0.base_type is a GenericType which is not
        contained in p1.base_type, a GenericType.

        """
        int_type = Type(name='Int')
        float_type = Type(name='Float')
        str_type = Type(name='Str')

        list_type = Type(name='List')
        set_type = Type(name='Set')

        number_type = GenericType(
            name='Number',
            contained_types=frozenset((int_type, float_type))
        )
        string_type = GenericType(
            name='String',
            contained_types=frozenset((str_type,))
        )
        collection_type = GenericType(
            name='Collection',
            contained_types=frozenset((list_type, set_type))
        )

        collection_of_numbers_type = ParametrizedType(
            name='Collection<Number>',
            base_type=collection_type,
            parameter_types=(number_type,)
        )

        collection_of_strings_type = ParametrizedType(
            name='Collection<String>',
            base_type=collection_type,
            parameter_types=(string_type,)
        )

        self.assertNotIn(string_type, number_type)
        self.assertNotIn(
            collection_of_strings_type, collection_of_numbers_type
        )

    @given(default_types(), default_parametrized_types())
    def test_parametrized_type_does_not_contain_Type(self, type1, ptype1):
        """Test that a ParametrizedType does not contain a Type"""
        self.assertNotIn(type1, ptype1)

    @given(default_generic_types(), default_parametrized_types())
    def test_parametrized_type_does_not_contain_GenericType(
        self, gtype1, ptype1
    ):
        """Test that a ParametrizedType does not contain a GenericType"""
        self.assertNotIn(gtype1, ptype1)

    @given(
        default_parametrized_types(),
        st.text() | st.integers() | st.none() | st.booleans() | st.floats()
    )
    def test_parametrized_type_contains_raises_TypeError(self, ptype1, junk):
        """Test that a ParametrizedType does not implement __contains__ for
        arbitrary candidates.

        """
        self.assertRaises(TypeError, ptype1.__contains__, junk)


class TestGenericType(unittest.TestCase):

    @given(
        st.shared(default_generic_types(), key='test_gt_eq_reflexive'),
        st.shared(default_generic_types(), key='test_gt_eq_reflexive')
    )
    def test_equals_reflexive(self, gtype1, gtype2):
        """Test that an object equals itself."""
        self.assertIs(gtype1, gtype2)
        self.assertEqual(gtype1, gtype2)

    @given(st.data())
    def test_equals_symmetric(self, data):
        """Test that for objects :math:`\{x,y\}, x = y \iff y = x`."""
        d = data.draw(distinct_generic_types(
            generic_ts=default_generic_types()
        ))
        gtype1 = d['type1']
        another_gtype = d['another_type']

        gtype2 = GenericType(
            name=gtype1.name,
            meta=gtype1.meta,
            contained_types=gtype1.contained_types
        )

        self.assertEqual(gtype1, gtype2)
        self.assertEqual(gtype2, gtype1)

        self.assertNotEqual(gtype1, another_gtype)
        self.assertNotEqual(another_gtype, gtype1)

    @given(
        st.shared(default_generic_types(), key='test_gt_eq_transitive'),
        st.shared(default_generic_types(), key='test_gt_eq_transitive').map(
            lambda t: GenericType(
                name=t.name,
                meta=t.meta,
                contained_types=t.contained_types
            )
        ),
        st.shared(default_generic_types(), key='test_gt_eq_transitive').map(
            lambda t: GenericType(
                name=t.name,
                meta=t.meta,
                contained_types=t.contained_types
            )
        )
    )
    def test_equals_transitive(self, gtype1, gtype2, gtype3):
        """Test that for objects :math:`\{x,y,z\}, x = y, y = z \iff x = z`."""
        self.assertEqual(gtype1, gtype2)
        self.assertEqual(gtype2, gtype3)
        self.assertEqual(gtype1, gtype3)

    @given(st.data())
    def test_equals_consistent(self, data):
        """Test that repeated equals calls return the same value."""
        d = data.draw(distinct_generic_types(
            generic_ts=default_generic_types()
        ))
        gtype1 = d['type1']
        another_gtype = d['another_type']

        gtype2 = GenericType(
            name=gtype1.name,
            meta=gtype1.meta,
            contained_types=gtype1.contained_types
        )

        self.assertEqual(gtype1, gtype2)
        self.assertEqual(gtype1, gtype2)
        self.assertEqual(gtype1, gtype2)

        self.assertNotEqual(gtype1, another_gtype)
        self.assertNotEqual(gtype1, another_gtype)
        self.assertNotEqual(gtype1, another_gtype)

    @given(default_generic_types())
    def test_hash_consistent(self, gtype1):
        """Test that repeated hash calls yield the same value."""
        hash1 = hash(gtype1)

        self.assertEqual(hash1, hash(gtype1))
        self.assertEqual(hash1, hash(gtype1))
        self.assertEqual(hash1, hash(gtype1))

    @given(
        st.shared(default_generic_types(), key='test_gt_hash_equals'),
        st.shared(default_generic_types(), key='test_gt_hash_equals').map(
            lambda t: GenericType(
                name=t.name,
                meta=t.meta,
                contained_types=t.contained_types
            )
        )
    )
    def test_hash_equals(self, gtype1, gtype2):
        """Test that when two objects are equal their hashes are equal."""
        self.assertEqual(gtype1, gtype2)
        self.assertEqual(hash(gtype1), hash(gtype2))

    @given(default_parametrized_types())
    def test_generic_type_pickle(self, gtype1):
        """Test that a GenericType instance can be pickled and unpickled using
        the default protocol.

        """
        pickled_generic_type = pickle.dumps(gtype1, -1)
        unpickled_generic_type = pickle.loads(pickled_generic_type)

        self.assertEqual(gtype1, unpickled_generic_type)

    @given(
        st.shared(default_generic_types(), key='test_gt_contains1'),
        st.shared(default_generic_types(), key='test_gt_contains1').map(
            lambda t: GenericType(
                name=t.name,
                meta=t.meta,
                contained_types=t.contained_types
            )
        )
    )
    def test_generic_type_contains_equal_generic_type(self, gtype1, gtype2):
        """Test that a GenericType contains another GenericType if the two
        GenericTypes are equal.

        """
        self.assertEqual(gtype1, gtype2)
        self.assertEqual(gtype2, gtype1)
        self.assertIn(gtype1, gtype2)
        self.assertIn(gtype1, gtype2)

    @given(st.data())
    def test_generic_type_not_contains_unequal_generic_type(self, data):
        """Test that a GenericType does not contain another GenericType if the
        two GenericTypes are unequal.

        """
        d = data.draw(distinct_generic_types(
            generic_ts=default_generic_types()
        ))
        gtype1 = d['type1']
        another_gtype = d['another_type']

        self.assertNotIn(gtype1, another_gtype)
        self.assertNotIn(another_gtype, gtype1)

    def test_generic_type_contains_Type(self):
        """Test that a GenericType contains a Type when the Type is contained
        by any of the GenericType's *contained_types*.

        """
        type1 = Type(name='one', meta='meta')
        generic_type_1 = GenericType(
            name='GenericType1',
            contained_types=frozenset((type1,)),
            meta='meta'
        )

        self.assertNotEqual(generic_type_1, type1)
        self.assertNotEqual(type1, generic_type_1)
        self.assertIn(type1, generic_type_1)

    def test_generic_type_not_contains_Type(self):
        """Test that a GenericType does not contain a Type when that Type is
        not contained by any of the GenericType's *contained_types*.

        """
        type1 = Type(name='one', meta='meta')
        type2 = Type(name='two', meta='meta')
        generic_type_1 = GenericType(
            name='GenericType1',
            contained_types=frozenset((type2,)),
            meta='meta'
        )

        self.assertNotEqual(generic_type_1, type1)
        self.assertNotEqual(type1, generic_type_1)
        self.assertNotIn(type1, generic_type_1)

    def test_generic_type_contains_ParametrizedType_with_Type_base(self):
        """Test that a GenericType contains a ParametrizedType when any of the
        *contained_types* contains the ParametrizedType's base type.

        """
        type1 = Type(name='one', meta='meta')
        type2 = Type(name='two', meta='meta')

        parametrized_type = ParametrizedType(
            name='ParametrizedType',
            base_type=type1,
            parameter_types=(type2,),
            meta='meta'
        )

        generic_type = GenericType(
            name='GenericType',
            contained_types=frozenset((type1, type2)),
            meta='meta'
        )

        self.assertIn(parametrized_type, generic_type)

    def test_generic_type_not_contains_ParametrizedType_with_Type_base(self):
        """Test that a GenericType does not contain a ParametrizedType when
        none of the *contained_types* contain the ParametrizedType's base type.

        """
        type1 = Type(name='one', meta='meta')
        type2 = Type(name='two', meta='meta')

        parametrized_type = ParametrizedType(
            name='ParametrizedType',
            base_type=type1,
            parameter_types=(type2,),
            meta='meta'
        )

        generic_type = GenericType(
            name='GenericType',
            contained_types=frozenset((type2,)),
            meta='meta'
        )

        self.assertNotIn(parametrized_type, generic_type)

    def test_generic_type_contains_ParametrizedType_with_generic_base(self):
        """Test that a ParametrizedType can be resolved to a GenericType if the
        ParametrizedType's *base_type* is a GenericType which is contained by
        the resolution target.

        """
        int_type = Type(name='Int')
        float_type = Type(name='Float')

        list_type = Type(name='List')
        set_type = Type(name='Set')

        number_type = GenericType(
            name='Number',
            contained_types=frozenset((int_type, float_type))
        )
        collection_type = GenericType(
            name='Collection',
            contained_types=frozenset((list_type, set_type))
        )

        collection_of_numbers_type = ParametrizedType(
            name='Collection<Number>',
            base_type=collection_type,
            parameter_types=(number_type,)
        )

        self.assertIn(collection_of_numbers_type, collection_type)

    def test_generic_type_not_contains_ParametrizedType_with_generic_base(
        self
    ):
        """Test that a ParametrizedType cannot be resolved to a GenericType if
        the ParametrizedType's *base_type* is a GenericType which is not
        contained by the resolution target.

        """
        int_type = Type(name='Int')
        float_type = Type(name='Float')

        list_type = Type(name='List')
        set_type = Type(name='Set')

        number_type = GenericType(
            name='Number',
            contained_types=frozenset((int_type, float_type))
        )
        collection_type = GenericType(
            name='Collection',
            contained_types=frozenset((list_type, set_type))
        )

        collection_of_numbers_type = ParametrizedType(
            name='Collection<Number>',
            base_type=collection_type,
            parameter_types=(number_type,)
        )

        self.assertNotIn(collection_of_numbers_type, number_type)

    def test_generic_type_contains_other(self):
        """Test that a GenericType contains another GenericType when any of
        the GenericType's *contained_types* contain the other GenericType.

        """
        type1 = Type(name='one', meta='meta')
        type2 = Type(name='two', meta='meta')

        generic_type_1 = GenericType(
            name='GenericType1',
            contained_types=frozenset((type1, type2)),
            meta='meta'
        )
        generic_type_2 = GenericType(
            name='GenericType2',
            contained_types=frozenset((generic_type_1,)),
            meta='meta'
        )

        self.assertIn(generic_type_1, generic_type_2)
        self.assertIn(generic_type_2, generic_type_1)

    def test_generic_type_not_contains_other(self):
        """Test that a GenericType does not contain another GenericType when
         none of the GenericType's *contained_types* contain the other
         GenericType.

        """
        type1 = Type(name='one', meta='meta')
        type2 = Type(name='two', meta='meta')

        generic_type_1 = GenericType(
            name='GenericType1',
            contained_types=frozenset((type2,)),
            meta='meta'
        )
        generic_type_2 = GenericType(
            name='GenericType2',
            contained_types=frozenset((type1,)),
            meta='meta'
        )

        self.assertNotIn(generic_type_1, generic_type_2)
        self.assertNotIn(generic_type_2, generic_type_1)
