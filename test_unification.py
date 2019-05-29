from .exceptions import BindingsConflict, ComplexTermShapesDiffer, ConstantsDiffer
from .unification import C, unify, V

from pytest import raises


def test_atoms():
    assert unify(8, 8) == {}
    with raises(ConstantsDiffer):
        unify(8, 9)


def test_var_instantiation():
    """Test that a var unifies with any other kind of thing."""
    assert unify(V('X'), 8) == {'X': 8}
    assert unify(V('X'), 'alf') == {'X': 'alf'}
    assert unify(V('X'), C('sum', 2, 3, 5)) == {'X': C('sum', 2, 3, 5)}


def test_unifiable_vars():
    """Test that vars unify with other vars."""
    assert unify(V('X'), V('Y')) == {'X': V('_1'),
                                     'Y': V('_1')}

def test_str():
    """Test string representations for C and V."""
    assert str(C('foo', 1, 2, V('X'))) == 'C("foo", 1, 2, V("X"))'


def test_complex():
    # Identical things should unify:
    assert unify(C('foo', 1, 2, 3), C('foo', 1, 2, 3)) == {}
    with raises(ConstantsDiffer):
        unify(C('foo', 1, 2, 3), C('foo', 5, 2, 3))
    with raises(ComplexTermShapesDiffer):
        unify(C('foo', 1, 2, 3), C('bar', 2, 3))
    # Simple single variable binding:
    assert unify(C('foo', V('x'), 2, 3), C('foo', 1, 2, 3)) == {'x': 1}
    # Variables that instantiate to the same value shouldn't step on each other's toes:
    assert unify(C('foo', V('x'), 1), C('foo', 1, V('x'))) == {'x': 1}
    # X can't be both 1 and 2:
    with raises(BindingsConflict):
        unify(C('foo', V('x'), 2), C('foo', 1, V('x')))
    # An arbitrary complicated thing:
    assert unify(C('k', C('s', 'g'), C('t', 'k'  )),
                 C('k', V('X')     , C('t', V('Y')))) == {
        'X': C('s', 'g'),
        'Y': 'k'
    }


def test_nested_complexes():
    assert unify(C('foo', C('bar', V('x'))), C('foo', C('bar', 5))) == {'x': 5}
