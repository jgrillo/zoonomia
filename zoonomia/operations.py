from zoonomia.tree import Node, Tree
from zoonomia.solution import BasisOperator, Solution


def full(max_depth, basis_set, terminal_set, dtype, objectives, rng):  # TODO: clean up docs
    """An implementation of Koza's full tree generation strategy augmented to
    take type information into account. Returns a candidate solution satisfying
    the property that all branches of the solution's tree representation have
    path length from root to leaf equal to max_depth. See Koza1992 and
    Montana1995.

    :param int max_depth: The maximum path length from root to leaf.
    :param zoonomia.operator.OperatorSet<BasisOperator> basis_set:
    :param zoonomia.operator.OperatorSet<TerminalOperator> terminal_set:
    :param type dtype: The return type of the resulting solution's functional
    representation.
    :param tuple<zoonomia.solution.Objective> objectives:
    :param random.Random rng:
    :return solution: A candidate solution.
    :rtype zoonomia.solution.Solution:
    """
    if max_depth <= 1:
        node = Node(operator=rng.choice(terminal_set[dtype]))
    else:
        node = Node(operator=rng.choice(basis_set[dtype]))

    root = node
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

                tree.add_edge(
                    edge=Edge(parent=parent, child=node, position=idx)
                )

        parents = children

    tree = Tree(root=root)

    return Solution(tree=tree, objectives=objectives)  # TODO: decouple Solution from Objectives?


def grow(max_depth, basis_set, terminal_set, dtype, objectives, rng):  # TODO: clean up docs
    """An implementation of Koza's grow tree generation strategy augmented to
    take type information into account. Returns a candidate solution whose
    graph representation has maximum path length from root to leaf constrained
    to the interval [1, max_depth]. See Koza1992 and Montana1995.

    :param int max_depth: The max path length from root to leaf.
    :param zoonomia.operator.OperatorSet<BasisOperator> basis_set:
    :param zoonomia.operator.OperatorSet<TerminalOperator> terminal_set:
    :param type dtype: The return type of the resulting solution's functional
    representation.
    :param tuple<zoonomia.solution.Objective> objectives:
    :param random.Random rng:
    :return solution: A candidate solution.
    :rtype zoonomia.solution.Solution:
    """
    if max_depth <= 1:
        node = Node(operator=rng.choice(terminal_set[dtype]))
    else:
        operator = rng.choice(basis_set.union(terminal_set)[dtype])
        if isinstance(operator, BasisOperator):
            node = Node(operator=operator)
        else:
            node = Node(operator=operator)

    root = node
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

                tree.add_edge(
                    edge=Edge(parent=parent, child=node, position=idx)
                )

        parents = children

    tree = Tree(root=root)

    return Solution(tree=tree, objectives=objectives)  # TODO: decouple Solution from Objectives?


def ramped_half_and_half(
    max_depth, population_size, basis_set, terminal_set, dtype, objectives, rng
):  # TODO: clean up docs
    """An implementation of something like Koza's ramped half-and-half
    population initialization procedure. See Koza1992.

    :param int max_depth: the max tree depth per individual.
    :param int population_size: number of individuals in the population.
    :param BasisSet<BasisOperator> basis_set:
    :param TerminalSet<TerminalOperator> terminal_set:
    :param type dtype: The return type of the resulting solutions' functional
    representations.
    :param tuple<zoonomia.solution.Objective> objectives:
    :param random.Random rng:
    :return population:
    :rtype frozenset:
    """
    counts = _random_depth_counts(
        max_depth=max_depth, population_size=population_size, rng=rng
    )

    return frozenset(
        _ramped_half_and_half_generator(
            counts=counts,
            basis_set=basis_set,
            terminal_set=terminal_set,
            objectives=objectives,
            dtype=dtype,
            rng=rng
        )
    )


def mutate_subtree(solution):
    """Perform subtree mutation on a solution, returning a new mutant solution.

    :param Solution solution:
    :return mutant:
    :rtype Solution:
    """
    raise NotImplementedError()  # FIXME: implement


def mutate_node(solution):
    """Perform a point mutation on a solution, returning a new mutant solution.

    :param Solution solution:
    :return mutant:
    :rtype Solution:
    """
    raise NotImplementedError()  # FIXME: implement


def crossover_subtree(solution1, solution2):
    """Perform subtree crossover between two solutions.

    :param Solution solution1:
    :param Solution solution2:
    :return children:
    :rtype tuple<Solution>:
    """
    raise NotImplementedError()  # FIXME: implement


def tournament_select(solution1, solution2, rng):  # TODO: clean up docs
    """Perform multi-objective tournament selection between two candidate
    solutions.

    :param Solution solution1:
    :param Solution solution2:
    :param random.Random rng:
    :return solution:
    :rtype Solution:
    """
    if solution1 > solution2:
        return solution1
    elif solution1 < solution2:
        return solution2
    else:  # TODO: maybe make a more nuanced decision here?
        return rng.choice((solution1, solution2))


def _ramped_half_and_half_generator(
    counts, basis_set, terminal_set, objectives, dtype, rng
):
    for depth, count in counts.items():
        for _ in xrange(count):
            if rng.getrandbits(1):
                yield full(
                    max_depth=depth,
                    basis_set=basis_set,
                    terminal_set=terminal_set,
                    dtype=dtype,
                    objectives=objectives,
                    rng=rng
                )
            else:
                yield grow(
                    max_depth=depth,
                    basis_set=basis_set,
                    terminal_set=terminal_set,
                    dtype=dtype,
                    objectives=objectives,
                    rng=rng
                )


def _random_depth_counts(max_depth, population_size, rng):
    counts = {d + 2: 0 for d in xrange(max_depth - 1)}
    for _ in xrange(population_size):
        counts[rng.choice(counts.keys())] += 1
    return counts
