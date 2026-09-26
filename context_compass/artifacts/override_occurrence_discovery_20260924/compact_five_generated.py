def execute(raw, reused):
    """Execute one prepared experimental shape under fixed reuse outcomes."""
    if tuple(sorted(raw)) != _keys:
        raise _Mismatch('Selector shape changed.')
    v0 = raw['a']
    v1 = raw['b']
    v2 = raw['c']
    g1 = True
    p0_0 = v0
    p0_1 = v1
    p0_2 = v2
    n4 = _constructors[4]()
    n5 = _constructors[5]()
    n0 = _constructors[0](a=p0_0, b=p0_1, c=p0_2, d=n4, e=n5)
    return n0
