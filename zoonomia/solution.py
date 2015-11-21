import itertools

from threading import Lock


class Objective(object):

    __slots__ = ('eval_func', 'weight', '_hash')

    def __init__(self, eval_func, weight):
        """An Objective contains a function for evaluating a Solution, and a
        weight by which the resulting fitness score will be multiplied.

        :param Function<Solution, float> eval_func: a function which computes a
        fitness score for a Solution.
        :param float weight: the weight to give this objective.
        """
        self.eval_func = eval_func
        self.weight = weight
        result = 17  # FIXME: make sure result isn't a long
        result = 31 * result + hash(eval_func)  # FIXME: this is turrbl
        result = 31 * result + hash(weight)
        self._hash = result

    def __repr__(self):
        return 'Objective(eval_func={eval_func}, weight={weight})'.format(
            eval_func=repr(self.eval_func), weight=repr(self.weight)
        )

    def evaluate(self, solution):
        """Compute the weighted fitness score of a solution with respect to
        this objective.

        :param Solution solution: a candidate solution.
        :return fitness: a fitness measurement of the solution with respect to
        this objective.
        :rtype Fitness:
        """
        # TODO: can we cache this somehow?
        score = self.eval_func(solution) * self.weight
        return Fitness(score=score)

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        return hash(self) == hash(other)


class Fitness(object):

    __slots__ = ('score', '_hash',)

    def __init__(self, score):
        """A Fitness object maps a real-valued fitness score to an Objective
        and a Solution.

        :param float score:
        """
        self.score = score
        result = 17  # FIXME: make sure result isn't a long
        result = 31 * result + hash(score)
        self._hash = result

    def __repr__(self):
        return 'Fitness(score={score})'.format(score=repr(self.score))

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        return hash(self) == hash(other)  # FIXME: semantics are weird

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
        'graph', 'objectives', 'map', '_hash', '_lock', '_fitness_tuple'
    )

    def __init__(self, graph, objectives, map_=map, fitness_tuple=None):
        """A Solution unites a graph representation with a collection of
        Objectives.

        :param networkx.Graph graph:
        :param tuple<Objective> objectives:
        :param Function<(Function<T, U>, iterable<T>), iterable<U>> map_: the
        map implementation to use in computing things (such as Fitness values)
        associated with this solution.
        :param tuple<Fitness> fitness_tuple: a tuple of fitness measurements,
        one for each objective.
        """
        self.graph = graph
        self.objectives = objectives
        self.map = map_
        self._fitness_tuple = fitness_tuple
        self._lock = Lock()
        result = 17  # FIXME: make sure result isn't a long
        result = 31 * result + hash(graph)
        result = 31 * result + hash(objectives)
        result = 31 * result + hash(map_)
        self._hash = result

    def evaluate(self):
        """Compute the weighted fitness score of a solution with respect to
        each objective. Results are computed and cached in a thread-safe
        manner, so repeated calls to this method from multiple threads should
        result in only one (potentially expensive) call to each associated
        Objective's evaluate method.

        :return fitness_tuple: a tuple of fitness measurements, one for each
        objective.
        :rtype tuple<Fitness>:
        """
        ##
        # NOTE: in what follows, it is assumed that self._fitness_tuple will be
        # None (as initialized) until it is given a tuple<Fitness> value, and
        # that this state transition will happen only once.
        ##
        if self._fitness_tuple is None:
            with self._lock:
                if self._fitness_tuple is None:
                    self._fitness_tuple = tuple(
                        self.map(lambda o: o.evaluate(self), self.objectives)
                    )
            return self._fitness_tuple
        else:
            return self._fitness_tuple

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
        return len(self.graph)  # FIXME: is this critical path length?

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        return (
            hash(self) == hash(other) and self.evaluate() == other.evaluate()
        )

    def __gt__(self, other):
        if self.objectives == other.objectives:
            return self.dominates(other)
        else:
            raise TypeError(
                'Cannot compare because objectives tuples do not match.'
            )

    def __ge__(self, other):  # FIXME: does this make sense?
        return self > other or self == other

    def __lt__(self, other):
        if self.objectives == other.objectives:
            return self.dominates(other)
        else:
            raise TypeError(
                'Cannot compare because objectives tuples do not match.'
            )

    def __le__(self, other):  # FIXME: does this make sense?
        return self < other or self == other
