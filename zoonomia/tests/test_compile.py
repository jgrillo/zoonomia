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

from jinja2 import Environment, PackageLoader

from zoonomia.tree import Node, Tree, iter_calls, iter_symbols
from zoonomia.lang import Symbol, Operator
from zoonomia.types import Type
from zoonomia.compile import compile_python_func, compile_python_tree


class TestCompile(unittest.TestCase):

    def test_python_function_template(self):
        """Test that the *templates.python_function.template* produces expected
        python function definition source code for the following tree:

                  plus
                 /   \
                x    power
                    /    \
                   y      z

        """
        env = Environment(
            loader=PackageLoader(
                package_name='zoonomia',
                package_path='templates'
            ),
            trim_blocks=True,
            lstrip_blocks=True
        )
        python_function_template = env.get_template('python_function.template')

        float_type = Type(name='float')

        plus = Operator(
            symbol=Symbol(name='float.__add__', dtype=float_type),
            signature=(float_type, float_type)
        )
        power = Operator(
            symbol=Symbol(name='pow', dtype=float_type),
            signature=(float_type, float_type)
        )
        x = Operator(symbol=Symbol(name='x', dtype=float_type))
        y = Operator(symbol=Symbol(name='y', dtype=float_type))
        z = Operator(symbol=Symbol(name='z', dtype=float_type))

        plus_node = Node(operator=plus)
        power_node = Node(operator=power)
        x_node = Node(operator=x)
        y_node = Node(operator=y)
        z_node = Node(operator=z)

        plus_node.add_child(child=x_node, position=0)
        plus_node.add_child(child=power_node, position=1)
        power_node.add_child(child=y_node, position=0)
        power_node.add_child(child=z_node, position=1)

        tree = Tree(root=plus_node)

        calls = iter_calls(tree=tree, result_formatter='result_{0}')
        symbols = iter_symbols(tree=tree)
        target_symbol = Symbol(name='test_func', dtype=float_type)

        expected = """
def test_func(x, y, z):
    result_0 = pow(y, z)
    result_1 = float.__add__(x, result_0)
    return result_1
"""

        self.assertEqual(
            expected,
            python_function_template.render(
                {'symbol': target_symbol, 'args': symbols, 'calls': calls}
            )
        )

    def test_compile_python_func(self):
        """Test that the source code of a python function gets compiled into
        the expected function.

        """
        source = u"""def f(x): return x ** 2"""
        func = compile_python_func(source, 'f')

        self.assertEqual(func(2), 4)

    def test_compile_python_func_raises_KeyError__when_name_incorrect(self):
        """Test that the compile_python_func raises a KeyError when the wrong
        name is provided.

        """
        source = u"""def f(x): return x ** 2"""

        self.assertRaises(KeyError, compile_python_func, source, 'g')

    def test_compile_python_tree(self):
        """Test that the following tree gets compiled into a python function
        which behaves as expected:

                  plus
                 /   \
                x    power
                    /    \
                   y      z

        """
        env = Environment(
            loader=PackageLoader(
                package_name='zoonomia',
                package_path='templates'
            ),
            trim_blocks=True,
            lstrip_blocks=True
        )
        python_function_template = env.get_template('python_function.template')

        float_type = Type(name='float')

        plus = Operator(
            symbol=Symbol(name='float.__add__', dtype=float_type),
            signature=(float_type, float_type)
        )
        power = Operator(
            symbol=Symbol(name='pow', dtype=float_type),
            signature=(float_type, float_type)
        )
        x = Operator(symbol=Symbol(name='x', dtype=float_type))
        y = Operator(symbol=Symbol(name='y', dtype=float_type))
        z = Operator(symbol=Symbol(name='z', dtype=float_type))

        plus_node = Node(operator=plus)
        power_node = Node(operator=power)
        x_node = Node(operator=x)
        y_node = Node(operator=y)
        z_node = Node(operator=z)

        plus_node.add_child(child=x_node, position=0)
        plus_node.add_child(child=power_node, position=1)
        power_node.add_child(child=y_node, position=0)
        power_node.add_child(child=z_node, position=1)

        func = compile_python_tree(
            symbol=Symbol(name='test_func', dtype=float_type),
            tree=Tree(root=plus_node),
            python_function_template=python_function_template
        )

        self.assertEqual(
            66.6, round(number=func(x=2.0, y=8.037419, z=2.0), ndigits=3)
        )
