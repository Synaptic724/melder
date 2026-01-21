from melder.utilities.helpers.class_wraps import class_wraps


def test_class_wraps_sets_metadata():
    @class_wraps("demo")
    def deco(cls):
        class Wrapped(cls):
            pass

        return Wrapped

    class Base:
        pass

    Wrapped = deco(Base)
    assert getattr(Wrapped, "__is_wrapped__", False) is True
    assert Wrapped.__wrapped__ is Base
    assert getattr(Wrapped, "__decorator_name__", None) == "demo"


def test_class_wraps_without_name_and_preserves_attrs():
    @class_wraps()
    def deco(cls):
        class Wrapped(cls):
            pass
        return Wrapped

    class Base:
        pass

    wrapped = deco(Base)
    assert getattr(wrapped, "__decorator_name__", None) is None
    assert wrapped.__wrapped__ is Base
    # update_wrapper preserves metadata on the wrapper function, not the returned class
    assert wrapped.__name__ == "Wrapped"


def test_class_wraps_on_multiple_classes_distinct_wrapped():
    @class_wraps("multi")
    def deco(cls):
        class Wrapped(cls):
            pass
        return Wrapped

    class A: ...
    class B: ...

    WA = deco(A)
    WB = deco(B)
    assert WA.__wrapped__ is A
    assert WB.__wrapped__ is B
    assert getattr(WA, "__decorator_name__") == "multi"
    assert getattr(WB, "__decorator_name__") == "multi"
