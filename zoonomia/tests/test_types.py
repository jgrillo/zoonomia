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

import pickle
import unittest

import hypothesis.strategies as st

from hypothesis import given, settings, HealthCheck

from zoonomia.types import Type, ParametrizedType

from zoonomia.tests.strategies.types import (
    distinct_types, default_types, distinct_parametrized_types,
    default_parametrized_types
)


class TestType(unittest.TestCase):
    BUFFER_SIZE = 8192 * 4
    SUPPRESSED_HEALTH_CHECKS = (HealthCheck.too_slow,)

    @given(
        st.shared(default_types(), key='test_type_eq_reflexive'),
        st.shared(default_types(), key='test_type_eq_reflexive')
    )
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_equals_reflexive(self, type1, type2):
        """Test that an object equals itself."""
        self.assertIs(type1, type2)
        self.assertEqual(type1, type2)

    @given(st.data())
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_equals_symmetric(self, data):
        """Test that for objects :math:`\{x,y\}, x = y \iff y = x`."""
        d = data.draw(distinct_types(ts=default_types()))
        type1 = d['type1']
        another_type = d['another_type']

        type2 = Type(
            name=type1.name,
            meta=type1.meta,
            contained_types=type1.contained_types
        )

        self.assertEqual(type1, type2)
        self.assertEqual(type2, type1)

        self.assertNotEqual(type1, another_type)
        self.assertNotEqual(another_type, type1)

    @given(
        st.shared(default_types(), key='test_type_eq_transitive'),
        st.shared(default_types(), key='test_type_eq_transitive').map(
            lambda t: Type(
                name=t.name,
                meta=t.meta,
                contained_types=t.contained_types
            )
        ),
        st.shared(default_types(), key='test_type_eq_transitive').map(
            lambda t: Type(
                name=t.name,
                meta=t.meta,
                contained_types=t.contained_types
            )
        )
    )
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_equals_transitive(self, type1, type2, type3):
        """Test that for objects :math:`\{x,y,z\}, x = y, y = z \iff x = z`."""
        self.assertEqual(type1, type2)
        self.assertEqual(type2, type3)
        self.assertEqual(type1, type3)

    @given(st.data())
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_equals_consistent(self, data):
        """Test that repeated equals calls return the same value."""
        d = data.draw(distinct_types(ts=default_types()))
        type1 = d['type1']
        another_type = d['another_type']

        type2 = Type(
            name=type1.name,
            meta=type1.meta,
            contained_types=type1.contained_types
        )

        self.assertEqual(type1, type2)
        self.assertEqual(type1, type2)
        self.assertEqual(type1, type2)

        self.assertNotEqual(type1, another_type)
        self.assertNotEqual(type1, another_type)
        self.assertNotEqual(type1, another_type)

    @given(default_types())
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_hash_consistent(self, type1):
        """Test that repeated hash calls yield the same value."""
        hash1 = hash(type1)

        self.assertEqual(hash1, hash(type1))
        self.assertEqual(hash1, hash(type1))
        self.assertEqual(hash1, hash(type1))

    @given(
        st.shared(default_types(), key='test_type_hash_equals'),
        st.shared(default_types(), key='test_type_hash_equals').map(
            lambda t: Type(
                name=t.name,
                meta=t.meta,
                contained_types=t.contained_types
            )
        )
    )
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_hash_equals(self, type1, type2):
        """Test that when two objects are equal their hashes are equal."""
        self.assertEqual(type1, type2)
        self.assertEqual(hash(type1), hash(type2))

    @given(default_parametrized_types())
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_type_pickle(self, type1):
        """Test that a Type instance can be pickled and unpickled using the 0
        protocol and the -1 protocol.

        """
        pickled_type = pickle.dumps(type1, -1)
        unpickled_type = pickle.loads(pickled_type)

        self.assertEqual(type1, unpickled_type)
        self.assertEqual(hash(type1), hash(unpickled_type))

        pickled_type = pickle.dumps(type1, 0)
        unpickled_type = pickle.loads(pickled_type)

        self.assertEqual(type1, unpickled_type)
        self.assertEqual(hash(type1), hash(unpickled_type))

    @given(
        st.shared(default_types(), key='test_type_contains1'),
        st.shared(default_types(), key='test_type_contains1').map(
            lambda t: Type(
                name=t.name,
                meta=t.meta,
                contained_types=t.contained_types
            )
        )
    )
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_type_contains_equal_type(self, type1, type2):
        """Test that a Type contains another Type if the two Types are equal.

        """
        self.assertEqual(type1, type2)
        self.assertEqual(type2, type1)
        self.assertIn(type1, type2)
        self.assertIn(type1, type2)

    def test_type_contains_another_type(self):  # FIXME: hypothesize
        """Test that another_type contains type1 when type1 is contained by any
        of another_types's *contained_types*.

        """
        type1 = Type(name='one', meta='meta')
        another_type = Type(
            name='Type1',
            contained_types=frozenset((type1,)),
            meta='meta'
        )

        self.assertNotEqual(another_type, type1)
        self.assertNotEqual(type1, another_type)
        self.assertIn(type1, another_type)

    def test_type_contains_other_type_2(self):  # FIXME: hypothesize
        """Test that a Type type1 contains another Type type2 when any of
        type1's *contained_types* contain type2.

        """
        type1 = Type(name='one', meta='meta')
        type2 = Type(name='two', meta='meta')

        another_type_1 = Type(
            name='Type1',
            contained_types=frozenset((type1, type2)),
            meta='meta'
        )
        another_type_2 = Type(
            name='Type2',
            contained_types=frozenset((another_type_1,)),
            meta='meta'
        )

        self.assertIn(type1, another_type_1)
        self.assertIn(type2, another_type_1)
        self.assertIn(another_type_1, another_type_2)
        self.assertIn(another_type_2, another_type_1)

        self.assertIn(type1, another_type_2)
        self.assertIn(type2, another_type_2)

    def test_type_not_contains_another_type(self):  # FIXME: hypothesize
        """Test that another_type does not contain a Type when that Type is
        not contained by any of another_type's *contained_types*.

        """
        type1 = Type(name='one', meta='meta')
        type2 = Type(name='two', meta='meta')
        another_type = Type(
            name='Type1',
            contained_types=frozenset((type2,)),
            meta='meta'
        )

        self.assertNotEqual(another_type, type1)
        self.assertNotEqual(type1, another_type)
        self.assertNotIn(type1, another_type)

    def test_type_not_contains_another_type_2(self):  # FIXME: hypothesize
        """Test that a Type does not contain another Type when none of the
        Type's *contained_types* contain the otherType.

        """
        type1 = Type(name='one', meta='meta')
        type2 = Type(name='two', meta='meta')

        another_type_1 = Type(
            name='Type1',
            contained_types=frozenset((type2,)),
            meta='meta'
        )
        another_type_2 = Type(
            name='Type2',
            contained_types=frozenset((type1,)),
            meta='meta'
        )

        self.assertNotIn(type1, another_type_1)
        self.assertIn(type1, another_type_2)

        self.assertIn(type2, another_type_1)
        self.assertNotIn(type2, another_type_2)

        self.assertNotIn(another_type_2, another_type_1)
        self.assertNotIn(another_type_1, another_type_2)

    def test_type_contains_ParametrizedType(self):  # FIXME: hypothesize
        """Test that a Type contains a ParametrizedType when any of the
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

        another_type = Type(
            name='Type',
            contained_types=frozenset((type1, type2)),
            meta='meta'
        )

        self.assertIn(parametrized_type, another_type)

    def test_type_contains_ParametrizedType_2(self):  # FIXME: hypothesize
        """Test that a ParametrizedType can be resolved to a Type if the
        ParametrizedType's *base_type* is a Type which is contained by
        the resolution target.

        """
        int_type = Type(name='Int')
        float_type = Type(name='Float')

        list_type = Type(name='List')
        set_type = Type(name='Set')

        number_type = Type(
            name='Number',
            contained_types=frozenset((int_type, float_type))
        )
        collection_type = Type(
            name='Collection',
            contained_types=frozenset((list_type, set_type))
        )

        collection_of_numbers_type = ParametrizedType(
            name='Collection<Number>',
            base_type=collection_type,
            parameter_types=(number_type,)
        )

        self.assertIn(collection_of_numbers_type, collection_type)

    def test_type_not_contains_ParametrizedType(self):  # FIXME: hypothesize
        """Test that a Type does not contain a ParametrizedType when none of the
        *contained_types* contain the ParametrizedType's base type.

        """
        type1 = Type(name='one', meta='meta')
        type2 = Type(name='two', meta='meta')

        parametrized_type = ParametrizedType(
            name='ParametrizedType',
            base_type=type1,
            parameter_types=(type2,),
            meta='meta'
        )

        another_type = Type(
            name='Type',
            contained_types=frozenset((type2,)),
            meta='meta'
        )

        self.assertNotIn(parametrized_type, another_type)

    def test_type_not_contains_ParametrizedType_2(self):  # FIXME: hypothesize
        """Test that a ParametrizedType cannot be resolved to a Type if
        the ParametrizedType's *base_type* is a Type which is notcontained by
        the resolution target.

        """
        int_type = Type(name='Int')
        float_type = Type(name='Float')

        list_type = Type(name='List')
        set_type = Type(name='Set')

        number_type = Type(
            name='Number',
            contained_types=frozenset((int_type, float_type))
        )
        collection_type = Type(
            name='Collection',
            contained_types=frozenset((list_type, set_type))
        )

        collection_of_numbers_type = ParametrizedType(
            name='Collection<Number>',
            base_type=collection_type,
            parameter_types=(number_type,)
        )

        self.assertNotIn(collection_of_numbers_type, number_type)


class TestParametrizedType(unittest.TestCase):
    BUFFER_SIZE = 8192 * 4
    SUPPRESSED_HEALTH_CHECKS = (HealthCheck.too_slow,)

    @given(
        st.shared(default_parametrized_types(), key='test_pt_eq_reflexive'),
        st.shared(default_parametrized_types(), key='test_pt_eq_reflexive')
    )
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_equals_reflexive(self, ptype1, ptype2):
        """Test that an object equals itself."""
        self.assertIs(ptype1, ptype2)
        self.assertEqual(ptype1, ptype2)

    @given(st.data())
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
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
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_equals_transitive(self, ptype1, ptype2, ptype3):
        """Test that for objects :math:`\{x,y,z\}, x = y, y = z \iff x = z`."""
        self.assertEqual(ptype1, ptype2)
        self.assertEqual(ptype2, ptype3)
        self.assertEqual(ptype1, ptype3)

    @given(st.data())
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
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
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
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
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_hash_equals(self, ptype1, ptype2):
        """Test that when two objects are equal their hashes are equal."""
        self.assertEqual(ptype1, ptype2)
        self.assertEqual(hash(ptype1), hash(ptype2))

    @given(default_parametrized_types())
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_parametrized_type_pickle(self, ptype1):
        """Test that a ParametrizedType instance can be pickled and unpickled
        using the 0 protocol and the -1 protocol.

        """
        pickled_parametrized_type = pickle.dumps(ptype1, -1)
        unpickled_parametrized_type = pickle.loads(pickled_parametrized_type)

        self.assertEqual(ptype1, unpickled_parametrized_type)
        self.assertEqual(hash(ptype1), hash(unpickled_parametrized_type))

        pickled_parametrized_type = pickle.dumps(ptype1, 0)
        unpickled_parametrized_type = pickle.loads(pickled_parametrized_type)

        self.assertEqual(ptype1, unpickled_parametrized_type)
        self.assertEqual(hash(ptype1), hash(unpickled_parametrized_type))

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
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_parametrized_type_contains_when_equal(self, ptype1, ptype2):
        """Test that a ParametrizedType contains another ParametrizedType when
        the two types are equal.

        """
        self.assertEqual(ptype1, ptype2)
        self.assertIn(ptype1, ptype2)
        self.assertIn(ptype2, ptype1)

    @given(st.data())
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
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

    def test_parametrized_type_raises_TypeError_when_ptypes_empty(self):
        """Test that a ParametrizedType raises TypeError when constructued with 
        an empty parameter_types param.

        """
        base_type = Type(name='type1', meta='meta1')
        self.assertRaises(
            TypeError,
            ParametrizedType,
            (),
            {'name': 'test', 'base_type': base_type, 'parameter_types': ()}
        )

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

        parameter_type_1 = Type(
            name='ParameterType1',
            contained_types=frozenset(
                (parameter_contained_type_1, parameter_contained_type_2)
            ),
            meta='meta'
        )
        parameter_type_2 = Type(
            name='ParameterType1',
            contained_types=frozenset(
                (parameter_contained_type_1, parameter_contained_type_3)
            ),
            meta='meta'
        )

        another_parametrized_type = ParametrizedType(
            name='ParametrizedType1',
            base_type=base_type_1,
            parameter_types=(parameter_type_1, parameter_type_2),
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

        self.assertIn(parametrized_type, another_parametrized_type)
        self.assertNotIn(another_parametrized_type, parametrized_type)

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

        parameter_type_1 = Type(
            name='ParameterType1',
            contained_types=frozenset(
                (parameter_contained_type_1, parameter_contained_type_2)
            ),
            meta='meta'
        )
        parameter_type_2 = Type(
            name='ParameterType1',
            contained_types=frozenset(
                (parameter_contained_type_1, parameter_contained_type_3)
            ),
            meta='meta'
        )

        another_parametrized_type = ParametrizedType(
            name='ParametrizedType1',
            base_type=base_type_1,
            parameter_types=(parameter_type_1, parameter_type_2),
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

        self.assertNotIn(parametrized_type, another_parametrized_type)
        self.assertNotIn(another_parametrized_type, parametrized_type)

    def test_parametrized_type_contains_with_one_type_parameter(self):
        """Test that a ParametrizedType p0 contains another ParametrizedType p1
        when p0.base_type is a Type which is contained in p1.base_type, a Type.

        """
        int_type = Type(name='Int')
        float_type = Type(name='Float')

        list_type = Type(name='List')
        set_type = Type(name='Set')

        number_type = Type(
            name='Number',
            contained_types=frozenset((int_type, float_type))
        )
        collection_type = Type(
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

    def test_parametrized_type_not_contains_with_one_type_parameter(self):
        """Test that a ParametrizedType p0 does not contain another
        ParametrizedType p1 when p0.base_type is a Type which is not contained
        in p1.base_type, a Type.

        """
        int_type = Type(name='Int')
        float_type = Type(name='Float')
        str_type = Type(name='Str')

        list_type = Type(name='List')
        set_type = Type(name='Set')

        number_type = Type(
            name='Number',
            contained_types=frozenset((int_type, float_type))
        )
        collection_type = Type(
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

    def test_parametrized_type_contains_with_two_type_parameters(self):
        """Test that a ParametrizedType p0 contains another ParametrizedType p1
        when p0.base_type is a Type which is contained in p1.base_type,
        a Type.

        """
        int_type = Type(name='Int')
        float_type = Type(name='Float')

        list_type = Type(name='List')
        set_type = Type(name='Set')

        number_type = Type(
            name='Number',
            contained_types=frozenset((int_type, float_type))
        )
        integer_type = Type(
            name='Integer',
            contained_types=frozenset((int_type,))
        )
        collection_type = Type(
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

    def test_parametrized_type_not_contains_with_two_type_parameters(self):
        """Test that a ParametrizedType p0 does not contain another
        ParametrizedType p1 when p0.base_type is a Type which is not
        contained in p1.base_type, a Type.

        """
        int_type = Type(name='Int')
        float_type = Type(name='Float')
        str_type = Type(name='Str')

        list_type = Type(name='List')
        set_type = Type(name='Set')

        number_type = Type(
            name='Number',
            contained_types=frozenset((int_type, float_type))
        )
        string_type = Type(
            name='String',
            contained_types=frozenset((str_type,))
        )
        collection_type = Type(
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
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_parametrized_type_does_not_contain_Type(self, type1, ptype1):
        """Test that a ParametrizedType does not contain a Type"""
        self.assertNotIn(type1, ptype1)

    @given(default_types(), default_parametrized_types())
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_parametrized_type_does_not_contain_Type(
        self, type1, ptype1
    ):
        """Test that a ParametrizedType does not contain a Type"""
        self.assertNotIn(type1, ptype1)

    @given(
        default_parametrized_types(),
        st.text() | st.integers() | st.none() | st.booleans() | st.floats()
    )
    @settings(
        buffer_size=BUFFER_SIZE, suppress_health_check=SUPPRESSED_HEALTH_CHECKS
    )
    def test_parametrized_type_contains_raises_TypeError(self, ptype1, junk):
        """Test that a ParametrizedType does not implement __contains__ for
        arbitrary candidates.

        """
        self.assertRaises(TypeError, ptype1.__contains__, junk)
