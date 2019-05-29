class CannotUnify(Exception):
    pass


class ConstantsDiffer(CannotUnify):
    def __init__(self, const_a, const_b):
        self.const_a = const_a
        self.const_b = const_b

    def __str__(self):
        return f'{repr(self.const_a)} cannot unify with {repr(self.const_b)}.'


class BindingsConflict(CannotUnify):
    def __init__(self, var_name, existing_value, conflicting_value):
        self.var_name = var_name
        self.existing_value = existing_value
        self.conflicting_value = conflicting_value
    
    def __str__(self):
        return f'Tried to bind {self.var_name} to {repr(self.conflicting_value)}, but it was already bound to {repr(self.existing_value)}.'


class ComplexTermShapesDiffer(CannotUnify):
    def __init__(self, complex_a, complex_b):
        self.a = complex_a
        self.b = complex_b

    def __str__(self):
        return f'{self.a.functor}/{self.a.arity()} cannot unify with {self.b.functor}/{self.b.arity()}.'


class TermsOfDifferentType(CannotUnify):
    def __init__(term_a, term_b):
        self.a = term_a
        self.b = term_b

    def __str__(self):
        return f'Cannot unify different term types {repr(self.a)} and {repr(self.b)}.'
