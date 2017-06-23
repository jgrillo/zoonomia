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

import unittest
import pickle

from zoonomia.tree import Node, Tree, iter_calls, iter_symbols
from zoonomia.lang import Symbol, Operator
from zoonomia.types import Type, TypeCheckError


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
        """Test that the add_child method raises TypeCheckError if the child's
        dtype does not match the node's operator's signature at the given
        position.

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
            TypeCheckError,
            basis_node.add_child,
            child=terminal_node,
            position=0
        )

    def test_add_child_raises_signature_missing_index(self):
        """Test that the add_child method raises TypeCheckError if the child's
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
            TypeCheckError,
            basis_node.add_child,
            child=terminal_node,
            position=1
        )

    def test_add_child_raises_when_child_already_present(self):
        """Test that add_child raises ValueError if a child is already present
        at the given position.

        """
        some_type = Type(name='SomeType')
        signature = (some_type,)
        dtype = some_type
        basis_symbol = Symbol(name='func', dtype=dtype)

        basis_op = Operator(symbol=basis_symbol, signature=signature)
        terminal_op = Operator(symbol=basis_symbol)

        basis_node = Node(operator=basis_op)
        terminal_node = Node(operator=terminal_op)

        self.assertIsNone(terminal_node.parent)
        self.assertIsNone(basis_node.left)

        basis_node.add_child(child=terminal_node, position=0)

        self.assertEqual(basis_node.left, terminal_node)
        self.assertIs(basis_node, terminal_node.parent)

        self.assertRaises(
            ValueError, basis_node.add_child, child=terminal_node, position=0
        )

    def test_add_remove_child(self):
        """Test that a Node's state changes appropriately when a child is added
        and removed.

        """
        some_type = Type(name='SomeType')
        signature = (some_type,)
        dtype = some_type
        basis_symbol = Symbol(name='func', dtype=dtype)

        basis_op = Operator(symbol=basis_symbol, signature=signature)
        terminal_op = Operator(symbol=basis_symbol)

        basis_node = Node(operator=basis_op)
        terminal_node = Node(operator=terminal_op)

        self.assertIsNone(terminal_node.parent)
        self.assertIsNone(basis_node.left)

        basis_node.add_child(child=terminal_node, position=0)

        self.assertEqual(basis_node.left, terminal_node)
        self.assertIs(basis_node, terminal_node.parent)

        basis_node.remove_child(position=0)

        self.assertIsNone(basis_node.left)
        self.assertIsNone(terminal_node.parent)

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
        0 protocol and -1 protocol.

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

        pickled_root = pickle.dumps(root, -1)
        unpickled_root = pickle.loads(pickled_root)

        self.assertEqual(root, unpickled_root)

        pickled_root = pickle.dumps(root, 0)
        unpickled_root = pickle.loads(pickled_root)

        self.assertEqual(root, unpickled_root)

    def test_node_graph_node_name(self):
        """Test that graph_node() returns a GraphNode object with the expected
        name.

        """
        some_type = Type(name='SomeType')
        signature = (some_type,)
        dtype = some_type
        symbol = Symbol(name='some_symbol', dtype=dtype)

        basis_op = Operator(symbol=symbol, signature=signature)
        terminal_op = Operator(symbol=symbol)

        basis_node = Node(operator=basis_op)
        terminal_node = Node(operator=terminal_op)

        self.assertEqual(
            '"some_symbol(SomeType) -> SomeType"',
            basis_node.graph_node().get_name()
        )

        self.assertEqual(
            '"some_symbol() -> SomeType"',
            terminal_node.graph_node().get_name()
        )


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

    def test_zero_depth_tree_post_order_iter(self):
        """Test that a tree consisting of just one Node behaves as expected
        upon post-order traversal.

        """
        int_type = Type(name='int')
        x = Operator(symbol=Symbol(name='term', dtype=int_type))

        node_1 = Node(operator=x)

        tree = Tree(root=node_1)
        tree_iter = iter(tree)

        iter_0 = next(tree_iter)

        self.assertRaises(StopIteration, next, tree_iter)

        self.assertIs(iter_0, node_1)

    def test_zero_depth_tree_pre_order_iter(self):
        """Test that a tree consisting of just one Node behaves as expected
        upon pre-order traversal.

        """
        int_type = Type(name='int')
        x = Operator(symbol=Symbol(name='term', dtype=int_type))

        node_1 = Node(operator=x)

        tree = Tree(root=node_1)
        pre_order_iter = tree.iter_pre_order()

        iter_0 = next(pre_order_iter)

        self.assertRaises(StopIteration, next, pre_order_iter)

        self.assertIs(iter_0, node_1)

    def test_zero_depth_tree_bfs_iter(self):
        """Test that a tree consisting of just one Node behaves as expected
        upon breadth-first traversal.

        """
        int_type = Type(name='int')
        x = Operator(symbol=Symbol(name='term', dtype=int_type))

        node_1 = Node(operator=x)

        tree = Tree(root=node_1)
        bfs_iter = tree.iter_bfs()

        iter_0 = next(bfs_iter)

        self.assertRaises(StopIteration, next, bfs_iter)

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

        iter_0 = next(tree_iter)
        iter_1 = next(tree_iter)
        iter_2 = next(tree_iter)

        self.assertRaises(StopIteration, next, tree_iter)

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
        pre_order_iter = tree.iter_pre_order()

        iter_0 = next(pre_order_iter)
        iter_1 = next(pre_order_iter)
        iter_2 = next(pre_order_iter)

        self.assertRaises(StopIteration, next, pre_order_iter)

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
        bfs_iter = tree.iter_bfs()

        iter_0 = next(bfs_iter)
        iter_1 = next(bfs_iter)
        iter_2 = next(bfs_iter)

        self.assertRaises(StopIteration, next, bfs_iter)

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

        iter_0 = next(tree_iter)
        iter_1 = next(tree_iter)
        iter_2 = next(tree_iter)
        iter_3 = next(tree_iter)
        iter_4 = next(tree_iter)
        iter_5 = next(tree_iter)
        iter_6 = next(tree_iter)
        iter_7 = next(tree_iter)
        iter_8 = next(tree_iter)
        iter_9 = next(tree_iter)
        iter_10 = next(tree_iter)

        self.assertRaises(StopIteration, next, tree_iter)

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
        pre_order_iter = tree.iter_pre_order()

        iter_0 = next(pre_order_iter)
        iter_1 = next(pre_order_iter)
        iter_2 = next(pre_order_iter)
        iter_3 = next(pre_order_iter)
        iter_4 = next(pre_order_iter)
        iter_5 = next(pre_order_iter)
        iter_6 = next(pre_order_iter)
        iter_7 = next(pre_order_iter)
        iter_8 = next(pre_order_iter)
        iter_9 = next(pre_order_iter)
        iter_10 = next(pre_order_iter)

        self.assertRaises(StopIteration, next, pre_order_iter)

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
        bfs_iter = tree.iter_bfs()

        iter_0 = next(bfs_iter)
        iter_1 = next(bfs_iter)
        iter_2 = next(bfs_iter)
        iter_3 = next(bfs_iter)
        iter_4 = next(bfs_iter)
        iter_5 = next(bfs_iter)
        iter_6 = next(bfs_iter)
        iter_7 = next(bfs_iter)
        iter_8 = next(bfs_iter)
        iter_9 = next(bfs_iter)
        iter_10 = next(bfs_iter)

        self.assertRaises(StopIteration, next, bfs_iter)

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

        iter_0 = next(tree_iter)
        iter_1 = next(tree_iter)
        iter_2 = next(tree_iter)
        iter_3 = next(tree_iter)
        iter_4 = next(tree_iter)
        iter_5 = next(tree_iter)
        iter_6 = next(tree_iter)
        iter_7 = next(tree_iter)
        iter_8 = next(tree_iter)
        iter_9 = next(tree_iter)
        iter_10 = next(tree_iter)
        iter_11 = next(tree_iter)
        iter_12 = next(tree_iter)
        iter_13 = next(tree_iter)

        self.assertRaises(StopIteration, next, tree_iter)

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
        pre_order_iter = tree.iter_pre_order()

        iter_0 = next(pre_order_iter)
        iter_1 = next(pre_order_iter)
        iter_2 = next(pre_order_iter)
        iter_3 = next(pre_order_iter)
        iter_4 = next(pre_order_iter)
        iter_5 = next(pre_order_iter)
        iter_6 = next(pre_order_iter)
        iter_7 = next(pre_order_iter)
        iter_8 = next(pre_order_iter)
        iter_9 = next(pre_order_iter)
        iter_10 = next(pre_order_iter)
        iter_11 = next(pre_order_iter)
        iter_12 = next(pre_order_iter)
        iter_13 = next(pre_order_iter)

        self.assertRaises(StopIteration, next, pre_order_iter)

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
        bfs_iter = tree.iter_bfs()

        iter_0 = next(bfs_iter)
        iter_1 = next(bfs_iter)
        iter_2 = next(bfs_iter)
        iter_3 = next(bfs_iter)
        iter_4 = next(bfs_iter)
        iter_5 = next(bfs_iter)
        iter_6 = next(bfs_iter)
        iter_7 = next(bfs_iter)
        iter_8 = next(bfs_iter)
        iter_9 = next(bfs_iter)
        iter_10 = next(bfs_iter)
        iter_11 = next(bfs_iter)
        iter_12 = next(bfs_iter)
        iter_13 = next(bfs_iter)

        self.assertRaises(StopIteration, next, bfs_iter)

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

        iter_0 = next(tree_iter)
        iter_1 = next(tree_iter)
        iter_2 = next(tree_iter)
        iter_3 = next(tree_iter)
        iter_4 = next(tree_iter)
        iter_5 = next(tree_iter)
        iter_6 = next(tree_iter)
        iter_7 = next(tree_iter)
        iter_8 = next(tree_iter)
        iter_9 = next(tree_iter)

        self.assertRaises(StopIteration, next, tree_iter)

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
        pre_order_iter = tree.iter_pre_order()

        iter_0 = next(pre_order_iter)
        iter_1 = next(pre_order_iter)
        iter_2 = next(pre_order_iter)
        iter_3 = next(pre_order_iter)
        iter_4 = next(pre_order_iter)
        iter_5 = next(pre_order_iter)
        iter_6 = next(pre_order_iter)
        iter_7 = next(pre_order_iter)
        iter_8 = next(pre_order_iter)
        iter_9 = next(pre_order_iter)

        self.assertRaises(StopIteration, next, pre_order_iter)

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
        bfs_iter = tree.iter_bfs()

        iter_0 = next(bfs_iter)
        iter_1 = next(bfs_iter)
        iter_2 = next(bfs_iter)
        iter_3 = next(bfs_iter)
        iter_4 = next(bfs_iter)
        iter_5 = next(bfs_iter)
        iter_6 = next(bfs_iter)
        iter_7 = next(bfs_iter)
        iter_8 = next(bfs_iter)
        iter_9 = next(bfs_iter)

        self.assertRaises(StopIteration, next, bfs_iter)

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

        iter_0 = next(tree_iter)
        iter_1 = next(tree_iter)
        iter_2 = next(tree_iter)
        iter_3 = next(tree_iter)
        iter_4 = next(tree_iter)
        iter_5 = next(tree_iter)

        self.assertRaises(StopIteration, next, tree_iter)

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
        pre_order_iter = tree.iter_pre_order()

        iter_0 = next(pre_order_iter)
        iter_1 = next(pre_order_iter)
        iter_2 = next(pre_order_iter)
        iter_3 = next(pre_order_iter)
        iter_4 = next(pre_order_iter)
        iter_5 = next(pre_order_iter)

        self.assertRaises(StopIteration, next, pre_order_iter)

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
        bfs_iter = tree.iter_bfs()

        iter_0 = next(bfs_iter)
        iter_1 = next(bfs_iter)
        iter_2 = next(bfs_iter)
        iter_3 = next(bfs_iter)
        iter_4 = next(bfs_iter)
        iter_5 = next(bfs_iter)

        self.assertRaises(StopIteration, next, bfs_iter)

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

    def test_tree_graph(self):
        """Test that graph() returns the expected pydot.Graph object for the
        following tree:

                             node_1
                            /      \
                        node_2    node_3
                      /   |   \
                node_4 node_5 node_6

        The resulting graph object should product the following output when its
        to_string() methods is called:

        digraph "arity_2(Int, Int) -> Int" {
        "arity_2(Int, Int) -> Int";
        "term_a() -> Int";
        "term_b() -> Int";
        "term_c() -> Str";
        "arity_3(Int, Int, Str) -> Int";
        "arity_3(Int, Int, Str) -> Int" -> "term_c() -> Str";
        "arity_3(Int, Int, Str) -> Int" -> "term_b() -> Int";
        "arity_3(Int, Int, Str) -> Int" -> "term_a() -> Int";
        "term_d() -> Int";
        "arity_2(Int, Int) -> Int";
        "arity_2(Int, Int) -> Int" -> "term_d() -> Int";
        "arity_2(Int, Int) -> Int" -> "arity_3(Int, Int, Str) -> Int";
        }

        """
        int_type = Type(name='Int')
        str_type = Type(name='Str')

        arity_3_op = Operator(
            symbol=Symbol(name='arity_3', dtype=int_type),
            signature=(int_type, int_type, str_type)
        )

        arity_2_op = Operator(
            symbol=Symbol(name='arity_2', dtype=int_type),
            signature=(int_type, int_type)
        )

        terminal_a_op = Operator(symbol=Symbol(name='term_a', dtype=int_type))
        terminal_b_op = Operator(symbol=Symbol(name='term_b', dtype=int_type))
        terminal_c_op = Operator(symbol=Symbol(name='term_c', dtype=str_type))
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

        expected = """digraph "arity_2(Int, Int) -> Int" {
"arity_2(Int, Int) -> Int";
"term_a() -> Int";
"term_b() -> Int";
"term_c() -> Str";
"arity_3(Int, Int, Str) -> Int";
"arity_3(Int, Int, Str) -> Int" -> "term_c() -> Str";
"arity_3(Int, Int, Str) -> Int" -> "term_b() -> Int";
"arity_3(Int, Int, Str) -> Int" -> "term_a() -> Int";
"term_d() -> Int";
"arity_2(Int, Int) -> Int";
"arity_2(Int, Int) -> Int" -> "term_d() -> Int";
"arity_2(Int, Int) -> Int" -> "arity_3(Int, Int, Str) -> Int";
}
"""
        self.assertEqual(expected, tree.graph().to_string())

    def test_tree_pickle(self):
        """Test that a Tree instance can be pickled and unpickled using the
        0 protocol and the -1 protocol.

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

        bfs_nodes = tuple(n for n in tree.iter_bfs())

        pickled_tree = pickle.dumps(tree, -1)
        unpickled_tree = pickle.loads(pickled_tree)

        unpickled_bfs_nodes = tuple(n for n in unpickled_tree.iter_bfs())

        self.assertEqual(tree, unpickled_tree)
        self.assertTupleEqual(bfs_nodes, unpickled_bfs_nodes)

        pickled_tree = pickle.dumps(tree, 0)
        unpickled_tree = pickle.loads(pickled_tree)

        unpickled_bfs_nodes = tuple(n for n in unpickled_tree.iter_bfs())

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

        calls = list(iter_calls(tree=tree, result_formatter='result_{0}'))

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

        symbols = list(iter_symbols(tree=tree))

        self.assertListEqual([symbol_1, symbol_2, symbol_3, symbol_5], symbols)

    def test_tree_getitem_and_delitem(self):
        """Test that a tree returns the expected nodes under __getitem__ and
        that the expected nodes are removed under __delitem__.

                             node_1
                            /      \
                        node_2    node_3
                      /   |   \
                node_4 node_5 node_6

        When __getitem__[0] is called, node_1 should be returned.
        When __getitem__[(0, 0)] is called, node_1 should be returned.
        When __getitem__[3] is called, node_5 should be returned.
        When __getitem__[(2, 1)] is called, node_5 should be returned.
        When __getitem__[5] is called, node_3 should be returned.
        When __getitem__[(1, 1)] is called, node_3 should be returned.

        """
        int_type = Type(name='Int')
        str_type = Type(name='Str')

        node_2_op = Operator(
            symbol=Symbol(name='node_2', dtype=int_type),
            signature=(int_type, int_type, str_type)
        )

        node_1_op = Operator(
            symbol=Symbol(name='node_1', dtype=int_type),
            signature=(int_type, int_type)
        )

        node_4_op = Operator(symbol=Symbol(name='node_4', dtype=int_type))
        node_5_op = Operator(symbol=Symbol(name='node_5', dtype=int_type))
        node_6_op = Operator(symbol=Symbol(name='node_6', dtype=str_type))
        node_3_op = Operator(symbol=Symbol(name='node_3', dtype=int_type))

        node_4 = Node(operator=node_4_op)
        node_5 = Node(operator=node_5_op)
        node_6 = Node(operator=node_6_op)
        node_2 = Node(operator=node_2_op)
        node_3 = Node(operator=node_3_op)
        node_1 = Node(operator=node_1_op)

        node_1.add_child(child=node_2, position=0)
        node_1.add_child(child=node_3, position=1)
        node_2.add_child(child=node_4, position=0)
        node_2.add_child(child=node_5, position=1)
        node_2.add_child(child=node_6, position=2)

        tree = Tree(root=node_1)

        self.assertEqual(node_1, tree[0])
        self.assertEqual(node_1, tree[(0, 0)])
        self.assertEqual(node_5, tree[3])
        self.assertEqual(node_5, tree[(2, 1)])
        self.assertEqual(node_3, tree[5])
        self.assertEqual(node_3, tree[(1, 1)])

        self.assertRaises(IndexError, tree.__getitem__, -1)
        self.assertRaises(IndexError, tree.__getitem__, (-1, 0))
        self.assertRaises(IndexError, tree.__getitem__, (0, -1))
        self.assertRaises(IndexError, tree.__getitem__, (-1, -1))

        self.assertEqual(6, len(tree))

        expected_pre_order = (node_1, node_2, node_4, node_5, node_6, node_3)
        pre_order = tuple(n for n in tree.iter_pre_order())
        self.assertTupleEqual(expected_pre_order, pre_order)

        expected_post_order = (node_4, node_5, node_6, node_2, node_3, node_1)
        post_order = tuple(n for n in tree)
        self.assertTupleEqual(expected_post_order, post_order)

        expected_bfs = (node_1, node_2, node_3, node_4, node_5, node_6)
        bfs = tuple(n for n in tree.iter_bfs())
        self.assertTupleEqual(expected_bfs, bfs)

        del tree[(1, 1)]  # first delete node_3

        # Now the tree looks like this:
        #
        #              node_1
        #             /      \
        #          node_2     *
        #        /   |   \
        #  node_4 node_5 node_6

        self.assertIsNone(node_3.parent)
        self.assertTupleEqual(node_1.right, (None,))

        node_3a_op = Operator(symbol=Symbol(name='node_3a', dtype=int_type))
        node_3a = Node(operator=node_3a_op)

        node_1.add_child(child=node_3a, position=1)

        # Now the tree looks like this:
        #
        #              node_1
        #             /      \
        #          node_2     node_3a
        #        /   |   \
        #  node_4 node_5 node_6

        self.assertTupleEqual((node_3a,), node_1.right)

        self.assertEqual(6, len(tree))

        expected_pre_order = (node_1, node_2, node_4, node_5, node_6, node_3a)
        pre_order = tuple(n for n in tree.iter_pre_order())
        self.assertTupleEqual(expected_pre_order, pre_order)

        expected_post_order = (node_4, node_5, node_6, node_2, node_3a, node_1)
        post_order = tuple(n for n in tree)
        self.assertTupleEqual(expected_post_order, post_order)

        expected_bfs = (node_1, node_2, node_3a, node_4, node_5, node_6)
        bfs = tuple(n for n in tree.iter_bfs())
        self.assertTupleEqual(expected_bfs, bfs)

        del tree[1]  # then delete node_2

        # Now the tree looks like this:
        #
        #              node_1
        #             /      \
        #            *     node_3a

        self.assertIsNone(node_2.parent)
        self.assertIsNone(node_1.left)

        node_2a_op = Operator(symbol=Symbol(name='node_2a', dtype=int_type))
        node_2a = Node(operator=node_2a_op)

        node_1.add_child(child=node_2a, position=0)

        # Now the tree looks like this:
        #
        #              node_1
        #             /      \
        #          node_2a  node_3a

        self.assertEqual(3, len(tree))

        expected_pre_order = (node_1, node_2a, node_3a)
        pre_order = tuple(n for n in tree.iter_pre_order())
        self.assertTupleEqual(expected_pre_order, pre_order)

        expected_post_order = (node_2a, node_3a, node_1)
        post_order = tuple(n for n in tree)
        self.assertTupleEqual(expected_post_order, post_order)

        expected_bfs = (node_1, node_2a, node_3a)
        bfs = tuple(n for n in tree.iter_bfs())
        self.assertTupleEqual(expected_bfs, bfs)

        # check that deleting the root node fails
        self.assertRaises(IndexError, tree.__delitem__, 0)

    def test_tree_setitem(self):
        """Test that we can build a tree using __setitem__.

                             node_1
                            /      \
                        node_2    node_3
                      /   |   \
                node_4 node_5 node_6

        """
        int_type = Type(name='Int')
        str_type = Type(name='Str')

        node_2_op = Operator(
            symbol=Symbol(name='node_2', dtype=int_type),
            signature=(int_type, int_type, str_type)
        )

        node_1_op = Operator(
            symbol=Symbol(name='node_1', dtype=int_type),
            signature=(int_type, int_type)
        )

        node_4_op = Operator(symbol=Symbol(name='node_4', dtype=int_type))
        node_5_op = Operator(symbol=Symbol(name='node_5', dtype=int_type))
        node_6_op = Operator(symbol=Symbol(name='node_6', dtype=str_type))
        node_3_op = Operator(symbol=Symbol(name='node_3', dtype=int_type))

        node_4 = Node(operator=node_4_op)
        node_5 = Node(operator=node_5_op)
        node_6 = Node(operator=node_6_op)
        node_2 = Node(operator=node_2_op)
        node_3 = Node(operator=node_3_op)
        node_1 = Node(operator=node_1_op)

        tree = Tree(root=node_1)
        self.assertEqual(tree[(0, 0)], node_1)

        tree[(1, 0)] = node_2
        self.assertEquals(tree[(1, 0)], node_2)

        tree[(1, 1)] = node_3
        self.assertEqual(tree[(1, 1)], node_3)

        tree[(2, 0)] = node_4
        self.assertEqual(tree[(2, 0)], node_4)

        tree[(2, 1)] = node_5
        self.assertEqual(tree[(2, 1)], node_5)

        tree[(2, 2)] = node_6
        self.assertEqual(tree[(2, 2)], node_6)
