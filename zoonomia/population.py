import random

from zoonomia.graph import full, grow


def ramped_half_and_half(max_depth, population_size, basis, terminal):
    """An implementation of something like Koza's ramped half-and-half
    population initialization procedure. See Koza1992.

    :param int max_depth: the max tree depth per individual.
    :param int population_size: number of individuals in the population.
    :return population:
    :rtype frozenset:
    """
    counts = random_depth_counts(
        max_depth=max_depth, population_size=population_size
    )
    individuals = set()
    for depth, count in counts.items():
        for _ in xrange(count):
            if random.getrandbits(1):
                individuals.add(
                    full(depth=depth, basis=basis, terminal=terminal)
                )
            else:
                individuals.add(
                    grow(max_depth=depth, basis=basis, terminal=terminal)
                )
    return frozenset(individuals)


def random_depth_counts(max_depth, population_size):
    """Compute a histogram of depths less than or equal to max_depth with
    constant total count equal to the population_size. This histogram
    represents the number of individuals that will be generated for each
    depth.

    :param int max_depth: the max tree depth per individual.
    :param int population_size: number of individuals in the population.
    :return counts: histogram of depths.
    :rtype dict<int, int>:
    """
    counts = {d + 2: 0 for d in xrange(max_depth - 1)}
    for _ in xrange(population_size):
        counts[random.choice(counts.keys())] += 1
    return counts
