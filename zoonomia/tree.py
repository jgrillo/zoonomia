import logging

from threading import RLock

log = logging.getLogger(__name__)  # FIXME


class Node(object):  # TODO: make lazy/immutable? make thread safe? Any gain?
    """Nodes are the fundamental elements of the trees used to represent
    candidate solutions in Zoonomia. A tree is composed by linking nodes
    together using the *add_child* method.

    .. warning::
        Nodes are not intended to be thread safe. You should construct
        tree structures from a single thread and only when you are done
        mutating the structure should the root node be passed into the
        constructor of zoonomia.tree.Tree.

    """

    __slots__ = ('operator', 'dtype', 'left', '_right', 'right')

    def __init__(self, operator):
        """A node has a unique identity and holds a reference to an operator.
        Optionally, a node can hold references to child nodes provided that
        those child nodes' operators' dtypes match this node's operator's
        signature.

        :param operator:
            A reference to the operator to associate with this node.

        :type operator:
            zoonomia.solution.BasisOperator or zoonomia.solution.TerminalOperator

        """
        self.operator = operator
        self.dtype = operator.dtype
        self.left = None
        self._right = None
        self.right = self._right

    def add_child(self, child, position):  # TODO: clean up docs
        """Add a child to this node corresponding to a *position* in the
        operator's signature. The child node's dtype must match the operator's
        signature at the given position.

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
        if self.operator.signature[position] is not child.dtype:
            log.error('child dtype does not match signature at position')  # FIXME
            raise TypeError('child dtype does not match signature at position')
        elif position == 0:
            self.left = child
        else:
            if self._right is None:
                self._right = [
                    None for _ in xrange(len(self.operator.signature) - 1)
                ]
            self._right[position - 1] = child
            self.right = tuple(r for r in reversed(self._right))

    def __hash__(self):  # FIXME: does this cause recursive explosion?
        return hash((self.operator, self.left, self.right))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __ne__(self, other):
        return hash(self) != hash(other)

    def __repr__(self):
        return (
            'Node(id={id}, operator={operator}, left={left}, right={right})'
        ).format(
            id={repr(id(self))},
            operator=repr(self.operator),
            left=repr(self.left),
            right=repr(self.right)
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

    __slots__ = ('root', 'dtype', '_lock', '_hash')

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
        self._lock = RLock()
        self._hash = None

    def __iter__(self):
        """Returns a post-order depth-first iterator over all nodes in this
        tree.

        :return: An iterator over all the nodes in this tree.
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

    def __hash__(self):
        if self._hash is None:
            with self._lock:
                if self._hash is None:
                    hashes = tuple(hash(node) for node in self)
                    self._hash = hash(hashes)
        return self._hash

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __ne__(self, other):
        return hash(self) != hash(other)
