"""Regression tests for 2026-07-17 audit findings BUG-266..BUG-269 in
`melder.utilities.helpers.package.Package`.

Each test is a minimal reproduction of the reported symptom and asserts the
corrected behavior.
"""

import pytest

from melder.utilities.helpers.package import Package


def _add(x, b=0):
    return x + b


def test_bug266_hash_membership_stable_after_set_insertion():
    # Hashing freezes the package, so membership stays stable and later binding
    # mutation is rejected instead of silently changing the hash.
    package = Package(_add, 1)
    seen = {package}
    assert package in seen
    with pytest.raises(RuntimeError):
        package.bind_args(2)
    assert package in seen


def test_bug267_normalize_many_preserves_existing_package_bindings():
    bound = Package(_add, 1).bind(b=2)
    normalized = Package._normalize_many(bound)
    assert normalized[0] is bound
    assert normalized[0]() == 3


def test_bug268_frozen_kwargs_accessor_returns_a_copy():
    package = Package(_add, 1).bind(b=2)
    _ = package.signature.arguments  # populate the signature cache
    package.freeze()
    leaked = package.kwargs
    leaked["b"] = 8
    assert package() == 3
    assert package.signature.arguments.get("b") == 2


def test_bug269_operations_after_cleanup_raise_canonical_runtimeerror():
    package = Package(_add, 1)
    package.cleanup()
    with pytest.raises(RuntimeError):
        package.unpack()
    with pytest.raises(RuntimeError):
        package()
    with pytest.raises(RuntimeError):
        repr(package)
