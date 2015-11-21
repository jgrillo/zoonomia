

def full(max_depth, basis_set, terminal_set, dtype):  # TODO: clean up docs
    """An implementation of Koza's full tree generation procedure. Returns
    a candidate solution satisfying the property that all branches of the
    solution's tree representation have path length from root to leaf equal to
    max_depth. See Koza1992.

    :param int max_depth: The maximum path length from root to leaf.
    :param BasisSet<BasisOperator> basis_set:
    :param TerminalSet<TerminalOperator> terminal_set:
    :param type dtype: The return type of the resulting solution's functional
    representation.
    :return solution: A candidate solution.
    :rtype zoonomia.solution.Solution:
    """
    pass  # FIXME: implement


def grow(max_depth, basis_set, terminal_set, dtype):  # TODO: clean up docs
    """An implementation of Koza's grow tree generation procedure. Returns
    a candidate solution whose graph representation has path length from root
    to leaf constrained to the interval [1, max_depth]. See Koza1992.

    :param int max_depth: The max path length from root to leaf.
    :param BasisSet<BasisOperator> basis_set:
    :param TerminalSet<TerminalOperator> terminal_set:
    :param type dtype: The return type of the resulting solution's functional
    representation.
    :return solution: A candidate solution.
    :rtype zoonomia.solution.Solution:
    """
    pass  # FIXME: implement


class BasisOperator(object):

    __slots__ = ('func', 'arity', 'input_dtypes', 'dtype', '_hash')

    def __init__(self, func, arity, input_dtypes=None, dtype=None):
        """A BasisOperator represents a member of the basis set. A
        BasisOperator must have arity greater than 0, and can optionally
        specify type information which is used to constrain the shape of
        candidate solutions.

        :param Function<(T0, ..., TN), U> func: A function of arity N+1 which
        takes N+1 arguments having type signature (T0, ..., TN) to a type U.
        :param int arity: The number of arguments. If input_dtypes is present,
        arity must match the cardinality of input_dtypes.
        :param tuple<type> input_dtypes: (Optional) type signature for func.
        You should make sure this matches the actual types that func expects,
        as this relationship is never validated. Instead, input_dtypes is used
        to constrain the shape of candidate solutions.
        :param U dtype: (Optional) output type for func. You should make sure
        this matches the actual type returned by func because it is used to
        constrain the shape of candidate solutions.
        """
        if arity <= 0:
            raise TypeError('Arity must be greater than 0')
        if input_dtypes is not None:
            if len(input_dtypes) != arity:
                raise TypeError(
                    ('arity={arity} does not match '
                     'len(input_dtypes)={cardinality}').format(
                        arity=arity, cardinality=len(input_dtypes)
                    )
                )
        self.func = func
        self.arity = arity
        self.input_dtypes = input_dtypes
        self.dtype = dtype
        result = 17  # FIXME this is turrbl
        result = 31 * result + hash(self.func)
        self._hash = result

    def __repr__(self):
        return (
            'BasisOperator(func={func}, arity={arity}, '
            'input_dtypes={input_dtypes}, dtype={dtype})'
        ).format(
            func=repr(self.func),
            arity=repr(self.arity),
            input_dtypes=repr(self.input_dtypes),
            output_dtypes=repr(self.dtype)
        )

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __hash__(self):
        return self._hash


class TerminalOperator(object):

    __slots__ = ('source', 'dtype', '_hash')

    def __init__(self, source, dtype=None):
        """A TerminalOperator represents a member of the terminal set. A
        TerminalOperator acts as a source which emits data of type dtype.

        :param iterator<T> source: An iterator which yields data of type T.
        :param T dtype: (Optional) the output type for source. You should make
        sure this matches the actual type yielded by source because it is used
        to constrain the shape of candidate solutions.
        """
        self.source = source
        self.dtype = dtype
        result = 17  # FIXME: this is turrbl
        result = 31 * result + hash(source)
        self._hash = result

    def __repr__(self):
        return 'TerminalOperator(source={source}, dtype={dtype})'.format(
            source=repr(self.source),
            dtype=repr(self.dtype)
        )

    def __iter__(self):
        return iter(self.source)

    def __next__(self):
        return self.source.next()

    def next(self):
        return self.__next__()

    def __hash__(self):
        return self._hash


class BasisSet(frozenset):

    def __init__(self, basis_operators):  # TODO: more detailed docs
        """A BasisSet contains BasisOperators and also provides a convenient
        mapping which allows a user to select either the subset of basis
        operators having output type dtype or the subset of basis operators
        having a particular type signature.

        :param iterable<BasisOperator> basis_operators:
        """
        super(BasisSet, self).__init__(basis_operators)
        self._DTYPE_TO_OPERATORS = {
            operator.dtype: frozenset(
                filter(lambda o: o.dtype is operator.dtype, self)
            )
            for operator in self
        }
        self._SIGNATURE_TO_OPERATORS = {
            (operator.input_dtypes, operator.arity): frozenset(
                filter(
                    lambda o: (
                        o.input_dtypes == operator.input_dtypes and
                        o.arity == operator.arity
                    ),
                    self
                )
            )
            for operator in self
        }

    def __getitem__(self, item):
        if isinstance(item, tuple):
            return self._SIGNATURE_TO_OPERATORS[item]
        else:
            return self._DTYPE_TO_OPERATORS[item]

    def __repr__(self):
        return 'BasisSet()'.format(
            # FIXME
        )


class TerminalSet(frozenset):

    def __init__(self, terminal_operators):  # TODO: more detailed docs
        """A TerminalSet contains TerminalOperators and also provides a
        convenient mapping which allows a user to select the subset of terminal
        operators having a particular output dtype.

        :param iterable<TerminalOperator> terminal_operators:
        """
        super(TerminalSet, self).__init__(terminal_operators)
        self._DTYPE_TO_OPERATORS = {
            operator.dtype: frozenset(
                filter(lambda o: o.dtype is operator.dtype, self)
            )
            for operator in self
        }

    def __getitem__(self, item):
        return self._DTYPE_TO_OPERATORS[item]

    def __repr__(self):
        return 'TerminalSet()'.format(
            # FIXME
        )

