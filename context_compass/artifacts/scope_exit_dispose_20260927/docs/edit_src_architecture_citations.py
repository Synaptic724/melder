"""Remap the src_architecture.md citations that the 0.2.8203 change set moved (second pass).

conduit.py (notch/add/remove verbs, the link isinstance check) and aetheric_frame.py (the unfrozen
branch of bind_frame_configuration) grew; the ranges are re-found by symbol. The branch's copy count is
recounted from the source (fourteen values; the text said twelve and six disable flags).
Usage: python edit_src_architecture_citations.py <doc path>
"""
import pathlib
import sys

doc = pathlib.Path(sys.argv[1])
text = doc.read_bytes().decode("utf-8")


def swap(old: str, new: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"anchor found {count} times:\n{old}")
    text = text.replace(old, new)


swap("  - src/melder/aether/conduit/conduit.py:5075, 5147 (`notch_spell`; starts the transaction)\n",
     "  - src/melder/aether/conduit/conduit.py:5280, 5352 (`notch_spell`; starts the transaction)\n")
swap("  - src/melder/aether/conduit/conduit.py:5165, 5220 (`add_to_spell_index`; starts it)\n",
     "  - src/melder/aether/conduit/conduit.py:5370, 5425 (`add_to_spell_index`; starts it)\n")
swap("  - src/melder/aether/conduit/conduit.py:5243, 5291 (`remove_from_spell_index`; starts it)\n",
     "  - src/melder/aether/conduit/conduit.py:5448, 5496 (`remove_from_spell_index`; starts it)\n")
swap("  - src/melder/aether/conduit/conduit.py:5024-5026 (the check and the raise -\n",
     "  - src/melder/aether/conduit/conduit.py:5229-5231 (the check and the raise -\n")
swap(
    "    DIFFERENT object while the existing posture is unfrozen, it copies TWELVE\n"
    "    attempted values onto the canonical posture - system_state, ai_native,\n"
    "    rift_enabled, shared_framewide_spellbook_configuration, all six `disable_*`\n"
    "    flags, and max_transaction_wait_time_in_seconds - and then calls\n",
    "    DIFFERENT object while the existing posture is unfrozen, it copies FOURTEEN\n"
    "    attempted values onto the canonical posture - system_state, ai_native,\n"
    "    rift_enabled, shared_framewide_spellbook_configuration, the two caching\n"
    "    settings, all seven `disable_*` flags, and\n"
    "    max_transaction_wait_time_in_seconds (recounted 2026-09-27; this said twelve,\n"
    "    with six disable flags) - and then calls\n",
)
swap(
    "  - src/melder/aether/aetheric_frame/aetheric_frame.py:645-694\n"
    "    (`bind_frame_configuration` unfrozen branch: the twelve-value copy plus\n",
    "  - src/melder/aether/aetheric_frame/aetheric_frame.py:691-752\n"
    "    (`bind_frame_configuration` unfrozen branch: the fourteen-value copy plus\n",
)
doc.write_bytes(text.encode("utf-8"))
print("edited", doc, len(text.splitlines()))
