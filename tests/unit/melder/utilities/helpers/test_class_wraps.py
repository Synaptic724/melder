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
