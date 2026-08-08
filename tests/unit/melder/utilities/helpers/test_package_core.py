import math
from functools import partial
from melder.utilities.helpers.package import Package, Pack
import pytest
import threading
import time


def _square(x):          # Helper functions used in several tests
    return x * x


def _add(a, b):
    return a + b


def delayed_add(a, b):
    time.sleep(0.01)
    return a + b


def constant_value():
    return 42


# FOUR @unittest.expectedFailure sites in this file -> @pytest.mark.xfail(strict=True).
# STRICT IS REQUIRED (defect 14): unittest reports an unexpected PASS as "unexpected success" and
# FAILS the run; bare @pytest.mark.xfail reports XPASS and leaves the run GREEN, and pyproject
# sets no xfail_strict. Every one of these four pins a rejection Package is supposed to perform
# but currently does not - exactly the case that must shout if it ever starts working.
class TestPackageThreadSafety:
    def test_parallel_calls_do_not_corrupt_state(self):
        """Ensure multiple threads calling the same Package do not conflict."""
        p = Package(delayed_add, 1, 2)
        results = []

        def worker():
            results.append(p())

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads: t.start()
        for t in threads: t.join(timeout=15)

        assert results == [3] * 10
        p.cleanup()

    def test_concurrent_binding_raises_on_frozen(self):
        """Ensure that frozen Package cannot be mutated in any thread."""
        p = Package(delayed_add, 2, 3)
        p.freeze()

        def attempt_bind():
            # Worker-thread assertion: cannot fail the test in either framework. Pre-existing.
            with pytest.raises(RuntimeError):
                p.bind(x=99)

        threads = [threading.Thread(target=attempt_bind) for _ in range(5)]
        for t in threads: t.start()
        for t in threads: t.join(timeout=15)
        p.cleanup()

    def test_normalize_task_accepts_package(self):
        p = Package(_add, 1, 2)
        normalized = Package._normalize_task(p)
        assert normalized(3, 4) == 7
        p.cleanup()

    def test_normalize_task_accepts_callable(self):
        fn = lambda x: x + 1
        normalized = Package._normalize_task(fn)
        assert normalized(4) == 5

    def test_normalize_task_rejects_none(self):
        with pytest.raises(TypeError):
            Package._normalize_task(None)

    @pytest.mark.xfail(strict=True)
    def test_normalize_task_rejects_coroutines(self):
        async def coro(): pass

        with pytest.raises(TypeError):
            Package._normalize_task(coro)

    def test_normalize_task_rejects_generators(self):
        def gen(): yield 1

        with pytest.raises(TypeError):
            Package._normalize_task(gen)

    def test_validate_callable_valid_function(self):
        p = Package(lambda x: x + 1)  # should not raise
        assert isinstance(p, Package)
        p.cleanup()

    def test_validate_callable_invalid_type(self):
        with pytest.raises(TypeError):
            Package(123)

    def test_validate_callable_is_none(self):
        with pytest.raises(TypeError):
            Package(None)

    @pytest.mark.xfail(strict=True)
    def test_validate_callable_rejects_coroutines(self):
        async def fake(): pass

        with pytest.raises(TypeError):
            Package(fake)

    def test_validate_callable_rejects_generators(self):
        def bad(): yield 1

        with pytest.raises(TypeError):
            Package(bad)

    def test_normalize_many_single_callable(self):
        out = Package._normalize_many(_square)
        assert len(out) == 1
        assert isinstance(out[0], Package)
        out[0].cleanup()


    def test_normalize_many_single_package(self):
        p = Package(_square)
        out = Package._normalize_many(p)
        assert out[0] == p
        p.cleanup()


    def test_normalize_many_rejects_none(self):
        with pytest.raises(TypeError):
            Package._normalize_many(None)

    def test_normalize_many_rejects_non_iterable_non_callable(self):
        with pytest.raises(TypeError):
            Package._normalize_many(1234)

    @pytest.mark.xfail(strict=True)
    def test_normalize_many_rejects_coroutine_in_iterable(self):
        async def bad(): pass

        with pytest.raises(TypeError):
            Package._normalize_many([_add, bad])

    def test_normalize_many_rejects_generator_in_iterable(self):
        def gen(): yield

        with pytest.raises(TypeError):
            Package._normalize_many([_add, gen])

    def test_normalize_many_valid_list_mixed_packages_and_funcs(self):
        items = [_add, Package(_square, 4)]
        out = Package._normalize_many(items)
        assert len(out) == 2
        assert all(isinstance(p, Package) for p in out)
        for p in out:
            p.cleanup()


    # ─────────────────────── helpers: is_valid_callable ─────────────────────── #
    def test_is_valid_callable_with_function(self):
        p = Package(lambda x: x + 1)
        assert isinstance(p, Package)
        p.cleanup()


    @pytest.mark.xfail(strict=True)
    def test_is_valid_callable_with_package(self):
        p = Package(len)
        # This is expected to fail because you cannot wrap a Package in another Package.
        try:
            Package(p)
        finally:
            p.cleanup()


    # ───────────────────────────── helpers: ensure ──────────────────────────── #
    def test_ensure_returns_package_on_valid_callable(self):
        out = Package(abs)
        assert isinstance(out, Package)
        out.cleanup()

    # ───────────────────────────── helpers: safe ────────────────────────────── #
    def test_safe_wraps_callable(self):
        wrapped = Package(sum)
        assert isinstance(wrapped, Package)
        wrapped.cleanup()

    # ───────────────────────── helper: from_partial ─────────────────────────── #
    def test_from_partial_creates_curried_package(self):
        # partial is not a method on Package, but we can test creating a Package from a partial
        p_partial = partial(pow, 2, 3)
        p = Package(p_partial)
        assert p() == 8
        p.cleanup()

    # ─────────────────────────── helper: merge_many ──────────────────────────── #
    def test_merge_many_basic_pipeline(self):
        p1 = Package(lambda x: x + 1)
        p2 = Package(lambda x: x * 2)
        combo = Package.merge_many([p1, p2])  # (x + 1) * 2
        assert combo(3) == 8
        p1.cleanup()
        p2.cleanup()
        combo.cleanup()


    def test_merge_many_requires_at_least_one(self):
        with pytest.raises(ValueError):
            Package.merge_many([])

    def test_merge_many_rejects_non_package(self):
        p1 = Package(abs)
        with pytest.raises(TypeError):
            Package.merge_many([p1, 123])
        p1.cleanup()

    def test_merge_many_chains_three(self):
        p1 = Package(lambda x: x + 1)
        p2 = Package(lambda x: x * 2)
        p3 = Package(lambda x: x - 3)
        combo = Package.merge_many([p1, p2, p3])  # ((x+1)*2) -3
        assert combo(4) == 7  # 7 is the correct result
        p1.cleanup()
        p2.cleanup()
        p3.cleanup()
        combo.cleanup()

    # ---------------------------------------------------------------------------
    #  Add these into your TestPackage class (or a new TestPackageHelpers class).
    #  They assume `Package` has the five helper methods we just added.
    # ---------------------------------------------------------------------------

    def test_signature_updates_after_multiple_binds(self):
        p = Package(pow, 2)
        _ = p.signature
        p.bind(exp=3)
        assert p.signature.arguments["exp"] == 3
        p.bind(exp=5)
        assert p.signature.arguments["exp"] == 5
        p.cleanup()

    def test_signature_with_args_and_kwargs(self):
        p = Package(pow, 2, exp=3)
        sig = p.signature.arguments
        assert sig["arg0"] == 2
        assert sig["exp"] == 3
        p.cleanup()

    def test_bind_threadsafe_multiple_threads(self):
        p = Package(_add, 1)
        threads = []

        def do_bind():
            for i in range(3):
                p.bind(debug=True)

        for _ in range(4):
            t = threading.Thread(target=do_bind)
            threads.append(t)
            t.start()

        for t in threads:
            t.join(timeout=15)

        assert p.kwargs["debug"] == True
        p.cleanup()

    def test_repr_works_when_func_is_lambda(self):
        p = Package(lambda x: x)
        assert "lambda" in repr(p)
        p.cleanup()

    def test_signature_cache_shared_safely(self):
        """Ensure the signature property is thread-safe and consistent."""
        p = Package(delayed_add, 5, 7)
        signatures = []

        def read_signature():
            for _ in range(10):
                sig = p.signature.arguments.copy()
                signatures.append(sig)

        threads = [threading.Thread(target=read_signature) for _ in range(5)]
        for t in threads: t.start()
        for t in threads: t.join(timeout=15)

        for sig in signatures:
            assert sig["arg0"] == 5
            assert sig["arg1"] == 7
        p.cleanup()

    def test_curry_creates_distinct_instances(self):
        """Ensure curry results in new thread-safe Packages."""
        base = Package(delayed_add, 1)

        def curried_worker(results):
            curried = base.curry(9)
            results.append(curried())

        results = []
        threads = [threading.Thread(target=curried_worker, args=(results,)) for _ in range(5)]
        for t in threads: t.start()
        for t in threads: t.join(timeout=15)

        assert results == [10] * 5
        base.cleanup()


    def test_hash_consistency_multithreaded(self):
        """Ensure hash() remains consistent across threads and never throws."""
        p = Package(constant_value)

        def read_hash(hashes):
            for _ in range(10):
                hashes.append(hash(p))

        hashes = []
        threads = [threading.Thread(target=read_hash, args=(hashes,)) for _ in range(4)]
        for t in threads: t.start()
        for t in threads: t.join(timeout=15)

        unique_hashes = set(hashes)
        assert len(unique_hashes) == 1
        p.cleanup()


class TestPackage:
    # ─────────────────────────── construction ─────────────────────────── #
    def test_ctor_valid(self):
        p = Package(_square, 3)
        assert isinstance(p, Package)
        p.cleanup()

    def test_ctor_rejects_non_callable(self):
        with pytest.raises(TypeError):
            Package(123)

    # ───────────────────────────── __call__ ───────────────────────────── #
    def test_call_without_extra_args(self):
        p = Package(_square, 4)
        assert p() == 16
        p.cleanup()

    def test_call_with_extra_args(self):
        p = Package(_add, 2)
        assert p(5) == 7
        p.cleanup()

    def test_call_with_extra_kwargs(self):
        def foo(a, b=0):
            return a - b
        p = Package(foo, 10)
        assert p(b=4) == 6
        p.cleanup()

    # ────────────────────────── attribute access ──────────────────────── #
    def test_getattr_fallback(self):
        p = Package(math.sqrt)
        # math.sqrt.__name__ exists – should be exposed via __getattr__
        assert p.__name__ == "sqrt"
        p.cleanup()

    # ─────────────────────── args / kwargs storage ─────────────────────── #
    def test_args_property(self):
        p = Package(_add, 1, 2)
        assert p.args == (1, 2)
        p.cleanup()

    def test_kwargs_property(self):
        p = Package(pow, 2, exp=3)
        assert p.kwargs == {"exp": 3}
        p.cleanup()

    # ──────────────────────────── __repr__ ────────────────────────────── #
    def test_repr_contains_func_name(self):
        p = Package(_square, 5)
        assert "_square" in repr(p)
        p.cleanup()

    # ───────────────────────── equality / hashing ─────────────────────── #
    def test_equality_same_content(self):
        p1 = Package(_square, 3)
        p2 = Package(_square, 3)
        assert p1 == p2
        assert hash(p1) == hash(p2)
        p1.cleanup()
        p2.cleanup()

    def test_inequality_different_args(self):
        p1 = Package(_square, 2)
        p2 = Package(_square, 3)
        assert p1 != p2
        p1.cleanup()
        p2.cleanup()

    def test_hashability_in_set(self):
        p1 = Package(_square, 2)
        p2 = Package(_square, 2)
        s = {p1, p2}
        assert len(s) == 1
        p1.cleanup()
        p2.cleanup()

    # ──────────────────────────── pipeline (|) ─────────────────────────── #
    def test_pipeline_basic(self):
        p1 = Package(_square, 3)
        p2 = Package(_square)
        p = p1 | p2
        assert p() == 81
        p1.cleanup()
        p2.cleanup()
        p.cleanup()


    def test_pipeline_chains_three(self):
        p1 = Package(_square, 2)
        p2 = Package(_square)
        p3 = Package(lambda x: x + 1)
        triple = p1 | p2 | p3
        assert triple() == 17 # (2**2)**2 + 1 = 16 + 1 = 17
        p1.cleanup()
        p2.cleanup()
        p3.cleanup()
        triple.cleanup()

    def test_pipeline_type_safety(self):
        p1 = Package(_square, 2)
        with pytest.raises(TypeError):
            _ = p1 | 123  # not a Package
        p1.cleanup()

    # ─────────────────────────── addition (+) ─────────────────────────── #
    def test_addition_results(self):
        p1 = Package(int, "5")
        p2 = Package(int, "7")
        p = p1 + p2
        assert p() == 12
        p1.cleanup()
        p2.cleanup()
        p.cleanup()

    def test_addition_propogates_args(self):
        inc = Package(lambda x: x + 1)
        dbl = Package(lambda x: x * 2)
        combo = inc + dbl
        assert combo(3) == 10  # (3+1) + (3*2)
        inc.cleanup()
        dbl.cleanup()
        combo.cleanup()

    def test_addition_type_safety(self):
        p1 = Package(_square, 2)
        with pytest.raises(TypeError):
            _ = p1 + "not-a-package"
        p1.cleanup()

    # ───────────────────── bind / curry helpers ───────────────────────── #
    def test_bind_mutates_kwargs(self):
        p = Package(pow, 2, exp=3)
        p.bind(exp=4)
        assert p() == 16  # 2**4
        p.cleanup()

    def test_curry_returns_new_instance(self):
        p1 = Package(_add, 1)
        p2 = p1.curry(4)

        assert p1 is not p2

        # `as cm` carries over; the ATTRIBUTE does not - unittest's cm.exception is pytest's
        # cm.value. Kept as a substring check on str(...) rather than folded into match=,
        # because match= is a REGEX and this literal contains quotes and a colon.
        with pytest.raises(TypeError) as cm:
            p1()
        assert "missing 1 required positional argument: 'b'" in str(cm.value)

        assert p2() == 5
        p1.cleanup()
        p2.cleanup()

    def test_signature_includes_bound_args(self):
        p = Package(_add, 10)
        sig = p.signature
        assert sig.arguments["arg0"] == 10
        p.cleanup()

    def test_signature_cache_clears_on_bind(self):
        p = Package(pow, 2)
        _ = p.signature             # populate cache
        p.bind(exp=5)
        assert p.signature.arguments["exp"] == 5
        p.cleanup()

    # ───────────────────────── misc edge cases ─────────────────────────── #
    def test_func_with_varargs(self):
        def collect(*vals):
            return vals
        p = Package(collect, 1, 2)
        assert p(3, 4) == (1, 2, 3, 4)
        p.cleanup()

    def test_func_with_varkw(self):
        def kw(**d):
            return d
        p = Package(kw, a=1)
        assert p(b=2) == {"a": 1, "b": 2}
        p.cleanup()

    def test_zero_arg_function(self):
        p = Package(lambda: 123)
        assert p() == 123
        p.cleanup()

    def test_repeated_curry(self):
        p1 = Package(_add, 1)
        p2 = p1.curry(2)
        p3 = p2.curry()  # second curry no args
        assert p3() == 3
        p1.cleanup()
        p2.cleanup()
        p3.cleanup()

    def test_repr_roundtrip_eval(self):
        p = Package(_square, 6)
        # eval(repr(p)) won't work automatically, but repr shouldn't raise
        assert isinstance(repr(p), str)
        p.cleanup()

    def test_attribute_passthrough_dir(self):
        p = Package(math.sin)
        assert "__call__" in dir(p)  # from Package
        assert "__name__" in dir(p)  # from wrapped func
        p.cleanup()

    def test_pipeline_preserves_extra_call_args(self):
        add1 = Package(lambda x: x + 1)
        dbl = Package(lambda x: x * 2)
        pipeline = (add1 | dbl)
        assert pipeline(5) == 12
        add1.cleanup()
        dbl.cleanup()
        pipeline.cleanup()

    def test_addition_preserves_kwargs(self):
        def foo(x, bonus=0):
            return x + bonus
        p1 = Package(foo, bonus=2)
        p2 = Package(foo, bonus=3)
        p = p1 + p2
        assert p(10) == 25 # (10+2) + (10+3) = 25
        p1.cleanup()
        p2.cleanup()
        p.cleanup()

    def test_hash_equality_after_bind(self):
        p1 = Package(_square, 4)
        p2 = Package(_square, 4)
        assert hash(p1) == hash(p2)

        # MIGRATION NOTE: this asserted the hash CHANGED after bind(). Hashing now
        # latches `_frozen`, so binding after a hash raises instead. A Package
        # whose hash moves under a dict key can never be found again; freezing at
        # the moment it becomes a key is what makes set/dict membership coherent.
        with pytest.raises(RuntimeError):
            p2.bind(debug=True)

        # Both were hashed above, so both are frozen and still equal.
        assert hash(p1) == hash(p2)

        # Binding before any hash is still allowed.
        p3 = Package(_square, 4)
        p3.bind(debug=True)
        assert hash(p3) != hash(p1)

        p1.cleanup()
        p2.cleanup()
        p3.cleanup()

    def test_using_partial_directly(self):
        p = Package(partial(_add, 2), 3)
        assert p() == 5
        p.cleanup()

    def test_callable_object_instance(self):
        class Mult:
            def __init__(self, factor):
                self.factor = factor
            def __call__(self, x):
                return x * self.factor
        mul3 = Mult(3)
        p = Package(mul3, 7)
        assert p() == 21
        p.cleanup()

    def test_fallback_getattr_magic(self):
        p = Package(len)
        assert callable(p.__call__)
        p.cleanup()

    def test_eq_handles_non_package(self):
        p = Package(len)
        assert p != 123
        p.cleanup()

    def test_package_is_hashable_after_curry(self):
        p = Package(int, "10")
        p2 = p.curry(20)  # new package with different content
        d = {p: "ten", p2: "twenty"}
        assert len(d) == 2
        p.cleanup()
        p2.cleanup()

    def test_or_chain_with_add(self):
        inc = Package(lambda x: x + 1)
        dbl = Package(lambda x: x * 2)
        p3 = Package(lambda x: x - 3)
        combo = (inc | dbl) + p3
        assert combo(4) == (4 + 1) * 2 + (4 - 3)  # → 10 + 1 = 11
        inc.cleanup()
        dbl.cleanup()
        p3.cleanup()
        combo.cleanup()

    def test_signature_after_curry(self):
        p = Pack(pow, 2)
        q = p.curry(5)
        assert q.signature.arguments["arg0"] == 2
        assert q.signature.arguments["arg1"] == 5
        p.cleanup()
        q.cleanup()

    def test_bind_returns_self(self):
        p = Package(str.upper, "hi")
        assert p.bind() is p  # bind with no kwargs returns same obj
        p.cleanup()

if __name__ == "__main__":
    pytest.main([__file__])
