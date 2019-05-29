from .exceptions import BindingsConflict, ComplexTermShapesDiffer, ConstantsDiffer
from .unification import C, unify, V

from pytest import raises


def unify_eq(a, b, vars):
    """Assert that the result of unifying ``a`` and ``b`` is the raw set of
    bindings spelled out in the dict ``vars``.

    (``vars`` explicitly lists temporary vars; it doesn't traverse them away.)

    """
    assert unify(a, b).vars == vars


def test_atoms():
    unify_eq(8, 8, {})
    with raises(ConstantsDiffer):
        unify(8, 9)


def test_var_instantiation():
    """Test that a var unifies with any other kind of thing."""
    unify_eq(V('X'), 8, {'X': 8})
    unify_eq(V('X'), 'alf', {'X': 'alf'})
    unify_eq(V('X'), C('sum', 2, 3, 5), {'X': C('sum', 2, 3, 5)})


def test_unifiable_vars():
    """Test that vars unify with other vars."""
    unify_eq(V('X'), V('Y'), {'X': V('_1'),
                              'Y': V('_1')})

def test_str():
    """Test string representations for C and V."""
    assert str(C('foo', 1, 2, V('X'))) == 'C("foo", 1, 2, V("X"))'


def test_complex():
    # Identical things should unify:
    unify_eq(C('foo', 1, 2, 3), C('foo', 1, 2, 3), {})
    with raises(ConstantsDiffer):
        unify(C('foo', 1, 2, 3), C('foo', 5, 2, 3))
    with raises(ComplexTermShapesDiffer):
        unify(C('foo', 1, 2, 3), C('bar', 2, 3))
    # Simple single variable binding:
    unify_eq(C('foo', V('x'), 2, 3), C('foo', 1, 2, 3), {'x': 1})
    # Variables that instantiate to the same value shouldn't step on each other's toes:
    unify_eq(C('foo', V('x'), 1), C('foo', 1, V('x')), {'x': 1})
    # X can't be both 1 and 2:
    with raises(BindingsConflict):
        unify(C('foo', V('x'), 2), C('foo', 1, V('x')))
    # An arbitrary complicated thing:
    unify_eq(C('k', C('s', 'g'), C('t', 'k'  )),
                    C('k', V('X')     , C('t', V('Y'))), {
        'X': C('s', 'g'),
        'Y': 'k'
    })


def test_nested_complexes():
    unify_eq(C('foo', C('bar', V('x'))), C('foo', C('bar', 5)), {'x': 5})


def test_intermediate_vars():
    """Make sure when multiple vars are bound to each other, we can still unify
    by effectively binding a terminal value to that shared binding."""
    unify_eq(C('foo', V('y'), C('bar', V('x'))),
             C('foo', V('x'), C('bar',    7  )), {
        'x': V('_1'),
        'y': V('_1'),
        '_1': 7
    })
