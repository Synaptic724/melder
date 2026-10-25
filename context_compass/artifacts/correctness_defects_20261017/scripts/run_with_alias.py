"""Run a probe written before 0.2.8253 renamed Spellbook.find_spell_by_id, with the old name aliased (melder_1)."""
import runpy
import sys

from melder.aether.spellbook.spellbook import Spellbook

Spellbook.find_spell_by_id = Spellbook.find_spell_by_spell_id
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name="__main__")
