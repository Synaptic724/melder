"""S6 part A: record its tests in tests_components.md and tests_architecture.md (0.2.8254).

Run from the repository root:
  python context_compass/artifacts/correctness_defects_20261017/scripts/s6_docs_tests.py <NOW> [--dry-run]
Exact-once substitutions; code-map extents measured from disk; the inventory recounted by the caller (integration
180 `.py`, 173 `test_*.py`; three tiers 848); added lines over 120 characters refused.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from s6_docs_common import check_lines, insert_before, loc_of, remeasure, sub  # noqa: E402

NOW = sys.argv[1]
DRY = "--dry-run" in sys.argv
REPO = pathlib.Path(".")
COMP = REPO / "context_compass/system_docs/tests_components.md"
ARCH = REPO / "context_compass/system_docs/tests_architecture.md"
NEW_TEST = "tests/integration/melder/conduit/test_conduit_integration_managed_settings_rebind.py"

# ---------------------------------------------------------------- tests_components
original = COMP.read_text(encoding="utf-8")
t = original
t = sub(t, "- Updated: 2026-10-17\n", "- Updated: 2026-10-18\n")
t = sub(
    t,
    "- managed spells (0.2.8241-0.2.8246): the member and its Phase 6 rank, the bind options with their refusals and\n"
    "  ids, the pool in each mode, the release registry and the lease, the plans' managed sites and the owner stamp\n"
    "  through an ownership transfer (see `### Subcomponent: Managed Spell Pools Unit Cluster` and the spellbook\n"
    "  clusters)\n",
    "- managed spells (0.2.8241-0.2.8246, 0.2.8254): the member and its Phase 6 rank, the bind options with their\n"
    "  refusals and the ids they leave alone, the pool in each mode and its rebind, the release registry and the lease,\n"
    "  the plans' managed sites and the owner stamp through an ownership transfer (see\n"
    "  `### Subcomponent: Managed Spell Pools Unit Cluster` and the spellbook clusters)\n",
)
t = sub(
    t,
    "  binding names, notches, borrowers and lessers, the release registry, ownership transfers and a restored world\n"
    "  (see `### Subcomponent: Conduit Integration Cluster`)\n",
    "  binding names, notches, borrowers and lessers, the release registry, ownership transfers, a restored world and a\n"
    "  settings change that keeps one spell and pool (0.2.8254) (see `### Subcomponent: Conduit Integration Cluster`)\n",
)
t = sub(
    t,
    "  out to their holders; the pool keeps no reference to an object out\n"
    "- the pool under eight threads (`test_managed_spell_quantity_multithreaded.py`): limited_quantity 3 never has\n",
    "  out to their holders; the pool keeps no reference to an object out; a rebind (0.2.8254) with equal settings keeps\n"
    "  the band, and one with new settings takes a higher or smaller limit, a timeout and reset names, keeps every\n"
    "  object alive and counted under a smaller limit (the fixed capacity evicting the oldest idle object at later\n"
    "  releases), resizes the band from elastic to limited_quantity and back like a fresh pool, wakes a queue waiter\n"
    "  into a raised limit, makes a limited pool turned queue wait, describes the new settings and leaves a torn-down\n"
    "  pool alone\n"
    "- the pool under eight threads (`test_managed_spell_quantity_multithreaded.py`): limited_quantity 3 never has\n",
)
t = sub(
    t,
    "  object to two leases (see `### Flow: Managed Pool Stress Under Eight Threads`)\n"
    "- the store (`test_creations_managed_quantities.py`): one pool per version, composed only for a managed spell\n"
    "  in a live store; an idempotent ensure that re-points a kept pool at a rebound Spell; a pool never in\n",
    "  object to two leases; a ninth thread changing the limit between 3 and 5 against eight leasers leaves the count\n"
    "  equal to the objects alive (0.2.8254) (see `### Flow: Managed Pool Stress Under Eight Threads`)\n"
    "- the store (`test_creations_managed_quantities.py`): one pool per version, composed only for a managed spell\n"
    "  in a live store; an idempotent ensure; a rebind under the same spell_id keeping the pool and giving it the new\n"
    "  Spell's settings, with the store lock free while it runs (0.2.8254); a pool never in\n",
)
t = sub(
    t,
    "  reset names that are not a list or tuple naming methods of the class; every existing member's spell id\n"
    "  byte-identical to 0.2.8241 while the part `managed:<mode>:<limit>:<timeout>:<names>` moves a managed\n"
    "  binding's id; the index minted with that id; the decorator form and `spell_id_inspector` parity. Around it:\n",
    "  reset names that are not a list or tuple naming methods of the class; every existing member's spell id\n"
    "  byte-identical to 0.2.8241, and a managed binding hashing exactly the inputs every binding hashes, whatever its\n"
    "  settings (0.2.8254; from 0.2.8242 to 0.2.8253 a `managed:<mode>:<limit>:<timeout>:<names>` part moved its id);\n"
    "  the index minted with that id; the decorator form and `spell_id_inspector` parity, which ignores the settings\n"
    "  too. Around it:\n",
)
t = sub(
    t,
    "  records the active and the parked versions' options; a restore rebinds both with their options and spell\n"
    "  ids, and a spell-index graft into a Book in another frame carries both members' options\n",
    "  records the active and the parked versions' options; a restore rebinds both with their options and spell\n"
    "  ids, and a spell-index graft into a Book in another frame carries both members' options; the parked version\n"
    "  differs in its disposal methods, because settings alone make the same spell (0.2.8254)\n",
)
t = sub(
    t,
    "  on the Spell, not in its metadata; one class bound unique, managed by default and managed with a limit gets\n"
    "  three ids; a refused binding (an option on `unique`, a managed function) registers nothing; a root's `bind`\n"
    "  and `bind_inactive` forward the options; SpellBinder ends in the same Spell\n",
    "  on the Spell, not in its metadata; one class bound unique and managed gets two ids, and managed with a limit\n"
    "  the managed one's id (0.2.8254; it was a third); a refused binding (an option on `unique`, a managed function)\n"
    "  registers nothing; a root's `bind` and `bind_inactive` forward the options (the parked version differing in its\n"
    "  disposal methods); SpellBinder ends in the same Spell\n",
)
t = sub(
    t,
    "  after the notch, `with` giving the object back. The creation cache's generation history ends at 21\n"
    "  (`test_cache_schema_version_integration.py`: generation 21 is admitted, 1-20 load cold)\n",
    "  after the notch, `with` giving the object back. The creation cache's generation history ends at 22\n"
    "  (`test_cache_schema_version_integration.py`: generation 22 is admitted, 1-21 load cold; 22 joined at 0.2.8254)\n",
)
BULLET = """- a managed spell's settings outside its spell_id (0.2.8254; `test_conduit_integration_managed_settings_rebind.py`, 3
  tests): staging the class again on its SpellIndex with only another limit is refused as the same spell and
  changes nothing; `cleanup_spell` then `bind` with limit 2 keeps the spell_id and the pool, leases up to 2,
  refuses a third and takes back the object leased before; elastic with three idle objects rebound
  limited_quantity 1 keeps all three alive and counted and disposes one at the next release above the limit. The
  other managed files make their second versions differ in identity - another class, or other disposal methods -
  where they differed in settings
"""
t = insert_before(t, "- contract consumers and dependents following a provider change (0.2.8250;\n"
                     "  `test_conduit_integration_notch_revalidation.py`, 16 tests)", BULLET)
t = sub(
    t,
    "- `tests/integration/melder/conduit/test_conduit_integration_notch_revalidation.py` (2026-10-16)\n\n"
    "### Subcomponent: Multithreading Integration Cluster\n",
    "- `tests/integration/melder/conduit/test_conduit_integration_notch_revalidation.py` (2026-10-16)\n"
    "- `" + NEW_TEST + "` (2026-10-18)\n\n"
    "### Subcomponent: Multithreading Integration Cluster\n",
)
t = sub(
    t,
    "   once. The release registry's stress file starts its workers the same way, behind one barrier with a join\n"
    "   timeout.\n   EVIDENCE:\n"
    "   - tests/unit/melder/aether/conduit/creations/test_managed_spell_quantity_multithreaded.py:77-124\n"
    "   - tests/unit/melder/aether/conduit/creations/test_managed_spell_quantity_multithreaded.py:127-238\n",
    "   once. The release registry's stress file starts its workers the same way, behind one barrier with a join\n"
    "   timeout. A ninth thread changing the pool's limit between 3 and 5, 200 times, against eight leasers (its own\n"
    "   barrier of nine, the same join timeout) leaves the count equal to the objects built and not destroyed, every\n"
    "   one idle and never more than 5 (0.2.8254).\n   EVIDENCE:\n"
    "   - tests/unit/melder/aether/conduit/creations/test_managed_spell_quantity_multithreaded.py:77-124\n"
    "   - tests/unit/melder/aether/conduit/creations/test_managed_spell_quantity_multithreaded.py:127-238\n"
    "   - tests/unit/melder/aether/conduit/creations/test_managed_spell_quantity_multithreaded.py:241-311\n",
)
NOTES = {
    "tests/unit/melder/aether/conduit/creations/test_managed_spell_quantity.py": (
        "  note: the managed pool per mode: reserve, waits, put_back and resets, destroy, adopt, abandon, cleanup (0.2.8243).\n",
        "  note: the managed pool per mode: reserve, waits, put_back and resets, destroy, adopt, abandon, cleanup (0.2.8243);\n"
        "    the rebind under the same spell_id (0.2.8254).\n"),
    "tests/unit/melder/aether/conduit/creations/test_managed_spell_quantity_multithreaded.py": (
        "  note: eight barrier-released threads against the pool's limits, waits and teardown (0.2.8243).\n",
        "  note: eight barrier-released threads against the pool's limits, waits and teardown (0.2.8243); a rebinding\n"
        "    ninth thread (0.2.8254).\n"),
    "tests/unit/melder/aether/conduit/creations/test_creations_managed_quantities.py": (
        "  note: the Creations pool map: ensure, cleanup order, the managed row, the registry calls (0.2.8243-0.2.8244).\n",
        "  note: the Creations pool map: ensure, cleanup order, the managed row, the registry calls (0.2.8243-0.2.8244); the\n"
        "    rebind after the store lock (0.2.8254).\n"),
    "tests/unit/melder/spellbook/bind/test_bind_managed_spell_options.py": (
        "  note: the four managed bind options at the Bind seam: defaults, refusals, the managed id part (0.2.8242).\n",
        "  note: the four managed bind options at the Bind seam: defaults, refusals, settings outside the id (0.2.8242,\n"
        "    0.2.8254).\n"),
    "tests/integration/melder/spellbook/test_managed_bind_options_integration.py": (
        "  note: managed bind options through a real Spellbook and its root (0.2.8242).\n",
        "  note: managed bind options through a real Spellbook and its root (0.2.8242); settings outside the id (0.2.8254).\n"),
}
for path, (old, new) in NOTES.items():
    t = remeasure(t, path, loc_of(REPO, path), NOW, old, new)
for path in (
    "tests/integration/melder/conduit/test_conduit_integration_managed_quantity_pool.py",
    "tests/integration/melder/conduit/test_conduit_integration_managed_spell_quantity.py",
    "tests/integration/melder/conduit/test_conduit_integration_release_managed_spell.py",
    "tests/integration/melder/conduit/test_conduit_integration_managed_transfer.py",
    "tests/integration/melder/crystallizer/test_managed_spell_options_record_integration.py",
):
    t = remeasure(t, path, loc_of(REPO, path), NOW)
RECORD = (f"- path: `{NEW_TEST}`\n  start_line: 1\n  end_line: {loc_of(REPO, NEW_TEST)}\n  loc: {loc_of(REPO, NEW_TEST)}\n"
          f"  verified_at: {NOW}\n"
          "  note: settings outside the spell_id: a settings-only re-stage refused; a rebind keeps one spell and pool\n"
          "    (0.2.8254).\n")
t = insert_before(t, "- path: `tests/integration/melder/conduit/test_conduit_integration_notch_revalidation.py`\n", RECORD)
t = sub(t, "above - 263 paths (recounted 2026-10-17) - and nothing else.",
        "above - 264 paths (recounted 2026-10-18) - and nothing else.")
t = sub(t, "- 172 `test_*.py` modules among 179 `.py` files (recounted 2026-10-17); the others are benches and the\n",
        "- 173 `test_*.py` modules among 180 `.py` files (recounted 2026-10-18); the others are benches and the\n")
t = sub(t, "builders - not every `test_*.py` module beneath it. The 847 test modules of the\n",
        "builders - not every `test_*.py` module beneath it. The 848 test modules of the\n")
t = sub(t, "- `tests/integration/melder/conduit/test_conduit_integration_managed_transfer.py`\n"
           "- `tests/integration/melder/crystallizer/test_managed_spell_options_record_integration.py`\n",
        "- `tests/integration/melder/conduit/test_conduit_integration_managed_transfer.py`\n"
        "- `" + NEW_TEST + "`\n"
        "- `tests/integration/melder/crystallizer/test_managed_spell_options_record_integration.py`\n")
HANDOFF = """2026-10-18 managed settings leave the spell_id (0.2.8254; part A of
STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool): the Conduit Integration Cluster gains
`test_conduit_integration_managed_settings_rebind.py` (3 tests: the settings-only re-stage refused, the rebind that
keeps one spell and pool, a mode change that destroys nothing), a key file with a code-map record; the Managed Spell
Pools Unit Cluster names the pool's ten rebind tests, the rebinding ninth thread of the stress file (its flow gains
the case) and the store's rebind after the store lock; the Spellbook clusters name the fingerprint without the
settings and the cache history ending at 22; the crystallizer and conduit clusters say their second versions now
differ in identity. Ten records are remeasured; counts are recounted from disk (integration 173 of 180; 848 test
modules in the three tiers). The core set is 264 paths, equal to the code map.

"""
t = insert_before(t, "2026-10-17 lookup by spell_id is exact (0.2.8253): the Aether/Nexus/Rift Unit Cluster gains\n", HANDOFF)
check_lines(original, t)
comp_text = t

# ---------------------------------------------------------------- tests_architecture
original_arch = ARCH.read_text(encoding="utf-8")
a = original_arch
a = sub(a, "- Updated: 2026-10-17\n", "- Updated: 2026-10-18\n")
a = sub(a, "- `integration/`: 179 `.py` files, 172 of them `test_*.py` (149, 88)\n",
        "- `integration/`: 180 `.py` files, 173 of them `test_*.py` (149, 88)\n")
a = sub(a, "Recounted 2026-10-17 with `find tests/<tier> -name '*.py'` (pycache excluded); the three tiers' 847 `test_*.py`\n",
        "Recounted 2026-10-18 with `find tests/<tier> -name '*.py'` (pycache excluded); the three tiers' 848 `test_*.py`\n")
ARCH_HANDOFF = """2026-10-18 managed settings leave the spell_id (0.2.8254): the inventory is recounted from disk (unit 512 `.py`,
component 168, integration 180, mocks 44, experimentation 204; 848 test modules in the three tiers) - the lane adds
one integration module (a managed spell's settings outside its spell_id), catalogued in `tests_components`, and a
ninth-thread rebind case to the managed pool's stress file after its other cases, so the worker-hang guard's evidence
under `## Failure Modes and Error Paths` (`_run_threads`, 94-124) does not move. No tier, conftest, declared marker or
shared support module changes, and no extent in this map moves.

"""
a = insert_before(a, "2026-10-17 lookup by spell_id is exact (0.2.8253): the inventory is recounted from disk (unit 512 `.py`,\n",
                  ARCH_HANDOFF)
check_lines(original_arch, a)

if DRY:
    print("dry run: ok;", len(original.splitlines()), "->", len(comp_text.splitlines()), "and",
          len(original_arch.splitlines()), "->", len(a.splitlines()), "lines")
else:
    COMP.write_text(comp_text, encoding="utf-8")
    ARCH.write_text(a, encoding="utf-8")
    print("wrote", COMP, "and", ARCH)
