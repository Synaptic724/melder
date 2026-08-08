import pytest
import inspect
from functools import wraps
from typing import Callable, Union, Iterable
from melder.utilities.helpers.package import Pack



# --- Some fake decorators to test wrapping and metadata ---
def simple_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def arg_changing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func("intercepted", *args, **kwargs)
    return wrapper

def no_wraps_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def raising_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        raise RuntimeError("Blocked by decorator")
    return wrapper

# Dummy functions
def dummy(): return "ok"
@simple_decorator
def decorated(): return "decorated"
@no_wraps_decorator
def hidden(): return "hidden"
@arg_changing_decorator
def intercepted(x): return f"got {x}"

# Generator and coroutine functions
def gen_func():
    yield 1

async def coro_func():
    return 1

# Coroutine object (not function)
async def coro(): return 1
coro_obj = coro()


# NOTE: `Package` is NOT imported at the top of this file - it arrives from the mid-file import
# further down (see the comment above it). Every use below sits inside a method body and so
# resolves at TEST RUN time, by which point the module has finished executing. Fragile but valid,
# and preserved exactly: hoisting that import would be an unrelated edit.
class TestPackAndPackMany:
    def test_pack_valid_callable(self):
        assert Package._pack(dummy)() == "ok"

    def test_pack_valid_package(self):
        p = Package(dummy)
        assert Package._pack(p).__name__ == dummy.__name__

    def test_pack_many_single_callable(self):
        result = Package._pack_many(dummy)
        assert len(result) == 1
        assert isinstance(result[0], Package)

    def test_pack_many_single_package(self):
        p = Package(dummy)
        result = Package._pack_many(p)
        assert result[0] == p

    def test_pack_many_iterable_of_callables(self):
        result = Package._pack_many([dummy, decorated])
        assert len(result) == 2

    def test_pack_many_iterable_mixed(self):
        p = Package(dummy)
        result = Package._pack_many([p, decorated])
        assert result[0] == p
        assert isinstance(result[1], Package)

    def test_pack_rejects_none(self):
        with pytest.raises(TypeError):
            Package._pack(None)

    def test_pack_many_rejects_none(self):
        with pytest.raises(TypeError):
            Package._pack_many(None)

    def test_pack_rejects_non_callable(self):
        with pytest.raises(TypeError):
            Package._pack(123)

    def test_pack_many_rejects_non_iterable(self):
        with pytest.raises(TypeError):
            Package._pack_many(123)

    def test_pack_rejects_generator_func(self):
        with pytest.raises(TypeError):
            Package._pack(gen_func)


    def test_pack_many_rejects_generator_in_list(self):
        with pytest.raises(TypeError):
            Package._pack_many([dummy, gen_func])

    def test_pack_decorated_simple(self):
        assert Package._pack(decorated)() == "decorated"

    def test_pack_many_decorated_simple(self):
        out = Package._pack_many(decorated)
        assert out[0]() == "decorated"

    def test_pack_preserves_wrapped_name(self):
        func = Package._pack(decorated)
        assert func.__name__ == "decorated"

    def test_pack_handles_no_wraps(self):
        result = Package._pack(hidden)
        assert callable(result)

    def test_pack_many_handles_mixed_decorators(self):
        result = Package._pack_many([dummy, decorated, hidden])
        assert len(result) == 3

    def test_decorator_altering_args_still_works(self):
        result = Package._pack(intercepted)
        assert result() == "got intercepted"

    def test_pack_many_with_decorator_argchanger(self):
        out = Package._pack_many(intercepted)
        assert out[0]() == "got intercepted"

    def test_pack_decorator_that_raises(self):
        @raising_decorator
        def boom(): return "nope"
        func = Package._pack(boom)
        with pytest.raises(RuntimeError):
            func()

    def test_pack_many_decorator_that_raises(self):
        @raising_decorator
        def boom(): return "nope"
        out = Package._pack_many([boom])
        with pytest.raises(RuntimeError):
            out[0]()

    def test_pack_of_lambda(self):
        f = lambda x: x + 1
        result = Package._pack(f)
        assert result(2) == 3

    def test_pack_many_of_lambdas(self):
        out = Package._pack_many([lambda x: x + 1, lambda x: x * 2])
        assert out[0](5) == 6
        assert out[1](3) == 6

    def test_pack_package_preserves_bound_args(self):
        # The lambda must accept two args to handle the pre-bound and new one
        p = Package(lambda x, y: x + y, 2)
        out = Package._pack(p)
        # This now correctly calls lambda(2, 3)
        assert out(3) == 5

    def test_pack_many_preserves_frozen_package(self):
        p = Package(dummy)
        p.freeze()
        out = Package._pack_many([p])
        assert out[0]() == "ok"

    def test_pack_signature_still_inspectable(self):
        f = lambda x, y: x + y
        result = Package._pack(f)
        sig = inspect.signature(result)
        assert "x" in sig.parameters

    def test_pack_many_all_package_instances(self):
        p1 = Package(lambda x: x + 1)
        p2 = Package(lambda x: x * 2)
        result = Package._pack_many([p1, p2])
        assert len(result) == 2
        # assertIs -> identity. Load-bearing: the point is that _pack_many returns the SAME
        # objects rather than re-wrapping them, and Package defines __eq__, so == would pass
        # even if it had created new wrappers.
        assert result[0] is p1
        assert result[1] is p2

    def test_pack_preserves_callable_object(self):
        class Foo:
            def __call__(self, x): return x * 3
        result = Package._pack(Foo())
        assert result(3) == 9

    def test_pack_many_callable_object_in_list(self):
        class Foo:
            def __call__(self, x): return x * 3
        out = Package._pack_many([Foo()])
        assert out[0](2) == 6

    def test_pack_preserves_docstring_if_exists(self):
        def foo(): "hi"
        result = Package._pack(foo)
        assert result.__doc__ == "hi"

    def test_pack_of_builtin_function(self):
        result = Package._pack(abs)
        assert result(-5) == 5

    def test_pack_many_builtins(self):
        result = Package._pack_many([abs, len])
        assert result[0](-9) == 9
        assert result[1]([1, 2, 3]) == 3


# The pin had a SECOND `import unittest` on this line, a duplicate of the top-of-file one. Both
# are dropped because nothing in the ported file uses unittest any more. The Package/Pack import
# below is NOT a duplicate and is LOAD-BEARING - it is the only place `Package` enters this
# module's namespace, and the class above depends on it resolving before any test runs.
from melder.utilities.helpers.package import Package, Pack


# --- Helper functions for advanced tests ---
def dynamic_join(*args, **kwargs):
    """Joins all positional and keyword args into a string."""
    s_args = ",".join(map(str, args))
    s_kwargs = ",".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
    return f"args=({s_args})|kwargs=({s_kwargs})"


def complex_func(name, salutation="Hello", punctuation="!"):
    """A function with mixed default and required args."""
    return f"{salutation}, {name}{punctuation}"


# --- Advanced Test Class ---
class TestPackageAdvancedScenarios:
    """
    Puts the Package class through the ringer with advanced use cases,
    focusing on composition, state interactions, and edge cases.
    """

    def test_merge_many_works_as_pipeline(self):
        """Ensures merge_many correctly composes a list of Packages."""
        p1 = Pack(lambda x: x + 5)
        p2 = Pack(str)
        p3 = Pack(lambda s: f"Result: {s}")

        # Should be equivalent to p3(p2(p1(x)))
        merged = Package.merge_many([p1, p2, p3])

        assert merged(10) == "Result: 15"

    def test_merge_many_validates_input(self):
        """Ensures merge_many rejects empty or invalid lists."""
        # DEFECT 13: the pin carried `msg=` on both of these. pytest.raises has NO msg parameter,
        # and match= is NOT a substitute - match= is a regex tested against the RAISED exception's
        # text, whereas msg= was the diagnostic shown when NOTHING was raised. The text is kept as
        # a comment rather than dropped silently, and deliberately NOT bolted onto a neighbouring
        # assertion, which would attach a message to something that is not what failed.
        with pytest.raises(ValueError):  # msg at pin: "Should reject empty list"
            Package.merge_many([])

        with pytest.raises(TypeError):  # msg at pin: "Should reject non-Package items"
            Package.merge_many([Pack(int), "not a package"])

    def test_dispose_prevents_further_calls(self):
        """Verifies that a cleaned Package cannot be called."""
        p = Pack(int, "10")
        assert p() == 10  # Works before dispose

        p.cleanup()
        assert p.cleaned

        # MIGRATION NOTE: this asserted TypeError, which was an artifact of the
        # CommandOps implementation setting `_func = None` and then trying to call
        # None. `_cleanup_core()` now DELETES the owned slots, so the access lands
        # in __getattr__ and surfaces the canonical cleaned-object error instead.
        # RuntimeError is the intended contract (see bug269 regression); TypeError
        # was the accident.
        with pytest.raises(RuntimeError):
            p()

    def test_error_in_composition_pipe_propagates(self):
        """Checks that an error in the middle of a pipeline is raised correctly."""
        p1 = Pack(lambda x: x * 2)
        p2_raises = Pack(lambda x: 1 / 0)  # This will raise an error
        p3 = Pack(str)

        composed = p1 | p2_raises | p3

        with pytest.raises(ZeroDivisionError):
            composed(10)

    # expectedFailure -> xfail(strict=True). Without strict, this silently stops reporting the
    # case it exists to catch (the __call__ zero-fill fallback starting to work).
    @pytest.mark.xfail(strict=True)
    def test_call_fallback_fills_missing_positional_args(self):
        """Tests the special __call__ logic that fills missing args with 0."""

        def needs_two(a, b):
            return a + b

        # Create a package that is missing its second required argument.
        p = Pack(needs_two, 5)

        # The __call__ fallback should supply '0' for the missing 'b' argument.
        # The call should effectively become needs_two(5, 0).
        assert p() == 5

    def test_composition_ignores_second_packages_args(self):
        """Tests that p1 | p2 correctly pipes p1's output as the sole input to p2."""
        # p1 will be called with its bound arg '5', returning 10.
        p1 = Pack(lambda x: x * 2, 5)
        # p2's bound arg '100' should be ignored in composition.
        p2 = Pack(lambda y: y + 1, 100)

        composed = p1 | p2  # Equivalent to p2(p1())

        # The result of p1() (which is 10) becomes the argument for p2.
        # So, the final call is effectively (lambda y: y + 1)(10).
        assert composed() == 11

    def test_addition_passes_call_args_to_both(self):
        """Tests that p1 + p2 calls both with the full combined arguments."""
        # p1(5) will call lambda(10, 5), returning 15
        p1 = Pack(lambda x, y: x + y, 10)
        # p2(5) will call lambda(2, 5), returning 10
        p2 = Pack(lambda x, y: x * y, 2)

        added = p1 + p2  # Equivalent to p1(*args, **kwargs) + p2(*args, **kwargs)

        # The call added(5) should be 15 + 10
        assert added(5) == 25

    def test_curry_after_bind_preserves_state(self):
        """Ensures curry() captures the Package's state at the moment of the call."""
        p1 = Pack(complex_func)
        p1.bind(salutation="Greetings")  # p1 is now mutated

        # p2 is a *new* Package with p1's state ("Greetings") plus the new arg "World".
        p2 = p1.curry("World")

        # Mutating p2 should not affect p1
        p2.bind(punctuation=".")

        # Verify p2 has the full, correct state
        assert p2() == "Greetings, World."
        # Verify p1 was not affected by p2's mutation
        assert p1.kwargs == {"salutation": "Greetings"}

    def test_hashing_and_equality_after_mutation(self):
        """Checks that __eq__ and __hash__ correctly reflect the Package's state."""
        p1 = Pack(complex_func)
        p2 = Pack(complex_func)

        # Two identical, fresh packages should be equal
        assert p1 == p2

        d = {p1: "original"}
        assert p2 in d  # p2 should be found using p1 as the key

        # MIGRATION NOTE: this used to mutate p1/p2 AFTER hashing them and assert
        # the hashes moved. That is precisely the bug freeze-on-hash closes - a
        # Package whose hash changes while it sits in a dict can no longer find
        # itself. `__hash__` now latches `_frozen`, so binding mutators raise once
        # the object has been used as a key.
        with pytest.raises(RuntimeError):
            p2.bind(name="mutated")

        # p1 was hashed too, as the dict key, so it is frozen on the same terms.
        with pytest.raises(RuntimeError):
            p1.bind(name="mutated")

        # Frozen does not mean unusable: equality, hash and lookup all still hold,
        # which is the point of freezing rather than forbidding.
        assert p1 == p2
        assert hash(p1) == hash(p2)
        assert p2 in d

        # A package that was never hashed is still freely mutable.
        fresh = Pack(complex_func)
        fresh.bind(name="mutated")
        assert fresh != p1

    def test_package_wrapping_function_with_star_args(self):
        """Tests argument packing with a function that uses *args and **kwargs."""
        # Pre-bind positional args 'a', 'b' and keyword arg 'sep'.
        p = Pack(dynamic_join, 'a', 'b', sep='-')

        # Call with additional positional args 'c', 'd' and keyword arg 'extra'.
        result = p('c', 'd', extra='!')

        # The final call should be dynamic_join('a', 'b', 'c', 'd', extra='!', sep='-')
        expected = "args=(a,b,c,d)|kwargs=(extra=!,sep=-)"
        assert result == expected

    def test_frozen_package_rejects_bind_but_allows_curry(self):
        """Ensures a frozen Package can't be mutated but can be curried (creating a new instance)."""
        p_frozen = Pack(complex_func, "freeze-me")
        p_frozen.freeze()

        # Bind must fail on a frozen package
        with pytest.raises(RuntimeError):
            p_frozen.bind(punctuation=".")

        # Curry should succeed because it creates a new, non-frozen Package
        p_curried = p_frozen.curry(salutation="Hola")
        assert isinstance(p_curried, Package)

        # The new package is mutable
        p_curried.bind(punctuation="?")
        assert p_curried() == "Hola, freeze-me?"

class TestPackVerify:
    """
    Tests for the Pack.verify() static method.
    """

    def test_verify_single_valid_pack(self):
        """Ensures Pack.verify() returns True for a valid Pack instance."""
        p = Pack(lambda: "test")
        assert Pack.verify(p)

    def test_verify_list_of_valid_packs(self):
        """Ensures Pack.verify() returns True for a list of valid Packs."""
        packs = [Pack(lambda: 1), Pack(lambda: 2)]
        assert Pack.verify(packs)

    def test_verify_rejects_non_pack_type(self):
        """Ensures Pack.verify() raises TypeError for non-Pack objects."""
        # assertRaisesRegex -> match=. Literal "Expected a Pack instance" audited: no regex
        # metacharacters, so it is safe unescaped and still means re.search.
        with pytest.raises(TypeError, match="Expected a Pack instance"):
            Pack.verify(123)
        with pytest.raises(TypeError, match="Expected a Pack instance"):
            Pack.verify("not a pack")
        with pytest.raises(TypeError, match="Expected a Pack instance"):
            Pack.verify(None)

    def test_verify_rejects_list_with_invalid_item(self):
        """Ensures Pack.verify() raises TypeError for a list containing non-Packs."""
        invalid_list = [Pack(lambda: 1), "not a pack", Pack(lambda: 3)]
        with pytest.raises(TypeError, match="Expected a Pack instance"):
            Pack.verify(invalid_list)

    def test_verify_handles_empty_list(self):
        """Ensures Pack.verify() handles an empty list gracefully."""
        assert Pack.verify([])

    def test_verify_handles_tuple_of_packs(self):
        """Ensures Pack.verify() works correctly with a tuple of Packs."""
        packs = (Pack(lambda: 1), Pack(lambda: 2))
        assert Pack.verify(packs)

    def test_verify_handles_set_of_packs(self):
        """Ensures Pack.verify() works correctly with a set of Packs."""
        # Note: Requires Pack to be hashable, which it is.
        packs = {Pack(lambda: 1), Pack(lambda: 2)}
        assert Pack.verify(packs)

    def test_verify_rejects_generator(self):
        """Ensures Pack.verify() correctly rejects a generator object."""

        def my_generator():
            yield Pack(lambda: 1)

        with pytest.raises(TypeError, match="Expected a Pack instance"):
            Pack.verify(my_generator())

if __name__ == "__main__":
    pytest.main([__file__])
