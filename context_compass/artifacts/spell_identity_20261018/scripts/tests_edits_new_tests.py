"""melder_0, 2026-10-18: the batch `new_tests` of tests_apply_s1_s2.py - the three new test modules no other batch
copies.

test_spell_code_digest.py (batch bind), test_spell_crystal_binding_hash.py (batch doubles) and the support module
(batches one_object_a and one_object_b) are copied by their batches; these three are copied here, from the staged
folder: the binding manifest's unit tests, decision B's digest tests (installed code named by version) and the
component test of spell identity.
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tests_apply_s1_s2 import TestApplier

MANIFEST_TEST = "tests/unit/melder/spellbook/bind/test_binding_manifest.py"
LIBRARIES_TEST = "tests/unit/melder/spellbook/bind/test_spell_code_digest_libraries.py"
IDENTITY_TEST = "tests/component/melder/spellbook/test_spellbook_component_spell_identity.py"


def apply(applier: "TestApplier") -> None:
    """Copy the binding manifest's unit tests, decision B's digest tests and the component test of spell identity."""
    applier.copy(MANIFEST_TEST)
    applier.copy(LIBRARIES_TEST)
    applier.copy(IDENTITY_TEST)
