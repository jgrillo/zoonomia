import unittest
import pickle

from zoonomia.tree import (
    Node, Tree, calls_iter, symbols_iter
)
from zoonomia.lang import Symbol, Operator
from zoonomia.types import Type


class TestNode(unittest.TestCase):

    def test_equals_reflexive(self):
        """Test that an object equals itself."""
        some_type = Type(name='SomeType')
        signature = (some_type,)
        dtype = some_type

        basis_op = Operator(
            symbol=Symbol('func', dtype=dtype), signature=signature
        )
        terminal_op = Operator(symbol=Symbol(name='term', dtype=dtype))

        node_1 = Node(operator=basis_op)
        terminal_node_1 = Node(operator=terminal_op)

        node_1.add_child(child=terminal_node_1, position=0)

        node_2 = node_1

        self.assertIs(node_1, node_2)
        self.assertEquals(node_1, node_2)

    def test_equals_symmetric(self):
        """Test that for objects :math:`\{x,y\}, x = y \iff y = x`."""
        some_type = Type(name='SomeType')
        signature = (some_type,)
        dtype = some_type

        basis_op = Operator(
            symbol=Symbol('func', dtype=dtype), signature=signature
        )
        terminal_op = Operator(symbol=Symbol(name='term', dtype=dtype))

        node_1 = Node(operator=basis_op)
        terminal_node_1 = Node(operator=terminal_op)

        node_1.add_child(child=terminal_node_1, position=0)

        node_2 = Node(operator=basis_op)
        terminal_node_2 = Node(operator=terminal_op)

        node_2.add_child(child=terminal_node_2, position=0)

        another_node = Node(operator=terminal_op)

        self.assertFalse(node_1 is node_2)

        self.assertEqual(node_1, node_2)
        self.assertEqual(node_2, node_1)

        self.assertFalse(node_1 is another_node)

        self.assertNotEqual(node_1, another_node)
        self.assertNotEqual(another_node, node_1)

    def test_equals_transitive(self):
        """Test that for objects :math:`\{x,y,z\}, x = y, y = z \iff x = z`."""
        some_type = Type(name='SomeType')
        signature = (some_type,)
        dtype = some_type

        basis_op = Operator(
            symbol=Symbol('func', dtype=dtype), signature=signature
        )
        terminal_op = Operator(symbol=Symbol(name='term', dtype=dtype))

        node_1 = Node(operator=basis_op)
        terminal_node_1 = Node(operator=terminal_op)

        node_1.add_child(child=terminal_node_1, position=0)

        node_2 = Node(operator=basis_op)
        terminal_node_2 = Node(operator=terminal_op)

        node_2.add_child(child=terminal_node_2, position=0)

        node_3 = Node(operator=basis_op)
        terminal_node_3 = Node(operator=terminal_op)

        node_3.add_child(child=terminal_node_3, position=0)

        self.assertFalse(node_1 is node_2)
        self.assertFalse(node_2 is node_3)
        self.assertFalse(node_1 is node_3)

        self.assertEqual(node_1, node_2)
        self.assertEqual(node_2, node_3)
        self.assertEqual(node_1, node_3)

    def test_equals_consistent(self):
        """Test that repeated equals calls return the same value."""
        some_type = Type(name='SomeType')
        signature = (some_type,)
        dtype = some_type

        basis_op = Operator(
            symbol=Symbol('func', dtype=dtype), signature=signature
        )
        terminal_op = Operator(symbol=Symbol(name='term', dtype=dtype))

        node_1 = Node(operator=basis_op)
        terminal_node_1 = Node(operator=terminal_op)

        node_1.add_child(child=terminal_node_1, position=0)

        node_2 = Node(operator=basis_op)
        terminal_node_2 = Node(operator=terminal_op)

        node_2.add_child(child=terminal_node_2, position=0)

        another_node = Node(operator=terminal_op)

        self.assertFalse(node_1 is node_2)

        self.assertEqual(node_1, node_2)
        self.assertEqual(node_1, node_2)
        self.assertEqual(node_1, node_2)

        self.assertFalse(node_1 is another_node)

        self.assertNotEqual(node_1, another_node)
        self.assertNotEqual(node_1, another_node)
        self.assertNotEqual(node_1, another_node)

    def test_hash_consistent(self):
        """Test that repeated hash calls yield the same value."""
        some_type = Type(name='SomeType')
        signature = (some_type,)
        dtype = some_type

        basis_op = Operator(
            symbol=Symbol('func', dtype=dtype), signature=signature
        )
        terminal_op = Operator(symbol=Symbol(name='term', dtype=dtype))

        node_1 = Node(operator=basis_op)
        terminal_node_1 = Node(operator=terminal_op)

        node_1.add_child(child=terminal_node_1, position=0)
        hash_1 = hash(node_1)

        self.assertEqual(hash_1, hash(node_1))
        self.assertEqual(hash_1, hash(node_1))
        self.assertEqual(hash_1, hash(node_1))

    def test_hash_equals(self):
        """Test that when two objects are equal their hashes are equal."""
        some_type = Type(name='SomeType')
        signature = (some_type,)
        dtype = some_type

        basis_op = Operator(
            symbol=Symbol('func', dtype=dtype), signature=signature
        )
        terminal_op = Operator(symbol=Symbol(name='term', dtype=dtype))

        node_1 = Node(operator=basis_op)
        terminal_node_1 = Node(operator=terminal_op)

        node_1.add_child(child=terminal_node_1, position=0)

        node_2 = Node(operator=basis_op)
        terminal_node_2 = Node(operator=terminal_op)

        node_2.add_child(child=terminal_node_2, position=0)

        self.assertFalse(node_1 is node_2)

        self.assertEqual(hash(node_1), hash(node_2))
        self.assertEqual(node_1, node_2)

    def test_node_operator_attribute(self):
        """Test that the *operator* attribute is a reference to the basis
        operator passed into the constructor.

        """
        some_type = Type(name='SomeType')
        signature = (some_type,)
        dtype = some_type
        symbol = Symbol(name='some_symbol', dtype=dtype)

        basis_op = Operator(symbol=symbol, signature=signature)

        basis_node_1 = Node(operator=basis_op)
        basis_node_2 = Node(operator=basis_op)

        self.assertIs(basis_node_1.operator, basis_node_2.operator)

    def test_node_dtype(self):
        """Test that a Node's dtype is identically the same as its operator's
        dtype.

        """
        some_type = Type(name='SomeType')
        basis_dtype = some_type
        basis_symbol = Symbol(name='func', dtype=basis_dtype)

        some_other_type = Type(name='SomeOtherType')
        terminal_dtype = some_other_type
        terminal_symbol = Symbol(name='term', dtype=terminal_dtype)

        signature = (some_type, some_other_type)

        basis_op = Operator(symbol=basis_symbol, signature=signature)
        terminal_op = Operator(symbol=terminal_symbol)

        basis_node = Node(operator=basis_op)
        terminal_node = Node(operator=terminal_op)

        self.assertIs(terminal_node.dtype, terminal_op.dtype)
        self.assertIs(basis_node.dtype, basis_op.dtype)

    def test_add_child_raises_signature_type_mismatch(self):
        """Test that the add_child method raises TypeError if the child's dtype
        does not match the node's operator's signature at the given position.

        """
        some_type = Type(name='SomeType')
        signature = (some_type,)
        basis_dtype = some_type
        basis_symbol = Symbol(name='func', dtype=basis_dtype)

        some_other_type = Type(name='SomeOtherType')
        terminal_dtype = some_other_type
        terminal_symbol = Symbol(name='term', dtype=terminal_dtype)

        basis_op = Operator(symbol=basis_symbol, signature=signature)
        terminal_op = Operator(symbol=terminal_symbol)

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
        some_type = Type(name='SomeType')
        signature = (some_type,)
        dtype = some_type
        basis_symbol = Symbol(name='func', dtype=dtype)

        basis_op = Operator(symbol=basis_symbol, signature=signature)
        terminal_op = Operator(symbol=basis_symbol)

        basis_node = Node(operator=basis_op)
        terminal_node = Node(operator=terminal_op)

        self.assertRaises(
            IndexError, basis_node.add_child, child=terminal_node, position=1
        )

    def test_node_left(self):
        """Test that a Node's left attribute contains the child corresponding
        to the operator's signature at position 0.

        """
        some_type = Type(name='SomeType')
        signature = (some_type,)
        dtype = some_type
        basis_symbol = Symbol(name='func', dtype=dtype)

        basis_op = Operator(symbol=basis_symbol, signature=signature)
        terminal_op = Operator(symbol=Symbol(name='term', dtype=dtype))

        basis_node = Node(operator=basis_op)
        terminal_node = Node(operator=terminal_op)

        basis_node.add_child(child=terminal_node, position=0)

        self.assertEqual(0, basis_node.depth)
        self.assertEqual(1, terminal_node.depth)

        self.assertIs(basis_node.left, terminal_node)

    def test_node_right(self):
        """Test that a Node's right attribute contains all the children
        corresponding to the nonzero signature positions, reversed.

        """
        some_type = Type(name='SomeType')
        some_other_type = Type(name='SomeOtherType')
        signature = (some_type, some_other_type, some_type)
        basis_dtype = some_type
        basis_symbol = Symbol(name='func', dtype=basis_dtype)

        terminal_1_dtype = some_other_type
        terminal_2_dtype = some_type

        basis_op = Operator(symbol=basis_symbol, signature=signature)
        terminal_op_1 = Operator(
            symbol=Symbol(name='term1', dtype=terminal_1_dtype)
        )
        terminal_op_2 = Operator(
            symbol=Symbol(name='term2', dtype=terminal_2_dtype)
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

        self.assertEqual(0, basis_node.depth)
        self.assertEqual(1, terminal_node_1.depth)
        self.assertEqual(1, terminal_node_2.depth)
        self.assertEqual(1, terminal_node_3.depth)

    def test_node_pickle(self):
        """Test that a Node instance can be pickled and unpickled using the
        default protocol.

        """
        some_type = Type(name='SomeType')
        signature = (some_type, some_type)
        dtype = some_type

        basis_op_0 = Operator(
            symbol=Symbol('func_0', dtype=dtype), signature=signature
        )
        basis_op_1 = Operator(
            symbol=Symbol('func_1', dtype=dtype), signature=signature
        )
        terminal_op_0 = Operator(symbol=Symbol(name='term_0', dtype=dtype))
        terminal_op_1 = Operator(symbol=Symbol(name='term_1', dtype=dtype))
        terminal_op_2 = Operator(symbol=Symbol(name='term_2', dtype=dtype))

        root = Node(operator=basis_op_0)
        basis_node = Node(operator=basis_op_1)
        terminal_node_0 = Node(operator=terminal_op_0)
        terminal_node_1 = Node(operator=terminal_op_1)
        terminal_node_2 = Node(operator=terminal_op_2)

        root.add_child(child=terminal_node_0, position=0)
        root.add_child(child=basis_node, position=1)

        basis_node.add_child(child=terminal_node_1, position=0)
        basis_node.add_child(child=terminal_node_2, position=1)

        pickled_root = pickle.dumps(root)
        unpickled_root = pickle.loads(pickled_root)

        self.assertEqual(root, unpickled_root)


class TestTree(unittest.TestCase):

    def test_equals_reflexive(self):
        """Test that an object equals itself."""
        int_type = Type(name='int')
        id_op_1 = Operator(
            symbol=Symbol(name='identity_1', dtype=int_type),
            signature=(int_type,)
        )

        terminal_op = Operator(symbol=Symbol(name='term', dtype=int_type))

        node_11 = Node(operator=id_op_1)
        node_12 = Node(operator=terminal_op)

        root_1 = Node(operator=id_op_1)
        root_1.add_child(child=node_11, position=0)
        node_11.add_child(child=node_12, position=0)

        tree_1 = Tree(root=root_1)
        tree_2 = tree_1

        self.assertIs(tree_1, tree_2)
        self.assertEquals(tree_1, tree_2)

    def test_equals_symmetric(self):
        """Test that for objects :math:`\{x,y\}, x = y \iff y = x`."""
        int_type = Type(name='int')
        id_op_1 = Operator(
            symbol=Symbol(name='identity_1', dtype=int_type),
            signature=(int_type,)
        )
        id_op_2 = Operator(
            symbol=Symbol(name='identity_2', dtype=int_type),
            signature=(int_type,)
        )

        terminal_op = Operator(symbol=Symbol(name='term', dtype=int_type))

        node_11 = Node(operator=id_op_1)
        node_12 = Node(operator=terminal_op)
        node_21 = Node(operator=id_op_1)
        node_22 = Node(operator=terminal_op)

        another_node_1 = Node(operator=id_op_2)
        another_node_2 = Node(operator=terminal_op)

        root_1 = Node(operator=id_op_1)
        root_1.add_child(child=node_11, position=0)
        node_11.add_child(child=node_12, position=0)

        root_2 = Node(operator=id_op_1)
        root_2.add_child(child=node_21, position=0)
        node_21.add_child(child=node_22, position=0)

        another_root = Node(operator=id_op_2)
        another_root.add_child(child=another_node_1, position=0)
        another_node_1.add_child(child=another_node_2, position=0)

        tree_1 = Tree(root=root_1)
        tree_2 = Tree(root=root_2)
        another_tree = Tree(root=another_root)

        self.assertFalse(tree_1 is tree_2)

        self.assertEqual(tree_1, tree_2)
        self.assertEqual(tree_2, tree_1)

        self.assertFalse(tree_1 is another_tree)

        self.assertNotEqual(tree_1, another_tree)
        self.assertNotEqual(another_tree, tree_1)

    def test_equals_transitive(self):
        """Test that for objects :math:`\{x,y,z\}, x = y, y = z \iff x = z`."""
        int_type = Type(name='int')
        id_op_1 = Operator(
            symbol=Symbol(name='identity_1', dtype=int_type),
            signature=(int_type,)
        )
        id_op_2 = Operator(
            symbol=Symbol(name='identity_2', dtype=int_type),
            signature=(int_type,)
        )

        terminal_op = Operator(symbol=Symbol(name='term', dtype=int_type))

        node_11 = Node(operator=id_op_1)
        node_12 = Node(operator=terminal_op)
        node_21 = Node(operator=id_op_1)
        node_22 = Node(operator=terminal_op)
        node_31 = Node(operator=id_op_1)
        node_32 = Node(operator=terminal_op)

        root_1 = Node(operator=id_op_2)
        root_1.add_child(child=node_11, position=0)
        node_11.add_child(child=node_12, position=0)

        root_2 = Node(operator=id_op_2)
        root_2.add_child(child=node_21, position=0)
        node_21.add_child(child=node_22, position=0)

        root_3 = Node(operator=id_op_2)
        root_3.add_child(child=node_31, position=0)
        node_31.add_child(child=node_32, position=0)

        tree_1 = Tree(root=root_1)
        tree_2 = Tree(root=root_2)
        tree_3 = Tree(root=root_3)

        self.assertFalse(tree_1 is tree_2)
        self.assertFalse(tree_2 is tree_3)
        self.assertFalse(tree_1 is tree_3)

        self.assertEquals(tree_1, tree_2)
        self.assertEquals(tree_2, tree_3)
        self.assertEquals(tree_1, tree_3)

    def test_equals_consistent(self):
        """Test that repeated equals calls return the same value."""
        int_type = Type(name='int')
        id_op_1 = Operator(
            symbol=Symbol(name='identity_1', dtype=int_type),
            signature=(int_type,)
        )
        id_op_2 = Operator(
            symbol=Symbol(name='identity_2', dtype=int_type),
            signature=(int_type,)
        )

        terminal_op = Operator(symbol=Symbol(name='term', dtype=int_type))

        node_11 = Node(operator=id_op_1)
        node_12 = Node(operator=terminal_op)
        node_21 = Node(operator=id_op_1)
        node_22 = Node(operator=terminal_op)

        another_node_1 = Node(operator=id_op_2)
        another_node_2 = Node(operator=terminal_op)

        root_1 = Node(operator=id_op_1)
        root_1.add_child(child=node_11, position=0)
        node_11.add_child(child=node_12, position=0)

        root_2 = Node(operator=id_op_1)
        root_2.add_child(child=node_21, position=0)
        node_21.add_child(child=node_22, position=0)

        another_root = Node(operator=id_op_2)
        another_root.add_child(child=another_node_1, position=0)
        another_node_1.add_child(child=another_node_2, position=0)

        tree_1 = Tree(root=root_1)
        tree_2 = Tree(root=root_2)
        another_tree = Tree(root=another_root)

        self.assertFalse(tree_1 is tree_2)

        self.assertEqual(tree_1, tree_2)
        self.assertEqual(tree_1, tree_2)
        self.assertEqual(tree_1, tree_2)

        self.assertFalse(tree_1 is another_tree)

        self.assertNotEqual(tree_1, another_tree)
        self.assertNotEqual(tree_1, another_tree)
        self.assertNotEqual(tree_1, another_tree)

    def test_hash_consistent(self):
        """Test that repeated hash calls yield the same value."""
        int_type = Type(name='int')
        id_op_1 = Operator(
            symbol=Symbol(name='identity_1', dtype=int_type),
            signature=(int_type,)
        )

        terminal_op = Operator(symbol=Symbol(name='term', dtype=int_type))

        node_11 = Node(operator=id_op_1)
        node_12 = Node(operator=terminal_op)

        root_1 = Node(operator=id_op_1)
        root_1.add_child(child=node_11, position=0)
        node_11.add_child(child=node_12, position=0)

        tree_1 = Tree(root=root_1)
        hash_1 = hash(tree_1)

        self.assertEqual(hash_1, hash(tree_1))
        self.assertEqual(hash_1, hash(tree_1))
        self.assertEqual(hash_1, hash(tree_1))

    def test_hash_equals(self):
        """Test that when two objects are equal their hashes are equal."""
        int_type = Type(name='int')
        id_op_1 = Operator(
            symbol=Symbol(name='identity_1', dtype=int_type),
            signature=(int_type,)
        )

        terminal_op = Operator(symbol=Symbol(name='term', dtype=int_type))

        node_11 = Node(operator=id_op_1)
        node_12 = Node(operator=terminal_op)
        node_21 = Node(operator=id_op_1)
        node_22 = Node(operator=terminal_op)

        root_1 = Node(operator=id_op_1)
        root_1.add_child(child=node_11, position=0)
        node_11.add_child(child=node_12, position=0)

        root_2 = Node(operator=id_op_1)
        root_2.add_child(child=node_21, position=0)
        node_21.add_child(child=node_22, position=0)

        tree_1 = Tree(root=root_1)
        tree_2 = Tree(root=root_2)

        self.assertFalse(tree_1 is tree_2)

        self.assertEqual(hash(tree_1), hash(tree_2))
        self.assertEqual(tree_1, tree_2)

    def test_zero_depth_tree_post_order_iter(self):
        """Test that a tree consisting of just one Node behaves as expected
        upon post-order traversal.

        """
        int_type = Type(name='int')
        x = Operator(symbol=Symbol(name='term', dtype=int_type))

        node_1 = Node(operator=x)

        tree = Tree(root=node_1)
        tree_iter = iter(tree)

        iter_0 = tree_iter.next()

        self.assertRaises(StopIteration, tree_iter.next)

        self.assertIs(iter_0, node_1)

    def test_zero_depth_tree_pre_order_iter(self):
        """Test that a tree consisting of just one Node behaves as expected
        upon pre-order traversal.

        """
        int_type = Type(name='int')
        x = Operator(symbol=Symbol(name='term', dtype=int_type))

        node_1 = Node(operator=x)

        tree = Tree(root=node_1)
        pre_order_iter = tree.pre_order_iter()

        iter_0 = pre_order_iter.next()

        self.assertRaises(StopIteration, pre_order_iter.next)

        self.assertIs(iter_0, node_1)

    def test_zero_depth_tree_bfs_iter(self):
        """Test that a tree consisting of just one Node behaves as expected
        upon breadth-first traversal.

        """
        int_type = Type(name='int')
        x = Operator(symbol=Symbol(name='term', dtype=int_type))

        node_1 = Node(operator=x)

        tree = Tree(root=node_1)
        bfs_iter = tree.bfs_iter()

        iter_0 = bfs_iter.next()

        self.assertRaises(StopIteration, bfs_iter.next)

        self.assertIs(iter_0, node_1)

    def test_unary_tree_post_order_iter(self):
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
        int_type = Type(name='int')
        id_op_1 = Operator(
            symbol=Symbol(name='identity', dtype=int_type),
            signature=(int_type,)
        )
        id_op_2 = Operator(
            symbol=Symbol(name='identity', dtype=int_type),
            signature=(int_type,)
        )
        x = Operator(symbol=Symbol(name='x', dtype=int_type))

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

    def test_unary_tree_pre_order_iter(self):
        """Test that a trivial tree (a singly-linked list, really) behaves as
        expected upon pre-order iteration. The tree looks like this:

                           node_1
                             |
                           node_2
                             |
                           node_3

        The expected iteration is pre-order depth-first, the nodes in the
        diagram are numbered accordingly.

        """
        int_type = Type(name='int')
        id_op_1 = Operator(
            symbol=Symbol(name='identity', dtype=int_type),
            signature=(int_type,)
        )
        id_op_2 = Operator(
            symbol=Symbol(name='identity', dtype=int_type),
            signature=(int_type,)
        )
        x = Operator(symbol=Symbol(name='x', dtype=int_type))

        node_3 = Node(operator=x)
        node_2 = Node(operator=id_op_2)
        node_1 = Node(operator=id_op_1)

        node_1.add_child(child=node_2, position=0)
        node_2.add_child(child=node_3, position=0)

        tree = Tree(root=node_1)
        pre_order_iter = tree.pre_order_iter()

        iter_0 = pre_order_iter.next()
        iter_1 = pre_order_iter.next()
        iter_2 = pre_order_iter.next()

        self.assertRaises(StopIteration, pre_order_iter.next)

        self.assertIs(iter_0, node_1)
        self.assertIs(iter_1, node_2)
        self.assertIs(iter_2, node_3)

    def test_unary_tree_bfs_iter(self):
        """Test that a trivial tree (a singly-linked list, really) behaves as
        expected upon breadth-first iteration. The tree looks like this:

                           node_1
                             |
                           node_2
                             |
                           node_3

        The expected iteration is breadth-first, the nodes in the diagram are
        numbered accordingly.

        """
        int_type = Type(name='int')
        id_op_1 = Operator(
            symbol=Symbol(name='identity', dtype=int_type),
            signature=(int_type,)
        )
        id_op_2 = Operator(
            symbol=Symbol(name='identity', dtype=int_type),
            signature=(int_type,)
        )
        x = Operator(symbol=Symbol(name='x', dtype=int_type))

        node_3 = Node(operator=x)
        node_2 = Node(operator=id_op_2)
        node_1 = Node(operator=id_op_1)

        node_1.add_child(child=node_2, position=0)
        node_2.add_child(child=node_3, position=0)

        tree = Tree(root=node_1)
        bfs_iter = tree.bfs_iter()

        iter_0 = bfs_iter.next()
        iter_1 = bfs_iter.next()
        iter_2 = bfs_iter.next()

        self.assertRaises(StopIteration, bfs_iter.next)

        self.assertIs(iter_0, node_1)
        self.assertIs(iter_1, node_2)
        self.assertIs(iter_2, node_3)

    def test_binary_tree_post_order_iter(self):
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
        int_type = Type(name='int')
        add_op = Operator(
            symbol=Symbol(name='add', dtype=int_type),
            signature=(int_type, int_type)
        )
        sub_op = Operator(
            symbol=Symbol(name='sub', dtype=int_type),
            signature=(int_type, int_type)
        )
        mul_op = Operator(
            symbol=Symbol(name='mul', dtype=int_type),
            signature=(int_type, int_type)
        )
        div_op = Operator(
            symbol=Symbol(name='div', dtype=int_type),
            signature=(int_type, int_type)
        )

        x = Operator(symbol=Symbol(name='x', dtype=int_type))
        y = Operator(symbol=Symbol(name='y', dtype=int_type))
        z = Operator(symbol=Symbol(name='z', dtype=int_type))
        three = Operator(symbol=Symbol(name='three', dtype=int_type))
        four = Operator(symbol=Symbol(name='four', dtype=int_type))
        five = Operator(symbol=Symbol(name='five', dtype=int_type))

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

    def test_binary_tree_pre_order_iter(self):
        """Test that iteration behaves as expected on an arity 2 tree with
        nontrivial structure. The tree looks like this:

                                node_1
                               /      \
                         node_2       node_7
                        /   \          /    \
                  node_3   node_4   node_8   node_9
                           /  \              /   \
                     node_5   node_6   node_10   node_11

        The expected iteration is pre-order depth-first, the nodes in the
        diagram are numbered accordingly.

        """
        int_type = Type(name='int')
        add_op = Operator(
            symbol=Symbol(name='add', dtype=int_type),
            signature=(int_type, int_type)
        )
        sub_op = Operator(
            symbol=Symbol(name='sub', dtype=int_type),
            signature=(int_type, int_type)
        )
        mul_op = Operator(
            symbol=Symbol(name='mul', dtype=int_type),
            signature=(int_type, int_type)
        )
        div_op = Operator(
            symbol=Symbol(name='div', dtype=int_type),
            signature=(int_type, int_type)
        )

        x = Operator(symbol=Symbol(name='x', dtype=int_type))
        y = Operator(symbol=Symbol(name='y', dtype=int_type))
        z = Operator(symbol=Symbol(name='z', dtype=int_type))
        three = Operator(symbol=Symbol(name='three', dtype=int_type))
        four = Operator(symbol=Symbol(name='four', dtype=int_type))
        five = Operator(symbol=Symbol(name='five', dtype=int_type))

        node_3 = Node(operator=x)
        node_5 = Node(operator=three)
        node_6 = Node(operator=four)
        node_4 = Node(operator=mul_op)
        node_2 = Node(operator=sub_op)
        node_8 = Node(operator=z)
        node_10 = Node(operator=y)
        node_11 = Node(operator=five)
        node_9 = Node(operator=div_op)
        node_7 = Node(operator=mul_op)
        node_1 = Node(operator=add_op)

        node_1.add_child(child=node_2, position=0)
        node_1.add_child(child=node_7, position=1)
        node_2.add_child(child=node_3, position=0)
        node_2.add_child(child=node_4, position=1)
        node_4.add_child(child=node_5, position=0)
        node_4.add_child(child=node_6, position=1)
        node_7.add_child(child=node_8, position=0)
        node_7.add_child(child=node_9, position=1)
        node_9.add_child(child=node_10, position=0)
        node_9.add_child(child=node_11, position=1)

        tree = Tree(root=node_1)
        pre_order_iter = tree.pre_order_iter()

        iter_0 = pre_order_iter.next()
        iter_1 = pre_order_iter.next()
        iter_2 = pre_order_iter.next()
        iter_3 = pre_order_iter.next()
        iter_4 = pre_order_iter.next()
        iter_5 = pre_order_iter.next()
        iter_6 = pre_order_iter.next()
        iter_7 = pre_order_iter.next()
        iter_8 = pre_order_iter.next()
        iter_9 = pre_order_iter.next()
        iter_10 = pre_order_iter.next()

        self.assertRaises(StopIteration, pre_order_iter.next)

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

    def test_binary_tree_bfs_iter(self):
        """Test that iteration behaves as expected on an arity 2 tree with
        nontrivial structure. The tree looks like this:

                                node_1
                               /      \
                         node_2       node_3
                        /   \          /    \
                  node_4   node_5   node_6   node_7
                           /  \              /   \
                     node_8   node_9   node_10   node_11

        The expected iteration is breadth-first, the nodes in the diagram are
        numbered accordingly.

        """
        int_type = Type(name='int')
        add_op = Operator(
            symbol=Symbol(name='add', dtype=int_type),
            signature=(int_type, int_type)
        )
        sub_op = Operator(
            symbol=Symbol(name='sub', dtype=int_type),
            signature=(int_type, int_type)
        )
        mul_op = Operator(
            symbol=Symbol(name='mul', dtype=int_type),
            signature=(int_type, int_type)
        )
        div_op = Operator(
            symbol=Symbol(name='div', dtype=int_type),
            signature=(int_type, int_type)
        )

        x = Operator(symbol=Symbol(name='x', dtype=int_type))
        y = Operator(symbol=Symbol(name='y', dtype=int_type))
        z = Operator(symbol=Symbol(name='z', dtype=int_type))
        three = Operator(symbol=Symbol(name='three', dtype=int_type))
        four = Operator(symbol=Symbol(name='four', dtype=int_type))
        five = Operator(symbol=Symbol(name='five', dtype=int_type))

        node_4 = Node(operator=x)
        node_8 = Node(operator=three)
        node_9 = Node(operator=four)
        node_5 = Node(operator=mul_op)
        node_2 = Node(operator=sub_op)
        node_6 = Node(operator=z)
        node_10 = Node(operator=y)
        node_11 = Node(operator=five)
        node_7 = Node(operator=div_op)
        node_3 = Node(operator=mul_op)
        node_1 = Node(operator=add_op)

        node_1.add_child(child=node_2, position=0)
        node_1.add_child(child=node_3, position=1)
        node_2.add_child(child=node_4, position=0)
        node_2.add_child(child=node_5, position=1)
        node_3.add_child(child=node_6, position=0)
        node_3.add_child(child=node_7, position=1)
        node_5.add_child(child=node_8, position=0)
        node_5.add_child(child=node_9, position=1)
        node_7.add_child(child=node_10, position=0)
        node_7.add_child(child=node_11, position=1)

        tree = Tree(root=node_1)
        bfs_iter = tree.bfs_iter()

        iter_0 = bfs_iter.next()
        iter_1 = bfs_iter.next()
        iter_2 = bfs_iter.next()
        iter_3 = bfs_iter.next()
        iter_4 = bfs_iter.next()
        iter_5 = bfs_iter.next()
        iter_6 = bfs_iter.next()
        iter_7 = bfs_iter.next()
        iter_8 = bfs_iter.next()
        iter_9 = bfs_iter.next()
        iter_10 = bfs_iter.next()

        self.assertRaises(StopIteration, bfs_iter.next)

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

    def test_multi_arity_tree_post_order_iter_1(self):
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
        int_type = Type(name='int')
        arity_3_op = Operator(
            symbol=Symbol(name='arity_3', dtype=int_type),
            signature=(int_type, int_type, int_type)
        )

        arity_2a_op = Operator(
            symbol=Symbol(name='arity_2a', dtype=int_type),
            signature=(int_type, int_type)
        )

        arity_2b_op = Operator(
            symbol=Symbol(name='arity_2b', dtype=int_type),
            signature=(int_type, int_type)
        )

        arity_2c_op = Operator(
            symbol=Symbol(name='arity_2c', dtype=int_type),
            signature=(int_type, int_type)
        )

        arity_2d_op = Operator(
            symbol=Symbol(name='arity_2d', dtype=int_type),
            signature=(int_type, int_type)
        )

        arity_2e_op = Operator(
            symbol=Symbol(name='arity_2e', dtype=int_type),
            signature=(int_type, int_type)
        )

        terminal_a_op = Operator(symbol=Symbol(name='term_a', dtype=int_type))
        terminal_b_op = Operator(symbol=Symbol(name='term_b', dtype=int_type))
        terminal_c_op = Operator(symbol=Symbol(name='term_c', dtype=int_type))
        terminal_d_op = Operator(symbol=Symbol(name='term_d', dtype=int_type))
        terminal_e_op = Operator(symbol=Symbol(name='term_e', dtype=int_type))
        terminal_f_op = Operator(symbol=Symbol(name='term_f', dtype=int_type))
        terminal_g_op = Operator(symbol=Symbol(name='term_g', dtype=int_type))
        terminal_h_op = Operator(symbol=Symbol(name='term_h', dtype=int_type))

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

    def test_multi_arity_tree_pre_order_iter_1(self):
        """Test that a nontrivial tree composed of operators having arbitrary
        arity behaves as expected upon iteration. The tree looks like this:

                              node_1
                            /   |   \
                     node_2  node_7  node_8
                    /   \            /    \
              node_3   node_4    node_9  node_10
                      /    \             /     \
                node_5    node_6    node_11   node_14
                                     /   \
                                node_12   node_13

        The expected iteration is pre-order depth-first, the nodes in the
        diagram are numbered accordingly.

        """
        int_type = Type(name='int')
        arity_3_op = Operator(
            symbol=Symbol(name='arity_3', dtype=int_type),
            signature=(int_type, int_type, int_type)
        )

        arity_2a_op = Operator(
            symbol=Symbol(name='arity_2a', dtype=int_type),
            signature=(int_type, int_type)
        )

        arity_2b_op = Operator(
            symbol=Symbol(name='arity_2b', dtype=int_type),
            signature=(int_type, int_type)
        )

        arity_2c_op = Operator(
            symbol=Symbol(name='arity_2c', dtype=int_type),
            signature=(int_type, int_type)
        )

        arity_2d_op = Operator(
            symbol=Symbol(name='arity_2d', dtype=int_type),
            signature=(int_type, int_type)
        )

        arity_2e_op = Operator(
            symbol=Symbol(name='arity_2e', dtype=int_type),
            signature=(int_type, int_type)
        )

        terminal_a_op = Operator(symbol=Symbol(name='term_a', dtype=int_type))
        terminal_b_op = Operator(symbol=Symbol(name='term_b', dtype=int_type))
        terminal_c_op = Operator(symbol=Symbol(name='term_c', dtype=int_type))
        terminal_d_op = Operator(symbol=Symbol(name='term_d', dtype=int_type))
        terminal_e_op = Operator(symbol=Symbol(name='term_e', dtype=int_type))
        terminal_f_op = Operator(symbol=Symbol(name='term_f', dtype=int_type))
        terminal_g_op = Operator(symbol=Symbol(name='term_g', dtype=int_type))
        terminal_h_op = Operator(symbol=Symbol(name='term_h', dtype=int_type))

        node_3 = Node(operator=terminal_a_op)
        node_5 = Node(operator=terminal_b_op)
        node_6 = Node(operator=terminal_c_op)
        node_4 = Node(operator=arity_2b_op)
        node_2 = Node(operator=arity_2a_op)
        node_7 = Node(operator=terminal_g_op)
        node_9 = Node(operator=terminal_h_op)
        node_12 = Node(operator=terminal_d_op)
        node_13 = Node(operator=terminal_e_op)
        node_11 = Node(operator=arity_2e_op)
        node_14 = Node(operator=terminal_f_op)
        node_10 = Node(operator=arity_2d_op)
        node_8 = Node(operator=arity_2c_op)
        node_1 = Node(operator=arity_3_op)

        node_1.add_child(child=node_2, position=0)
        node_1.add_child(child=node_7, position=1)
        node_1.add_child(child=node_8, position=2)
        node_2.add_child(child=node_3, position=0)
        node_2.add_child(child=node_4, position=1)
        node_4.add_child(child=node_5, position=0)
        node_4.add_child(child=node_6, position=1)
        node_8.add_child(child=node_9, position=0)
        node_8.add_child(child=node_10, position=1)
        node_10.add_child(child=node_11, position=0)
        node_10.add_child(child=node_14, position=1)
        node_11.add_child(child=node_12, position=0)
        node_11.add_child(child=node_13, position=1)

        tree = Tree(root=node_1)
        pre_order_iter = tree.pre_order_iter()

        iter_0 = pre_order_iter.next()
        iter_1 = pre_order_iter.next()
        iter_2 = pre_order_iter.next()
        iter_3 = pre_order_iter.next()
        iter_4 = pre_order_iter.next()
        iter_5 = pre_order_iter.next()
        iter_6 = pre_order_iter.next()
        iter_7 = pre_order_iter.next()
        iter_8 = pre_order_iter.next()
        iter_9 = pre_order_iter.next()
        iter_10 = pre_order_iter.next()
        iter_11 = pre_order_iter.next()
        iter_12 = pre_order_iter.next()
        iter_13 = pre_order_iter.next()

        self.assertRaises(StopIteration, pre_order_iter.next)

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

    def test_multi_arity_tree_bfs_iter_1(self):
        """Test that a nontrivial tree composed of operators having arbitrary
        arity behaves as expected upon iteration. The tree looks like this:

                              node_1
                            /   |   \
                     node_2  node_3  node_4
                    /   \            /    \
              node_5   node_6    node_7  node_8
                      /    \             /     \
                node_9    node_10   node_11   node_12
                                     /   \
                                node_13  node_14

        The expected iteration is breadth-first, the nodes in the diagram are
        numbered accordingly.

        """
        int_type = Type(name='int')
        arity_3_op = Operator(
            symbol=Symbol(name='arity_3', dtype=int_type),
            signature=(int_type, int_type, int_type)
        )

        arity_2a_op = Operator(
            symbol=Symbol(name='arity_2a', dtype=int_type),
            signature=(int_type, int_type)
        )

        arity_2b_op = Operator(
            symbol=Symbol(name='arity_2b', dtype=int_type),
            signature=(int_type, int_type)
        )

        arity_2c_op = Operator(
            symbol=Symbol(name='arity_2c', dtype=int_type),
            signature=(int_type, int_type)
        )

        arity_2d_op = Operator(
            symbol=Symbol(name='arity_2d', dtype=int_type),
            signature=(int_type, int_type)
        )

        arity_2e_op = Operator(
            symbol=Symbol(name='arity_2e', dtype=int_type),
            signature=(int_type, int_type)
        )

        terminal_a_op = Operator(symbol=Symbol(name='term_a', dtype=int_type))
        terminal_b_op = Operator(symbol=Symbol(name='term_b', dtype=int_type))
        terminal_c_op = Operator(symbol=Symbol(name='term_c', dtype=int_type))
        terminal_d_op = Operator(symbol=Symbol(name='term_d', dtype=int_type))
        terminal_e_op = Operator(symbol=Symbol(name='term_e', dtype=int_type))
        terminal_f_op = Operator(symbol=Symbol(name='term_f', dtype=int_type))
        terminal_g_op = Operator(symbol=Symbol(name='term_g', dtype=int_type))
        terminal_h_op = Operator(symbol=Symbol(name='term_h', dtype=int_type))

        node_5 = Node(operator=terminal_a_op)
        node_9 = Node(operator=terminal_b_op)
        node_10 = Node(operator=terminal_c_op)
        node_6 = Node(operator=arity_2b_op)
        node_2 = Node(operator=arity_2a_op)
        node_3 = Node(operator=terminal_g_op)
        node_7 = Node(operator=terminal_h_op)
        node_13 = Node(operator=terminal_d_op)
        node_14 = Node(operator=terminal_e_op)
        node_11 = Node(operator=arity_2e_op)
        node_12 = Node(operator=terminal_f_op)
        node_8 = Node(operator=arity_2d_op)
        node_4 = Node(operator=arity_2c_op)
        node_1 = Node(operator=arity_3_op)

        node_1.add_child(child=node_2, position=0)
        node_1.add_child(child=node_3, position=1)
        node_1.add_child(child=node_4, position=2)
        node_2.add_child(child=node_5, position=0)
        node_2.add_child(child=node_6, position=1)
        node_4.add_child(child=node_7, position=0)
        node_4.add_child(child=node_8, position=1)
        node_6.add_child(child=node_9, position=0)
        node_6.add_child(child=node_10, position=1)
        node_8.add_child(child=node_11, position=0)
        node_8.add_child(child=node_12, position=1)
        node_11.add_child(child=node_13, position=0)
        node_11.add_child(child=node_14, position=1)

        tree = Tree(root=node_1)
        bfs_iter = tree.bfs_iter()

        iter_0 = bfs_iter.next()
        iter_1 = bfs_iter.next()
        iter_2 = bfs_iter.next()
        iter_3 = bfs_iter.next()
        iter_4 = bfs_iter.next()
        iter_5 = bfs_iter.next()
        iter_6 = bfs_iter.next()
        iter_7 = bfs_iter.next()
        iter_8 = bfs_iter.next()
        iter_9 = bfs_iter.next()
        iter_10 = bfs_iter.next()
        iter_11 = bfs_iter.next()
        iter_12 = bfs_iter.next()
        iter_13 = bfs_iter.next()

        self.assertRaises(StopIteration, bfs_iter.next)

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

    def test_multi_arity_tree_post_order_iter_2(self):
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
        int_type = Type(name='int')
        arity_3_op = Operator(
            symbol=Symbol(name='arity_3', dtype=int_type),
            signature=(int_type, int_type, int_type)
        )

        arity_2a_op = Operator(
            symbol=Symbol(name='arity_2a', dtype=int_type),
            signature=(int_type, int_type)
        )

        arity_2b_op = Operator(
            symbol=Symbol(name='arity_2b', dtype=int_type),
            signature=(int_type, int_type)
        )

        arity_2c_op = Operator(
            symbol=Symbol(name='arity_2c', dtype=int_type),
            signature=(int_type, int_type)
        )

        terminal_a_op = Operator(symbol=Symbol(name='term_a', dtype=int_type))
        terminal_b_op = Operator(symbol=Symbol(name='term_b', dtype=int_type))
        terminal_c_op = Operator(symbol=Symbol(name='term_c', dtype=int_type))
        terminal_d_op = Operator(symbol=Symbol(name='term_d', dtype=int_type))
        terminal_e_op = Operator(symbol=Symbol(name='term_e', dtype=int_type))
        terminal_f_op = Operator(symbol=Symbol(name='term_f', dtype=int_type))

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

    def test_multi_arity_tree_pre_order_iter_2(self):
        """Test iteration over a different multi-arity tree. The tree looks
        like this:

                              node_1
                            /   |    \
                     node_2  node_5    node_8
                   /    \     /   \      |    \
            node_3 node_4 node_6 node_7 node_9 node_10

        The expected iteration is pre-order depth-first, the nodes in the
        diagram are numbered accordingly.

        """
        int_type = Type(name='int')
        arity_3_op = Operator(
            symbol=Symbol(name='arity_3', dtype=int_type),
            signature=(int_type, int_type, int_type)
        )

        arity_2a_op = Operator(
            symbol=Symbol(name='arity_2a', dtype=int_type),
            signature=(int_type, int_type)
        )

        arity_2b_op = Operator(
            symbol=Symbol(name='arity_2b', dtype=int_type),
            signature=(int_type, int_type)
        )

        arity_2c_op = Operator(
            symbol=Symbol(name='arity_2c', dtype=int_type),
            signature=(int_type, int_type)
        )

        terminal_a_op = Operator(symbol=Symbol(name='term_a', dtype=int_type))
        terminal_b_op = Operator(symbol=Symbol(name='term_b', dtype=int_type))
        terminal_c_op = Operator(symbol=Symbol(name='term_c', dtype=int_type))
        terminal_d_op = Operator(symbol=Symbol(name='term_d', dtype=int_type))
        terminal_e_op = Operator(symbol=Symbol(name='term_e', dtype=int_type))
        terminal_f_op = Operator(symbol=Symbol(name='term_f', dtype=int_type))

        node_3 = Node(operator=terminal_a_op)
        node_4 = Node(operator=terminal_b_op)
        node_2 = Node(operator=arity_2a_op)
        node_6 = Node(operator=terminal_c_op)
        node_7 = Node(operator=terminal_d_op)
        node_5 = Node(operator=arity_2b_op)
        node_9 = Node(operator=terminal_e_op)
        node_10 = Node(operator=terminal_f_op)
        node_8 = Node(operator=arity_2c_op)
        node_1 = Node(operator=arity_3_op)

        node_1.add_child(child=node_2, position=0)
        node_1.add_child(child=node_5, position=1)
        node_1.add_child(child=node_8, position=2)
        node_2.add_child(child=node_3, position=0)
        node_2.add_child(child=node_4, position=1)
        node_5.add_child(child=node_6, position=0)
        node_5.add_child(child=node_7, position=1)
        node_8.add_child(child=node_9, position=0)
        node_8.add_child(child=node_10, position=1)

        tree = Tree(root=node_1)
        pre_order_iter = tree.pre_order_iter()

        iter_0 = pre_order_iter.next()
        iter_1 = pre_order_iter.next()
        iter_2 = pre_order_iter.next()
        iter_3 = pre_order_iter.next()
        iter_4 = pre_order_iter.next()
        iter_5 = pre_order_iter.next()
        iter_6 = pre_order_iter.next()
        iter_7 = pre_order_iter.next()
        iter_8 = pre_order_iter.next()
        iter_9 = pre_order_iter.next()

        self.assertRaises(StopIteration, pre_order_iter.next)

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

    def test_multi_arity_tree_bfs_iter_2(self):
        """Test iteration over a different multi-arity tree. The tree looks
        like this:

                               node_1
                            /   |     \
                     node_2  node_3    node_4
                   /    \     /   \      |    \
            node_5 node_6 node_7 node_8 node_9 node_10

        The expected iteration is breadth-first, the nodes in the diagram are
        numbered accordingly.

        """
        int_type = Type(name='int')
        arity_3_op = Operator(
            symbol=Symbol(name='arity_3', dtype=int_type),
            signature=(int_type, int_type, int_type)
        )

        arity_2a_op = Operator(
            symbol=Symbol(name='arity_2a', dtype=int_type),
            signature=(int_type, int_type)
        )

        arity_2b_op = Operator(
            symbol=Symbol(name='arity_2b', dtype=int_type),
            signature=(int_type, int_type)
        )

        arity_2c_op = Operator(
            symbol=Symbol(name='arity_2c', dtype=int_type),
            signature=(int_type, int_type)
        )

        terminal_a_op = Operator(symbol=Symbol(name='term_a', dtype=int_type))
        terminal_b_op = Operator(symbol=Symbol(name='term_b', dtype=int_type))
        terminal_c_op = Operator(symbol=Symbol(name='term_c', dtype=int_type))
        terminal_d_op = Operator(symbol=Symbol(name='term_d', dtype=int_type))
        terminal_e_op = Operator(symbol=Symbol(name='term_e', dtype=int_type))
        terminal_f_op = Operator(symbol=Symbol(name='term_f', dtype=int_type))

        node_5 = Node(operator=terminal_a_op)
        node_6 = Node(operator=terminal_b_op)
        node_2 = Node(operator=arity_2a_op)
        node_7 = Node(operator=terminal_c_op)
        node_8 = Node(operator=terminal_d_op)
        node_3 = Node(operator=arity_2b_op)
        node_9 = Node(operator=terminal_e_op)
        node_10 = Node(operator=terminal_f_op)
        node_4 = Node(operator=arity_2c_op)
        node_1 = Node(operator=arity_3_op)

        node_1.add_child(child=node_2, position=0)
        node_1.add_child(child=node_3, position=1)
        node_1.add_child(child=node_4, position=2)
        node_2.add_child(child=node_5, position=0)
        node_2.add_child(child=node_6, position=1)
        node_3.add_child(child=node_7, position=0)
        node_3.add_child(child=node_8, position=1)
        node_4.add_child(child=node_9, position=0)
        node_4.add_child(child=node_10, position=1)

        tree = Tree(root=node_1)
        bfs_iter = tree.bfs_iter()

        iter_0 = bfs_iter.next()
        iter_1 = bfs_iter.next()
        iter_2 = bfs_iter.next()
        iter_3 = bfs_iter.next()
        iter_4 = bfs_iter.next()
        iter_5 = bfs_iter.next()
        iter_6 = bfs_iter.next()
        iter_7 = bfs_iter.next()
        iter_8 = bfs_iter.next()
        iter_9 = bfs_iter.next()

        self.assertRaises(StopIteration, bfs_iter.next)

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

    def test_multi_arity_tree_post_order_iter_3(self):
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
        int_type = Type(name='int')
        arity_3_op = Operator(
            symbol=Symbol(name='arity_3', dtype=int_type),
            signature=(int_type, int_type, int_type)
        )

        arity_2_op = Operator(
            symbol=Symbol(name='arity_2', dtype=int_type),
            signature=(int_type, int_type)
        )

        terminal_a_op = Operator(symbol=Symbol(name='term_a', dtype=int_type))
        terminal_b_op = Operator(symbol=Symbol(name='term_b', dtype=int_type))
        terminal_c_op = Operator(symbol=Symbol(name='term_c', dtype=int_type))
        terminal_d_op = Operator(symbol=Symbol(name='term_d', dtype=int_type))

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

    def test_multi_arity_tree_pr_order_iter_3(self):
        """Test a iteration over a different multi-arity tree. The tree looks
        like this:

                             node_1
                            /      \
                        node_2    node_6
                      /   |   \
                node_3 node_4 node_5

        The expected iteration is pre-order depth-first, the nodes in the
        diagram are numbered accordingly.

        """
        int_type = Type(name='int')
        arity_3_op = Operator(
            symbol=Symbol(name='arity_3', dtype=int_type),
            signature=(int_type, int_type, int_type)
        )

        arity_2_op = Operator(
            symbol=Symbol(name='arity_2', dtype=int_type),
            signature=(int_type, int_type)
        )

        terminal_a_op = Operator(symbol=Symbol(name='term_a', dtype=int_type))
        terminal_b_op = Operator(symbol=Symbol(name='term_b', dtype=int_type))
        terminal_c_op = Operator(symbol=Symbol(name='term_c', dtype=int_type))
        terminal_d_op = Operator(symbol=Symbol(name='term_d', dtype=int_type))

        node_3 = Node(operator=terminal_a_op)
        node_4 = Node(operator=terminal_b_op)
        node_5 = Node(operator=terminal_c_op)
        node_2 = Node(operator=arity_3_op)
        node_6 = Node(operator=terminal_d_op)
        node_1 = Node(operator=arity_2_op)

        node_1.add_child(child=node_2, position=0)
        node_1.add_child(child=node_6, position=1)
        node_2.add_child(child=node_3, position=0)
        node_2.add_child(child=node_4, position=1)
        node_2.add_child(child=node_5, position=2)

        tree = Tree(root=node_1)
        pre_order_iter = tree.pre_order_iter()

        iter_0 = pre_order_iter.next()
        iter_1 = pre_order_iter.next()
        iter_2 = pre_order_iter.next()
        iter_3 = pre_order_iter.next()
        iter_4 = pre_order_iter.next()
        iter_5 = pre_order_iter.next()

        self.assertRaises(StopIteration, pre_order_iter.next)

        self.assertIs(iter_0, node_1)
        self.assertIs(iter_1, node_2)
        self.assertIs(iter_2, node_3)
        self.assertIs(iter_3, node_4)
        self.assertIs(iter_4, node_5)
        self.assertIs(iter_5, node_6)

    def test_multi_arity_tree_bfs_iter_3(self):
        """Test a iteration over a different multi-arity tree. The tree looks
        like this:

                             node_1
                            /      \
                        node_2    node_3
                      /   |   \
                node_4 node_5 node_6

        The expected iteration is breadth-first, the nodes in the diagram are
        numbered accordingly.

        """
        int_type = Type(name='int')
        arity_3_op = Operator(
            symbol=Symbol(name='arity_3', dtype=int_type),
            signature=(int_type, int_type, int_type)
        )

        arity_2_op = Operator(
            symbol=Symbol(name='arity_2', dtype=int_type),
            signature=(int_type, int_type)
        )

        terminal_a_op = Operator(symbol=Symbol(name='term_a', dtype=int_type))
        terminal_b_op = Operator(symbol=Symbol(name='term_b', dtype=int_type))
        terminal_c_op = Operator(symbol=Symbol(name='term_c', dtype=int_type))
        terminal_d_op = Operator(symbol=Symbol(name='term_d', dtype=int_type))

        node_4 = Node(operator=terminal_a_op)
        node_5 = Node(operator=terminal_b_op)
        node_6 = Node(operator=terminal_c_op)
        node_2 = Node(operator=arity_3_op)
        node_3 = Node(operator=terminal_d_op)
        node_1 = Node(operator=arity_2_op)

        node_1.add_child(child=node_2, position=0)
        node_1.add_child(child=node_3, position=1)
        node_2.add_child(child=node_4, position=0)
        node_2.add_child(child=node_5, position=1)
        node_2.add_child(child=node_6, position=2)

        tree = Tree(root=node_1)
        bfs_iter = tree.bfs_iter()

        iter_0 = bfs_iter.next()
        iter_1 = bfs_iter.next()
        iter_2 = bfs_iter.next()
        iter_3 = bfs_iter.next()
        iter_4 = bfs_iter.next()
        iter_5 = bfs_iter.next()

        self.assertRaises(StopIteration, bfs_iter.next)

        self.assertIs(iter_0, node_1)
        self.assertIs(iter_1, node_2)
        self.assertIs(iter_2, node_3)
        self.assertIs(iter_3, node_4)
        self.assertIs(iter_4, node_5)
        self.assertIs(iter_5, node_6)

    def test_tree_get_dimensions(self):
        """Test that *get_dimensions* behaves as expected for the following
        tree:

                             node_1
                            /      \
                        node_2    node_3
                      /   |   \
                node_4 node_5 node_6

        The expected dimensions tuple is (1, 2, 3)

        """
        int_type = Type(name='int')
        arity_3_op = Operator(
            symbol=Symbol(name='arity_3', dtype=int_type),
            signature=(int_type, int_type, int_type)
        )

        arity_2_op = Operator(
            symbol=Symbol(name='arity_2', dtype=int_type),
            signature=(int_type, int_type)
        )

        terminal_a_op = Operator(symbol=Symbol(name='term_a', dtype=int_type))
        terminal_b_op = Operator(symbol=Symbol(name='term_b', dtype=int_type))
        terminal_c_op = Operator(symbol=Symbol(name='term_c', dtype=int_type))
        terminal_d_op = Operator(symbol=Symbol(name='term_d', dtype=int_type))

        node_4 = Node(operator=terminal_a_op)
        node_5 = Node(operator=terminal_b_op)
        node_6 = Node(operator=terminal_c_op)
        node_2 = Node(operator=arity_3_op)
        node_3 = Node(operator=terminal_d_op)
        node_1 = Node(operator=arity_2_op)

        node_1.add_child(child=node_2, position=0)
        node_1.add_child(child=node_3, position=1)
        node_2.add_child(child=node_4, position=0)
        node_2.add_child(child=node_5, position=1)
        node_2.add_child(child=node_6, position=2)

        tree = Tree(root=node_1)
        self.assertEqual((1, 2, 3), tree.get_dimensions())

    def test_tree_len(self):
        """Test that __len__ behaves as expected for the following tree:

                             node_1
                            /      \
                        node_2    node_3
                      /   |   \
                node_4 node_5 node_6

        The expected length is 6

        """
        int_type = Type(name='int')
        arity_3_op = Operator(
            symbol=Symbol(name='arity_3', dtype=int_type),
            signature=(int_type, int_type, int_type)
        )

        arity_2_op = Operator(
            symbol=Symbol(name='arity_2', dtype=int_type),
            signature=(int_type, int_type)
        )

        terminal_a_op = Operator(symbol=Symbol(name='term_a', dtype=int_type))
        terminal_b_op = Operator(symbol=Symbol(name='term_b', dtype=int_type))
        terminal_c_op = Operator(symbol=Symbol(name='term_c', dtype=int_type))
        terminal_d_op = Operator(symbol=Symbol(name='term_d', dtype=int_type))

        node_4 = Node(operator=terminal_a_op)
        node_5 = Node(operator=terminal_b_op)
        node_6 = Node(operator=terminal_c_op)
        node_2 = Node(operator=arity_3_op)
        node_3 = Node(operator=terminal_d_op)
        node_1 = Node(operator=arity_2_op)

        node_1.add_child(child=node_2, position=0)
        node_1.add_child(child=node_3, position=1)
        node_2.add_child(child=node_4, position=0)
        node_2.add_child(child=node_5, position=1)
        node_2.add_child(child=node_6, position=2)

        tree = Tree(root=node_1)
        self.assertEqual(6, len(tree))

    def test_tree_pickle(self):
        """Test that a Tree instance can be pickled and unpickled using the
        default protocol.

        """
        some_type = Type(name='SomeType')
        signature = (some_type, some_type)
        dtype = some_type

        basis_op_0 = Operator(
            symbol=Symbol('func_0', dtype=dtype), signature=signature
        )
        basis_op_1 = Operator(
            symbol=Symbol('func_1', dtype=dtype), signature=signature
        )
        terminal_op_0 = Operator(symbol=Symbol(name='term_0', dtype=dtype))
        terminal_op_1 = Operator(symbol=Symbol(name='term_1', dtype=dtype))
        terminal_op_2 = Operator(symbol=Symbol(name='term_2', dtype=dtype))

        root = Node(operator=basis_op_0)
        basis_node = Node(operator=basis_op_1)
        terminal_node_0 = Node(operator=terminal_op_0)
        terminal_node_1 = Node(operator=terminal_op_1)
        terminal_node_2 = Node(operator=terminal_op_2)

        root.add_child(child=terminal_node_0, position=0)
        root.add_child(child=basis_node, position=1)

        basis_node.add_child(child=terminal_node_1, position=0)
        basis_node.add_child(child=terminal_node_2, position=1)

        tree = Tree(root=root)

        bfs_nodes = tuple(n for n in tree.bfs_iter())

        pickled_tree = pickle.dumps(tree)
        unpickled_tree = pickle.loads(pickled_tree)

        unpickled_bfs_nodes = tuple(n for n in unpickled_tree.bfs_iter())

        self.assertEqual(tree, unpickled_tree)
        self.assertTupleEqual(bfs_nodes, unpickled_bfs_nodes)

    def test_calls_iter(self):
        """Test that a calls_iter formed over the following tree emits the
        correct Call objects in the correct order:

                             node_6
                            /      \
                        node_4    node_5
                      /   |   \
                node_1 node_2 node_3

        The calls should proceed as follows:

        node_4(symbol_1, symbol_2, symbol_3) --> call_1
        node_6(call_1, symbol_4) --> call_2

        """
        int_type = Type(name='int')
        float_type = Type(name='float')
        str_type = Type(name='str')

        node_4_op = Operator(
            symbol=Symbol(name='node_4_func', dtype=int_type),
            signature=(int_type, float_type, str_type)
        )

        root_op = Operator(
            symbol=Symbol(name='root_func', dtype=int_type),
            signature=(int_type, int_type)
        )

        terminal_a_op = Operator(symbol=Symbol(name='term_a', dtype=int_type))
        terminal_b_op = Operator(
            symbol=Symbol(name='term_b', dtype=float_type)
        )
        terminal_c_op = Operator(symbol=Symbol(name='term_c', dtype=str_type))
        terminal_d_op = Operator(symbol=Symbol(name='term_d', dtype=int_type))

        node_1 = Node(operator=terminal_a_op)
        node_2 = Node(operator=terminal_b_op)
        node_3 = Node(operator=terminal_c_op)
        node_4 = Node(operator=node_4_op)
        node_5 = Node(operator=terminal_d_op)
        node_6 = Node(operator=root_op)

        node_6.add_child(child=node_4, position=0)
        node_6.add_child(child=node_5, position=1)
        node_4.add_child(child=node_1, position=0)
        node_4.add_child(child=node_2, position=1)
        node_4.add_child(child=node_3, position=2)

        tree = Tree(root=node_6)

        calls = list(calls_iter(tree=tree, result_formatter='result_{0}'))

        symbol_1 = node_1.operator.symbol
        symbol_2 = node_2.operator.symbol
        symbol_3 = node_3.operator.symbol
        call_1 = node_4.operator(
            target=Symbol(name='result_0', dtype=int_type),
            args=(symbol_1, symbol_2, symbol_3)
        )
        symbol_4 = node_5.operator.symbol
        call_2 = node_6.operator(
            target=Symbol(name='result_1', dtype=int_type), args=(
                call_1.target, symbol_4
            )
        )
        self.maxDiff = None
        self.assertListEqual([call_1, call_2], calls)

    def test_symbols_iter(self):
        """Test that a symbols_iter formed over the following tree emits the
        correct Symbol objects in the correct order:

                             node_6
                            /      \
                        node_4    node_5
                      /   |   \
                node_1 node_2 node_3

        The symbols should be emitted in the following order:

        symbol_1
        symbol_2
        symbol_3
        symbol_5

        """
        int_type = Type(name='int')
        float_type = Type(name='float')
        str_type = Type(name='str')

        node_4_op = Operator(
            symbol=Symbol(name='node_4_func', dtype=int_type),
            signature=(int_type, float_type, str_type)
        )

        root_op = Operator(
            symbol=Symbol(name='root_func', dtype=int_type),
            signature=(int_type, int_type)
        )

        terminal_a_op = Operator(symbol=Symbol(name='term_a', dtype=int_type))
        terminal_b_op = Operator(
            symbol=Symbol(name='term_b', dtype=float_type)
        )
        terminal_c_op = Operator(symbol=Symbol(name='term_c', dtype=str_type))
        terminal_d_op = Operator(symbol=Symbol(name='term_d', dtype=int_type))

        node_1 = Node(operator=terminal_a_op)
        node_2 = Node(operator=terminal_b_op)
        node_3 = Node(operator=terminal_c_op)
        node_4 = Node(operator=node_4_op)
        node_5 = Node(operator=terminal_d_op)
        node_6 = Node(operator=root_op)

        node_6.add_child(child=node_4, position=0)
        node_6.add_child(child=node_5, position=1)
        node_4.add_child(child=node_1, position=0)
        node_4.add_child(child=node_2, position=1)
        node_4.add_child(child=node_3, position=2)

        tree = Tree(root=node_6)

        symbol_1 = terminal_a_op()
        symbol_2 = terminal_b_op()
        symbol_3 = terminal_c_op()
        symbol_5 = terminal_d_op()

        symbols = list(symbols_iter(tree=tree))

        self.assertListEqual([symbol_1, symbol_2, symbol_3, symbol_5], symbols)
