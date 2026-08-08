import pytest
import time
import threading
from functools import partial
from melder.utilities.helpers.package import Package, Pack

# Helper functions
def _square(x): return x * x
def _add(a, b): return a + b
def delayed_add(a, b): time.sleep(0.01); return a + b
def constant_value(): return 42

class TestPackage:

    # --- Basic Functionality ---
    def test_package_wraps_function(self):
        p = Package(_add, 2, 3)
        assert p() == 5

    def test_package_wraps_lambda(self):
        p = Package(lambda x: x + 1, 5)
        assert p() == 6

    def test_package_wraps_multiple_args(self):
        p = Package(lambda x, y: x * y, 3, 4)
        assert p() == 12

    def test_package_with_kwargs(self):
        def greet(name, punctuation="!"): return f"Hello, {name}{punctuation}"
        p = Package(greet, "Alice", punctuation=".")
        assert p() == "Hello, Alice."

    def test_package_with_partial(self):
        p = Package(partial(lambda x, y: x + y, 3), 5)
        assert p() == 8

    # --- Edge Cases ---
    def test_package_rejects_non_callable(self):
        with pytest.raises(TypeError):
            Package(123)

    def test_package_rejects_none(self):
        with pytest.raises(TypeError):
            Package(None)

    # `@unittest.expectedFailure` -> `@pytest.mark.xfail(strict=True)`. STRICT IS REQUIRED:
    # unittest reports an unexpected PASS as "unexpected success" and FAILS the run; bare
    # @pytest.mark.xfail reports XPASS and leaves the run green, and pyproject sets no
    # xfail_strict. Without strict this stops reporting the very thing it exists to catch -
    # Package silently starting to accept a coroutine it is supposed to reject.
    @pytest.mark.xfail(strict=True)
    def test_package_rejects_coroutine(self):
        async def coro(): pass
        with pytest.raises(TypeError):
            Package(coro)

    def test_package_rejects_generator(self):
        def gen(): yield
        with pytest.raises(TypeError):
            Package(gen)

    # --- Handling Multiple Functions ---
    def test_pack_many_single_function(self):
        out = Package._pack_many([lambda x: x + 1])
        assert len(out) == 1
        assert isinstance(out[0], Package)
        assert out[0](5) == 6

    def test_pack_many_multiple_functions(self):
        out = Package._pack_many([lambda x: x + 1, lambda x: x * 2])
        assert len(out) == 2
        assert isinstance(out[0], Package)
        assert isinstance(out[1], Package)
        assert out[0](5) == 6
        assert out[1](5) == 10

    def test_pack_many_with_mixed_types(self):
        p1 = Package(lambda x: x + 1)
        p2 = lambda x: x * 2
        result = Package._pack_many([p1, p2])
        assert len(result) == 2
        assert isinstance(result[0], Package)
        assert isinstance(result[1], Package)
        assert result[0](5) == 6
        assert result[1](5) == 10

    # --- Composability ---
    def test_pipeline_basic(self):
        p1 = Package(lambda x: x + 1)
        p2 = Package(lambda x: x * 2)
        p3 = p1 | p2
        assert p3(3) == 8 # (3 + 1) * 2 = 8

    def test_pipeline_chain(self):
        p1 = Package(lambda x: x + 1)
        p2 = Package(lambda x: x * 2)
        p3 = p1 | p2 | Package(lambda x: x - 3)
        assert p3(3) == 5 # ((3 + 1) * 2) - 3 = 5

    def test_addition_operator(self):
        p1 = Package(lambda x: x + 1)
        p2 = Package(lambda x: x * 2)
        added = p1 + p2
        assert added(3) == 10  # (3 + 1) + (3 * 2) = 4 + 6 = 10

    def test_merge_many_basic(self):
        p1 = Package(lambda x: x + 1)
        p2 = Package(lambda x: x * 2)
        combo = Package.merge_many([p1, p2])
        assert combo(3) == 8 # p2(p1(3)) => (3 + 1) * 2 = 8

    # --- Thread Safety ---
    def test_parallel_calls_do_not_corrupt_state(self):
        p = Package(delayed_add, 1, 2)
        results = []

        def worker():
            results.append(p())

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads: t.start()
        for t in threads: t.join(timeout=15)

        assert results == [3] * 10

    def test_frozen_package_cannot_be_mutated(self):
        p = Package(delayed_add, 2, 3)
        p.freeze()

        def attempt_bind():
            # Runs on a worker thread, so a failure here cannot fail the test in either
            # framework. Pre-existing at the pin; preserved as-is.
            with pytest.raises(RuntimeError):
                p.bind(a=99)

        threads = [threading.Thread(target=attempt_bind) for _ in range(5)]
        for t in threads: t.start()
        for t in threads: t.join(timeout=15)

    # --- Curry and Bind Tests ---
    def test_curry_creates_new_instance(self):
        p = Package(_add, 2)
        curried_p = p.curry(3)
        assert p != curried_p
        assert curried_p() == 5
        assert p.args == (2,)

    def test_bind_mutates_kwargs(self):
        def power(base, exp): return base ** exp
        p = Package(power, 2, exp=3)
        p.bind(exp=4)
        assert p() == 16

    def test_signature_after_bind(self):
        def power(base, exp): return base ** exp
        p = Package(power, 2)
        assert p.signature.arguments["arg0"] == 2
        assert "exp" not in p.signature.arguments
        p.bind(exp=5)
        assert p.signature.arguments["exp"] == 5

    # `@unittest.skip(reason)` -> `@pytest.mark.skip(reason=...)`. The reason string is the ONLY
    # record of why this is off, so it is carried over verbatim rather than dropped. The test is
    # NOT re-enabled: activating a test that has never run in this state is a behaviour change,
    # not a port, and its 5 assertions stay counted either way.
    @pytest.mark.skip(reason="Skipping test for missing arguments fallback behavior")
    def test_fallback_behavior_for_missing_arguments(self):
        """
        Tests the special case where the Package class supplies `0` for missing arguments
        instead of raising a TypeError, which was the root cause of the BypassConductor failures.
        """

        # Test 1: Function requiring one argument gets 0.
        def needs_one(x):
            return x

        p1 = Pack(needs_one)
        # Should execute needs_one(0) instead of raising an error.
        assert p1() == 0

        # Test 2: Function requiring two arguments gets two 0s.
        def needs_two(a, b):
            return a + b

        p2 = Pack(needs_two)
        # Should execute needs_two(0, 0).
        assert p2() == 0

        # Test 3: One argument supplied, one missing.
        p3 = Pack(needs_two, 5)
        # Should execute needs_two(5, 0).
        assert p3() == 5

        # Test 4: Mixed required and default arguments.
        def mixed_req_default(x, y=10):
            return x * y

        p4 = Pack(mixed_req_default)
        # Should execute mixed_req_default(0, y=10).
        assert p4() == 0

        # Test 5: The fallback should NOT apply to missing keyword-only arguments.
        def needs_keyword_only(*, val):
            return val

        p5 = Pack(needs_keyword_only)
        # This SHOULD raise a TypeError because the fallback only handles positional args.
        with pytest.raises(TypeError):
            p5()

    def test_curry_with_new_params(self):
        p = Package(_add, 3)
        curried_p = p.curry(4)
        assert curried_p() == 7

    # --- Hashing and Equality ---
    def test_hash_consistency(self):
        p1 = Package(constant_value)
        p2 = Package(constant_value)
        assert hash(p1) == hash(p2)
        assert p1 == p2

    def test_inequality_after_binding(self):
        p1 = Package(_square, 2)
        p2 = Package(_square, 2)
        assert p1 == p2
        p2.bind(debug=True)
        assert p1 != p2

    def test_equality_after_mutation_and_reversal(self):
        # FIX: The test logic was changed to ensure a true state comparison.
        def func(a, b=1): return a + b
        # Start both packages in an identical, non-default state for a clear comparison.
        p1 = Package(func, 1).bind(b=10)
        p2 = Package(func, 1).bind(b=20) # Start p2 in a different state.
        assert p1 != p2

        # Mutate p2 back to the original state of p1.
        p2.bind(b=10)
        assert p1 == p2

    def test_addition_operator_after_bind(self):
        p1 = Package(lambda x: x + 1)
        p2 = Package(lambda x, y: x * y)
        p2.bind(y=3)
        p3 = p1 + p2
        assert p3(5) == 21 # (5 + 1) + (5 * 3) = 6 + 15 = 21

if __name__ == "__main__":
    pytest.main([__file__])
