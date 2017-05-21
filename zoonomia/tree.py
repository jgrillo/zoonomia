import logging
from queue import Queue
from collections import Counter
from threading import RLock

from zoonomia.lang import Symbol

log = logging.getLogger(__name__)  # FIXME


def calls_iter(tree, result_formatter):
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


def symbols_iter(tree):
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


class Node(object):
    """Nodes are the fundamental elements of the trees used to represent
    candidate solutions in Zoonomia. A tree is composed by linking nodes
    together using the *add_child* method.

    .. warning::
        Nodes are not intended to be thread safe. You should construct
        tree structures from a single thread and only when you are done
        mutating the structure should the root node be passed into the
        constructor of zoonomia.tree.Tree.

    .. warning::
        Nodes are not meant to be shared between trees. You should compose
        a tree structure from Node objects in a single thread, pass the
        root node to the zoonomia.tree.Tree constructor, and never again
        touch or use any of those Nodes.

    """

    __slots__ = ('operator', 'dtype', 'left', '_right', 'right', 'depth')

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
        self.depth = 0

    def __getstate__(self):
        return {
            'operator': self.operator,
            'left': self.left,
            '_right': self._right,
            'right': self.right,
            'depth': self.depth
        }

    def __setstate__(self, state):
        self.__init__(state['operator'])
        self.left = state['left']
        self._right = state['_right']
        self.right = state['right']
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

        :raise TypeError:
            If child's dtype doesn't match the operator's signature at the
            given position.

        :raise IndexError:
            If child's signature does not contain an index corresponding to the
            given position.

        """
        if child.dtype not in self.operator.signature[position]:
            raise TypeError(
                (
                    'child dtype {0} does not match operator {1} signature at '
                    'position {2}'
                ).format(
                    repr(child.dtype), repr(self.operator), position
                )
            )
        elif position == 0:
            self.left = child
        else:
            self._right[position - 1] = child
            self.right = tuple(reversed(self._right))
        child.depth = self.depth + 1

    def __hash__(self):
        """Compute the integer hashcode for this node instance.

        .. warning::
            Do not rely on a node's hash value until you are finished adding
            children.

        :return: An integer hash value.
        :rtype: int

        """
        return hash((
            'Node', self.operator, hash(self.left), hash(self.right), self.depth
        ))

    def __eq__(self, other):
        return (
            self.operator == other.operator and
            self.left == other.left and
            self.right == other.right and
            self.depth == other.depth
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return (
            'Node(operator={operator}, left={left}, right={right}, '
            'depth={depth})'
        ).format(
            operator=repr(self.operator),
            left=repr(self.left),
            right=repr(self.right),
            depth=repr(self.depth)
        )


class Tree(object):
    """Whereas a tree data structure is composed of zoonomia.tree.Node objects
    which refer to each other in a potentially complicated manner, a Tree
    instance is a "handle" which we can use to abstract away that complexity
    and actually use the tree to do work.

    .. note::
        While the Nodes which are used to construct a tree data structure are
        not thread-safe, if you make sure that once a Tree is constructed
        nothing will change its nodes you can be sure that the tree is
        "effectively immutable" and therefore "safe".

    """

    __slots__ = ('root', 'dtype', '_dimensions', '_lock', '_hash')

    def __init__(self, root):
        """A Tree instance is a thin wrapper around a tree data structure
        composed of Nodes that supports post-order depth-first iteration over
        all the nodes. You should ensure that the tree data structure is
        fully-populated before you attempt iteration.

        :param root:
            The root node of the tree data structure which this instance will
            "wrap".

        :type root: zoonomia.tree.Node

        """
        self.root = root
        self.dtype = root.dtype
        self._dimensions = None
        self._lock = RLock()
        self._hash = None

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
                    # we are on the right-most branch moving up and to the left
                    yield node
                else:
                    # we are on an inner-right branch moving upwards
                    stack.append(node)

            last = node

    def pre_order_iter(self):
        """Returns a pre-order depth-first iterator over all the nodes in this
        tree.

        :return: A pre-order depth-first iterator over this tree.
        :rtype: collections.Iterator[zoonomia.tree.Node]

        """
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

    def bfs_iter(self):
        """Returns a breadth-first iterator over all the nodes in this tree.

        :return: A breadth-first iterator over this tree.
        :rtype: collections.Iterator[zoonomia.tree.Node]

        """
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
        if self._dimensions is None:
            with self._lock:
                if self._dimensions is None:
                    counter = Counter(node.depth for node in self.bfs_iter())
                    self._dimensions = tuple(
                        counter.get(key) for key in sorted(counter.keys())
                    )
        return self._dimensions

    def __len__(self):
        """Returns the total number of nodes in the tree.

        :return: The number of nodes in this tree.
        :rtype: int

        """
        return sum(self.get_dimensions())

    def __hash__(self):
        if self._hash is None:
            with self._lock:
                if self._hash is None:
                    hashes = tuple(hash(node) for node in self)
                    self._hash = hash(('Tree', hashes))
        return self._hash

    def __eq__(self, other):
        return all(s == o for s, o in zip(self, other))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return 'Tree(root={root})'.format(root=repr(self.root))
