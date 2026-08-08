import inspect
import pytest
from functools import wraps
from melder.utilities.helpers.package import Pack


def simple_decorator(f):
    def wrapper(*a, **k): return f(*a, **k)
    return wrapper

def good_decorator(f):
    @wraps(f)
    def wrapper(*a, **k): return f(*a, **k)
    return wrapper

def async_decorator(f):
    async def wrapper(*a, **k): return await f(*a, **k)
    return wrapper


class TestPackDecorators:

    def test_good_decorator_is_wrapped_clean(self):
        @good_decorator
        def greet(name): return f"hi {name}"

        p = Pack(greet, "Mark")  # ← pre-bind one positional argument
        assert p() == "hi Mark"  # call with no extras, still works
        assert "arg0" in p.signature.arguments  # now arg0 exists

    def test_bad_decorator_still_executes(self):
        """
        Test that a function with a non-@wraps decorator still executes under Pack.
        Signature will reflect the wrapper, not the original.
        """

        @simple_decorator
        def shout(name): return f"yo {name}"

        p = Pack(shout)
        assert p("Zen") == "yo Zen"

        sig = inspect.signature(p._func)
        assert isinstance(sig, inspect.Signature)

        # Decorator wrapper has parameters *a, **k (as named)
        assert "a" in sig.parameters
        assert "k" in sig.parameters

        # Ensure their kinds are VAR_POSITIONAL and VAR_KEYWORD
        assert sig.parameters["a"].kind == inspect.Parameter.VAR_POSITIONAL
        assert sig.parameters["k"].kind == inspect.Parameter.VAR_KEYWORD


    def test_double_decorated_still_works(self):
        @good_decorator
        @simple_decorator
        def echo(x): return x

        p = Pack(echo)
        assert p("sound") == "sound"

    # `@unittest.expectedFailure` -> `@pytest.mark.xfail(strict=True)`. STRICT IS REQUIRED, not
    # stylistic. Verified against the installed runners rather than assumed:
    #   unittest.expectedFailure : test fails -> "expected failures=1" (run OK)
    #                              test PASSES -> "unexpected success"  -> run FAILED
    #   xfail(strict=True)       : test fails -> xfailed; test PASSES -> FAILED   [MATCHES]
    #   xfail (no strict)        : test PASSES -> XPASS, run stays GREEN          [WEAKER]
    # Plain @pytest.mark.xfail would silently stop reporting the case this test exists to catch -
    # namely Pack accepting a coroutine it should reject. The repo sets no xfail_strict in
    # pyproject, so the default is non-strict and the marker must carry strict=True explicitly.
    @pytest.mark.xfail(strict=True)
    def test_async_decorated_function_rejected(self):
        async def coro(x): return x
        wrapped = async_decorator(coro)

        with pytest.raises(TypeError):
            _ = Pack(wrapped)

    def test_decorator_without_wrapping_name_fallback(self):
        @simple_decorator
        def greet(name): return f"hello {name}"

        p = Pack(greet)
        assert callable(p)
        assert p("Neo") == "hello Neo"

    def test_plain_function_works(self):
        def double(x): return x * 2
        p = Pack(double)
        assert p(10) == 20


if __name__ == "__main__":
    pytest.main([__file__])
