"""S6 part A: promote the managed_settings_spell_id patch into src_components.md (0.2.8254).

Run from the repository root:
  python context_compass/artifacts/correctness_defects_20261017/scripts/s6_docs_src_components.py <NOW> [--dry-run]
Exact-once substitutions; code-map extents measured from disk; numeric citations into bind.py remapped to the
lines that hold what they are cited for; added lines over 120 characters refused.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from s6_docs_common import check_lines, insert_before, loc_of, remeasure, sub  # noqa: E402

NOW = sys.argv[1]
DRY = "--dry-run" in sys.argv
REPO = pathlib.Path(".")
DOC = REPO / "context_compass/system_docs/src_components.md"
original = DOC.read_text(encoding="utf-8")
t = original

t = sub(t, "- Updated: 2026-10-17\n", "- Updated: 2026-10-18\n")

# Binding Pipeline: the managed options leave the fingerprint.
t = sub(
    t,
    "kept in order. `sha256_profile` appends `managed:<mode>:<limit>:<timeout>:<names>` only for managed bindings, so every\n"
    "other spell id is byte-identical; `spell_id_inspector` matches bind. The Spell keeps the normalized values behind\n",
    "kept in order. They are settings of the one spell, not its identity (0.2.8254; the owner's ruling, chat 2026-10-17:\n"
    "the bind call's settings must not change the SHA256): `sha256_profile` takes no managed keyword and hashes a managed\n"
    "binding exactly as any other - binding profile, spell name, spellframe, binding name, existence, resolved disposal\n"
    "names, resolvable - so one class bound managed at one address with one disposal list has one spell_id whatever its\n"
    "settings, and every other spell id is byte-identical. From 0.2.8242 to 0.2.8253 it appended a last part\n"
    "`managed:<mode>:<limit>:<timeout>:<names>` (`_managed_fingerprint_part`, removed), so every managed spell_id moved\n"
    "once. `spell_id_inspector` normalizes the four as bind does (it refuses what bind refuses) and hashes without them.\n"
    "A settings-only `bind_inactive` onto the spell's SpellIndex meets the collision refusal; a settings change is\n"
    "`cleanup_spell`, then `bind`, whose pool takes the new settings (Component: Managed Spell Pools). The Spell keeps\n"
    "the normalized values behind\n",
)
t = sub(
    t,
    "EVIDENCE: `src/melder/aether/spellbook/bind/bind.py:Bind._normalize_managed_options`, `Bind.sha256_profile`,\n",
    "EVIDENCE: `src/melder/aether/spellbook/bind/bind.py:Bind._normalize_managed_options`, `Bind.sha256_profile`,\n"
    "`Bind.spell_id_inspector`, `Bind._bind_logic`,\n",
)

# Binding Pipeline outputs: remap the numeric citations into bind.py.
t = sub(t, "  - src/melder/aether/spellbook/bind/bind.py:453-581 (`bind`, decorator,\n",
        "  - src/melder/aether/spellbook/bind/bind.py:466-603 (`bind`, decorator,\n")
t = sub(t, "  - src/melder/aether/spellbook/bind/bind.py:62-106 (`assert_allowed`)\n",
        "  - src/melder/aether/spellbook/bind/bind.py:66-110 (`assert_allowed`)\n")
t = sub(t, "  - src/melder/aether/spellbook/bind/bind.py:93-97\n",
        "  - src/melder/aether/spellbook/bind/bind.py:106-110\n")
t = sub(t, "  - src/melder/aether/spellbook/bind/bind.py:946-956\n",
        "  - src/melder/aether/spellbook/bind/bind.py:1072-1082\n")
t = sub(t, "  - src/melder/aether/spellbook/bind/bind.py:1006-1026\n",
        "  - src/melder/aether/spellbook/bind/bind.py:1083-1099\n"
        "  - src/melder/aether/spellbook/bind/bind.py:1132-1152\n")

# Registration Refusal: the one live call site.
t = sub(
    t,
    "  `src/melder/aether/spellbook/bind/bind.py:657` (in `Bind._bind_logic`) -\n"
    "  `assert_allowed(spell, context=\"bind\")`. (Was cited as `:363` here and `:364`\n"
    "  in `src_architecture.md` before subsequent edits, and as `:404` in both until 2026-10-01; the\n"
    "  current call is on 657. The documents disagreeing\n",
    "  `src/melder/aether/spellbook/bind/bind.py:715` (in `Bind._bind_logic`) -\n"
    "  `assert_allowed(spell, context=\"bind\")`. (Was cited as `:363` here and `:364`\n"
    "  in `src_architecture.md` before subsequent edits, as `:404` in both until 2026-10-01, and as `:657`\n"
    "  here until 2026-10-18; the current call is on 715. The documents disagreeing\n",
)

# Creations: the rebind.
t = sub(
    t,
    "`ensure_managed_quantity(spell)` returns or composes the version's pool under the store lock (idempotent; a rebind\n"
    "under the same id re-points it) and registers it with `ReleaseManagedSpell` after the lock; `get_managed_quantity` is\n",
    "`ensure_managed_quantity(spell)` returns or composes the version's pool under the store lock (idempotent) and\n"
    "registers it with `ReleaseManagedSpell` after the lock. When the store already holds a pool under the spell_id - a\n"
    "rebind after `cleanup_spell`, which since 0.2.8254 may carry other managed settings - it releases the store lock and\n"
    "calls `ManagedSpellQuantity._rebind_spell`, which re-points the pool and gives it the new Spell's settings, so the\n"
    "store lock stays a leaf; `get_managed_quantity` is\n",
)

# Managed Spell Pools.
t = sub(
    t,
    "- `ManagedSpellExhaustedError`: the refusal of limited_quantity (at its limit) and queue (at its timeout).\n\nInputs:\n",
    "- `ManagedSpellExhaustedError`: the refusal of limited_quantity (at its limit) and queue (at its timeout).\n"
    "- `ManagedSpellQuantity._rebind_spell(spell)` (0.2.8254): called by `Creations.ensure_managed_quantity` when a\n"
    "  rebind under the same spell_id meets the pool; re-points the Spell, its class (re-registered by the store) and\n"
    "  its disposal list, and when a setting differs takes the new mode, limit, timeout and reset names with the\n"
    "  retention sizes `__init__` gives them (elastic: baseline min(20, limit), maximum the limit; limited_quantity and\n"
    "  queue: both the limit; the target restarts at the baseline, the decay step follows), then wakes every waiter.\n"
    "  Equal settings are a pure re-point. A torn-down pool is left as it is.\n\nInputs:\n",
)
t = sub(
    t,
    "- The Spell's normalized options (mode, limit, timeout, reset names), its disposal names and its identity, read when\n"
    "  `Creations.ensure_managed_quantity` composes the pool at owner stamping.\n",
    "- The Spell's normalized options (mode, limit, timeout, reset names), its disposal names and its identity, read when\n"
    "  `Creations.ensure_managed_quantity` composes the pool at owner stamping, and again when a rebind under the same\n"
    "  spell_id meets it (0.2.8254).\n",
)
t = sub(
    t,
    "- The registry lock is a leaf held only to publish; every read is lock-free. Creations registers and unregisters\n"
    "  outside its store lock: owner stamping holds the Spell lock, takes the store's leaf lock for the map, releases it,\n"
    "  then takes the registry's leaf lock to publish. No edge joins frame -> conduit -> Book.\n",
    "- The registry lock is a leaf held only to publish; every read is lock-free. Creations registers and unregisters\n"
    "  outside its store lock: owner stamping holds the Spell lock, takes the store's leaf lock for the map, releases it,\n"
    "  then takes the registry's leaf lock to publish. No edge joins frame -> conduit -> Book.\n"
    "- A rebind (0.2.8254) reads the Spell's settings before the pool lock and writes them under it, after the store lock\n"
    "  is released (Spell lock -> pool lock, as owner stamping already takes it). A lease or a release racing it sees the\n"
    "  old or the new policy for that one call: `reserve()` reads the mode once and checks the limit in force under the\n"
    "  pool lock, `put_back` reads the reset names once, and an idle pop serves an object built for this spell_id.\n",
)
t = sub(
    t,
    "- One pool per (root store, managed spell version). `count` (objects built and alive) rises only in `reserve()`,\n"
    "  after the mode's check, so it never exceeds the limit of a limited_quantity or queue pool; a released object the\n"
    "  pool never built (a fresh override object) is pooled uncounted, because releases are trusted, never checked.\n",
    "- One pool per (root store, managed spell version). `count` (objects built and alive) rises only in `reserve()`,\n"
    "  after the mode's check, so it never rises above the limit of a limited_quantity or queue pool; a rebind to a\n"
    "  lower limit keeps the objects alive above it, counted, until destroys bring the count down (0.2.8254). A released\n"
    "  object the pool never built (a fresh override object) is pooled uncounted, because releases are trusted, never\n"
    "  checked.\n"
    "- The pool's policy is its current Spell's settings: a rebind under the spell_id takes them and destroys nothing\n"
    "  (0.2.8254).\n",
)

GEN22 = """- Generation 22 (2026-10-18, `managed_settings_leave_spell_id`, 0.2.8254): the envelope is unchanged; the bump retires
  bundles written while a managed spell's settings were part of its spell_id (0.2.8242-0.2.8253). Every managed
  spell_id moved once and a bundle keys its payloads by spell_id, so such a bundle could only miss; the release change
  already cold-starts it, and the bump records why, as the owner asked ("you gotta notch the version for the cache").
  EVIDENCE: `src/melder/utilities/caching_system/caching_system.py:CachingSystem.CACHE_VERSION_HISTORY`.
"""
t = insert_before(
    t,
    "EVIDENCE: `src/melder/utilities/caching_system/caching_system.py:CachingSystem`,\n"
    "`src/melder/aether/spellbook/spellbook.py:Spellbook._emit_cache_file_if_required` and\n",
    GEN22,
)

t = sub(
    t,
    "  T[Ownership transfer] -->|managed row moves; stamp follows| Q\n",
    "  T[Ownership transfer] -->|managed row moves; stamp follows| Q\n"
    "  N[Rebind under the same spell_id] --> E\n"
    "  E -->|pool found: _rebind_spell takes the new settings| Q\n",
)

for path in (
    "src/melder/aether/spellbook/bind/bind.py",
    "src/melder/aether/conduit/creations/managed_spell_quantity.py",
    "src/melder/aether/conduit/creations/creations.py",
    "src/melder/aether/spellbook/existence/managed_spell_mode.py",
    "src/melder/crystallizer/crystals/spell_crystal.py",
):
    t = remeasure(t, path, loc_of(REPO, path), NOW)
CACHE = "src/melder/utilities/caching_system/caching_system.py"
t = remeasure(
    t, CACHE, loc_of(REPO, CACHE), NOW,
    "  note: release-bound creation-cache admission and atomic envelope persistence; generation 21 (0.2.8248).\n",
    "  note: release-bound creation-cache admission and atomic envelope persistence; generation 22 (0.2.8254).\n",
)

HANDOFF = """2026-10-18 managed settings leave the spell_id (0.2.8254; part A of
STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool): the Binding Pipeline carries the fingerprint
without the four managed settings and `spell_id_inspector`'s parity; Creations and SpellSpace carries the rebind that
`ensure_managed_quantity` runs after the store lock; Managed Spell Pools carries `_rebind_spell` - the settings and
retention sizes a rebind takes, its locks, the invariant that it destroys nothing - and the count invariant's lower
limit; Spellbook Core carries creation cache generation 22; the managed pools diagram and the code map (six files
remeasured) follow. The numeric citations into bind.py were remapped line by line: five were stale since earlier
lanes (the outputs' `bind`, `assert_allowed` and refusal ranges, the two fingerprint ranges), and the Registration
Refusal call site moves from 657 to 715.

"""
t = insert_before(t, "2026-10-17 lookup by spell_id is exact (0.2.8253; the owner's rule: a spell_id and a SpellIndex are separate\n",
                  HANDOFF)

check_lines(original, t)
if DRY:
    print("dry run: ok;", len(original.splitlines()), "->", len(t.splitlines()), "lines")
else:
    DOC.write_text(t, encoding="utf-8")
    print("wrote", DOC, len(original.splitlines()), "->", len(t.splitlines()), "lines")
