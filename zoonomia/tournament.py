

def tournament_select(solution1, solution2, rng):  # TODO: clean up docs
    """Perform multi-objective tournament selection between two candidate
    solutions.

    :param zoonomia.solution.Solution solution1:
    :param zoonomia.solution.Solution solution2:
    :param random.Random rng:
    :return solution:
    :rtype zoonomia.solution.Solution:
    """
    if solution1 > solution2:
        return solution1
    elif solution1 < solution2:
        return solution2
    else:  # TODO: maybe make a more nuanced decision here?
        return rng.choice((solution1, solution2))
