#   Copyright 2015-2017 Jesse C. Grillo
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

from queue import Queue
from collections import Counter
from threading import RLock

from pydot import Graph, Node as GraphNode, Edge as GraphEdge

from zoonomia.lang import Symbol
from zoonomia.types import TypeCheckError


def iter_calls(tree, result_formatter):
    """Returns an Iterator over the *tree* which emits *Call* objects
    representing abstract function calls.

    :param tree:
        A Tree of Operators.

    :type tree: zoonomia.tree.Tree

    :param result_formatter:
        A formatting string to use while formatting result handles' Symbol
        names. This string should take a single parameter which will be filled
        with an integral value. For example, the formatting string 'result_{0}'
        will become 'result_N' for the Nth function call obtained by iterating
        over the tree.

    :type result_formatter: str

    :return:
        An iterator over all the Calls in the *tree*.

    :rtype:
        collections.Iterator[zoonomia.solution.Call]

    """
    stack = []
    call_count = 0

    for node in tree:
        if node.left is None:  # node is a terminal
            stack.append(node.operator())  # put terminal Symbol on the stack
        else:
            signature_length = len(node.operator.signature)
            call = node.operator(
                target=Symbol(
                    name=result_formatter.format(call_count), dtype=node.dtype
                ),
                args=tuple(reversed(tuple(
                    stack.pop() for _ in range(signature_length)
                )))
            )
            stack.append(call.target)
            yield call
            call_count += 1


def iter_symbols(tree):
    """Returns an Iterator over the *tree* which emits *Symbol* objects, one
    for each of the terminal nodes.

    :param tree:
        A Tree of Operators.

    :type tree: zoonomia.tree.Tree

    :return:
        An iterator over all the Symbols in the *tree*.

    :rtype:
        collections.Iterator[zoonomia.solution.Symbol]

    """
    for node in tree:
        if node.left is None:
            yield node.operator()


def check_types_compatible(parent, child, position):
    """Check that child's return type is compatible with the parent at the given
    position. Returns None if compatible, raises otherwise.

    :param parent: The parent node.
    :type parent: Node

    :param child: The child node.
    :type child: Node

    :param position: The parent's signature position to test.
    :type position: int

    :raises TypeCheckError:
        if child cannot be attached to parent at the given position due to a
        type signature incompatibility.

    """
    if len(parent.operator.signature) >= position + 1:
        if child.dtype not in parent.operator.signature[position]:
            raise TypeCheckError(
                'child {0} does not match parent {1} at position {2}'.format(
                    child.operator.signature_str(),
                    parent.operator.signature_str(),
                    position
                )
            )
    else:
        raise TypeCheckError(
            'Parent signature {0} does not contain position {1}'.format(
                parent.operator.signature_str(),
                position
            )
        )


class Node(object):
    """Nodes are the fundamental elements of the trees used to represent
    candidate solutions in Zoonomia. A tree is composed by linking nodes
    together using the *add_child* method.

    """

    __slots__ = (
        'operator', 'dtype', 'left', '_right', 'right', 'parent', 'depth',
        'position', '_lock'
    )

    def __init__(self, operator):
        """A node holds a reference to an operator. Optionally, a node can hold
        references to child nodes provided that those child nodes' operators'
        dtypes match this node's operator's signature.

        :param operator:
            A reference to the operator to associate with this node.

        :type operator: zoonomia.lang.Operator

        """
        self.operator = operator
        self.dtype = self.operator.dtype
        self.left = None
        self._right = [None for _ in range(len(self.operator.signature) - 1)]
        self.right = None
        self.parent = None
        self.depth = 0
        self.position = 0
        self._lock = RLock()

    def __getstate__(self):
        with self._lock:
            return {
                'operator': self.operator,
                'left': self.left,
                '_right': self._right,
                'right': self.right,
                'parent': self.parent,
                'depth': self.depth
            }

    def __setstate__(self, state):
        self.__init__(state['operator'])

        with self._lock:
            self.left = state['left']
            self._right = state['_right']
            self.right = state['right']
            self.parent = state['parent']
            self.depth = state['depth']

    def add_child(self, child, position):
        """Add a child to this node corresponding to a *position* in the
        operator's *signature*. The child node's *dtype* must match the
        operator's signature at the given *position*.

        :param child:
            A reference to another Node instance.

        :type child: zoonomia.tree.Node

        :param position:
            The position, corresponding to an element of the operator's
            signature, to "wire up" the child node's operator's output.

        :type position: int

        :raise TypeCheckError:
            if child's dtype doesn't match the operator's signature at the
            given position.

        :raise ValueError: if a child is already present at that position.

        """
        with self._lock:
            check_types_compatible(self, child, position)

            if position == 0:
                if self.left is not None:
                    raise ValueError(
                        'child {0} already present at position 0'.format(
                            repr(self.left)
                        )
                    )

                child.parent = self
                self.left = child
            else:
                if self._right[position - 1] is not None:
                    raise ValueError(
                        'child {0} already present at position {1}'.format(
                            repr(self._right[position - 1]), position
                        )
                    )

                child.position = position
                child.parent = self
                self._right[position - 1] = child
                self.right = tuple(reversed(self._right))
            child.depth = self.depth + 1

    def remove_child(self, position):
        """Removes the child at the given position.

        :param position:
            The position, corresponding to an element of the operator's
            signature, to remove a child from.

        :type position: int

        """
        with self._lock:
            if position == 0:
                child = self.left

                if child is not None:
                    child.parent = None

                self.left = None
            else:
                child = self._right[position - 1]

                if child is not None:
                    child.parent = None

                self._right[position - 1] = None
                self.right = tuple(reversed(self._right))

    def graph_node(self):
        """Build the pydot.Node object corresponding to this tree node.

        :return: A pydot graphviz Node object.
        :rtype: pydot.Node

        """
        return GraphNode(name=self.operator.signature_str())

    def __eq__(self, other):  # can't check parent because recursion
        if isinstance(other, Node):
            with self._lock:
                return (
                    self.operator == other.operator and
                    self.left == other.left and
                    self.right == other.right and
                    self.depth == other.depth
                )
        else:
            return NotImplemented

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        with self._lock:
            return (
                'Node(id={id}, operator={operator}, left={left}, right={right},'
                ' parent={parent}, depth={depth})'
            ).format(
                id=id(self),
                operator=repr(self.operator),
                left=repr(self.left),
                right=repr(self.right),
                parent=repr(id(self.parent)),
                depth=repr(self.depth)
            )


class Tree(object):
    """Whereas a tree data structure is composed of zoonomia.tree.Node objects
    which refer to each other in a potentially complicated manner, a Tree
    instance is a "handle" which we can use to abstract away that complexity
    and actually use the tree to do work.

    """

    __slots__ = ('root', 'dtype', '_lock')

    def __init__(self, root):
        """A Tree instance is a thin wrapper around a tree data structure
        composed of Nodes that supports iteration over all the nodes and looking
        up nodes by index. You should ensure that the tree data structure is
        fully-populated before you construct a Tree instance.

        :param root:
            The root node of the tree data structure which this instance will
            "wrap".

        :type root: zoonomia.tree.Node

        """
        self.root = root
        self.dtype = root.dtype
        self._lock = RLock()

    def __getstate__(self):
        return {'root': self.root}

    def __setstate__(self, state):
        self.__init__(state['root'])

    def __iter__(self):
        """Returns a post-order depth-first iterator over all nodes in this
        tree.

        :return: A post-order depth-first iterator over this tree.
        :rtype: collections.Iterator[zoonomia.tree.Node]

        """
        with self._lock:
            stack = [self.root]
            last = None

            while len(stack) > 0:
                node = stack.pop()

                if node.left is None:
                    # this is a terminal node
                    yield node
                elif (
                    last is None
                ) or (
                    node is last.left
                ) or (
                    last.right is not None and node in last.right
                ):
                    # moving down
                    stack.append(node)
                    stack.append(node.left)
                elif last is node.left:
                    if node.right is None:
                        # moving up on a unary branch
                        yield node
                    else:
                        # moving up and to the right
                        for right in node.right:
                            stack.append(node)
                            stack.append(right)
                elif node.right is not None and last in node.right:
                    if last is node.right[0]:
                        # we are on the right-most branch moving up and left
                        yield node
                    else:
                        # we are on an inner-right branch moving upwards
                        stack.append(node)

                last = node

    def iter_pre_order(self):
        """Returns a pre-order depth-first iterator over all the nodes in this
        tree.

        :return: A pre-order depth-first iterator over this tree.
        :rtype: collections.Iterator[zoonomia.tree.Node]

        """
        with self._lock:
            stack = [self.root]
            last = None

            while len(stack) > 0:
                node = stack.pop()

                if node.left is None:
                    # this is a terminal node
                    yield node
                elif (
                    last is None
                ) or (
                    node is last.left
                ) or (
                    last.right is not None and node in last.right
                ):
                    # moving down
                    stack.append(node)
                    stack.append(node.left)
                    yield node
                elif last is node.left:
                    if node.right is not None:
                        # moving up and to the right
                        for right in node.right:
                            stack.append(node)
                            stack.append(right)
                elif node.right is not None and last in node.right:
                    if last is not node.right[0]:
                        # we are on an inner-right branch moving upwards
                        stack.append(node)

                last = node

    def iter_bfs(self):
        """Returns a breadth-first iterator over all the nodes in this tree.

        :return: A breadth-first iterator over this tree.
        :rtype: collections.Iterator[zoonomia.tree.Node]

        """
        with self._lock:
            q = Queue()
            q.put(self.root)

            while not q.empty():
                node = q.get()
                yield node

                if node.left is not None:
                    q.put(node.left)
                    if node.right is not None:
                        for right in reversed(node.right):
                            q.put(right)

    def get_dimensions(self):
        """Returns a tuple of int values indicating number of nodes at a given
        depth. For example, *get_dimensions()[2]* would give the number of
        nodes in this tree at depth 2.

        :return: A tuple representing the dimensions of the tree.
        :rtype: tuple[int]

        """
        with self._lock:
            counter = Counter(node.depth for node in self.iter_bfs())
            return tuple(
                counter.get(key) for key in sorted(counter.keys())
            )

    def graph(self):
        """Build the pydot graphviz graph corresponding to this tree. You can
        use this graph to visualize the tree with a graphviz renderer.

        :return: The pydot graphviz Graph corresponding to this tree.
        :rtype: pydot.Graph

        """
        with self._lock:
            graph = Graph(graph_name=self.root.operator.signature_str())
            graph.add_node(graph_node=self.root.graph_node())

            stack = []
            for node in self:
                if node.left is None:  # terminal node
                    graph.add_node(graph_node=node.graph_node())
                    stack.append(node)
                else:  # basis node
                    graph.add_node(graph_node=node.graph_node())
                    for _ in range(len(node.operator.signature)):
                        terminal_node = stack.pop()

                        graph.add_edge(
                            graph_edge=GraphEdge(
                                src=node.operator.signature_str(),
                                dst=terminal_node.operator.signature_str()
                            )
                        )
                    stack.append(node)

            return graph

    def __len__(self):
        """Returns the total number of nodes in the tree.

        :return: The number of nodes in this tree.
        :rtype: int

        """
        return sum(self.get_dimensions())

    def __eq__(self, other):
        if isinstance(other, Tree):
            with self._lock:
                return all(s == o for s, o in zip(self, other))
        else:
            return NotImplemented

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return 'Tree(root={root})'.format(root=repr(self.root))

    def __getitem__(self, key):
        """A tree can be indexed into with an int or a 2-tuple of ints. This
        method returns the node at the given index.

        .. warning::
            This method is linear in the number of nodes in the tree.

        :param key:
            If integer, signifies the position corresponding to a pre-order
            labelling of the tree. If tuple (x, y), return the yth node at depth
            x where y is computed in a breadth-first manner (left to right).

        :type key: int | tuple[int]

        :raise IndexError: if the key is out of bounds.

        :raise TypeError: if the key is formatted improperly.

        :return: The node at the given position.
        :rtype: Node

        """
        if isinstance(key, int):
            with self._lock:
                if key < 0:
                    raise IndexError('key {0} is out of bounds.'.format(key))

                for idx, node in enumerate(self.iter_pre_order()):
                    if idx == key:
                        return node

                raise IndexError('key {0} is out of bounds.'.format(key))
        elif isinstance(key, tuple):
            if len(key) != 2:
                raise TypeError(
                    'tuple key {0} must have two integer elements'.format(key)
                )
            elif not isinstance(key[0], int) or not isinstance(key[1], int):
                raise TypeError(
                    'tuple key {0} must contain integer elements'.format(key)
                )
            else:
                with self._lock:
                    x = key[0]
                    y = key[1]

                    if x < 0 or y < 0:
                        raise IndexError(
                            'key {0} is out of bounds.'.format(key)
                        )

                    for node in self.iter_bfs():
                        if node.depth == x and node.position == y:
                            return node

                    raise IndexError('key {0} is out of bounds.'.format(key))
        else:
            raise TypeError(
                'key {0} must be an integer or 2-tuple of integers'.format(key)
            )

    def __setitem__(self, key, value):  # FIXME: test
        """A tree can be indexed into with an int or a 2-tuple of ints. This
        method inserts a node at the given index. While you can mutate a tree by
        manually calling :py:method::`zoonomia.tree.Node.remove_child` and
        :py:method::`zoonomia.tree.Node.add_child` on its underlying nodes, you
        should use this method instead as it performs additional checks which
        will ensure the tree is left in a consistent state even if an error is
        encountered.

        .. warning::
            This method is linear in the number of nodes in the tree.

        :param key:
            If integer, signifies the position corresponding to a pre-order
            labelling of the tree. If tuple (x, y), return the yth node at depth
            x where y is computed in a breadth-first manner (left to right).

        :type key: int | tuple[int]

        :param value: The node to insert at the given index.
        :type value: Node

        :raise IndexError: if the key is out of bounds.

        :raise TypeError: if the key is formatted improperly.

        :raise TypeCheckError:
            if the value has improper type signature for insertion at the
            location specified by the key.

        """
        if isinstance(key, int):
            with self._lock:
                if key < 0:
                    raise IndexError('key {0} is out of bounds.'.format(key))

                found = False
                for idx, node in enumerate(self.iter_pre_order()):
                    if idx == key:
                        # perform type checks and mutate the tree
                        found = self._mutate_tree_safely(node=node, value=value)

                if not found:  # we didn't locate the node
                    raise IndexError('key {0} is out of bounds.'.format(key))

        elif isinstance(key, tuple):
            if len(key) != 2:
                raise TypeError(
                    'tuple key {0} must have two elements'.format(key)
                )
            elif not isinstance(key[0], int) or not isinstance(key[1], int):
                raise TypeError(
                    'tuple key {0} must contain integer elements'.format(key)
                )
            else:
                with self._lock:
                    x = key[0]
                    y = key[1]

                    if x < 0 or y < 0:
                        raise IndexError(
                            'key {0} is out of bounds.'.format(key)
                        )

                    found = False
                    for node in self.iter_bfs():
                        if node.depth == x and node.position == y:
                            # perform type checks and mutate the tree
                            found = self._mutate_tree_safely(
                                node=node, value=value
                            )

                    if not found: # we didn't locate the node
                        raise IndexError(
                            'key {0} is out of bounds.'.format(key)
                        )
        else:
            raise TypeError(
                'key {0} must be an integer or 2-tuple of integers'.format(key)
            )

    @staticmethod
    def _mutate_tree_safely(node, value):
        parent = node.parent

        check_types_compatible(  # check parent
            parent=parent, child=value, position=node.position
        )

        if node.left is not None:  # check left child
            check_types_compatible(
                parent=value, child=node.left, position=node.left.position
            )

        if node.right is not None:  # check right children
            for pos, right in enumerate(node.right):
                check_types_compatible(
                    parent=value, child=right, position=right.position
                )

        # insert the new node
        parent.remove_child(position=node.position)
        parent.add_child(child=value, position=node.position)

        # wire up the children if any exist
        if node.left is not None:
            value.add_child(child=node.left, position=0)

            if node.right is not None:
                for pos, right in enumerate(node.right):
                    value.add_child(child=right, position=pos + 1)

        return True

    def __delitem__(self, key):
        """A tree can be indexed into with an int or a 2-tuple of ints. This
        method removes the node at the given index.

        .. note::
            You cannot delete the root node, so this method will raise
            IndexError if called with keys 0 or (0, 0).

        .. warning::
            This method is linear in the number of nodes in the tree.

        .. warning::
            This method can leave the tree in an inconsistent state--i.e. a
            state where the iterator methods will fail.

        :param key:
            If integer, signifies the position corresponding to a pre-order
            labelling of the tree. If tuple (x, y), return the yth node at depth
            x where y is computed in a breadth-first manner (left to right).

        :type key: int | tuple[int]

        :raise IndexError: if the key is out of bounds.

        :raise TypeError: if the key is formatted improperly.

        """
        with self._lock:
            node = self[key]

            if node.parent is not None:
                parent = node.parent
                parent.remove_child(node.position)
            else:  # node is root
                raise IndexError('Cannot delete the root node.')
