import itertools
import logging

from threading import Lock

from zoonomia.helper import compute_hash

log = logging.getLogger(__name__)  # FIXME


class Objective(object):

    __slots__ = ('_eval_func', '_weight')

    def __init__(self, eval_func, weight):
        """An Objective contains a function for evaluating a Solution, and a
        weight by which the resulting fitness score will be multiplied.

        :param Function<Solution, float> eval_func: a function which computes a
        fitness score for a Solution.
        :param float weight: the weight to give this objective.
        """
        self._eval_func = eval_func
        self._weight = weight

    def __repr__(self):
        return 'Objective(eval_func={eval_func}, weight={weight})'.format(
            eval_func=repr(self._eval_func), weight=repr(self._weight)
        )

    def evaluate(self, solution):
        """Compute the fitness measurement of a solution with respect to this
        objective.

        :param Solution solution: a candidate solution.
        :return fitness: a fitness measurement of the solution with respect to
        this objective.
        :rtype Fitness:
        """
        score = self._eval_func(solution) * self._weight
        return Fitness(score=score, objective=self)


class Fitness(object):

    __slots__ = ('score', '_objective', '_hash')

    def __init__(self, score, objective):
        """A Fitness maps a fitness measurement to an Objective.

        :param float score:
        :param Objective objective:
        """
        self.score = score
        self._objective = objective
        self._hash = compute_hash(self.score, self._objective)

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
        'graph', 'objectives', 'map', '_hash', '_lock', '_fitnesses'
    )

    def __init__(self, graph, objectives, map_=map):
        """A Solution unites a graph representation with a collection of
        Objectives.

        :param networkx.Graph graph:
        :param tuple<Objective> objectives:
        :param Function<(Function<T, U>, iterable<T>), iterable<U>> map_: the
        map implementation to use in computing things (such as Fitness values)
        associated with this solution.
        """
        self.graph = graph
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

        :return fitness_tuple: A tuple of Fitness measurements.
        :rtype tuple<Fitness>:
        """
        ##
        # NOTE: in what follows, it is assumed that self._fitnesses will be
        # None (as initialized) until it is given a tuple<Fitness> value, and
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
                    self._hash = compute_hash(
                        self.objectives,
                        self._fitnesses
                    )
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

        :param Solution other: Another candidate solution.
        :return dominant: Whether this solution dominates other.
        :rtype bool:
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
            'Solution(graph={graph}, objectives={objectives}, map_={map_})'
        ).format(
            graph=repr(self.graph),
            objectives=repr(self.objectives),
            map_=repr(self.map)
        )

    def __len__(self):
        return len(self.graph)

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
