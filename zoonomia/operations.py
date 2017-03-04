import copy

from zoonomia.tree import Node, Tree
from zoonomia.solution import Solution


def full(
    max_depth, basis_operators, terminal_operators, dtype, objectives, rng
):
    """An implementation of Koza's *full* tree generation strategy augmented to
    take type information into account. Returns a candidate solution satisfying
    the property that all branches of the solution's tree representation have
    path length from root to leaf equal to :math:`d_{max}`. See Koza1992 and
    Montana1995.

    :param max_depth:
        The maximum tree depth from root to leaf.

    :type max_depth: int

    :param basis_operators:
        The OperatorTable of basis operators which, together with
        *terminal_operators*, satisfy the closure property.

    :type basis_operators:
        zoonomia.solution.OperatorTable[zoonomia.solution.Operator]

    :param terminal_operators:
        The OperatorTable of terminal operators which, together with
        *terminal_operators*, satisfy the closure property.

    :type terminal_operators:
        zoonomia.solution.OperatorTable[zoonomia.solution.Operator]

    :param dtype:
        The return type of the resulting solution's functional representation.

    :type dtype: Type or GenericType or ParametrizedType

    :param objectives:
        The objectives that the resulting solution will be constructed with.

    :type objectives: tuple[zoonomia.solution.Objective]

    :param rng:
        A random number generator instance.

    :type rng: random.Random

    :return: A candidate solution.

    :rtype: zoonomia.solution.Solution

    """
    if max_depth <= 1:
        node = Node(operator=rng.choice(tuple(terminal_operators[dtype])))
    else:
        node = Node(operator=rng.choice(tuple(basis_operators[dtype])))

    root = node
    depth = 1
    parents = [node]

    while depth < max_depth:
        depth += 1
        children = []

        for parent in parents:
            for idx, t in enumerate(parent.operator.signature):
                node = Node(
                    operator=rng.choice(tuple(terminal_operators[t]))
                ) if depth == max_depth else Node(
                    operator=rng.choice(tuple(basis_operators[t]))
                )

                children.append(node)

                parent.add_child(child=node, position=idx)

        parents = children

    tree = Tree(root=root)

    return Solution(tree=tree, objectives=objectives)


def grow(
    max_depth, basis_operators, terminal_operators, dtype, objectives, rng
):
    """An implementation of Koza's *grow* tree generation strategy augmented to
    take type information into account. Returns a candidate solution whose
    graph representation has maximum path length from root to leaf constrained
    to the interval :math:`[1, d_{max}]`. See Koza1992 and Montana1995.

    :param max_depth: The maximum tree depth from root to leaf.

    :type max_depth: int

    :param basis_operators:
        The OperatorTable of basis operators which, together with
        *terminal_operators*, satisfy the closure property.

    :type basis_operators:
        zoonomia.solution.OperatorTable[zoonomia.solution.Operator]

    :param terminal_operators:
        The OperatorTable of terminal operators which, together with
        *basis_operators*, satisfy the closure property.

    :type terminal_operators:
        zoonomia.solution.OperatorTable[zoonomia.solution.Operator]

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
        node = Node(operator=rng.choice(tuple(terminal_operators[dtype])))
    else:
        operator = rng.choice(
            tuple(basis_operators.union(terminal_operators)[dtype])
        )
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
                    node = Node(
                        operator=rng.choice(tuple(terminal_operators[t]))
                    )
                else:
                    operator = rng.choice(
                        tuple(basis_operators.union(terminal_operators)[t])
                    )
                    node = Node(operator=operator)
                    if node.left is not None:  # node contains a basis operator
                        children.append(node)

                parent.add_child(child=node, position=idx)

        parents = children

    tree = Tree(root=root)

    return Solution(tree=tree, objectives=objectives)


def ramped_half_and_half(
    max_depth, population_size, basis_operators, terminal_operators, dtype,
    objectives, rng
):
    """An implementation of something like Koza's ramped half-and-half
    population initialization procedure. See Koza1992.

    :param max_depth: the max tree depth per individual.

    :type max_depth: int

    :param population_size: number of individuals in the population.

    :type population_size: int

    :param basis_operators:
        The OperatorTable of basis operators which, together with
        *terminal_operators*, satisfy the closure property.

    :type basis_operators:
        zoonomia.solution.OperatorTable[zoonomia.solution.Operator]

    :param terminal_operators:
        The OperatorTable of terminal operators which, together with
        *basis_operators*, satisfy the closure property.

    :type terminal_operators:
        zoonomia.solution.OperatorTable[zoonomia.solution.Operator]

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
            basis_operators=basis_operators,
            terminal_operators=terminal_operators,
            objectives=objectives,
            dtype=dtype,
            rng=rng
        )
    )


def mutate_subtree(
    solution, max_depth, basis_operators, terminal_operators, rng
):
    """Perform subtree mutation on a solution by randomly selecting a Node and
    replacing it (and all its descendants) with a subtree of depth *max_depth*
    generated by the ramped_half_and_half method.

    This is accomplished by conducting a pre-order traversal until we reach a
    randomly-chosen depth, and choosing (randomly) a branch at that depth to
    serve as the sacrificial node. We then generate a tree of depth

    :param solution: A solution.

    :type solution: zoonomia.solution.Solution

    :param max_depth: The max tree depth for the subtree.

    :type max_depth: int

    :param basis_operators: An OperatorTable of basis Operators.

    :type basis_operators: OperatorTable

    :param terminal_operators: An OperatorTable of terminal Operators.

    :type terminal_operators: OperatorTable

    :param rng: A random number generator instance.

    :type rng: random.Random

    :return: A mutant solution.

    :rtype: zoonomia.solution.Solution

    """
    dimensions = solution.tree.get_dimensions()
    target_depth = rng.choice(range(len(dimensions) - 1))
    target_branch = rng.choice(range(dimensions[target_depth]))

    branch = 0
    root = None
    previous = None
    stack = []
    for node in solution.tree.pre_order_iter():
        if node.depth == target_depth:
            if branch == target_branch:
                root = copy.deepcopy(node)
                previous = root
        elif node.depth > target_depth:
            previous.add_child(node, position)

# post-order
#            7
#          /   \
#         2     6
#       /  \   /  \
#      1    3  4   5

# pre-order
#            1
#          /   \
#         2     5
#       /  \   /  \
#      3    4  6   7


def mutate_interior_node(solution, basis_operators, rng):
    """Perform a point mutation on a solution by replacing a randomly-chosen
    interior node with a new Node having an Operator chosen at random from
    *basis_operators*. Returns a new mutant solution.

    :param solution: A solution.

    :type solution: zoonomia.solution.Solution

    :param basis_operators: An OperatorTable of basis Operators.

    :type basis_operators: OperatorTable

    :param rng: A random number generator instance.

    :type rng: random.Random

    :return: A mutant solution.

    :rtype: zoonomia.solution.Solution

    """
    raise NotImplementedError()  # FIXME: implement


def mutate_leaf_node(solution, terminal_operators, rng):
    """Perform a point mutation on a solution by replacing a randomly-chosen
    leaf node with a new Node having an Operator chosen at random from
    *terminal_operators*. Returns a new mutant solution.

    :param solution: A solution.

    :type solution: zoonomia.solution.Solution

    :param terminal_operators: An OperatorTable of terminal Operators.

    :type terminal_operators: OperatorTable

    :param rng: A random number generator instance.

    :type rng: random.Random

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
    counts, basis_operators, terminal_operators, objectives, dtype, rng
):
    for depth, count in counts.items():
        for _ in range(count):
            if rng.getrandbits(1):
                yield full(
                    max_depth=depth,
                    basis_operators=basis_operators,
                    terminal_operators=terminal_operators,
                    dtype=dtype,
                    objectives=objectives,
                    rng=rng
                )
            else:
                yield grow(
                    max_depth=depth,
                    basis_operators=basis_operators,
                    terminal_operators=terminal_operators,
                    dtype=dtype,
                    objectives=objectives,
                    rng=rng
                )


def _random_depth_counts(max_depth, population_size, rng):
    # computes a histogram of initial tree depths for a population having
    # *population_size* individuals.
    counts = {d + 1: 0 for d in range(max_depth)}
    for _ in range(population_size):
        counts[rng.choice(counts.keys())] += 1
    return counts
