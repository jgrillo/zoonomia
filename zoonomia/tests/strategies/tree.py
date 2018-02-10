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

"""This module defines builders for `Hypothesis <https://hypothesis.works>`_
strategies sufficient for constructing objects found in :mod:`zoonomia.tree` to
use in Hypothesis tests.

"""

import hypothesis.strategies as st

from hypothesis.strategies import composite

from zoonomia.tree import Node, Tree
from zoonomia.lang import Operator, Symbol

from zoonomia.tests.strategies.lang import default_operators


def nodes(operator_ts):
    """Build a :class:`zoonomia.tree.Node` strategy.

    :param operator_ts: A strategy of :class:`zoonomia.lang.Operator` instances.
    :type operator_ts: hypothesis.strategies.SearchStrategy

    :return: A node strategy.
    :rtype: hypothesis.strategies.SearchStrategy

    """
    return st.builds(Node, **{'operator': operator_ts})


def default_nodes():
    return nodes(operator_ts=default_operators())


@composite
def trees(draw, node_ts, max_depth=5):
    """Build a :class:`zoonomia.tree.Tree` strategy.

    :param node_ts: A strategy of :class:`zoonomia.tree.Node` instances.
    :type node_ts: hypothesis.strategies.SearchStrategy

    :param max_depth: The maximum depth of a tree.
    :type max_depth: int

    :return: A tree nodes strategy.
    :rtype: hypothesis.strategies.SearchStrategy

    """
    root = draw(node_ts)
    dtype = root.dtype

    basis_op = Operator(
        symbol=Symbol(
            name='basis_op',
            dtype=dtype
        ),
        signature=(dtype, dtype)
    )
    terminal_op = Operator(
        symbol=Symbol(
            name='terminal_op',
            dtype=dtype
        )
    )

    parents = [root]
    depth = 0

    while len(parents) > 0:
        children = []
        for parent in parents:
            for position, _ in enumerate(parent.operator.signature):
                if depth == max_depth:
                    node = Node(operator=terminal_op)
                else:
                    node = Node(operator=basis_op)

                parent.add_child(position=position, child=node)
                children.append(node)
        parents = children
        depth += 1

    return Tree(root=root)


def default_trees():
    return trees(node_ts=default_nodes())
