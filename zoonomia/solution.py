import itertools
import logging

from threading import Lock

from zoonomia.tree import Tree

log = logging.getLogger(__name__)  # FIXME


def verify_closure_property(basis_set, terminal_set):  # TODO: clean up docs
    """Verify that the OperatorSets *basis_set* and *terminal_set* together
    satisfy a strongly-typed version of the closure property. You can use this
    function to unit-test your OperatorSets. See Koza1992 for more about the
    closure property.

    .. warning::
        This function can only check that the combined *basis_set* and
        *terminal_set* is closed with respect to *types*. You must ensure that
        the functions you provide are well-behaved (in the closure sense) given
        any *values* they might encounter.

    :param basis_set:
        The candidate basis set to test for closure.

    :type basis_set: zoonomia.solution.OperatorSet[BasisOperator]

    :param terminal_set:
        The candidate terminal set to test for closure.

    :type terminal_set: zoonomia.solution.OperatorSet[TerminalOperator]

    :return: True if the closure property is satisfied, False otherwise.
    :rtype: bool

    """
    operator_set = basis_set.union(terminal_set)
    closed = True

    for basis_operator in basis_set:
        for dtype in basis_operator.signature:
            try:
                operators = operator_set[dtype]
                if len(operators) == 1 and operators[0] is basis_operator:
                    # The only operator that has this return type is the one
                    # whose signature we're currently inspecting. Given finite
                    # space, that won't work!
                    closed = False
            except KeyError:
                # No operators exist for this type
                closed = False

    return closed


class BasisOperator(object):

    __slots__ = ('func', 'signature', 'dtype')

    def __init__(self, func, signature, dtype):
        """A BasisOperator represents a member of the basis set. A
        BasisOperator contains a reference to a function, a tuple type
        *signature* corresponding to that function, and a reference *dtype* to
        that function's return type.

        :param func:
            A function of arity :math:`N+1` which takes :math:`N+1` arguments
            having type signature :math:`(T0, ..., TN)` to a result of type
            :math:`U`.

        :type func: (T) -> U

        :param signature:
            Type signature for *func*. You should make sure this matches the
            actual types that the function expects.

        :type signature: tuple[type]

        :param dtype:
            Output type for *func*. You should make sure this matches the
            actual type returned by the function.

        :type dtype: U
        """
        self.func = func
        self.signature = signature
        self.dtype = dtype

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


class TerminalOperator(object):

    __slots__ = ('source', 'dtype')

    def __init__(self, source, dtype):
        """A TerminalOperator represents a member of the terminal set. A
        TerminalOperator acts as a source which emits data of type dtype.

        :param source: An iterable which yields data of type T.

        :type source: collections.Iterable[T]

        :param dtype:
            The output type for source. You should make sure this matches the
            actual type yielded by source.

        :type dtype: T

        """
        self.source = source
        self.dtype = dtype

    def __repr__(self):
        return 'TerminalOperator(source={source}, dtype={dtype})'.format(
            source=repr(self.source),
            dtype=repr(self.dtype)
        )

    def __iter__(self):
        return iter(self.source)


class OperatorSet(object):

    __slots__ = ('operators', '_dtype_to_operators', '_signature_to_operators')

    def __init__(self, operators):
        """An OperatorSet contains BasisOperators and TerminalOperators and
        also provides a convenient mapping which allows a user to select either
        the subset of operators having output type dtype or the subset of
        basis operators having a particular type signature.

        :param operators:

        :type operators: collections.Iterable[BasisOperator|TerminalOperator]
        """
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
        """Returns an OperatorSet containing those elements which are in the
        union of both this OperatorSet and the other OperatorSet.

        :param other:
        :type other: OperatorSet

        :return union:
        :rtype: OperatorSet
        """
        return OperatorSet(
            operators=self.operators.union(other.operators)
        )

    def __iter__(self):
        """Returns an iterator over this instance's operators.

        :return: An iterator of operators.
        :rtype: collections.Iterator[BasisOperator|TerminalOperator]
        """
        return iter(self.operators)

    def __getitem__(self, item):
        """If item is a tuple, select those BasisOperators belonging to this
        OperatorSet which have signatures equal to item. If item is a type,
        select those BasisOperators and TerminalOperators which have dtype
        equal to item.

        :param item: A *signature* or *dtype*.

        :type item: tuple[type] or type

        :raise KeyError:
            If the given *item* has no associated operators in this
            OperatorSet.

        :return:
            The operators belonging to this OperatorSet which match the
            signature or dtype *item*.

        :rtype: tuple[BasisOperator] or tuple[TerminalOperator|BasisOperator]
        """
        if isinstance(item, tuple):
            return self._signature_to_operators[item]
        else:
            return self._dtype_to_operators[item]

    def __repr__(self):
        return 'OperatorSet({0})'.format(
            '{' + ', '.join(map(repr, self.operators)) + '}'
        )


class Objective(object):

    __slots__ = ('_eval_func', '_weight', '_hash')

    def __init__(self, eval_func, weight):
        """An Objective contains a reference to a function for evaluating a
        Solution, and a weight by which the resulting fitness score will be
        multiplied.

        :param eval_func:
            A function which computes a fitness score for a Solution.

        :type eval_func: (zoonomia.solution.Solution) -> float

        :param weight:
            The weight to give this objective.

        :type weight: float

        """
        self._eval_func = eval_func
        self._weight = weight
        self._hash = hash((eval_func, weight))

    def __repr__(self):
        return 'Objective(eval_func={eval_func}, weight={weight})'.format(
            eval_func=repr(self._eval_func), weight=repr(self._weight)
        )

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        return hash(self) == hash(other)

    def evaluate(self, solution):
        """Compute the fitness measurement of a solution with respect to this
        objective.

        :param solution: A candidate solution.

        :type solution: zoonomia.solution.Solution

        :return:
            A fitness measurement of the solution with respect to this
            objective.

        :rtype zoonomia.solution.Fitness:

        """
        score = self._eval_func(solution) * self._weight
        return Fitness(score=score, objective=self)


class Fitness(object):

    __slots__ = ('score', '_objective', '_hash')

    def __init__(self, score, objective):
        """A Fitness maps a fitness measurement to an Objective.

        :param score:
        :type score: float

        :param objective:
        :type objective: zoonomia.solution.Objective
        """
        self.score = score
        self._objective = objective
        self._hash = hash((score, objective))

    def __repr__(self):
        return 'Fitness(score={score}, objective={objective})'.format(
            score=repr(self.score), objective=repr(self._objective)
        )

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        hash(self) == hash(other)

    def __gt__(self, other):
        return self.score > other.score

    def __ge__(self, other):
        return self.score >= other.score

    def __lt__(self, other):
        return self.score < other.score

    def __le__(self, other):
        return self.score <= other.score


class Solution(object):

    __slots__ = (
        'tree', 'objectives', 'map', '_hash', '_lock', '_fitnesses'
    )

    def __init__(self, tree, objectives, map_=map):
        """A Solution unites a tree representation with a collection of
        Objectives.

        :param tree:

        :type tree:
            zoonomia.tree.Tree

        :param objectives:


        :type objectives:
            tuple[zoonomia.solution.Objective]

        :param  map_:
            The map implementation to use in computing things (such as Fitness
            values) associated with this solution.

        :type map_:
            ((T) -> U, collections.Iterable[T]) -> collectons.Iterable[U]

        """
        self.tree = tree
        self.objectives = objectives
        self.map = map_
        self._fitnesses = None
        self._lock = Lock()
        self._hash = None

    def evaluate(self):
        """Compute the weighted fitness score of a solution with respect to
        each objective. Results are computed and cached in a thread-safe
        manner, so repeated calls to this method from multiple threads should
        result in only one (potentially expensive) call to each associated
        Objective's evaluate method.

        :return: A tuple of Fitness measurements.
        :rtype: tuple[zoonomia.solution.Fitness]

        """
        ##
        # NOTE: in what follows, it is assumed that self._fitnesses will be
        # None (as initialized) until it is given a tuple[Fitness] value, and
        # that this state transition will happen only once.
        ##
        if self._fitnesses is None:
            with self._lock:
                if self._fitnesses is None:
                    self._fitnesses = tuple(
                        self.map(
                            lambda o: Fitness(
                                score=o.evaluate(self), objective=o
                            ),
                            self.objectives
                        )
                    )
                    self._hash = hash((self.objectives, self._fitnesses))
            return self._fitnesses
        else:
            return self._fitnesses

    def dominates(self, other):
        """Predicate function to determine whether this solution dominates
        another solution in the Pareto sense. That is, we say that this
        solution dominates another solution if for all Objectives associated
        with both solutions the corresponding Fitness measurements for this
        solution are all greater than or equal to--and at least one Fitness
        measurement is strictly greater than--the corresponding Fitness
        measurements for the other solution.

        :param other: Another candidate solution.
        :type other: zoonomia.solution.Solution

        :return: Whether this solution dominates other.
        :rtype: bool

        """
        return any(
            f1 > f2 for f1, f2 in
            itertools.izip(self.evaluate(), other.evaluate())
        ) and all(
            f1 >= f2 for f1, f2 in
            itertools.izip(self.evaluate(), other.evaluate())
        )

    def __repr__(self):
        return (
            'Solution(tree={tree}, objectives={objectives}, map_={map_})'
        ).format(
            tree=repr(self.tree),
            objectives=repr(self.objectives),
            map_=repr(self.map)
        )

    def __hash__(self):
        if self._hash is None:
            with self._lock:
                if self._hash is None:
                    log.warn(
                        'Evaluation triggered by hash for solution %s', self
                    )
                    self.evaluate()
        return self._hash

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __gt__(self, other):
        if self.objectives == other.objectives:
            return self.dominates(other)
        else:
            return False

    def __ge__(self, other):
        return self > other or self == other

    def __lt__(self, other):
        if self.objectives == other.objectives:
            return self.dominates(other)
        else:
            return False

    def __le__(self, other):
        return self < other or self == other
