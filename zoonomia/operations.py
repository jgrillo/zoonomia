#   Copyright 2015-2018 Jesse C. Grillo
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

    :type dtype: Type | ParametrizedType

    :param objectives:
        The objectives that the resulting solution will be constructed with.

    :type objectives: tuple[zoonomia.solution.Objective]

    :param rng:
        A random number generator instance.

    :type rng: random.Random

    :return: A candidate solution.
    :rtype: zoonomia.solution.Solution

    """
    root = full_tree(
        max_depth=max_depth,
        basis_operators=basis_operators,
        terminal_operators=terminal_operators,
        dtype=dtype,
        rng=rng
    )
    tree = Tree(root=root)

    return Solution(tree=tree, objectives=objectives)


def full_tree(max_depth, basis_operators, terminal_operators, dtype, rng):
    """Helper function to build the tree of nodes for :func:`full`.

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

    :type dtype: Type | ParametrizedType

    :param rng:
        A random number generator instance.

    :type rng: random.Random

    :return: The root node of a tree built using the *full* strategy.
    :rtype: zoonomia.tree.Node

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

    return root


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

    :type dtype: Type | ParametrizedType

    :param objectives:
        The objectives that the resulting solution will be constructed with.

    :type objectives: tuple[zoonomia.solution.Objective]

    :param rng: A random number generator instance.
    :type rng: random.Random

    :return: A candidate solution.
    :rtype: zoonomia.solution.Solution

    """
    root = grow_tree(
        max_depth=max_depth,
        basis_operators=basis_operators,
        terminal_operators=terminal_operators,
        dtype=dtype,
        rng=rng
    )
    tree = Tree(root=root)

    return Solution(tree=tree, objectives=objectives)


def grow_tree(max_depth, basis_operators, terminal_operators, dtype, rng):
    """Helper function to build the tree of Nodes for :func:`grow`.

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

    :type dtype: Type | ParametrizedType

    :param rng: A random number generator instance.
    :type rng: random.Random

    :return: The root node of a tree built using the *grow* strategy.
    :rtype: zoonomia.tree.Node

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

    return root


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

    :type dtype: Type | ParametrizedType

    :param objectives:
        The objectives that the resulting solution will be constructed with.

    :type objectives: tuple[zoonomia.solution.Objective]

    :param rng: A random number generator instance.
    :type rng: random.Random

    :return:
    :rtype: tuple

    """
    counts = _random_depth_counts(
        max_depth=max_depth, population_size=population_size, rng=rng
    )

    return tuple(
        _ramped_half_and_half_generator(
            counts=counts,
            basis_operators=basis_operators,
            terminal_operators=terminal_operators,
            objectives=objectives,
            dtype=dtype,
            rng=rng
        )
    )


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
        counts[rng.choice(tuple(counts.keys()))] += 1
    return counts


def mutate_subtree(
    solution, max_depth, basis_operators, terminal_operators, rng
):
    """Perform subtree mutation on a solution by randomly selecting a Node and
    replacing it (and all its descendants) with a subtree of depth *max_depth*.

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
    mutant = copy.deepcopy(solution.tree)

    dimensions = mutant.get_dimensions()
    target_idx = rng.randint(0, sum(dimensions) - 1)

    mutation_root = mutant[target_idx]
    mutation_parent = mutation_root.parent
    mutation_position = mutation_root.position
    del mutant[target_idx]

    if rng.getrandbits(1):
        mutation = full_tree(
            max_depth=max_depth,
            basis_operators=basis_operators,
            terminal_operators=terminal_operators,
            dtype=mutant.operator.signature[mutation_position],
            rng=rng
        )
    else:
        mutation = grow_tree(
            max_depth=max_depth,
            basis_operators=basis_operators,
            terminal_operators=terminal_operators,
            dtype=mutant.operator.signature[mutation_position],
            rng=rng
        )

    mutation_parent.add_child(position=mutation_position, child=mutation)

    return Solution(
        tree=mutant, objectives=solution.objectives, map_=solution.map
    )


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
    mutant = copy.deepcopy(solution.tree)

    dimensions = mutant.get_dimensions()

    if len(dimensions) < 3:  # there are no interior nodes to mutate, so no-op
        return mutant

    target_depth = rng.randint(0, len(dimensions) - 2)  # not a leaf
    target_branch = rng.randint(0, dimensions[target_depth])

    mutation_site = mutant[(target_depth, target_branch)]
    site_parent = mutation_site.parent
    site_position = mutation_site.position
    site_left = mutation_site.left
    site_right = mutation_site.right


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
    solutions. This is basically just a toy, there are much better selection
    algorithms than tournament selection. It's the only selection operator
    included with Zoonomia. You are encouraged to implement your own!

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
