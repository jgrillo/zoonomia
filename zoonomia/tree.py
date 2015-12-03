import logging

log = logging.getLogger(__name__)  # FIXME


class Node(object):  # TODO: make lazy/immutable? make thread safe?

    __slots__ = ('operator', 'dtype', 'left', '_right', 'right')

    def __init__(self, operator):  # TODO: clean up docs
        """A node has a unique identity and holds a reference to an operator.
        Optionally, a node can hold references to child nodes provided that
        those child nodes' operators' dtypes match this node's operator's
        signature.

        WARNING: Nodes are not (yet) thread safe.

        :param BasisOperator or TerminalOperator operator:
        """
        self.operator = operator
        self.dtype = operator.dtype
        self.left = None
        self._right = None
        self.right = self._right

    def add_child(self, child, position):  # TODO: clean up docs
        """Add a child to this node corresponding to a position in the
        operator's signature. The child node's dtype must match the operator's
        signature at the given position. It is expected that this method will
        be called once for each location in the operator's signature.

        :param Node child:
        :param int position:

        :raise TypeError: if child's dtype doesn't match the operator's
        signature at the given position
        :raise IndexError: if child's signature does not contain an index
        corresponding to the given position.
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

    __slots__ = ('root', 'dtype')

    def __init__(self, root):
        """A Tree instance is a thin wrapper around a tree data structure
        composed of Nodes that supports post-order depth-first iteration over
        all the nodes. You should ensure that the tree data structure is
        fully-populated before you attempt iteration.

        :param Node root:
        """
        self.root = root
        self.dtype = root.dtype

    def __iter__(self):
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
