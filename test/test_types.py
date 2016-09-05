import pickle
import unittest

from zoonomia.types import Type, ParametrizedType, GenericType


class TestType(unittest.TestCase):

    def test_type_equals(self):
        """Test that two Types having equal hashes are equal."""
        type1 = Type(name='one', meta='meta')
        type2 = Type(name='one', meta='meta')

        self.assertEqual(hash(type1), hash(type2))
        self.assertEqual(type1, type2)
        self.assertEqual(type2, type1)

    def test_type_not_equals(self):
        """Test that two Types having different hashes are not equal."""
        type1 = Type(name='one', meta='meta')
        type2 = Type(name='two', meta='meta')

        self.assertNotEqual(hash(type1), hash(type2))
        self.assertNotEqual(type1, type2)
        self.assertNotEqual(type2, type1)

    def test_type_pickle(self):
        """Test that a Type instance can be pickled and unpickled using the
        default protocol.

        """
        type1 = Type(name='one', meta='meta')

        pickled_type = pickle.dumps(type1)
        unpickled_type = pickle.loads(pickled_type)

        self.assertEqual(type1, unpickled_type)

    def test_type_contains__returns_True_when_types_equal(self):
        """Test that a Type contains another Type when the Types are equal."""
        type1 = Type(name='one', meta='meta')
        type2 = Type(name='one', meta='meta')

        self.assertEqual(type1, type2)
        self.assertIn(type1, type2)
        self.assertIn(type2, type1)

    def test_type_contains__returns_False_when_types_not_equal(self):
        """Test that a Type does not contain another Type when the Types are
        not equal.

        """
        type1 = Type(name='one', meta='meta')
        type2 = Type(name='two', meta='meta')

        self.assertNotEqual(type1, type2)
        self.assertNotIn(type1, type2)
        self.assertNotIn(type2, type1)

    def test_type_contains__returns_False_when_ParametrizedType(self):
        """Test that a Type does not contain a ParametrizedType."""
        plain_type = Type(name='one', meta='meta')
        parametrized_type = ParametrizedType(
            name='parametrized',
            base_type=plain_type,
            parameter_types=(plain_type,),
            meta='meta'
        )

        self.assertNotIn(parametrized_type, plain_type)

    def test_type_contains__returns_False_when_GenericType(self):
        """Test that a Type does not contain a GenericType."""
        plain_type = Type(name='one', meta='meta')
        generic_type = GenericType(
            name='generic', contained_types=(plain_type,), meta='meta'
        )

        self.assertNotIn(generic_type, plain_type)

    def test_type_contains__raises_TypeError(self):
        """Test that a Type does not implement __contains__ for arbitrary
        candidates.

        """
        plain_type = Type(name='one', meta='meta')

        self.assertRaises(TypeError, plain_type.__contains__, (int,))


class TestParametrizedType(unittest.TestCase):

    def test_parametrized_type_equals(self):
        """Test that two ParametrizedTypes having equal hashes are equal."""
        plain_type = Type(name='one', meta='meta')
        parametrized_type_1 = ParametrizedType(
            name='ParametrizedType',
            base_type=plain_type,
            parameter_types=(plain_type,),
            meta='meta'
        )
        parametrized_type_2 = ParametrizedType(
            name='ParametrizedType',
            base_type=plain_type,
            parameter_types=(plain_type,),
            meta='meta'
        )

        self.assertEqual(hash(parametrized_type_1), hash(parametrized_type_2))
        self.assertEqual(parametrized_type_1, parametrized_type_2)
        self.assertEqual(parametrized_type_2, parametrized_type_1)

    def test_parametrized_type_not_equals(self):
        """Test that two ParametrizedTypes having different hashes are not
        equal.

        """
        plain_type = Type(name='one', meta='meta')
        parametrized_type_1 = ParametrizedType(
            name='ParametrizedType1',
            base_type=plain_type,
            parameter_types=(plain_type,),
            meta='meta'
        )
        parametrized_type_2 = ParametrizedType(
            name='ParametrizedType2',
            base_type=plain_type,
            parameter_types=(plain_type,),
            meta='meta'
        )

        self.assertNotEqual(
            hash(parametrized_type_1), hash(parametrized_type_2)
        )
        self.assertNotEqual(parametrized_type_1, parametrized_type_2)
        self.assertNotEqual(parametrized_type_2, parametrized_type_1)

    def test_parametrized_type_pickle(self):
        """Test that a ParametrizedType instance can be pickled and unpickled
        using the default protocol.

        """
        plain_type = Type(name='one', meta='meta')
        parametrized_type = ParametrizedType(
            name='ParametrizedType1',
            base_type=plain_type,
            parameter_types=(plain_type,),
            meta='meta'
        )

        pickled_parametrized_type = pickle.dumps(parametrized_type)
        unpickled_parametrized_type = pickle.loads(pickled_parametrized_type)

        self.assertEqual(parametrized_type, unpickled_parametrized_type)

    def test_parametrized_type_contains_when_equal(self):
        """Test that a ParametrizedType contains another ParametrizedType when
        the two types are equal.

        """
        plain_type = Type(name='one', meta='meta')
        parametrized_type_1 = ParametrizedType(
            name='ParametrizedType',
            base_type=plain_type,
            parameter_types=(plain_type,),
            meta='meta'
        )
        parametrized_type_2 = ParametrizedType(
            name='ParametrizedType',
            base_type=plain_type,
            parameter_types=(plain_type,),
            meta='meta'
        )

        self.assertEqual(parametrized_type_1, parametrized_type_2)
        self.assertIn(parametrized_type_1, parametrized_type_2)
        self.assertIn(parametrized_type_2, parametrized_type_1)

    def test_parametrized_type_not_contains_when_len_parameters_ne(self):
        """Test that a ParametrizedType does not contain another
        ParametrizedType *candidate* when the number of *candidate's*
        parameters does not equal the number of *self's* parameters.

        """
        base_type_1 = Type(name='base', meta='base')
        base_type_2 = Type(name='base', meta='base')

        self.assertEqual(base_type_1, base_type_2)

        parameter_type_1 = Type(name='parameter1', meta='meta')
        parameter_type_2 = Type(name='parameter2', meta='meta')
        parametrized_type_1 = ParametrizedType(
            name='ParametrizedType1',
            base_type=base_type_1,
            parameter_types=(parameter_type_1,),
            meta='meta'
        )
        parametrized_type_2 = ParametrizedType(
            name='ParametrizedType2',
            base_type=base_type_2,
            parameter_types=(parameter_type_1, parameter_type_2),
            meta='meta'
        )

        self.assertNotIn(parametrized_type_1, parametrized_type_2)
        self.assertNotIn(parametrized_type_2, parametrized_type_1)

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

    def test_parametrized_type_does_not_contain_Type(self):
        """Test that a ParametrizedType does not contain a Type"""
        base_type = Type(name='BaseType', meta='meta')
        parameter_type = Type(name='ParameterType', meta='meta')
        parametrized_type = ParametrizedType(
            name='ParametrizedType',
            base_type=base_type,
            parameter_types=(parameter_type,),
            meta='meta'
        )

        self.assertNotIn(base_type, parametrized_type)
        self.assertNotIn(parameter_type, parametrized_type)

    def test_parametrized_type_does_not_contain_GenericType(self):
        """Test that a ParametrizedType does not contain a GenericType"""
        base_type = Type(name='BaseType', meta='meta')
        parameter_type = GenericType(
            name='ParameterType',
            contained_types=frozenset((base_type,)),
            meta='meta'
        )
        parametrized_type = ParametrizedType(
            name='ParametrizedType',
            base_type=base_type,
            parameter_types=(parameter_type,),
            meta='meta'
        )

        self.assertNotIn(base_type, parametrized_type)
        self.assertNotIn(parameter_type, parametrized_type)

    def test_parametrized_type_contains_raises_TypeError(self):
        """Test that a ParametrizedType does not implement __contains__ for
        arbitrary candidates.

        """
        base_type = Type(name='BaseType', meta='meta')
        parameter_type = Type(name='ParameterType', meta='meta')
        parametrized_type = ParametrizedType(
            name='ParametrizedType',
            base_type=base_type,
            parameter_types=(parameter_type,),
            meta='meta'
        )

        self.assertRaises(TypeError, parametrized_type.__contains__, type)


class TestGenericType(unittest.TestCase):

    def test_generic_type_equals(self):
        """Test that two GenericTypes having equal hashes are equal."""
        type1 = Type(name='one', meta='meta')
        generic_type_1 = GenericType(
            name='GenericType',
            contained_types=frozenset((type1,)),
            meta='meta'
        )
        generic_type_2 = GenericType(
            name='GenericType',
            contained_types=frozenset((type1,)),
            meta='meta'
        )

        self.assertEqual(hash(generic_type_1), hash(generic_type_2))
        self.assertEqual(generic_type_1, generic_type_2)
        self.assertEqual(generic_type_2, generic_type_1)

    def test_generic_type_not_equals(self):
        """Test that two GenericTypes having different hashes are not equal."""
        type1 = Type(name='one', meta='meta')
        type2 = Type(name='two', meta='meta')
        generic_type_1 = GenericType(
            name='GenericType1',
            contained_types=frozenset((type1,)),
            meta='meta'
        )
        generic_type_2 = GenericType(
            name='GenericType2',
            contained_types=frozenset((type2,)),
            meta='meta'
        )

        self.assertNotEqual(hash(generic_type_1), hash(generic_type_2))
        self.assertNotEqual(generic_type_1, generic_type_2)
        self.assertNotEqual(generic_type_2, generic_type_1)

    def test_generic_type_pickle(self):
        """Test that a GenericType instance can be pickled and unpickled using
        the default protocol.

        """
        type1 = Type(name='one', meta='meta')
        generic_type = GenericType(
            name='GenericType',
            contained_types=frozenset((type1,)),
            meta='meta'
        )

        pickled_generic_type = pickle.dumps(generic_type)
        unpickled_generic_type = pickle.loads(pickled_generic_type)

        self.assertEqual(generic_type, unpickled_generic_type)

    def test_generic_type_contains_equal_generic_type(self):
        """Test that a GenericType contains another GenericType if the two
        GenericTypes are equal.

        """
        type1 = Type(name='one', meta='meta')
        generic_type_1 = GenericType(
            name='GenericType',
            contained_types=frozenset((type1,)),
            meta='meta'
        )
        generic_type_2 = GenericType(
            name='GenericType',
            contained_types=frozenset((type1,)),
            meta='meta'
        )

        self.assertEqual(generic_type_1, generic_type_2)
        self.assertEqual(generic_type_2, generic_type_1)
        self.assertIn(generic_type_1, generic_type_2)
        self.assertIn(generic_type_2, generic_type_1)

    def test_generic_type_not_contains_unequal_generic_type(self):
        """Test that a GenericType does not contain another GenericType if the
        two GenericTypes are unequal.

        """
        type1 = Type(name='one', meta='meta')
        type2 = Type(name='two', meta='meta')
        generic_type_1 = GenericType(
            name='GenericType1',
            contained_types=frozenset((type1,)),
            meta='meta'
        )
        generic_type_2 = GenericType(
            name='GenericType2',
            contained_types=frozenset((type2,)),
            meta='meta'
        )

        self.assertNotEqual(generic_type_1, generic_type_2)
        self.assertNotEqual(generic_type_2, generic_type_1)
        self.assertNotIn(generic_type_1, generic_type_2)
        self.assertNotIn(generic_type_2, generic_type_1)

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

    def test_generic_type_contains_other_when_other_equals_self(self):
        """Test that a GenericType contains another GenericType when the two
        generics are equal.

        """
        hail_satan = Type(name='666', meta='meta')

        generic_type_1 = GenericType(
            name='GenericType',
            contained_types=frozenset((hail_satan,)),
            meta='rull meta'
        )
        generic_type_2 = GenericType(
            name='GenericType',
            contained_types=frozenset((hail_satan,)),
            meta='rull meta'
        )

        self.assertEqual(generic_type_1, generic_type_2)
        self.assertEqual(generic_type_2, generic_type_1)

        self.assertIn(generic_type_1, generic_type_2)
        self.assertIn(generic_type_2, generic_type_1)
