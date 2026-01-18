"""
Re-export scan_bind mock module for integration tests.

Re-exports a decorated object from another module to trigger re-export checks.
"""
from tests.mocks.spellbook.scan_bind_module_core import ScanCoreAlpha

ReexportedAlpha = ScanCoreAlpha
