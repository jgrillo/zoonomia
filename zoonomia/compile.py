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

from zoonomia.tree import calls_iter, symbols_iter


def compile_python_func(source, name):
    """Compile a Python function and return a reference to the compiled
    function reified in the host environment.

    .. note::
        See this very helpful article for information about the intricacies of
        runtime code generation in Python:
        http://lucumr.pocoo.org/2011/2/1/exec-in-python/

    :param source:
        The Python source code to compile.

    :type source: basestring

    :param name:
        The name of the Python function. This name must match the name given
        the function defined in the *source*.

    :type name: basestring

    :raise KeyError:
        if the *name* does not match the function defined in *source*.

    :return:
        A reference to the compiled function.

    :rtype: function

    """
    code = compile(source=source, filename='<string>', mode='exec')
    namespace = {}
    exec(code, namespace)
    return namespace[name]


def compile_python_tree(symbol, tree, python_function_template, **kwargs):
    """Compiles the source code resulting from rendering arguments against the
    jinja2.Template *python_function_template*. Returns a handle to the
    compiled Python function reified in the host environment.

    .. note::
        You may wish to use *zoonomia/templates/python_function.template*,
        which is sufficient for writing a very basic python function with no
        imports, as a starting point for your *python_function_template*.

    :param symbol:
        The Symbol in the host environment to which the reified, compiled
        function will be bound.

    :type symbol: zoonomia.lang.Symbol

    :param tree:
        A Tree of Operators.

    :type tree: zoonomia.tree.Tree

    :param python_function_template:
        A jinja2.Template against which the Calls and Symbols in the *tree*
        will be rendered.

    :type python_function_template: jinja2.Template

    :param kwargs:
        Additional kwargs will be passed to the *python_function_template*.

    :return:
        A function handle obtained by compiling and reifying the source code
        generated by rendering the *python_function_template*.

    :rtype: function

    """
    calls = calls_iter(tree=tree, result_formatter='result_{0}')
    symbols = symbols_iter(tree=tree)

    render_kwargs = {'symbol': symbol, 'args': symbols, 'calls': calls}
    render_kwargs.update(kwargs)

    source = python_function_template.render(render_kwargs)

    return compile_python_func(source=source, name=symbol.name)
