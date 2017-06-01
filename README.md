## Zoonomia

[![Documentation Status](https://readthedocs.org/projects/zoonomia/badge/?version=latest)](https://zoonomia.readthedocs.org/en/latest/?badge=latest) [![Build Status](https://travis-ci.org/jgrillo/zoonomia.svg)](https://travis-ci.org/jgrillo/zoonomia)

> 
>

Zoonomia is a library for Strongly Typed Genetic Programming (STGP). STGP is an
extension to Genetic Programming where candidate solutions are richly typed. In 
plain Genetic Programming we assume all data have the same type, and we write 
basis functions to all work with that type. Because all the basis functions work 
on the same data type, we can shuffle them about without worrying about whether 
they'll work. In STGP we give basis functions explicit type signatures and rely 
on more carefully designed genetic operators to construct candidate solutions 
which obey these type constraints. In other words, we decorate our basis 
functions with type signatures to give the space of possible candidate solutions 
some more structure. Not only can we feed candidate solutions richly typed data 
streams, but the candidate solutions themselves can transform data in more 
interesting ways internally.

Zoonomia provides the user a bolt-on generic type system and some machinery for
using it to generate random constructs which are "safe" within that type system. 
Zoonomia aims to be *minimal*--it will create candidate solutions which are 
"safe" according to the types you give it, but it's up to you to make sure your 
basis functions are implemented safely with respect to those types. All Zoonomia 
can do is compose programs using your basis functions in a constrained way. 
Moreover, Zoonomia aims to be *flexible*--it doesn't specify a target language, 
allowing you to hook into a compiler of your choosing. A simple compiler which 
leverages Python's `exec()` is included. A consequence of this flexibility is 
that Zoonomia's type system can't know anything about your target language. All 
it can do is constrain how your basis functions can be composed. This is *not* 
type safety!

Zoonomia also provides the environmental scaffolding necessary to evolve 
populations of random computer programs and apply selection pressures to them 
such that they evolve to become better at some task. In this sense, Zoonomia is 
a tool for building multiobjective optimizers. However, no great effort has yet 
been made to provide sophisticated algorithms. Instead, Zoonomia gives *you* the 
basic infrastructure to build *your own* evolutionary algorithms.

## Example usage

In the following example we will evolve a simple 

```python
from zoonomia.types import Type, GenericType, ParametrizedType
from zoonomia.lang import Symbol, Operator, OperatorTable
from zoonomia.solution import Objective, Fitness, Solution 
from zoonomia.operations import (
    ramped_half_and_half, crossover_subtree, mutate_subtree, 
    mutate_interior_node, mutate_leaf_node, tournament_select
)



```
TBD

See [the documentation](http://zoonomia.readthedocs.org/en/latest/) for more 
information about how 

## Contributing

This is very fresh software, and it was written by a junior developer in his 
spare time. It is not "battle tested" in any sense, and it is probably deeply 
unsound and broken in ways which would seem obvious to people who actually know 
things about type systems, compilers, and programming languages. If in the 
course of attempting to use this software you find a bad idea, something that 
doesn't work, or a naive implementation, please open an issue. Pull requests are 
also welcome.

Another way someone might contribute is by expanding Zoonomia's collection of 
evolutionary algorithms. There is a large body of research having to do with 
interesting genetic operators. Zoonomia currently only has the simplest 
operators: tournament selection, point and subtree mutation, subtree crossover, 
full/grow/ramped half-and-half generation. This situation needs improvement. 

If you do choose to contribute (thank you in advance, by the way), please try to 
make sure that whatever code you write is carefully documented and covered by 
tests.

## building and running the tests

In the project root, build a virtualenv, install the dependencies, and run the
tests using PyTest:

`python3 -mvenv venv`
`. venv/bin/activate`
`pip install -r requirements.txt && pip install -r requirements-test.txt`
`pip install -e .`
`py.test`

## Resources

To learn more about Genetic Programming in general and STGP in particular, 
consult the following resources:

* [Strongly Typed Genetic Programming (Montana 2002)](http://davidmontana.net/papers/stgp.pdf)
* [A Field Guide to Genetic Programming (Poli, Langdon, McPhee 2008)](http://cswww.essex.ac.uk/staff/rpoli/gp-field-guide/)
* [The Genetic Programming Bibliography (Langdon, Chen)](http://www.cs.bham.ac.uk/~wbl/biblio/)

## Todo

Some ideas for improvement.

### Scaffolding

- [ ] [ADFs](http://cswww.essex.ac.uk/staff/rpoli/gp-field-guide/61EvolvingModularandHierarchicalStructures.html#12_1)
- [ ] **Backwards-compatible wire format:** Zoonomia objects implement the 
      `pickle` protocol which is great for shuttling them around between Python 
      processes. To implement a scalable distributed GP system we'll need a wire 
      format that allows them to be transmitted safely and efficiently over the 
      Internet. This format should probably be 
      [Google Protocol Buffers](https://developers.google.com/protocol-buffers/docs/pythontutorial).
- [ ] **Migration operators:** we can implement migration between processes 
      initially and leverage a wire format for clustering later.
- [ ] **Performance profiling & benchmarking:** Not a lot of attention has been
      paid to performance during initial development. Moving forward, we should
      keep an eye on performance by profiling the code and building a benchmark 
      suite to detect performance regressions.

### Algorithms

- [ ] [Lexicase selection](https://push-language.hampshire.edu/t/lexicase-selection/90)
- [ ] [NSGAII](https://www.iitk.ac.in/kangal/Deb_NSGA-II.pdf)
- [ ] NSGAIII: [1](http://www.egr.msu.edu/~kdeb/papers/k2012009.pdf), [2](http://www.egr.msu.edu/~kdeb/papers/k2012010.pdf)
- [ ] [Probabilistic Tree Creation (PTC1 & PTC2)](https://cs.gmu.edu/~sean/papers/thesis2p.pdf)
