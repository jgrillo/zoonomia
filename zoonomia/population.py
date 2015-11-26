from zoonomia.graph import full, grow


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
    counts = random_depth_counts(
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


def random_depth_counts(max_depth, population_size, rng):  # TODO: clean up docs
    """Compute a histogram of depths less than or equal to max_depth with
    constant total count equal to the population_size. This histogram
    represents the number of individuals that will be generated for each
    depth.

    :param int max_depth: the max tree depth per individual.
    :param int population_size: number of individuals in the population.
    :param random.Random rng:
    :return counts: histogram of depths.
    :rtype dict<int, int>:
    """
    counts = {d + 2: 0 for d in xrange(max_depth - 1)}
    for _ in xrange(population_size):
        counts[rng.choice(counts.keys())] += 1
    return counts
