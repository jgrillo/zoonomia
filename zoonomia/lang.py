from threading import Lock

from zoonomia.types import Type, GenericType, ParametrizedType


class Symbol(object):

    __slots__ = ('name', 'dtype', '_hash')

    def __init__(self, name, dtype):
        """A Symbol instance represents some data *symbol* in an alien
        execution environment.

        :param name:
            The name of some symbol in the execution environment.

        :type name: str

        :param dtype:
            The type of the underlying data in the execution environment.

        :type dtype: Type or GenericType or ParametrizedType

        """
        self.name = name
        self.dtype = dtype
        self._hash = hash((self.name, self.dtype))

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __ne__(self, other):
        return hash(self) != hash(other)

    def __repr__(self):
        return 'Symbol(name={symbol}, dtype={dtype})'.format(
            symbol=repr(self.name), dtype=repr(self.dtype)
        )


class Call(object):

    __slots__ = ('target', 'symbol', 'args', 'dtype', '_operator', '_hash')

    def __init__(self, target, operator, args):
        """A Call instance represents a function call in an alien execution
        environment. A Call associates an Operator having a particular type
        *signature* and a tuple of concrete arguments *args* of the
        appropriate types with a binding *target* in the execution environment.

        :param target:
            The symbol to which the results of this call will be bound in the
            execution environment.

        :type target: Symbol

        :param operator:
            The Operator corresponding to the underlying function in the
            execution environment.

        :type operator: Operator

        :param args:
            A tuple of Symbols corresponding to data in the execution
            environment representing arguments to the underlying function.

        :type args: tuple[zoonomia.solution.Symbol]

        """
        self.target = target
        self.dtype = operator.dtype
        self.symbol = operator.symbol
        self._operator = operator
        self.args = args
        self._hash = hash(
            (self.target, self.dtype, self.symbol, self._operator, self.args)
        )

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __ne__(self, other):
        return hash(self) != hash(other)

    def __repr__(self):
        return (
            'Call(target={target}, operator={operator}, args={args})'
        ).format(
            target=repr(self.target),
            operator=repr(self._operator),
            args=repr(self.args)
        )


class Operator(object):

    __slots__ = ('symbol', 'signature', 'dtype', '_hash')

    def __init__(self, symbol, signature=tuple()):
        """An Operator is an abstraction over some underlying function, perhaps
        in an alien programming language or environment, which takes arguments
        conforming to the given type *signature* and returns a value of type
        *dtype*. If an operator's signature is empty it is considered a
        terminal operator, otherwise it is considered a basis operator.

        :param symbol:
            The symbol of the underlying function or data in the execution
            environment.

        :type symbol: Symbol

        :param signature:
            The type signature of the underlying function. Defaults to an empty
            tuple, indicating that the operator is a terminal operator.

        :type signature: tuple[Type|ParametrizedType|GenericType]

        """
        self.symbol = symbol
        self.signature = signature
        self.dtype = symbol.dtype
        self._hash = hash((self.symbol, self.signature, self.dtype))

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __ne__(self, other):
        return hash(self) != hash(other)

    def __repr__(self):
        return (
            'Operator(symbol={symbol}, signature={signature}, dtype={dtype})'
        ).format(
            symbol=repr(self.symbol),
            signature=repr(self.signature),
            dtype=repr(self.dtype)
        )

    def __str__(self):
        return self.symbol.name

    def __call__(self, target=None, args=None):
        """Symbolically "call" this instance's *symbol* on the *args*. Returns
        a *zoonomia.solution.Call* object which represents an abstract function
        call.

        :param target:
            The symbol to which the results of this call will be bound in the
            execution environment.

        :type target: Symbol

        :param args:
            Zero or more *zoonomia.solution.Operator* instances whose string
            (symbol) representations will form the arguments for the function
            call in the client language.

        :type args: tuple[zoonomia.solution.Symbol|zoonomia.solution.Call]

        :return:
            Abstract representation of a function call.

        :rtype: zoonomia.solution.Call or zoonomia.solution.Symbol

        """
        if args is not None and target is not None:
            return Call(target=target, operator=self, args=args)
        elif args is None and target is None:
            return self.symbol
        else:
            raise TypeError('must specify target if not a terminal operator')


class OperatorSet(object):

    __slots__ = ('operators', '_dtype_to_operators', '_lock')

    def __init__(self, operators):
        """An OperatorSet contains Operators and also provides a convenient
        mapping which allows a user to select the subset of operators having
        output types which can be resolved to a particular type.

        :param operators:
            An iterable of Operators to initialize this instance with.

        :type operators: collections.Iterable[zoonomia.solution.Operator]

        """
        self.operators = frozenset(operators)
        self._lock = Lock()
        self._dtype_to_operators = dict()

        for operator in self.operators:
            self._dtype_to_operators[operator.dtype] = frozenset(
                o for o in self.operators if o.dtype in operator.dtype
            )

    def union(self, other):
        """Returns an OperatorSet containing those elements which are in the
        union of both this OperatorSet and the other OperatorSet.

        :param other: Another OperatorSet.
        :type other: zoonomia.lang.OperatorSet

        :return: An OperatorSet
        :rtype: zoonomia.solution.OperatorSet

        """
        return OperatorSet(
            operators=self.operators.union(other.operators)
        )

    def __iter__(self):
        """Returns an iterator over this instance's operators.

        :return: An iterator of operators.
        :rtype: collections.Iterator[Operator]
        """
        return iter(self.operators)

    def __getitem__(self, item):
        """Select those Operators which have *dtype* that can be resolved to
        *item*. That is, select all the Operators whose return type is
        contained by *item*.

        :param item: A type.

        :type item: zoonomia.types.Type or zoonomia.types.GenericType

        :raise KeyError:
            If the given *item* has no associated operators in this
            OperatorSet.

        :raise TypeError:
            If *item* is not a Type, GenericType, or ParametrizedType.

        :return:
            The operators belonging to this OperatorSet which match the
            signature or dtype *item*.

        :rtype: frozenset[Operator]

        """
        if isinstance(item, (Type, GenericType, ParametrizedType)):
            if item not in self._dtype_to_operators.keys():
                with self._lock:
                    ts = self._dtype_to_operators.keys()

                    if item not in ts:
                        contains = False
                        resolved_types = []

                        for t in ts:
                            if t in item:  # t can be resolved to item
                                contains = True
                                resolved_types.append(
                                    self._dtype_to_operators[t]
                                )

                        if contains:
                            self._dtype_to_operators[item] = frozenset(
                                resolved_types
                            )
                        else:
                            raise KeyError(item)

            return self._dtype_to_operators[item]
        else:
            raise TypeError(
                'item must be a Type, GenericType, or ParametrizedType'
            )

    def __repr__(self):
        return 'OperatorSet({0})'.format(
            '{' + ', '.join(map(repr, self.operators)) + '}'
        )
