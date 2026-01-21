"""
Lambda scan_bind mock module for integration tests.

Defines a scan_bind-decorated lambda with explicit binding name.
"""
from melder.spellbook.bind.scan import scan_bind
from melder.spellbook.existence.existence import Existence

LAMBDA_CALLS: list[str] = []


def reset_lambda_calls() -> None:
    """
    Purpose:
        Reset lambda call tracking for integration tests.
    Contract:
        Clears the LAMBDA_CALLS list in place.
    Returns:
        None.
    """
    LAMBDA_CALLS.clear()


def _record_lambda_call() -> object:
    """
    Purpose:
        Record a lambda invocation and return a new object.
    Contract:
        Appends a marker to LAMBDA_CALLS and returns a new object instance.
    Returns:
        object: A new object instance.
    """
    LAMBDA_CALLS.append("called")
    return object()


decorated_lambda = scan_bind(
    existence=Existence.unique,
    permissions="create",
    spellframe="scan_lambda",
    binding_name="lambda_factory",
)(lambda: _record_lambda_call())
