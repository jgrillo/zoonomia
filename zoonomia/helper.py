from collections import Iterable


def compute_hash(*items):
    """Compute a simple hash of one or more items. If an item is iterable, mix
    together the hashcodes of each element.

    :param object items: One or more objects.
    :raise TypeError: if item (or one of item's elements) is not hashable.
    :return hash_value:
    :rtype int:
    """
    if isinstance(items, Iterable):
        return reduce(
            lambda acc, i: 31 * acc + _compute_hashcode(i),
            items,
            17
        )
    else:
        return _compute_hashcode(items)


def _compute_hashcode(field):
    if isinstance(field, bool):
        return 1 if field else 0
    elif field is None:
        return 0
    elif isinstance(field, int):
        return field
    elif isinstance(field, long):
        return int(field ^ (field >> 32))
    else:
        hash_ = hash(field)
        return int(hash_ ^ (hash_ >> 32))
