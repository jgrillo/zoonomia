import logging

from threading import RLock

log = logging.getLogger(__name__)  # FIXME


class Objective(object):

    __slots__ = ('eval_func', 'weight', '_hash')

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
        obj.eval_func = eval_func
        obj.weight = weight
        obj._hash = hash((obj.eval_func, obj.weight))
        return obj

    def __getstate__(self):
        return self.eval_func, self.weight, self._hash

    def __getnewargs__(self):
        return self.eval_func, self.weight

    def __setstate__(self, state):
        _eval_func, _weight, _hash = state

        self.eval_func = _eval_func
        self.weight = _weight
        self._hash = _hash

    def __repr__(self):
        return 'Objective(eval_func={eval_func}, weight={weight})'.format(
            eval_func=repr(self.eval_func), weight=repr(self.weight)
        )

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        return (
            self.eval_func == other.eval_func and self.weight == other.weight
        )

    def __ne__(self, other):
        return not self.__eq__(other)

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
        score = self.eval_func(solution) * self.weight
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
        return self.score, self.objective, self._hash

    def __getnewargs__(self):
        return self.score, self.objective

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
        return self.score == other.score and self.objective == other.objective

    def __ne__(self, other):
        return not self.__eq__(other)

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


class Solution(object):  # FIXME: should fitnesses be futures?
    """The Solution type provides an abstraction over a candidate solution's
    tree representation, the objectives against which the candidate will be
    measured, and the results of evaluating the candidate solution against its
    objectives.

    """

    __slots__ = ('tree', 'map', 'objectives', 'fitnesses', '_hash', '_lock')

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
        obj.fitnesses = None
        obj._lock = RLock()
        obj._hash = None
        return obj

    def __getstate__(self):
        return (
            self.tree, self.objectives, self.map, self.fitnesses, self._hash
        )

    def __getnewargs__(self):
        return self.tree, self.objectives, self.map

    def __setstate__(self, state):
        tree, objectives, map_, fitnesses, _hash = state

        self.tree = tree
        self.objectives = objectives
        self.map = map_
        self.fitnesses = fitnesses
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
        if self.fitnesses is None:
            with self._lock:
                if self.fitnesses is None:
                    fitnesses = self.map(
                        lambda o: o.evaluate(self), self.objectives
                    )
                    ordered_fitnesses = [
                        None for _ in range(len(self.objectives))
                    ]

                    for fitness in fitnesses:
                        idx = self.objectives.index(fitness.objective)
                        ordered_fitnesses[idx] = fitness

                    self.fitnesses = tuple(ordered_fitnesses)
                    self._hash = hash(
                        (self.tree, self.fitnesses, self.objectives)
                    )
        # TODO: asynchronize by making _fitnesses a generator?
        return self.fitnesses

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
                    f1 > f2 for f1, f2 in zip(self.evaluate(), other.evaluate())
            ) and all(
                    f1 >= f2 for f1, f2 in
                    zip(self.evaluate(), other.evaluate())
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
                    log.warning('Evaluation triggered by hash for %s', self)
                    self.evaluate()

        return self._hash

    def __eq__(self, other):
        """Computes whether this solution equals another solution in a
        thread-safe manner. If this instance's *evaluate* method or the other
        instance's *evaluate* method has not been called prior to the first
        call to *__eq__*, calling this method will trigger one or perhaps two
        potentially expensive *evaluate* calls.

        :param other: The other solution.

        :type other: Solution

        :return: Whether this solution equals the other solution.

        :rtype: bool

        """
        hash(other)  # potentially trigger evaluation of other

        if self._hash is None:
            with self._lock:
                if self._hash is None:
                    log.warning('Evaluation triggered by __eq__ for %s', self)
                    self.evaluate()

        return (
            self.tree == other.tree and
            self.fitnesses == other.fitnesses and
            self.objectives == other.objectives
        )

    def __ne__(self, other):
        """Computes whether this solution doesn't equal another solution in a
        thread-safe manner. If this instance's *evaluate* method or the other
        instance's *evaluate* method has not been called prior to the first
        call to *__eq__*, calling this method will trigger one or perhaps two
        potentially expensive *evaluate* calls.

        :param other: The other solution.

        :type other: Solution

        :return: Whether this solution equals the other solution.

        :rtype: bool

        """
        return not self.__eq__(other)

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
