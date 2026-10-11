"""
Write gen_classes_t.py (4000 module-level classes T0..T3999) next to this script; c2_spell_ids_read_stress.py's
conjure mode binds one per new Book. Generated on demand rather than kept, to keep the evidence folder small.

Usage: python make_gen_classes_t.py
"""
import pathlib

lines = ['"""Module-level classes for the conjure-preflight stress (one distinct class per Book C)."""', ""]
for i in range(4000):
    lines += ["", f"class T{i}:", f'    """Distinct spell T{i}."""', "", "    def __init__(self) -> None:",
              f"        self.value = {i}", ""]
(pathlib.Path(__file__).parent / "gen_classes_t.py").write_text("\n".join(lines) + "\n", encoding="utf-8")
