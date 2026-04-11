import asyncio

import pytest

from melder.utilities.helpers.package import Pack
from melder.utilities.helpers.package import Package


def _add(a: int, b: int = 0) -> int:
    """Add two integers."""
    return a + b


async def _async_add(a: int, b: int = 0) -> int:
    """Add two integers asynchronously."""
    return a + b


def _generator():
    yield 1


def test_package_rejects_invalid_constructor_inputs() -> None:
    """
    Purpose:
        Validate Package rejects unsupported constructor inputs.
    Contract:
        - Rejects existing Package instances.
        - Rejects non-callables.
        - Rejects generator functions.
    Returns:
        None.
    Raises:
        AssertionError: If invalid inputs are accepted.
    """
    base = Package(_add)

    with pytest.raises(TypeError, match="existing Package instance"):
        Package(base)

    with pytest.raises(TypeError, match="Expected callable"):
        Package._normalize_task(123)

    with pytest.raises(TypeError, match="Generator functions are not supported"):
        Package(_generator)


def test_package_sync_execution_describe_and_doc_surface() -> None:
    """
    Purpose:
        Validate the core sync Package execution and description surface.
    Contract:
        - __call__ executes synchronously with bound args.
        - execute_sync mirrors __call__ for sync packages.
        - describe exposes callable identity.
        - __doc__ proxies the wrapped callable docstring.
    Returns:
        None.
    Raises:
        AssertionError: If sync package behavior is incorrect.
    """
    package = Package(_add, 2).bind(b=3)

    assert package() == 5
    assert package.execute_sync() == 5
    assert package.is_async is False
    assert package.is_coroutine() is False
    assert package.__doc__ == _add.__doc__
    assert "_add" in package.describe()


def test_package_async_execution_surface() -> None:
    """
    Purpose:
        Validate async Package execution and coroutine access.
    Contract:
        - Async packages expose coroutine metadata.
        - execute_async awaits the wrapped coroutine.
        - execute_sync rejects async packages.
        - get_coroutine returns the wrapped async function.
    Returns:
        None.
    Raises:
        AssertionError: If async package behavior is incorrect.
    """
    package = Package(_async_add, 4).bind(b=5)

    assert package.is_async is True
    assert package.is_coroutine() is True
    assert package.get_coroutine() is _async_add
    assert asyncio.run(package.execute_async()) == 9

    with pytest.raises(TypeError, match="async"):
        package.execute_sync()


def test_package_execute_async_rejects_sync_packages() -> None:
    """
    Purpose:
        Validate execute_async rejects sync packages.
    Contract:
        Sync packages cannot be awaited through execute_async.
    Returns:
        None.
    Raises:
        AssertionError: If sync packages are accepted.
    """
    package = Package(_add, 1, 2)

    with pytest.raises(TypeError, match="sync"):
        asyncio.run(package.execute_async())


def test_package_bind_override_curry_signature_and_freeze() -> None:
    """
    Purpose:
        Validate Package argument mutation helpers and signature snapshotting.
    Contract:
        - bind_args replaces positional args.
        - bind merges kwargs.
        - override replaces both args and kwargs.
        - curry returns a new Package without mutating the original.
        - freeze blocks later argument mutation.
    Returns:
        None.
    Raises:
        AssertionError: If binding helpers behave incorrectly.
    """
    package = Package(_add, 1)
    package.bind(b=2)
    assert package() == 3
    assert package.args == (1,)
    assert package.kwargs == {"b": 2}
    assert package.signature.arguments == {"arg0": 1, "b": 2}

    package.bind_args(4)
    assert package() == 6
    assert package.args == (4,)

    package.override(7, b=8)
    assert package() == 15
    assert package.args == (7,)
    assert package.kwargs == {"b": 8}

    curried = package.curry(9)
    assert curried is not package
    assert package.args == (7,)
    assert curried.args == (7, 9)

    package.freeze()
    with pytest.raises(RuntimeError, match="frozen"):
        package.bind_args(1)
    with pytest.raises(RuntimeError, match="frozen"):
        package.bind(b=1)
    with pytest.raises(RuntimeError, match="frozen"):
        package.override(1, b=1)


def test_package_unpack_and_unpack_and_cleanup() -> None:
    """
    Purpose:
        Validate Package unpacking helpers.
    Contract:
        - unpack returns the original callable and detached argument snapshots.
        - unpack_and_cleanup returns the same data and marks the package cleaned.
    Returns:
        None.
    Raises:
        AssertionError: If unpack helpers are incorrect.
    """
    package = Package(_add, 2).bind(b=3)

    func, args, kwargs = package.unpack()
    assert func is _add
    assert args == (2,)
    assert kwargs == {"b": 3}

    func2, args2, kwargs2 = package.unpack_and_cleanup()
    assert func2 is _add
    assert args2 == (2,)
    assert kwargs2 == {"b": 3}
    assert package.cleaned is True


def test_package_composition_addition_and_merge_many() -> None:
    """
    Purpose:
        Validate Package composition helpers.
    Contract:
        - | composes left-to-right.
        - + adds results from two package executions.
        - merge_many composes multiple packages.
    Returns:
        None.
    Raises:
        AssertionError: If composition behavior is incorrect.
    """
    upper = Package(str.upper)
    first = Package(lambda value: f"a{value}")
    second = Package(lambda value: f"{value}b")

    pipeline = first | second | upper
    assert pipeline("x") == "AXB"

    add_left = Package(lambda value: value + 1)
    add_right = Package(lambda value: value + 2)
    assert (add_left + add_right)(3) == 9

    merged = Package.merge_many([first, second, upper])
    assert merged("x") == "AXB"


def test_package_bundle_verify_and_pack_helpers() -> None:
    """
    Purpose:
        Validate the static package normalization helpers.
    Contract:
        - bundle returns existing packages unchanged.
        - bundle wraps raw callables.
        - verify accepts packages and iterables of packages.
        - verify rejects non-packages.
    Returns:
        None.
    Raises:
        AssertionError: If normalization helpers are incorrect.
    """
    packaged = Package(_add)

    assert Package.bundle(packaged) is packaged
    wrapped = Package.bundle(_add)
    assert isinstance(wrapped, Package)

    many = Package.bundle([_add, packaged])
    assert isinstance(many, list)
    assert len(many) == 2
    assert all(isinstance(item, Package) for item in many)

    assert Package.verify(packaged) is True
    assert Package.verify([packaged, Package(_add)]) is True

    with pytest.raises(TypeError, match="Expected a Pack instance"):
        Package.verify(123)

    normalized = Package._normalize_many([_add, packaged])
    assert len(normalized) == 2
    assert isinstance(normalized[0], Package)
    assert normalized[1] is packaged


def test_package_equality_hash_repr_and_getattr_surface() -> None:
    """
    Purpose:
        Validate Package identity/introspection helpers.
    Contract:
        - Equality and hash depend on wrapped callable and bound args/kwargs.
        - __repr__ exposes callable name and bindings.
        - __getattr__ falls back to the wrapped callable object.
        - __dir__ includes wrapped-callable attributes.
    Returns:
        None.
    Raises:
        AssertionError: If identity or introspection behavior is incorrect.
    """
    left = Package(_add, 1).bind(b=2)
    same = Package(_add, 1).bind(b=2)
    different = Package(_add, 1).bind(b=3)

    assert left == same
    assert hash(left) == hash(same)
    assert left != different

    repr_text = repr(left)
    assert "Package" in repr_text
    assert "_add" in repr_text

    fallback = left.some_missing_attribute
    assert callable(fallback)
    assert fallback.__wrapped__ is _add
    assert "__wrapped__" in dir(left)


def test_pack_alias_matches_package() -> None:
    """
    Purpose:
        Validate the Pack alias remains usable.
    Contract:
        Pack is the Package class alias.
    Returns:
        None.
    Raises:
        AssertionError: If the alias diverges.
    """
    package = Pack(_add, 1, 2)
    assert isinstance(package, Package)
    assert package() == 3
