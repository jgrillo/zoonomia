import itertools

import networkx as nx

from zoonomia.helper import compute_hash
from zoonomia.solution import Solution


def full(max_depth, basis_set, terminal_set, dtype, objectives, rng):  # TODO: clean up docs
    """An implementation of Koza's full tree generation strategy augmented to
    take type information into account. Returns a candidate solution satisfying
    the property that all branches of the solution's tree representation have
    path length from root to leaf equal to max_depth. See Koza1992 and
    Montana1995.

    :param int max_depth: The maximum path length from root to leaf.
    :param BasisSet<BasisOperator> basis_set:
    :param TerminalSet<TerminalOperator> terminal_set:
    :param type dtype: The return type of the resulting solution's functional
    representation.
    :param tuple<zoonomia.solution.Objective> objectives:
    :param random.Random rng:
    :return solution: A candidate solution.
    :rtype zoonomia.solution.Solution:
    """
    dag = nx.DiGraph()

    if max_depth <= 1:
        node = Node(operator=rng.choice(terminal_set[dtype]))
    else:
        node = Node(operator=rng.choice(basis_set[dtype]))

    dag.add_node(node)

    depth = 1
    parents = [node]

    while depth < max_depth:
        depth += 1
        children = []

        for parent in parents:
            for idx, t in enumerate(parent.operator.signature):
                node = Node(
                    operator=rng.choice(terminal_set[t])
                ) if depth == max_depth else Node(
                    operator=rng.choice(basis_set[dtype])
                )

                children.append(node)
                dag.add_node(node)
                dag.add_edge(
                    u=node, v=parent, attr_dict={'dtype': t, 'pos': idx}
                )

        parents = children

    return Solution(graph=dag, objectives=objectives)  # TODO: decouple Solution from Objectives?


def grow(max_depth, basis_set, terminal_set, dtype, objectives, rng):  # TODO: clean up docs
    """An implementation of Koza's grow tree generation strategy augmented to
    take type information into account. Returns a candidate solution whose
    graph representation has maximum path length from root to leaf constrained
    to the interval [1, max_depth]. See Koza1992 and Montana1995.

    :param int max_depth: The max path length from root to leaf.
    :param BasisSet<BasisOperator> basis_set:
    :param TerminalSet<TerminalOperator> terminal_set:
    :param type dtype: The return type of the resulting solution's functional
    representation.
    :param typle<zoonomia.solution.Objective> objectives:
    :param random.Random rng:
    :return solution: A candidate solution.
    :rtype zoonomia.solution.Solution:
    """
    dag = nx.DiGraph()

    if max_depth <= 1:
        node = Node(operator=rng.choice(terminal_set[dtype]))
    else:
        node = Node(operator=rng.choice(basis_set.union(terminal_set)[dtype]))

    dag.add_node(node)

    depth = 1
    parents = [node]

    while depth < max_depth:
        depth += 1
        children = []

        for parent in parents:
            for idx, t in enumerate(parent.operator.signature):
                if depth == max_depth:
                    node = Node(operator=rng.choice(terminal_set[t]))
                else:
                    operator = rng.choice(basis_set.union(terminal_set)[t])
                    if isinstance(operator, BasisOperator):
                        node = Node(operator=operator)
                        children.append(node)
                    else:
                        node = Node(operator=operator)

                dag.add_node(node)
                dag.add_edge(
                    u=node, v=parent, attr_dict={'dtype': t, 'pos': idx}
                )

        parents = children

    return Solution(graph=dag, objectives=objectives)  # TODO: decouple Solution from Objectives?


def mutate_subtree(solution):
    pass  # FIXME: implement


def mutate_node(solution):
    pass  # FIXME: implement


def crossover_subtree(solution1, solution2):
    pass  # FIXME: implement


def crossover_node(solution1, solution2):
    pass  # FIXME: implement


class BasisOperator(object):

    __slots__ = ('func', 'signature', 'dtype', '_hash')

    def __init__(self, func, signature, dtype):  # TODO: clean up docs
        """A BasisOperator represents a member of the basis set. A
        BasisOperator must have arity greater than 0, and can optionally
        specify type information which is used to constrain the shape of
        candidate solutions.

        :param Function<(T0, ..., TN), U> func: A function of arity N+1 which
        takes N+1 arguments having type signature (T0, ..., TN) to a type U.
        :param tuple<T> signature: Type signature for func. You should make
        sure this matches the actual types that func expects, as this
        relationship is never validated. Instead, signature is used to
        constrain the shape of candidate solutions.
        :param U dtype: Output type for func. You should make sure this matches
        the actual type returned by func because it is used to constrain the
        shape of candidate solutions.
        """
        self.func = func
        self.signature = signature
        self.dtype = dtype
        self._hash = compute_hash(self.func, self.signature, self.dtype)

    def __repr__(self):
        return (
            'BasisOperator(func={func}, signature={signature}, dtype={dtype})'
        ).format(
            func=repr(self.func),
            signature=repr(self.signature),
            dtype=repr(self.dtype)
        )

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        return hash(self) == hash(other)


class TerminalOperator(object):

    __slots__ = ('source', 'dtype', '_hash')

    def __init__(self, source, dtype):  # TODO: clean up docs
        """A TerminalOperator represents a member of the terminal set. A
        TerminalOperator acts as a source which emits data of type dtype.

        :param iterator<T> source: An iterator which yields data of type T.
        :param T dtype: The output type for source. You should make sure this
        matches the actual type yielded by source because it is used to
        constrain the shape of candidate solutions.
        """
        self.source = source
        self.dtype = dtype
        self._hash = compute_hash(self.source, self.dtype)

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

    def __eq__(self, other):
        return hash(self) == hash(other)


class _OperatorSet(object):

    __slots__ = ('operators', '_dtype_to_operators', '_signature_to_operators')

    def __init__(self, operators):
        self.operators = frozenset(operators)
        self._dtype_to_operators = {
            operator.dtype: tuple(
                o for o in self.operators if o.dtype == operator.dtype
            )
            for operator in self.operators
        }
        self._signature_to_operators = {
            operator.signature: tuple(
                o for o in self.operators if o.signature == operator.signature
            )
            for operator in self.operators if hasattr(operator, 'signature')
        }

    def union(self, other):
        return _OperatorSet(
            operators=itertools.chain(self.operators, other.operators)
        )

    def __getitem__(self, item):
        if isinstance(item, tuple):
            return self._signature_to_operators[item]
        else:
            return self._dtype_to_operators[item]

    def __repr__(self):
        return 'OperatorSet({0})'.format(
            '{' + ', '.join(map(repr, self.operators)) + '}'
        )


class BasisSet(_OperatorSet):

    __slots__ = ()

    def __init__(self, basis_operators):  # TODO: more detailed docs
        """A BasisSet contains BasisOperators and also provides a convenient
        mapping which allows a user to select either the subset of basis
        operators having output type dtype or the subset of basis operators
        having a particular type signature.

        :param iterable<BasisOperator> basis_operators:
        """
        super(BasisSet, self).__init__(operators=basis_operators)

    def __getitem__(self, signature):
        """Look up the set of BasisOperators having the specified call
        signature.

        :param tuple<type> signature: Call signature
        :rtype tuple<BasisOperator>:
        """
        return self._signature_to_operators[signature]

    def __repr__(self):
        return 'BasisSet({0})'.format(
            '{' + ', '.join(map(repr, self.operators)) + '}'
        )


class TerminalSet(_OperatorSet):

    __slots__ = ()

    def __init__(self, terminal_operators):
        """A TerminalSet contains TerminalOperators and also provides a
        convenient mapping which allows a user to select the subset of terminal
        operators having a particular output dtype.

        :param iterable<TerminalOperator> terminal_operators:
        """
        super(TerminalSet, self).__init__(operators=terminal_operators)

    def __getitem__(self, dtype):
        """Look up the set of TerminalOperators having the return type dtype.

        :param type dtype: Return type.
        :rtype tuple<BasisOperator>:
        """
        return self._dtype_to_operators[dtype]

    def __repr__(self):
        return 'TerminalSet({0})'.format(
            '{' + ', '.join(map(repr, self.operators)) + '}'
        )


class Node(object):

    __slots__ = ('operator',)

    def __init__(self, operator):
        """A node has a unique hash and holds a reference to an operator.

        :param BasisOperator operator:
        """
        self.operator = operator

    def __repr__(self):
        return 'Node(operator={operator})'.format(operator=repr(self.operator))
