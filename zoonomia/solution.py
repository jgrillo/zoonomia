import itertools
import logging

from threading import RLock

log = logging.getLogger(__name__)  # FIXME


class Objective(object):

    __slots__ = ('_eval_func', '_weight', '_hash')

    def __new__(cls, eval_func, weight):
        """An Objective contains a reference to a function for evaluating a
        Solution, and a weight by which the resulting fitness score will be
        multiplied.

        :param eval_func:
            A function which computes a fitness score for a Solution. Note that
            this function must be a 'top-level' (i.e. module scope) function if
            you require your Objective to be pickleable.

        :type eval_func: (zoonomia.solution.Solution) -> float

        :param weight:
            The weight to give this objective.

        :type weight: float

        """
        obj = super(Objective, cls).__new__(cls)
        obj._eval_func = eval_func
        obj._weight = weight
        obj._hash = hash((obj._eval_func, obj._weight))
        return obj

    def __getstate__(self):
        return (self._eval_func, self._weight, self._hash)

    def __setstate__(self, state):
        _eval_func, _weight, _hash = state

        self._eval_func = _eval_func
        self._weight = _weight
        self._hash = _hash

    def __repr__(self):
        return 'Objective(eval_func={eval_func}, weight={weight})'.format(
            eval_func=repr(self._eval_func), weight=repr(self._weight)
        )

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __ne__(self, other):
        return hash(self) != hash(other)

    def evaluate(self, solution):
        """Compute the fitness measurement of a solution with respect to this
        objective.

        :param solution: A candidate solution.

        :type solution: zoonomia.solution.Solution

        :return:
            A fitness measurement of the solution with respect to this
            objective.

        :rtype: zoonomia.solution.Fitness

        """
        score = self._eval_func(solution) * self._weight
        return Fitness(score=score, objective=self)


class Fitness(object):

    __slots__ = ('score', 'objective', '_hash')

    def __new__(cls, score, objective):
        """A Fitness maps a fitness measurement to an Objective, and provides
        comparison methods which allow a user to impose an ordering (by
        *score*) on a collection of Fitness objects.

        :param score: A fitness measurement.
        :type score: float

        :param objective: The Objective against which *score* was computed.
        :type objective: zoonomia.solution.Objective

        """
        obj = super(Fitness, cls).__new__(cls)
        obj.score = score
        obj.objective = objective
        obj._hash = hash((obj.score, obj.objective))
        return obj

    def __getstate__(self):
        return (self.score, self.objective, self._hash)

    def __setstate__(self, state):
        score, objective, _hash = state

        self.score = score
        self.objective = objective
        self._hash = _hash

    def __repr__(self):
        return 'Fitness(score={score}, objective={objective})'.format(
            score=repr(self.score), objective=repr(self.objective)
        )

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __ne__(self, other):
        return hash(self) != hash(other)

    def __gt__(self, other):
        return (
            self.score > other.score and self.objective == other.objective
        )

    def __ge__(self, other):
        return (
            self.score >= other.score and self.objective == other.objective
        )

    def __lt__(self, other):
        return (
            self.score < other.score and self.objective == other.objective
        )

    def __le__(self, other):
        return (
            self.score <= other.score and self.objective == other.objective
        )


class Solution(object):
    """The Solution type provides an abstraction over a candidate solution's
    tree representation, the objectives against which the candidate will be
    measured, and the results of evaluating the candidate solution against its
    objectives.

    """

    __slots__ = ('tree', 'map', 'objectives', '_fitnesses', '_hash', '_lock')

    def __new__(cls, tree, objectives, map_=map):
        """A Solution instance unites a Tree representation with a tuple of
        Objectives, and provides functionality to evaluate the representation's
        fitness with respect to each of those Objectives. Solution instances
        can also be ordered with respect to the Pareto-dominance of their
        respective fitness score collections.

        :param tree:
            A Tree representation of some computer program.

        :type tree: zoonomia.tree.Tree

        :param objectives:
            The Objectives to evaluate this Solution against.

        :type objectives: tuple[zoonomia.solution.Objective]

        :param  map_:
            The map implementation to use in computing things (such as Fitness
            values) associated with this solution. This implementation need not
            preserve ordering, as the methods which use it ensure that ordering
            is preserved where required.

        :type map_:
            ((T) -> U, collections.Iterable[T]) -> collectons.Iterable[U]

        """
        obj = super(Solution, cls).__new__(cls)
        obj.tree = tree
        obj.objectives = objectives
        obj.map = map_
        obj._fitnesses = None
        obj._lock = RLock()
        obj._hash = None
        return obj

    def __getstate__(self):
        return (
            self.tree, self.objectives, self.map, self._fitnesses, self._hash
        )

    def __setstate__(self, state):
        tree, objectives, map_, _fitnesses, _hash = state

        self.tree = tree
        self.objectives = objectives
        self.map = map_
        self._fitnesses = _fitnesses
        self._hash = _hash
        self._lock = RLock()

    def evaluate(self):
        """Compute the weighted fitness score of a solution with respect to
        each objective. Results are computed and cached in a thread-safe
        manner, so repeated calls to this method from multiple threads should
        result in only one (potentially expensive) call to each associated
        Objective's evaluate method.

        :return: A tuple of Fitness measurements.
        :rtype: tuple[zoonomia.solution.Fitness]

        """
        if self._fitnesses is None:
            with self._lock:
                if self._fitnesses is None:
                    fitnesses = self.map(
                        lambda o: o.evaluate(self), self.objectives
                    )
                    ordered_fitnesses = [
                        None for _ in xrange(len(self.objectives))
                    ]

                    for fitness in fitnesses:
                        idx = self.objectives.index(fitness.objective)
                        ordered_fitnesses[idx] = fitness

                    self._fitnesses = tuple(ordered_fitnesses)
                    self._hash = hash(
                        (self.tree, self._fitnesses, self.objectives)
                    )
        # TODO: asynchronize by making _fitnesses a generator?
        return self._fitnesses

    def dominates(self, other):
        """Predicate function to determine whether this solution dominates
        another solution in the Pareto sense. That is, we say that this
        solution *dominates* another solution if for all Objectives associated
        with both solutions the corresponding Fitness measurements for this
        solution are all greater than or equal to--and at least one Fitness
        measurement is strictly greater than--the corresponding Fitness
        measurements for the other solution.

        :param other: Another candidate solution.
        :type other: zoonomia.solution.Solution

        :raise TypeError:
            If this instance's *objectives* are unequal to *other*'s
            objectives.

        :return: Whether this solution dominates *other*.
        :rtype: bool

        """
        if self.objectives == other.objectives:
            return any(
                    f1 > f2 for f1, f2 in
                    itertools.izip(self.evaluate(), other.evaluate())
            ) and all(
                    f1 >= f2 for f1, f2 in
                    itertools.izip(self.evaluate(), other.evaluate())
            )
        else:
            raise TypeError(
                    'method is nonsense for solutions with unequal objectives'
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
        """Computes this solution's hash in a thread-safe manner. A solution's
        hash is computed by combining the hashes of its *tree*, its
        *objectives*, and the zoonomia.solution.Fitness instances corresponding
        to those objectives. Values are cached in keeping with the immutable
        semantics of this class, but users should be aware that if this
        instance's *evaluate* method has not been called prior to the first
        call to *__hash__*, calling this method will trigger one (and only one)
        potentially expensive *evaluate* call.

        :return: The integer hash code for this instance.
        :rtype: int

        """
        if self._hash is None:
            with self._lock:
                if self._hash is None:
                    log.warn('Evaluation triggered by hash for %s', self)
                    self.evaluate()
        return self._hash

    def __eq__(self, other):
        """Two solution instances are equal if their hashes are equal.

        :param other: Another solution.
        :type other: zoonomia.solution.Solution

        :return: Whether this solution and *other* have equal hashes.
        :rtype: bool

        """
        return hash(self) == hash(other)

    def __ne__(self, other):
        """Two solution instances are unequal if their hashes are unequal.

        :param other: Another solution.
        :type other: zoonomia.solution.Solution

        :return: Whether this solution and *other* have unequal hashes.
        :rtype: bool

        """
        return hash(self) != hash(other)

    def __gt__(self, other):
        """This solution instance is greater than the *other* solution instance
        if this solution's *objectives* are equal to the other solution's
        objectives and this solution *dominates* the other solution.

        :param other: Another solution.
        :type other: zoonomia.solution.Solution

        :raise TypeError:
            If this instance's *objectives* are unequal to *other*'s
            objectives.

        :return:
            Whether this solution dominates the *other* solution and has equal
            objectives.

        :rtype: bool

        """
        return self.dominates(other)

    def __lt__(self, other):
        """This solution instance is less than the *other* solution instance if
        this solution's *objectives* are equal to the other solution's
        objectives and this solution is *dominated* by the other solution.

        :param other: Another solution.
        :type other: zoonomia.solution.Solution

        :raise TypeError:
            If this instance's *objectives* are unequal to *other*'s
            objectives.

        :return:
            Whether this solution is dominated by the *other* solution and has
            equal objectives.

        :rtype: bool

        """
        return other.dominates(self)

    def __len__(self):
        """Returns the total number of nodes in this solution's tree
        representation.

        :return: The total number of nodes in this solution's tree.
        :rtype: int

        """
        return len(self.tree)
