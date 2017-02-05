from threading import Lock

from zoonomia.types import Type, GenericType, ParametrizedType


class Symbol(object):

    __slots__ = ('name', 'dtype', '_hash')

    def __new__(cls, name, dtype):
        """A Symbol instance represents some data *symbol* in an alien
        execution environment.

        :param name:
            The name of some symbol in the execution environment.

        :type name: str

        :param dtype:
            The type of the underlying data in the execution environment.

        :type dtype: Type or GenericType or ParametrizedType

        """
        obj = super(Symbol, cls).__new__(cls)
        obj.name = name
        obj.dtype = dtype
        obj._hash = hash((obj.name, obj.dtype))
        return obj

    def __getstate__(self):
        return self.name, self.dtype, self._hash

    def __setstate__(self, state):
        name, dtype, _hash = state

        self.name = name
        self.dtype = dtype
        self._hash = _hash

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        return self.name == other.name and self.dtype == other.dtype

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return 'Symbol(name={symbol}, dtype={dtype})'.format(
            symbol=repr(self.name), dtype=repr(self.dtype)
        )


class Operator(object):

    __slots__ = ('symbol', 'signature', 'dtype', '_hash')

    def __new__(cls, symbol, signature=tuple()):
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
        obj = super(Operator, cls).__new__(cls)
        obj.symbol = symbol
        obj.signature = signature
        obj.dtype = symbol.dtype
        obj._hash = hash((obj.symbol, obj.signature, obj.dtype))
        return obj

    def __getstate__(self):
        return self.symbol, self.signature, self.dtype, self._hash

    def __setstate__(self, state):
        symbol, signature, dtype, _hash = state

        self.symbol = symbol
        self.signature = signature
        self.dtype = dtype
        self._hash = _hash

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        return (
            self.symbol == other.symbol and
            self.signature == other.signature and
            self.dtype == other.dtype
        )

    def __ne__(self, other):
        return not self.__eq__(other)

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


class Call(object):

    __slots__ = ('target', 'symbol', 'args', 'dtype', 'operator', '_hash')

    def __new__(cls, target, operator, args):
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
        obj = super(Call, cls).__new__(cls)
        obj.target = target
        obj.dtype = operator.dtype
        obj.symbol = operator.symbol
        obj.operator = operator
        obj.args = args
        obj._hash = hash(
            (obj.target, obj.dtype, obj.symbol, obj.operator, obj.args)
        )
        return obj

    def __getstate__(self):
        return (
            self.target, self.symbol, self.args, self.dtype, self.operator,
            self._hash
        )

    def __setstate__(self, state):
        target, symbol, args, dtype, operator, _hash = state

        self.target = target
        self.symbol = symbol
        self.args = args
        self.dtype = dtype
        self.operator = operator
        self._hash = _hash

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        return (
            self.target == other.target and
            self.symbol == other.symbol and
            self.args == other.args and
            self.dtype == other.dtype and
            self.operator == other.operator
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return (
            'Call(target={target}, operator={operator}, args={args})'
        ).format(
            target=repr(self.target),
            operator=repr(self.operator),
            args=repr(self.args)
        )


class OperatorTable(object):

    __slots__ = ('operators', '_dtype_to_operators', '_lock', '_hash')

    def __new__(cls, operators):
        """An OperatorTable contains Operators and also provides a convenient
        mapping which allows a user to select the subset of operators having
        output types which can be resolved to a particular type. This object is
        more or less modeled after Montana's *types possibility table*. See
        Montana1995.

        :param operators:
            An iterable of Operators to initialize this instance with.

        :type operators: collections.Iterable[zoonomia.solution.Operator]

        """
        obj = super(OperatorTable, cls).__new__(cls)
        obj.operators = frozenset(operators)
        obj._lock = Lock()
        obj._dtype_to_operators = dict()
        obj._hash = hash(('OperatorTable', obj.operators))

        for operator in obj.operators:
            obj._dtype_to_operators[operator.dtype] = frozenset(
                o for o in obj.operators if o.dtype in operator.dtype
            )

        return obj

    def __getstate__(self):
        return self.operators, self._dtype_to_operators, self._hash

    def __setstate__(self, state):
        operators, _dtype_to_operators, _hash = state

        self.operators = operators
        self._lock = Lock()
        self._dtype_to_operators = _dtype_to_operators
        self._hash = _hash

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        return self.operators == other.operators

    def __ne__(self, other):
        return not self.__eq__(other)

    def union(self, other):
        """Returns an OperatorTable containing those elements which are members
        of both this OperatorTable and the other OperatorTable.

        :param other: Another OperatorTable.
        :type other: zoonomia.lang.OperatorTable

        :return: An OperatorTable
        :rtype: zoonomia.solution.OperatorTable

        """
        return OperatorTable(operators=self.operators.union(other.operators))

    def __iter__(self):
        """Returns an iterator over this instance's operators.

        :return: An iterator of operators.
        :rtype: collections.Iterator[Operator]
        """
        return iter(self.operators)

    def __getitem__(self, dtype):
        """Select those Operators for which the give *dtype* can be resolved to
        their *dtype*. That is, select all the Operators whose return type is
        contained by *dtype*.

        :param dtype: A type.

        :type dtype: Type | GenericType | ParametrizedType

        :raise KeyError:
            If the given *dtype* has no associated operators in this
            OperatorTable.

        :raise TypeError:
            If *dtype* is not a Type, GenericType, or ParametrizedType.

        :return:
            The Operators belonging to this OperatorTable for which the given
            *dtype* can be resolved to their return *dtype*.

        :rtype: frozenset[Operator]

        """
        if isinstance(dtype, (Type, GenericType, ParametrizedType)):
            if dtype in self:
                return self._dtype_to_operators[dtype]
            else:
                raise KeyError(dtype)
        else:
            raise TypeError(
                'dtype must be a Type, GenericType, or ParametrizedType'
            )

    def __contains__(self, dtype):
        """Check whether this OperatorTable contains any Operators
        corresponding to the given *dtype*.

        :param dtype: A type.

        :type dtype: Type | GenericType | ParametrizedType

        :raise TypeError:
            If *dtype* is not a Type, GenericType, or ParametrizedType.

        :return:
            Whether this OperatorTable contains any Operators for which the
            given *dtype* can be resolved to their return *dtype*.

        :rtype: bool

        """
        if isinstance(dtype, (Type, GenericType, ParametrizedType)):
            if dtype not in self._dtype_to_operators:
                with self._lock:
                    ts = self._dtype_to_operators.keys()

                    if dtype not in ts:
                        contains = False
                        resolved_types = []

                        for t in ts:
                            if t in dtype:  # dtype can be resolved to t
                                contains = True

                                for o in self._dtype_to_operators[t]:
                                    resolved_types.append(o)

                        if contains:
                            self._dtype_to_operators[dtype] = frozenset(
                                resolved_types
                            )

            return dtype in self._dtype_to_operators
        else:
            raise TypeError(
                'dtype must be a Type, GenericType, or ParametrizedType'
            )

    def __repr__(self):
        return 'OperatorTable({0})'.format(
            '{' + ', '.join(map(repr, self.operators)) + '}'
        )
