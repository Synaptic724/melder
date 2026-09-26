def execute(raw, reused):
    """Execute one prepared experimental shape under fixed reuse outcomes."""
    if tuple(sorted(raw)) != _keys:
        raise _Mismatch('Selector shape changed.')
    v0 = raw['left']
    v1 = raw['right']
    g1 = True
    p8_0 = v0
    p8_1 = v1
    n8 = _constructors[8](left=p8_0, right=p8_1)
    return n8
