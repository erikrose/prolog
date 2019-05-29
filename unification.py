"""Unification demo

Here I try to better understand unification by implementing it. We do it in an
imaginary Prolog-ish (rather than breadth-first Kanren-ish) language having...

* numeric literals like 8
* symbols (atoms) like 'foof'
* variables like V('VariableName'), and
* complex terms of the form functor(term_1, term_2, ...), spelled C('functor
  name', term_1, term_2, ...)

Open questions:
* How do you implement OR? A special disj form?
* How do you represent lists?

"""
from pprint import pformat

from .exceptions import BindingsConflict, ComplexTermShapesDiffer, ConstantsDiffer, TermsOfDifferentType


def is_atom(a):
    """We represent atoms as strings for brevity."""
    return isinstance(a, str)


def is_number(a):
    return isinstance(a, int)


def is_constant(a):
    return is_atom(a) or is_number(a)


def is_variable(a):
    return isinstance(a, V)


def is_complex(a):
    return isinstance(a, C)


class Variables:
    """A scope of instantiated variables

    An acyclic digraph of variables pointing to their values, possibly through
    other intermediate variables

    """
    def __init__(self):
        self.vars = {}
        self._generated_id = 0

    def bind(self, var_name, value):
        """Add a new binding for a variable.

        If that variable is bound to another variable (and so on), ending in an
        unbound variable, bind that variable instead. However, if the chain of
        bindings already ends in an assigned value, raise BindingsConflict.

        """
        existing_value = self.vars.get(var_name)
        if existing_value is None:
            self.vars[var_name] = value
        elif is_variable(existing_value):
            self.bind(existing_value.name, value)
        elif existing_value != value:  # Does it ever happen that existing_value would == value if we simply followed all the intermediate variable references?
            raise BindingsConflict(var_name, self.vars[var_name], value)

    def __getitem__(self, var_name):
        """Return the value of a variable, traversing any intermediate variable
        bindings."""
        value = self.vars[var_name]
        return self[value.name] if is_variable(value) else value

    def new(self):
        """Generate and return a new variable, for use in unifying 2 other
        variables."""
        self._generated_id += 1
        return V(f'_{self._generated_id}')

    def __str__(self):
        """Print a representation that can serve as user-facing query
        results."""
        return pformat(self.vars)  # Soft-wrap to 80 columns.


class V:
    """A class that represents a variable name, to distinguish it from an
    atomic string"""

    def __init__(self, var_name):
        self.name = var_name

    def __eq__(self, other):
        return isinstance(other, V) and self.name == other.name

    def __str__(self):
        return f'V("{self.name}")'

    __repr__ = __str__


class C:
    """A complex term"""

    def __init__(self, functor_name, *args):
        self.functor = functor_name
        self.args = args

    def arity(self):
        return len(self.args)

    def __eq__(self, other):
        return isinstance(other, C) and self.functor == other.functor and self.args == other.args

    def __str__(self):
        return f'C("{self.functor}"' + ('' if self.arity() == 0 else ', ' + ', '.join(str(arg) for arg in self.args)) + ')'

    __repr__ = __str__


def unify(a, b, vars=None):
    """Try to unify terms ``a`` and ``b``. Raise a CannotUnify subclass if it
    can't be done. Otherwise, return a Variables instance which maps variable
    names to the values necessary to make unification succeed."""
    # Inspired by http://learnprolognow.org/lpnpage.php?pagetype=html&pageid=lpn-htmlse5.
    if vars is None:
        vars = Variables()

    if is_constant(a) and is_constant(b):
        if a != b:
            raise ConstantsDiffer(a, b)
    elif is_variable(a) and is_variable(b):
        # Conceptual, bind 2 vars to each other. However, that would create a
        # cycle in the binding graph which we'd have to painstakingly check for
        # at points. Instead, create a new temp variable, and point both vars
        # to it. Then we keep our binding graph nice and acyclic.
        new_var = vars.new()
        vars.bind(a.name, new_var)
        vars.bind(b.name, new_var)
    elif is_variable(a):
        vars.bind(a.name, b)
    elif is_variable(b):
        vars.bind(b.name, a)
    elif is_complex(a) and is_complex(b):
        # If the functors are the same and the arities are the same and all the
        # args unify, then the complex terms unify.
        if a.functor != b.functor or a.arity() != b.arity():
            raise ComplexTermShapesDiffer(a, b)
        for c, d in zip(a.args, b.args):
            unify(c, d, vars)
    else:
        raise TermsOfDifferentType(a, b)
    return vars
