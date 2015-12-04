import unittest

from zoonomia.tree import Node, Tree
from zoonomia.solution import BasisOperator, TerminalOperator


class SomeType(object):

    def __init__(self, arg=None):
        self.arg = arg


class SomeOtherType(object):

    def __init__(self, arg=None):
        self.arg = arg


class TestNode(unittest.TestCase):

    def test_node_operator_reference(self):
        """Test that two different Nodes can refer to the same operator.

        """
        def func(t): SomeType(arg=t.arg)
        signature = (SomeType,)
        dtype = SomeType

        basis_op = BasisOperator(func=func, signature=signature, dtype=dtype)

        basis_node_1 = Node(operator=basis_op)
        basis_node_2 = Node(operator=basis_op)

        self.assertIs(basis_node_1.operator, basis_node_2.operator)

    def test_node_identity_unique(self):
        """Test that two different Nodes which refer to the same operator are
        identically distinct.

        """
        def func(t): SomeType(arg=t.arg)
        signature = (SomeType,)
        dtype = SomeType

        basis_op = BasisOperator(func=func, signature=signature, dtype=dtype)

        basis_node_1 = Node(operator=basis_op)
        basis_node_2 = Node(operator=basis_op)

        self.assertIsNot(basis_node_1, basis_node_2)

    def test_node_dtype(self):
        """Test that a Node's dtype is identically the same as its operator's
        dtype.

        """
        def func(t): SomeType(arg=t.arg)
        signature = (SomeType,)
        basis_dtype = SomeType

        source = (SomeOtherType(arg=i) for i in xrange(666))
        terminal_dtype = SomeOtherType

        basis_op = BasisOperator(
            func=func, signature=signature, dtype=basis_dtype
        )
        terminal_op = TerminalOperator(source=source, dtype=terminal_dtype)

        basis_node = Node(operator=basis_op)
        terminal_node = Node(operator=terminal_op)

        self.assertIs(terminal_node.dtype, terminal_op.dtype)
        self.assertIs(basis_node.dtype, basis_op.dtype)

    def test_add_child_raises_signature_type_mismatch(self):
        """Test that the add_child method raises TypeError if the child's dtype
        does not match the node's operator's signature at the given position.

        """
        def func(t): SomeType(arg=t.arg)
        signature = (SomeType,)
        basis_dtype = SomeType

        source = (SomeOtherType(arg=i) for i in xrange(666))
        terminal_dtype = SomeOtherType

        basis_op = BasisOperator(
            func=func, signature=signature, dtype=basis_dtype
        )
        terminal_op = TerminalOperator(source=source, dtype=terminal_dtype)

        basis_node = Node(operator=basis_op)
        terminal_node = Node(operator=terminal_op)

        self.assertRaises(
            TypeError, basis_node.add_child, child=terminal_node, position=0
        )

    def test_add_child_raises_signature_missing_index(self):
        """Test that the add_child method raises IndexError if the child's
        signature does not contain an index corresponding to the given
        position.

        """
        def func(t): SomeType(arg=t.arg)
        signature = (SomeType,)
        dtype = SomeType

        source = (SomeType(arg=i) for i in xrange(666))

        basis_op = BasisOperator(
            func=func, signature=signature, dtype=dtype
        )
        terminal_op = TerminalOperator(source=source, dtype=dtype)

        basis_node = Node(operator=basis_op)
        terminal_node = Node(operator=terminal_op)

        self.assertRaises(
            IndexError, basis_node.add_child, child=terminal_node, position=1
        )

    def test_node_left(self):
        """Test that a Node's left attribute contains the child corresponding
        to the operator's signature at position 0.

        """
        def func(t): SomeType(arg=t.arg)
        signature = (SomeType,)
        dtype = SomeType

        source = (SomeType(arg=i) for i in xrange(666))

        basis_op = BasisOperator(
            func=func, signature=signature, dtype=dtype
        )
        terminal_op = TerminalOperator(source=source, dtype=dtype)

        basis_node = Node(operator=basis_op)
        terminal_node = Node(operator=terminal_op)

        basis_node.add_child(child=terminal_node, position=0)

        self.assertIs(basis_node.left, terminal_node)

    def test_node_right(self):
        """Test that a Node's right attribute contains all the children
        corresponding to the nonzero signature positions, reversed.

        """
        def func(t, u, v): SomeType(arg=t.arg + u.arg + v.arg)
        signature = (SomeType, SomeOtherType, SomeType)
        basis_dtype = SomeType

        source_1 = (SomeOtherType(arg=i) for i in xrange(666))
        terminal_1_dtype = SomeOtherType

        source_2 = (SomeType(arg=i) for i in xrange(666))
        terminal_2_dtype = SomeType

        basis_op = BasisOperator(
            func=func, signature=signature, dtype=basis_dtype
        )
        terminal_op_1 = TerminalOperator(
            source=source_1, dtype=terminal_1_dtype
        )
        terminal_op_2 = TerminalOperator(
            source=source_2, dtype=terminal_2_dtype
        )

        basis_node = Node(operator=basis_op)
        terminal_node_1 = Node(operator=terminal_op_2)
        terminal_node_2 = Node(operator=terminal_op_1)
        terminal_node_3 = Node(operator=terminal_op_2)

        basis_node.add_child(child=terminal_node_1, position=0)

        self.assertIsNone(basis_node.right)

        basis_node.add_child(child=terminal_node_2, position=1)

        self.assertTupleEqual(
            basis_node.right, (None, terminal_node_2)
        )

        basis_node.add_child(child=terminal_node_3, position=2)

        self.assertTupleEqual(
            basis_node.right, (terminal_node_3, terminal_node_2)
        )


class TestTree(unittest.TestCase):

    def test_zero_depth_tree_iter(self):
        """Test that a tree consisting of just one TerminalNode behaves as
        expected upon iteration.

        """
        x = TerminalOperator(source=xrange(10), dtype=int)

        node_1 = Node(operator=x)

        tree = Tree(root=node_1)
        tree_iter = iter(tree)

        iter_0 = tree_iter.next()

        self.assertRaises(StopIteration, tree_iter.next)

        self.assertIs(iter_0, node_1)

    def test_unary_tree_iter(self):
        """Test that a trivial tree (a singly-linked list, really) behaves as
        expected upon iteration. The tree looks like this:

                           node_3
                             |
                           node_2
                             |
                           node_1

        The expected iteration is post-order depth-first, the nodes in the
        diagram are numbered accordingly.

        """
        def identity(a): return a

        id_op_1 = BasisOperator(func=identity, signature=(int,), dtype=int)
        id_op_2 = BasisOperator(func=identity, signature=(int,), dtype=int)

        x = TerminalOperator(source=xrange(10), dtype=int)

        node_1 = Node(operator=x)
        node_2 = Node(operator=id_op_2)
        node_3 = Node(operator=id_op_1)

        node_3.add_child(child=node_2, position=0)
        node_2.add_child(child=node_1, position=0)

        tree = Tree(root=node_3)
        tree_iter = iter(tree)

        iter_0 = tree_iter.next()
        iter_1 = tree_iter.next()
        iter_2 = tree_iter.next()

        self.assertRaises(StopIteration, tree_iter.next)

        self.assertIs(iter_0, node_1)
        self.assertIs(iter_1, node_2)
        self.assertIs(iter_2, node_3)

    def test_binary_tree_iter(self):
        """Test that iteration behaves as expected on an arity 2 tree with
        nontrivial structure. The tree looks like this:

                                node_11
                               /       \
                         node_5        node_10
                        /   \           /     \
                  node_1    node_4   node_6   node_9
                           /  \               /   \
                    node_2   node_3     node_7   node_8

        The expected iteration is post-order depth-first, the nodes in the
        diagram are numbered accordingly.

        """
        def add(a, b): return a + b

        def sub(a, b): return a - b

        def mul(a, b): return a * b

        def div(a, b): return a / b

        add_op = BasisOperator(func=add, signature=(int, int), dtype=int)
        sub_op = BasisOperator(func=sub, signature=(int, int), dtype=int)
        mul_op = BasisOperator(func=mul, signature=(int, int), dtype=int)
        div_op = BasisOperator(func=div, signature=(int, int), dtype=int)

        x = TerminalOperator(source=xrange(10), dtype=int)
        y = TerminalOperator(source=xrange(10), dtype=int)
        z = TerminalOperator(source=xrange(10), dtype=int)
        three = TerminalOperator(source=(3 for _ in xrange(10)), dtype=int)
        four = TerminalOperator(source=(4 for _ in xrange(10)), dtype=int)
        five = TerminalOperator(source=(5 for _ in xrange(10)), dtype=int)

        node_1 = Node(operator=x)
        node_2 = Node(operator=three)
        node_3 = Node(operator=four)
        node_4 = Node(operator=mul_op)
        node_5 = Node(operator=sub_op)
        node_6 = Node(operator=z)
        node_7 = Node(operator=y)
        node_8 = Node(operator=five)
        node_9 = Node(operator=div_op)
        node_10 = Node(operator=mul_op)
        node_11 = Node(operator=add_op)

        node_11.add_child(child=node_5, position=0)
        node_11.add_child(child=node_10, position=1)
        node_5.add_child(child=node_1, position=0)
        node_5.add_child(child=node_4, position=1)
        node_4.add_child(child=node_2, position=0)
        node_4.add_child(child=node_3, position=1)
        node_10.add_child(child=node_6, position=0)
        node_10.add_child(child=node_9, position=1)
        node_9.add_child(child=node_7, position=0)
        node_9.add_child(child=node_8, position=1)

        tree = Tree(root=node_11)
        tree_iter = iter(tree)

        iter_0 = tree_iter.next()
        iter_1 = tree_iter.next()
        iter_2 = tree_iter.next()
        iter_3 = tree_iter.next()
        iter_4 = tree_iter.next()
        iter_5 = tree_iter.next()
        iter_6 = tree_iter.next()
        iter_7 = tree_iter.next()
        iter_8 = tree_iter.next()
        iter_9 = tree_iter.next()
        iter_10 = tree_iter.next()

        self.assertRaises(StopIteration, tree_iter.next)

        self.assertIs(iter_0, node_1)
        self.assertIs(iter_1, node_2)
        self.assertIs(iter_2, node_3)
        self.assertIs(iter_3, node_4)
        self.assertIs(iter_4, node_5)
        self.assertIs(iter_5, node_6)
        self.assertIs(iter_6, node_7)
        self.assertIs(iter_7, node_8)
        self.assertIs(iter_8, node_9)
        self.assertIs(iter_9, node_10)
        self.assertIs(iter_10, node_11)

    def test_multi_arity_tree_iter_1(self):
        """Test that a nontrivial tree composed of operators having arbitrary
        arity behaves as expected upon iteration. The tree looks like this:

                             node_14
                            /   |   \
                     node_5  node_6  node_13
                    /   \            /    \
              node_1   node_4    node_7  node_12
                      /    \             /     \
                node_2    node_3    node_10   node_11
                                     /   \
                                node_8   node_9

        The expected iteration is post-order depth-first, the nodes in the
        diagram are numbered accordingly.

        """
        def arity_3(a, b, c): return a + b + c

        def arity_2a(a, b): return a + b

        def arity_2b(a, b): return a + b

        def arity_2c(a, b): return a + b

        def arity_2d(a, b): return a + b

        def arity_2e(a, b): return a + b

        arity_3_op = BasisOperator(
            func=arity_3, signature=(int, int, int), dtype=int
        )

        arity_2a_op = BasisOperator(
            func=arity_2a, signature=(int, int), dtype=int
        )

        arity_2b_op = BasisOperator(
            func=arity_2b, signature=(int, int), dtype=int
        )

        arity_2c_op = BasisOperator(
            func=arity_2c, signature=(int, int), dtype=int
        )

        arity_2d_op = BasisOperator(
            func=arity_2d, signature=(int, int), dtype=int
        )

        arity_2e_op = BasisOperator(
            func=arity_2e, signature=(int, int), dtype=int
        )

        terminal_a_op = TerminalOperator(source=xrange(10), dtype=int)
        terminal_b_op = TerminalOperator(source=xrange(10), dtype=int)
        terminal_c_op = TerminalOperator(source=xrange(10), dtype=int)
        terminal_d_op = TerminalOperator(source=xrange(10), dtype=int)
        terminal_e_op = TerminalOperator(source=xrange(10), dtype=int)
        terminal_f_op = TerminalOperator(source=xrange(10), dtype=int)
        terminal_g_op = TerminalOperator(source=xrange(10), dtype=int)
        terminal_h_op = TerminalOperator(source=xrange(10), dtype=int)

        node_1 = Node(operator=terminal_a_op)
        node_2 = Node(operator=terminal_b_op)
        node_3 = Node(operator=terminal_c_op)
        node_4 = Node(operator=arity_2b_op)
        node_5 = Node(operator=arity_2a_op)
        node_6 = Node(operator=terminal_g_op)
        node_7 = Node(operator=terminal_h_op)
        node_8 = Node(operator=terminal_d_op)
        node_9 = Node(operator=terminal_e_op)
        node_10 = Node(operator=arity_2e_op)
        node_11 = Node(operator=terminal_f_op)
        node_12 = Node(operator=arity_2d_op)
        node_13 = Node(operator=arity_2c_op)
        node_14 = Node(operator=arity_3_op)

        node_14.add_child(child=node_5, position=0)
        node_14.add_child(child=node_6, position=1)
        node_14.add_child(child=node_13, position=2)
        node_5.add_child(child=node_1, position=0)
        node_5.add_child(child=node_4, position=1)
        node_4.add_child(child=node_2, position=0)
        node_4.add_child(child=node_3, position=1)
        node_13.add_child(child=node_7, position=0)
        node_13.add_child(child=node_12, position=1)
        node_12.add_child(child=node_10, position=0)
        node_12.add_child(child=node_11, position=1)
        node_10.add_child(child=node_8, position=0)
        node_10.add_child(child=node_9, position=1)

        tree = Tree(root=node_14)
        tree_iter = iter(tree)

        iter_0 = tree_iter.next()
        iter_1 = tree_iter.next()
        iter_2 = tree_iter.next()
        iter_3 = tree_iter.next()
        iter_4 = tree_iter.next()
        iter_5 = tree_iter.next()
        iter_6 = tree_iter.next()
        iter_7 = tree_iter.next()
        iter_8 = tree_iter.next()
        iter_9 = tree_iter.next()
        iter_10 = tree_iter.next()
        iter_11 = tree_iter.next()
        iter_12 = tree_iter.next()
        iter_13 = tree_iter.next()

        self.assertRaises(StopIteration, tree_iter.next)

        self.assertIs(iter_0, node_1)
        self.assertIs(iter_1, node_2)
        self.assertIs(iter_2, node_3)
        self.assertIs(iter_3, node_4)
        self.assertIs(iter_4, node_5)
        self.assertIs(iter_5, node_6)
        self.assertIs(iter_6, node_7)
        self.assertIs(iter_7, node_8)
        self.assertIs(iter_8, node_9)
        self.assertIs(iter_9, node_10)
        self.assertIs(iter_10, node_11)
        self.assertIs(iter_11, node_12)
        self.assertIs(iter_12, node_13)
        self.assertIs(iter_13, node_14)

    def test_multi_arity_tree_iter_2(self):
        """Test iteration over a different multi-arity tree. The tree looks
        like this:

                              node_10
                            /   |     \
                     node_3  node_6    node_9
                   /    \     /   \      |    \
            node_1 node_2 node_4 node_5 node_7 node_8

        The expected iteration is post-order depth-first, the nodes in the
        diagram are numbered accordingly.

        """
        def arity_3(a, b, c): return a + b + c

        def arity_2a(a, b): return a + b

        def arity_2b(a, b): return a + b

        def arity_2c(a, b): return a + b

        arity_3_op = BasisOperator(
            func=arity_3, signature=(int, int, int), dtype=int
        )

        arity_2a_op = BasisOperator(
            func=arity_2a, signature=(int, int), dtype=int
        )

        arity_2b_op = BasisOperator(
            func=arity_2b, signature=(int, int), dtype=int
        )

        arity_2c_op = BasisOperator(
            func=arity_2c, signature=(int, int), dtype=int
        )

        terminal_a_op = TerminalOperator(source=xrange(10), dtype=int)
        terminal_b_op = TerminalOperator(source=xrange(10), dtype=int)
        terminal_c_op = TerminalOperator(source=xrange(10), dtype=int)
        terminal_d_op = TerminalOperator(source=xrange(10), dtype=int)
        terminal_e_op = TerminalOperator(source=xrange(10), dtype=int)
        terminal_f_op = TerminalOperator(source=xrange(10), dtype=int)

        node_1 = Node(operator=terminal_a_op)
        node_2 = Node(operator=terminal_b_op)
        node_3 = Node(operator=arity_2a_op)
        node_4 = Node(operator=terminal_c_op)
        node_5 = Node(operator=terminal_d_op)
        node_6 = Node(operator=arity_2b_op)
        node_7 = Node(operator=terminal_e_op)
        node_8 = Node(operator=terminal_f_op)
        node_9 = Node(operator=arity_2c_op)
        node_10 = Node(operator=arity_3_op)

        node_10.add_child(child=node_3, position=0)
        node_10.add_child(child=node_6, position=1)
        node_10.add_child(child=node_9, position=2)
        node_3.add_child(child=node_1, position=0)
        node_3.add_child(child=node_2, position=1)
        node_6.add_child(child=node_4, position=0)
        node_6.add_child(child=node_5, position=1)
        node_9.add_child(child=node_7, position=0)
        node_9.add_child(child=node_8, position=1)

        tree = Tree(root=node_10)
        tree_iter = iter(tree)

        iter_0 = tree_iter.next()
        iter_1 = tree_iter.next()
        iter_2 = tree_iter.next()
        iter_3 = tree_iter.next()
        iter_4 = tree_iter.next()
        iter_5 = tree_iter.next()
        iter_6 = tree_iter.next()
        iter_7 = tree_iter.next()
        iter_8 = tree_iter.next()
        iter_9 = tree_iter.next()

        self.assertRaises(StopIteration, tree_iter.next)

        self.assertIs(iter_0, node_1)
        self.assertIs(iter_1, node_2)
        self.assertIs(iter_2, node_3)
        self.assertIs(iter_3, node_4)
        self.assertIs(iter_4, node_5)
        self.assertIs(iter_5, node_6)
        self.assertIs(iter_6, node_7)
        self.assertIs(iter_7, node_8)
        self.assertIs(iter_8, node_9)
        self.assertIs(iter_9, node_10)

    def test_multi_arity_tree_iter_3(self):
        """Test a iteration over a different multi-arity tree. The tree looks
        like this:

                             node_6
                            /      \
                        node_4    node_5
                      /   |   \
                node_1 node_2 node_3

        The expected iteration is post-order depth-first, the nodes in the
        diagram are numbered accordingly.

        """
        def arity_3(a, b, c): return a + b + c

        def arity_2(a, b): return a + b

        arity_3_op = BasisOperator(
            func=arity_3, signature=(int, int, int), dtype=int
        )

        arity_2_op = BasisOperator(
            func=arity_2, signature=(int, int), dtype=int
        )

        terminal_a_op = TerminalOperator(source=xrange(10), dtype=int)
        terminal_b_op = TerminalOperator(source=xrange(10), dtype=int)
        terminal_c_op = TerminalOperator(source=xrange(10), dtype=int)
        terminal_d_op = TerminalOperator(source=xrange(10), dtype=int)

        node_1 = Node(operator=terminal_a_op)
        node_2 = Node(operator=terminal_b_op)
        node_3 = Node(operator=terminal_c_op)
        node_4 = Node(operator=arity_3_op)
        node_5 = Node(operator=terminal_d_op)
        node_6 = Node(operator=arity_2_op)

        node_6.add_child(child=node_4, position=0)
        node_6.add_child(child=node_5, position=1)
        node_4.add_child(child=node_1, position=0)
        node_4.add_child(child=node_2, position=1)
        node_4.add_child(child=node_3, position=2)

        tree = Tree(root=node_6)
        tree_iter = iter(tree)

        iter_0 = tree_iter.next()
        iter_1 = tree_iter.next()
        iter_2 = tree_iter.next()
        iter_3 = tree_iter.next()
        iter_4 = tree_iter.next()
        iter_5 = tree_iter.next()

        self.assertRaises(StopIteration, tree_iter.next)

        self.assertIs(iter_0, node_1)
        self.assertIs(iter_1, node_2)
        self.assertIs(iter_2, node_3)
        self.assertIs(iter_3, node_4)
        self.assertIs(iter_4, node_5)
        self.assertIs(iter_5, node_6)
