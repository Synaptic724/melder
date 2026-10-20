"""S7 follow-up to s7_docs_tests.py: the meld door's method is `meld_existing_spell` (conduit_meld.py:733).

Run from the repository root: python context_compass/artifacts/managed_spell_quantity_20261015/scripts/s7_docs_tests_fix.py
"""
import pathlib

DOC = pathlib.Path("context_compass/system_docs/tests_components.md")
text = DOC.read_bytes().decode("utf-8")
old = "spell, `meld_existing` refuses it, and both live probes"
assert text.count(old) == 1, text.count(old)
text = text.replace(old, "spell, `meld_existing_spell` refuses it, and both live probes")
DOC.write_bytes(text.encode("utf-8"))
print("fixed: meld_existing_spell")
