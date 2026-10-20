"""S6 part A: promote the managed_settings_spell_id patch into src_architecture.md (0.2.8254).

Run from the repository root:
  python context_compass/artifacts/correctness_defects_20261017/scripts/s6_docs_src_architecture.py <NOW> [--dry-run]
Exact-once substitutions; code-map extents measured from disk; added lines over 120 characters refused.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from s6_docs_common import check_lines, insert_before, loc_of, remeasure, sub  # noqa: E402

NOW = sys.argv[1]
DRY = "--dry-run" in sys.argv
REPO = pathlib.Path(".")
DOC = REPO / "context_compass/system_docs/src_architecture.md"
original = DOC.read_text(encoding="utf-8")
t = original

t = sub(t, "- Updated: 2026-10-17\n", "- Updated: 2026-10-18\n")

t = sub(
    t,
    "  `ReleaseManagedSpell` (optionally reset) and reused; the pool, not the meld, decides when an object is disposed.\n"
    "- ReleaseManagedSpell: the process singleton",
    "  `ReleaseManagedSpell` (optionally reset) and reused; the pool, not the meld, decides when an object is disposed.\n"
    "  Its four bind settings (mode, limit, queue timeout, reset methods) are settings of the one spell, not part of its\n"
    "  spell_id (0.2.8254).\n"
    "- ReleaseManagedSpell: the process singleton",
)

t = sub(
    t,
    "  `managed`, `release_all`, `describe`), `ManagedSpellLease` and `ManagedSpellExhaustedError`, exported at the\n"
    "  package root with `ManagedSpellMode`.\n- `Conduit.create_lesser_conduit(...)` for child scopes.\n",
    "  `managed`, `release_all`, `describe`), `ManagedSpellLease` and `ManagedSpellExhaustedError`, exported at the\n"
    "  package root with `ManagedSpellMode`. The four options are the spell's settings, not part of its spell_id\n"
    "  (0.2.8254): changing them is `cleanup_spell` and a new `bind`, which keeps the spell_id and the pool.\n"
    "- `Conduit.create_lesser_conduit(...)` for child scopes.\n",
)

INVARIANT = """- A managed spell's settings are not part of its spell_id (2026-10-18, 0.2.8254; the owner's ruling, chat 2026-10-17:
  "the bind call itself shouldn't impact the actual SHA256 thats absurd"): `Bind.sha256_profile` hashes the binding
  profile, the spell name, spellframe, binding name, existence, the resolved disposal names and resolvable (the hash
  domain) and nothing else, so one class bound managed at one address with one disposal list has one spell_id
  whatever its mode, limit, queue timeout or reset methods. `_normalize_managed_options` still checks and normalizes
  the four before the fingerprint, the Spell keeps them, and `spell_id_inspector` checks them as bind does and hashes
  without them. A settings-only re-stage therefore meets the existing collision refusal, and a rebind under the same
  spell_id (`cleanup_spell`, then `bind`) meets the pool the earlier definition left in the owner store:
  `Creations.ensure_managed_quantity` finds it under the store lock, releases that lock and calls
  `ManagedSpellQuantity._rebind_spell`, which under the pool lock re-points the Spell, its class and its disposal list
  and, when a setting differs, takes the new mode, limit, timeout and reset names, sizes the retention band as a
  fresh pool of those settings (elastic: baseline min(20, limit), maximum the limit; limited_quantity and queue: both
  the limit; the target back at the baseline) and wakes every waiter to re-check. Equal settings (an ownership
  transfer's restamp) are a pure re-point that keeps the band. Nothing is destroyed: the count stays the objects
  alive, even above a lower limit, and the pool settles as objects are released. No emitted plan reads a managed
  setting, so plans are unchanged; creation cache generation 22 ("managed_settings_leave_spell_id") retires the
  bundles written while the settings were hashed (the release change cold-starts them anyway). Locks: the store lock
  stays a leaf (the rebind runs after it is released), the pool lock stays a leaf taken under the Spell lock as owner
  stamping takes it, and no user code runs under either. Not changed: the address, existence, disposal names and
  resolvable stay in the spell_id (owner, 2026-10-18), and one class staged in one SpellIndex at another address or
  with another disposal list is still a second version with its own pool (part B of
  STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool, pending).
  EVIDENCE: `src/melder/aether/spellbook/bind/bind.py:Bind.sha256_profile`, `Bind.spell_id_inspector`,
  `Bind._bind_logic`, `src/melder/aether/conduit/creations/managed_spell_quantity.py:ManagedSpellQuantity._rebind_spell`,
  `src/melder/aether/conduit/creations/creations.py:Creations.ensure_managed_quantity` and
  `src/melder/utilities/caching_system/caching_system.py:CachingSystem.CACHE_VERSION_HISTORY`.
"""
t = insert_before(t, "- Lookup by spell_id is exact (2026-10-17, 0.2.8253; the owner's rule: a spell_id - the SHA256 `bind` and\n",
                  INVARIANT)

t = sub(
    t,
    "  unique, managed and many spells; any holder may depend on it). Its four bind options are normalized once in\n"
    "  `Bind._normalize_managed_options` and hashed into the spell id only for managed bindings, so no other spell id\n"
    "  moves; the crystal records them (RecordVersion 4.2.0) and restore and graft replay them.",
    "  unique, managed and many spells; any holder may depend on it). Its four bind options are normalized once in\n"
    "  `Bind._normalize_managed_options` (0.2.8242-0.2.8253 hashed them into a managed spell's id; since 0.2.8254 they\n"
    "  are settings, not identity - see the 0.2.8254 entry at the top of this section); the crystal records them\n"
    "  (RecordVersion 4.2.0) and restore and graft replay them.",
)

FAILURES = """- Breaking (0.2.8254): every managed spell's spell_id moves once - the four settings left the fingerprint - and no
  other spell's does. `bind_inactive` of a managed binding that differs from the version on its SpellIndex only in
  its settings raises the existing RuntimeError "Spell ID collision detected. ..." with nothing registered (it was a
  second version with its own pool); change settings with `cleanup_spell`, then `bind` (the spell_id and the pool
  stay). Under process-wide spell ids one managed class bound at one address in two frames is one spell_id whatever
  its settings, so the second binding is refused as a duplicate, as any spell's is: at its bind once the first
  frame's Book is conjured, else at its conjure ("Conjure refused: ... already registered"). Bundles written before
  are cold once (generation 22), and a Crystallizer record made by 0.2.8242-0.2.8253 restores through `bind`, which
  gives each managed spell its new spell_id.
  EVIDENCE: `src/melder/aether/spellbook/bind/bind.py:Bind.sha256_profile` and
  `src/melder/utilities/caching_system/caching_system.py:CachingSystem.CACHE_VERSION_HISTORY`.
- Fixed in 0.2.8254: changing a managed spell's settings no longer leaves a pool counting an object it never gets
  back. A rebind with other settings minted a new spell_id and a second pool, and a release with no filter of an
  object leased before went to the new version's pool uncounted while the disposed version's pool counted it out
  for good; staging the class with only another limit in its SpellIndex did the same across a notch, and a
  limited_quantity or queue pool so stranded refused leases once its count reached the limit. A rebind now meets its
  pool under the same spell_id and the pool takes the new settings, and a settings-only re-stage is refused. Known,
  not fixed (part B of STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool): one class staged in
  one SpellIndex at another address or with another disposal list is still a second version with its own pool, so
  an unfiltered release after a notch still goes to the active version's pool; pass `spell_id=` to route it.
  EVIDENCE: `src/melder/aether/conduit/creations/managed_spell_quantity.py:ManagedSpellQuantity._rebind_spell`,
  `src/melder/aether/conduit/creations/creations.py:Creations.ensure_managed_quantity` and
  `src/melder/aether/conduit/creations/release_managed_spell.py:ReleaseManagedSpell._resolve_pool`.
"""
t = insert_before(t, "- Breaking (0.2.8253): `Spellbook.find_spell_by_id` and `Conduit.get_spell_by_id` are gone, with no alias (a call\n",
                  FAILURES)

t = sub(t, "  `src/melder/aether/spellbook/bind/bind.py:713` (in `Bind._bind_logic`) -\n",
        "  `src/melder/aether/spellbook/bind/bind.py:715` (in `Bind._bind_logic`) -\n")

t = sub(
    t,
    "ownership transfer -> rows carry the pool; the owner stamp follows; a failed one stamps back, discards composed pools\n",
    "ownership transfer -> rows carry the pool; the owner stamp follows; a failed one stamps back, discards composed pools\n"
    "rebind under the same spell_id (cleanup_spell, bind) -> ensure_managed_quantity -> the same pool, new settings\n",
)
t = sub(
    t,
    "  T[Root teardown] --> C[Pools cleaned before the store's registry]\n```\n",
    "  T[Root teardown] --> C[Pools cleaned before the store's registry]\n"
    "  N[Rebind under the same spell_id] -->|the pool takes the new settings| P\n```\n",
)

BIND = "src/melder/aether/spellbook/bind/bind.py"
t = remeasure(
    t, BIND, loc_of(REPO, BIND), NOW,
    "  note: binding pipeline; classifies the spellframe kind and refuses concrete-class frames (0.2.8222); normalizes and\n"
    "    fingerprints the managed options (`_normalize_managed_options`, 0.2.8242).\n",
    "  note: binding pipeline; classifies the spellframe kind and refuses concrete-class frames (0.2.8222); normalizes the\n"
    "    managed options (`_normalize_managed_options`, 0.2.8242), which the fingerprint leaves out since 0.2.8254.\n",
)
MODE = "src/melder/aether/spellbook/existence/managed_spell_mode.py"
t = remeasure(
    t, MODE, loc_of(REPO, MODE), NOW,
    "  note: `ManagedSpellMode`: elastic, limited_quantity, queue (0.2.8242).\n",
    "  note: `ManagedSpellMode`: elastic, limited_quantity, queue (0.2.8242); a setting, not identity (0.2.8254).\n",
)
CRYSTAL = "src/melder/crystallizer/crystals/spell_crystal.py"
t = remeasure(
    t, CRYSTAL, loc_of(REPO, CRYSTAL), NOW,
    "    managed options (RecordVersion 4.2.0, 0.2.8242).\n",
    "    managed options (RecordVersion 4.2.0, 0.2.8242), settings a replayed bind passes, not identity (0.2.8254).\n",
)
POOL = "src/melder/aether/conduit/creations/managed_spell_quantity.py"
t = remeasure(
    t, POOL, loc_of(REPO, POOL), NOW,
    "    abandon, adopt, destroy and cleanup (0.2.8243).\n",
    "    abandon, adopt, destroy and cleanup (0.2.8243); `_rebind_spell` gives a same-spell_id rebind the new settings\n"
    "    (0.2.8254).\n",
)
STORE = "src/melder/aether/conduit/creations/creations.py"
t = remeasure(
    t, STORE, loc_of(REPO, STORE), NOW,
    "    cleaned first, the `managed` row (0.2.8243-0.2.8246).\n",
    "    cleaned first, the `managed` row (0.2.8243-0.2.8246); `ensure_managed_quantity` rebinds a found pool after the\n"
    "    store lock (0.2.8254).\n",
)
CACHE = "src/melder/utilities/caching_system/caching_system.py"
t = remeasure(
    t, CACHE, loc_of(REPO, CACHE), NOW,
    "    generation 21, \"managed_spell_lease_codegen\" (0.2.8248).\n",
    "    generation 22, \"managed_settings_leave_spell_id\" (0.2.8254).\n",
)

HANDOFF = """2026-10-18 managed settings leave the spell_id (0.2.8254; part A of
STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool, on the owner's ruling "the bind call itself
shouldn't impact the actual SHA256"): a managed spell's mode, limit, queue timeout and reset methods are settings of
the one spell, not its identity - the fingerprint no longer hashes them, a rebind under the same spell_id gives its
pool the new settings, and creation cache generation 22 retires older bundles. The glossary, the boundary list, a new
operational invariant (the 0.2.8241-0.2.8243 pools entry's hashing sentence points at it), two failure modes (one
Breaking, one fixed with its part-B residue), the managed lease diagram and the code map (six files remeasured)
carry it; the component map carries the per-component contracts. The guardrail's citation of the internal-bind call
moves to bind.py:715 (it had drifted two lines). Open with the owner: part B (refusing a second managed version of
one class in one SpellIndex), a record holding two settings-only versions of one class, and whether more of the bind
call leaves the spell_id.

"""
t = insert_before(t, "2026-10-17 lookup by spell_id is exact (0.2.8253; the owner's rule: a spell_id and a SpellIndex are separate\n",
                  HANDOFF)

check_lines(original, t)
if DRY:
    print("dry run: ok;", len(original.splitlines()), "->", len(t.splitlines()), "lines")
else:
    DOC.write_text(t, encoding="utf-8")
    print("wrote", DOC, len(original.splitlines()), "->", len(t.splitlines()), "lines")
