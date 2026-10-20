"""S7: re-point src_architecture's numeric citations into the files the managed lane changed (conduit.py,
spellbook.py, aether.py, bind.py) at the code they name, remeasured on 0.2.8246. Historical handoff entries keep
their wording. Every replacement is exact and counted.

Run from the repository root: python s7_docs_architecture_citations.py
"""
import pathlib

DOC = pathlib.Path("context_compass/system_docs/src_architecture.md")
text = DOC.read_text(encoding="utf-8")
edits = [
    ("same thing and are also wrong - see `src/melder/aether/spellbook/spellbook.py:3742`, which states the",
     "same thing and are also wrong - see `src/melder/aether/spellbook/spellbook.py:3811-3813`, which states the"),
    ("  - src/melder/aether/conduit/conduit.py:5347, 5419 (`notch_spell`; starts the transaction)\n",
     "  - src/melder/aether/conduit/conduit.py:5622, 5694 (`notch_spell`; starts the transaction)\n"),
    ("  - src/melder/aether/conduit/conduit.py:5437, 5492 (`add_to_spell_index`; starts it)\n",
     "  - src/melder/aether/conduit/conduit.py:5712, 5767 (`add_to_spell_index`; starts it)\n"),
    ("  - src/melder/aether/conduit/conduit.py:5515, 5563 (`remove_from_spell_index`; starts it)\n",
     "  - src/melder/aether/conduit/conduit.py:5790, 5838 (`remove_from_spell_index`; starts it)\n"),
    ("  - src/melder/aether/spellbook/spellbook.py:3899 (`_add_to_spell_index` entry)\n",
     "  - src/melder/aether/spellbook/spellbook.py:3968 (`_add_to_spell_index` entry)\n"),
    ("  - src/melder/aether/spellbook/spellbook.py:3932 (`_apply_add_to_index` seam)\n",
     "  - src/melder/aether/spellbook/spellbook.py:4001 (`_apply_add_to_index` seam)\n"),
    ("EVIDENCE: src/melder/aether/spellbook/spellbook.py:3757-4192 (the three seams, remeasured 2026-09-30);",
     "EVIDENCE: src/melder/aether/spellbook/spellbook.py:3826-4261 (the three seams, remeasured 2026-10-15);"),
    ("`src/melder/aether/spellbook/bind/bind.py:657` (in `Bind._bind_logic`) -",
     "`src/melder/aether/spellbook/bind/bind.py:713` (in `Bind._bind_logic`) -"),
    ("   - src/melder/aether/spellbook/spellbook.py:3757-3897\n", "   - src/melder/aether/spellbook/spellbook.py:3826-3966\n"),
    ("   - src/melder/aether/spellbook/spellbook.py:3932-4026\n", "   - src/melder/aether/spellbook/spellbook.py:4001-4095\n"),
    ("   - src/melder/aether/spellbook/spellbook.py:4107-4192\n", "   - src/melder/aether/spellbook/spellbook.py:4176-4261\n"),
    ("   - src/melder/aether/conduit/conduit.py:5461-5549\n", "   - src/melder/aether/conduit/conduit.py:5622-5710\n"),
    ("   - src/melder/aether/conduit/conduit.py:5746-5775\n", "   - src/melder/aether/conduit/conduit.py:5907-5936\n"),
    ("  - src/melder/aether/conduit/conduit.py:5296-5298 (the check and the raise -",
     "  - src/melder/aether/conduit/conduit.py:5571-5573 (the check and the raise -"),
    ("  - src/melder/aether/aether.py:116 (`_instance` class slot)\n",
     "  - src/melder/aether/aether.py:120 (`_instance` class slot)\n"),
    ("  - src/melder/aether/aether.py:130-134 (double-checked construction)\n",
     "  - src/melder/aether/aether.py:134-138 (double-checked construction)\n"),
    ("  - src/melder/aether/aether.py:245-251 (identity-checked rollback when construction fails)\n",
     "  - src/melder/aether/aether.py:260-266 (identity-checked rollback when construction fails)\n"),
    ("  - src/melder/aether/aether.py:278-282, 323-332 (cleanup's `_cleaned` return; the unconditional reset)\n",
     "  - src/melder/aether/aether.py:296-300, 347-356 (cleanup's `_cleaned` return; the unconditional reset)\n"),
    ("  - src/melder/aether/spellbook/spellbook.py:267 (`_conjured` initialised)\n",
     "  - src/melder/aether/spellbook/spellbook.py:269 (`_conjured` initialised)\n"),
    ("  - src/melder/aether/spellbook/spellbook.py:704 (ownership check reads it)\n",
     "  - src/melder/aether/spellbook/spellbook.py:706 (ownership check reads it)\n"),
    ("  - src/melder/aether/spellbook/spellbook.py:762 (deleted on cleanup)\n",
     "  - src/melder/aether/spellbook/spellbook.py:764 (deleted on cleanup)\n"),
    ("  - src/melder/aether/spellbook/spellbook.py:6612-6655\n"
     "    (`Spellbook._settle_or_inherit_conjure_mode`; in-place settle :6546-6558,\n"
     "    effective-mode return :6559; remeasured 2026-09-30 at 0.2.8215)\n",
     "  - src/melder/aether/spellbook/spellbook.py:6788-6831\n"
     "    (`Spellbook._settle_or_inherit_conjure_mode`; in-place settle :6818-6830,\n"
     "    effective-mode return :6831; remeasured 2026-10-15 at 0.2.8246)\n"),
    ("  - src/melder/aether/spellbook/spellbook.py:6868\n", "  - src/melder/aether/spellbook/spellbook.py:7044\n"),
]
for old, new in edits:
    assert text.count(old) == 1, old[:100]
    text = text.replace(old, new)
DOC.write_text(text, encoding="utf-8")
print("re-pointed", len(edits), "citations")
