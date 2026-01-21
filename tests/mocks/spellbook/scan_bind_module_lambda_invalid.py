"""
Invalid lambda scan_bind mock module for integration tests.

Defines a scan_bind-decorated lambda without a binding name to trigger
binding validation errors.
"""
from melder.spellbook.bind.scan import scan_bind
from melder.spellbook.existence.existence import Existence

invalid_lambda = scan_bind(
    existence=Existence.unique,
    permissions="create",
    spellframe="scan_lambda_invalid",
)(lambda: "invalid")
