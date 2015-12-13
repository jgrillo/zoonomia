from zoonomia.tree import Node, Tree
from zoonomia.solution import BasisOperator, Solution


def build_types_possibility_table(
    basis_set, terminal_set, max_depth, grow_=False
):
    """This function returns a "types possibility table" which, for each depth
    :math:`d_{i} \in [1, ..., d_{max}]` gives the possible return types for a
    tree of maximum depth :math:`i`. See Montana1995.

    :param basis_set:
        The OperatorSet of basis operators which, together with *terminal_set*,
        satisfy the closure property.

    :type basis_set: zoonomia.solution.OperatorSet[BasisOperator]

    :param terminal_set:
        The OperatorSet of terminal operators which, together with
        *terminal_set*, satisfy the closure property.

    :type terminal_set: zoonomia.solution.OperatorSet[TerminalOperator]

    :param max_depth: The maximum tree depth from root to leaf.
    :type max_depth: int

    :param grow_:
        Whether to generate a table for the *grow* method. Default is to
        generate a table for the *full* method.

    :type grow_: bool

    :return:
        A lookup table which for index :math:`i` provides a list of all the
        possible return types for a tree of maximum depth :math:`i`.

    :rtype: tuple[frozenset[type]]

    """
    table = [set() for _ in xrange(max_depth)]

    for terminal in terminal_set:
        if terminal.dtype not in table[0]:
            table[0].add(terminal.dtype)

    for idx in xrange(1, max_depth):
        if grow_:
            table[idx].update(table[idx - 1])

        for basis in basis_set:
            if (
                all(dtype in table[idx - 1] for dtype in basis.signature) and
                basis.dtype not in table[idx]
            ):
                table[idx].add(basis.dtype)

    return tuple(map(frozenset, table))


def full(max_depth, basis_set, terminal_set, dtype, objectives, rng):
    """An implementation of Koza's *full* tree generation strategy augmented to
    take type information into account. Returns a candidate solution satisfying
    the property that all branches of the solution's tree representation have
    path length from root to leaf equal to :math:`d_{max}`. See Koza1992 and
    Montana1995.

    :param max_depth: The maximum tree depth from root to leaf.
    :type max_depth: int

    :param basis_set:
        The OperatorSet of basis operators which, together with *terminal_set*,
        satisfy the closure property.

    :type basis_set:
        zoonomia.solution.BasisSet[zoonomia.solution.BasisOperator]

    :param terminal_set:
        The OperatorSet of terminal operators which, together with
        *terminal_set*, satisfy the closure property.

    :type terminal_set:
        zoonomia.solution.TerminalSet[zoonomia.solution.TerminalOperator]

    :param dtype:
        The return type of the resulting solution's functional representation.

    :type dtype: type

    :param objectives:
        The objectives that the resulting solution will be constructed with.

    :type objectives: tuple[zoonomia.solution.Objective]

    :param rng: A random number generator instance.
    :type rng: random.Random

    :return: A candidate solution.
    :rtype: zoonomia.solution.Solution

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


def grow(max_depth, basis_set, terminal_set, dtype, objectives, rng):
    """An implementation of Koza's *grow* tree generation strategy augmented to
    take type information into account. Returns a candidate solution whose
    graph representation has maximum path length from root to leaf constrained
    to the interval :math:`[1, d_{max}]`. See Koza1992 and Montana1995.

    :param max_depth: The maximum tree depth from root to leaf.
    :type max_depth: int

    :param basis_set:
        The OperatorSet of basis operators which, together with *terminal_set*,
        satisfy the closure property.

    :type basis_set:
        zoonomia.solution.BasisSet[zoonomia.solution.BasisOperator]

    :param terminal_set:
        The OperatorSet of terminal operators which, together with
        *basis_set*, satisfy the closure property.

    :type terminal_set:
        zoonomia.solution.TerminalSet[zoonomia.solution.TerminalOperator]

    :param dtype:
        The return type of the resulting solution's functional representation.

    :type dtype: type

    :param objectives:
        The objectives that the resulting solution will be constructed with.

    :type objectives: tuple[zoonomia.solution.Objective]

    :param rng: A random number generator instance.
    :type rng: random.Random

    :return: A candidate solution.
    :rtype: zoonomia.solution.Solution

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
):
    """An implementation of something like Koza's ramped half-and-half
    population initialization procedure. See Koza1992.

    :param max_depth: the max tree depth per individual.
    :type max_depth: int

    :param population_size: number of individuals in the population.
    :type population_size: int

    :param basis_set:
        The OperatorSet of basis operators which, together with *terminal_set*,
        satisfy the closure property.

    :type basis_set:
        zoonomia.solution.BasisSet[zoonomia.solution.BasisOperator]

    :param terminal_set:
        The OperatorSet of terminal operators which, together with
        *basis_set*, satisfy the closure property.

    :type terminal_set:
        zoonomia.solution.TerminalSet[zoonomia.solution.TerminalOperator]

    :param dtype:
        The return type of the resulting solutions' functional representations.

    :type dtype: type

    :param objectives:
        The objectives that the resulting solution will be constructed with.

    :type objectives: tuple[zoonomia.solution.Objective]

    :param rng: A random number generator instance.
    :type rng: random.Random

    :return:
    :rtype: frozenset

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

    :param solution: A solution.
    :type solution: zoonomia.solution.Solution

    :return: A mutant solution.

    :rtype: zoonomia.solution.Solution
    """
    raise NotImplementedError()  # FIXME: implement


def mutate_node(solution):
    """Perform a point mutation on a solution, returning a new mutant solution.

    :param solution: A solution.
    :type solution: zoonomia.solution.Solution

    :return: A mutant solution.

    :rtype: zoonomia.solution.Solution
    """
    raise NotImplementedError()  # FIXME: implement


def crossover_subtree(solution_1, solution_2):
    """Perform subtree crossover between two solutions.

    :param solution_1: A solution.
    :type solution_1: zoonomia.solution.Solution

    :param solution_2: Another solution.
    :type solution_2: zoonomia.solution.Solution

    :return: Two mutant solution offspring.

    :rtype: tuple[zoonomia.solution.Solution]
    """
    raise NotImplementedError()  # FIXME: implement


def tournament_select(solution_1, solution_2, rng):  # TODO: clean up docs
    """Perform multi-objective tournament selection between two candidate
    solutions.

    :param solution_1: A candidate solution.
    :type solution_1: zoonomia.solution.Solution

    :param solution_2: Another candidate solution.
    :type solution_2: zoonomia.solution.Solution

    :param rng: A random number generator instance.
    :type rng: random.Random

    :return: The solution which wins the tournament.

    :rtype: zoonomia.solution.Solution

    """
    if solution_1 > solution_2:
        return solution_1
    elif solution_1 < solution_2:
        return solution_2
    else:  # TODO: maybe make a more nuanced decision here?
        return rng.choice((solution_1, solution_2))


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
