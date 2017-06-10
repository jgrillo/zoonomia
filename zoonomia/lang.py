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

from threading import Lock

from zoonomia.types import Type, ParametrizedType


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

        :type dtype: Type | ParametrizedType

        """
        self.name = name
        self.dtype = dtype
        self._hash = hash(('Symbol', self.name, self.dtype))

    def __getstate__(self):
        return {'name': self.name, 'dtype': self.dtype}

    def __setstate__(self, state):
        self.__init__(state['name'], state['dtype'])

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        if isinstance(other, Symbol):
            return self.name == other.name and self.dtype == other.dtype
        else:
            return NotImplemented

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return 'Symbol(name={symbol}, dtype={dtype})'.format(
            symbol=repr(self.name), dtype=repr(self.dtype)
        )

    def format_str(self):
        return self.name + '({0}) -> ' + self.dtype.name


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

        :type signature: tuple[Type|ParametrizedType]

        """
        self.symbol = symbol
        self.signature = signature
        self.dtype = symbol.dtype
        self._hash = hash(('Operator', self.symbol, self.signature, self.dtype))

    def __getstate__(self):
        return {'symbol': self.symbol, 'signature': self.signature}

    def __setstate__(self, state):
        self.__init__(state['symbol'], state['signature'])

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        if isinstance(other, Operator):
            return (
                self.symbol == other.symbol and
                self.signature == other.signature and
                self.dtype == other.dtype
            )
        else:
            return NotImplemented

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

    def signature_str(self):
        return self.symbol.format_str().format(
            ', '.join(t.name for t in self.signature)
        )

    def __call__(self, target=None, args=None):
        """Symbolically "call" this instance's *symbol* on the *args*. Returns
        a *Call* object which represents an abstract function
        call.

        :param target:
            The symbol to which the results of this call will be bound in the
            execution environment.

        :type target: Symbol

        :param args:
            Zero or more *Operator* instances whose string (symbol) 
            representations will form the arguments for the function call in 
            the client language.

        :type args: tuple[Symbol|Call]

        :raise TypeError:
            If args doesn't match signature or if target is absent and args are
            present (i.e. this is a basis operator and args are absent).

        :return:
            Abstract representation of a function call.

        :rtype: Call|Symbol

        """
        if args is not None and target is not None:
            if len(args) != len(self.signature):
                raise TypeError('args and signature must have same size.')
            elif not all(a.dtype in s for a, s in zip(args, self.signature)):
                raise TypeError('arg types must match the signature.')
            else:
                return Call(target=target, operator=self, args=args)
        elif args is None and target is None:
            return self.symbol
        else:
            raise TypeError('must specify target if not a terminal operator')


class Call(object):

    __slots__ = ('target', 'symbol', 'args', 'dtype', 'operator', '_hash')

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

        :type args: tuple[Symbol]

        """
        self.target = target
        self.dtype = operator.dtype
        self.symbol = operator.symbol
        self.operator = operator
        self.args = args
        self._hash = hash((
            'Call',
            self.target,
            self.dtype,
            self.symbol,
            self.operator,
            self.args
        ))

    def __getstate__(self):
        return {
            'target': self.target, 'operator': self.operator, 'args': self.args
        }

    def __setstate__(self, state):
        self.__init__(state['target'], state['operator'], state['args'])

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        if isinstance(other, Call):
            return (
                self.target == other.target and
                self.symbol == other.symbol and
                self.args == other.args and
                self.dtype == other.dtype and
                self.operator == other.operator
            )
        else:
            return NotImplemented

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

    def __init__(self, operators):
        """An OperatorTable contains Operators and also provides a convenient
        mapping which allows a user to select the subset of operators having
        output types which can be resolved to a particular type. This object is
        more or less modeled after Montana's *types possibility table*. See
        Montana1995.

        :param operators:
            An iterator of Operators to initialize this instance with.

        :type operators: collections.Iterator[Operator]

        """
        self.operators = frozenset(operators)
        self._lock = Lock()
        self._dtype_to_operators = dict()
        self._hash = hash(('OperatorTable', self.operators))

        for operator in self.operators:
            self._dtype_to_operators[operator.dtype] = frozenset(
                o for o in self.operators if o.dtype in operator.dtype
            )

    def __getstate__(self):
        return {'operators': self.operators}

    def __setstate__(self, state):
        self.__init__(state['operators'])

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        if isinstance(other, OperatorTable):
            return self.operators == other.operators
        else:
            return NotImplemented

    def __ne__(self, other):
        return not self.__eq__(other)

    def union(self, other):
        """Returns an OperatorTable containing those elements which are members
        of both this OperatorTable and the other OperatorTable.

        :param other: Another OperatorTable.
        :type other: OperatorTable

        :return: An OperatorTable
        :rtype: OperatorTable

        """
        if isinstance(other, OperatorTable):
            return OperatorTable(
                operators=self.operators.union(other.operators)
            )
        else:
            raise TypeError(
                'other must be OperatorTable, found: {0}'.format(repr(other))
            )

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

        :type dtype: Type | ParametrizedType

        :raise KeyError:
            If the given *dtype* has no associated operators in this
            OperatorTable.

        :raise TypeError:
            If *dtype* is not a Type or ParametrizedType.

        :return:
            The Operators belonging to this OperatorTable for which the given
            *dtype* can be resolved to their return *dtype*.

        :rtype: frozenset[Operator]

        """
        if isinstance(dtype, (Type, ParametrizedType)):
            if dtype in self:  # N.B.: This does the necessary synchronization
                return self._dtype_to_operators[dtype]
            else:
                raise KeyError(dtype)
        else:
            raise TypeError(
                'dtype must be a Type or ParametrizedType, found: {0}'.format(
                    repr(dtype)
                )
            )

    def __contains__(self, dtype):
        """Check whether this OperatorTable contains any Operators
        corresponding to the given *dtype*.

        :param dtype: A type.

        :type dtype: Type | ParametrizedType

        :raise TypeError:
            If *dtype* is not a Type or ParametrizedType.

        :return:
            Whether this OperatorTable contains any Operators for which the
            given *dtype* can be resolved to their return *dtype*.

        :rtype: bool

        """
        if isinstance(dtype, (Type, ParametrizedType)):
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
                'dtype must be a Type or ParametrizedType, found: {0}'.format(
                    repr(dtype)
                )
            )

    def __repr__(self):
        return 'OperatorTable({0})'.format(
            '{' + ', '.join(map(repr, self.operators)) + '}'
        )
