"""S7: promote the managed_spell_quantity lane into src_architecture.md (glossary, boundary list, guardrails, boot,
meld, transfer and cleanup sequences, four operational invariants, five failure modes, the code map, the sources,
a diagram and the handoff). Every edit is anchored on exact text and the file is written once, at the end.

Run from the repository root: python s7_docs_architecture.py <NOW>
"""
import pathlib
import re
import sys

now = sys.argv[1]
DOC = pathlib.Path("context_compass/system_docs/src_architecture.md")
text = DOC.read_text(encoding="utf-8")
before = set(text.splitlines())


def replace_once(old: str, new: str) -> None:
    global text
    assert text.count(old) == 1, old[:100]
    text = text.replace(old, new)


def insert_after(anchor: str, block: str) -> None:
    replace_once(anchor, anchor + block)


# ---- glossary --------------------------------------------------------------------------------------------------
insert_after(
    "- Custody key: the key the Crystallizer's record keeps one spell's crystal under - the spell id under\n"
    "  process-wide spell ids, `\"<spell_id>@<frame>\"` under per-frame ids, where one spell id can be bound in\n"
    "  several frames (0.2.8214).\n",
    "- Managed spell: a spell bound with `Existence.managed_spell_quantity` (0.2.8241-0.2.8246). Its objects are leased\n"
    "  from the `ManagedSpellQuantity` pool its owning root keeps for that version, given back explicitly through\n"
    "  `ReleaseManagedSpell` (optionally reset) and reused; the pool, not the meld, decides when an object is disposed.\n"
    "- ReleaseManagedSpell: the process singleton Aether builds last and owns - the class-keyed registry of the pools\n"
    "  live root stores hold, through which a managed object goes back to its pool (0.2.8244).\n",
)

# ---- boundary list ---------------------------------------------------------------------------------------------
insert_after(
    "- `Conduit.meld(...)` for resolving instances.\n",
    "- `Conduit.managed_spell_meld(spell=None, *, spell_id=None, spellframe=None, binding_name=None, override=None)`\n"
    "  (0.2.8245): a meld of a managed spell that returns a `ManagedSpellLease`; its `with` gives the object back.\n"
    "- Managed spells (0.2.8241-0.2.8246): `Existence.managed_spell_quantity` and the keyword-only bind options\n"
    "  `managed_spell_mode` (`ManagedSpellMode`: elastic | limited_quantity | queue), `managed_spell_limit`,\n"
    "  `managed_spell_timeout_seconds` and `managed_spell_reset_methods` on `Spellbook.bind` / `bind_inactive`, the\n"
    "  Conduit facades, `SpellBinder.as_managed_spell_quantity` and `scan_bind`; `ReleaseManagedSpell()` (`release`,\n"
    "  `managed`, `release_all`, `describe`), `ManagedSpellLease` and `ManagedSpellExhaustedError`, exported at the\n"
    "  package root with `ManagedSpellMode`.\n",
)

# ---- guardrails ----------------------------------------------------------------------------------------------
replace_once(
    "alongside `MANIFEST_VERSION`, `BUILT_FOR_VERSION` and `MANIFEST_ENTRY_COUNT` (620 at\n"
    "  0.2.8216; `ManyDisposalBucket` joined the manifest, 619 at 0.2.8215).",
    "alongside `MANIFEST_VERSION`, `BUILT_FOR_VERSION` and `MANIFEST_ENTRY_COUNT` (628 at\n"
    "  0.2.8246: the managed-spell classes joined at 0.2.8242-0.2.8244; 620 at 0.2.8216).",
)
replace_once(
    "- The first `Aether()` boot eagerly constructs hidden singleton support\n"
    "  objects, including `AetherUtilitySystem`, `Crystallizer`, and `Nexus`.\n",
    "- The first `Aether()` boot eagerly constructs hidden singleton support\n"
    "  objects, including `AetherUtilitySystem`, `Crystallizer`, `Nexus` and, last,\n"
    "  `ReleaseManagedSpell` (0.2.8244).\n",
)

# ---- boot ----------------------------------------------------------------------------------------------------
replace_once(
    "     this fixed order: `Crystallizer`, `AetherUtilitySystem`, `LoadGate`, the\n"
    "     aetheric `Mediator` plane, `MutationResearch`, then `Nexus`. Crystallizer\n"
    "     leads because MutationResearch and Nexus read it out of the host as they\n"
    "     construct. All six are EAGER. MutationResearch was lazy once and was made\n"
    "     eager by owner ruling (2026-08-03): a bare `MutationResearch()` before\n"
    "     its first touch raised instead of returning the hosted root. No\n"
    "     `AethericFrame` is constructed at boot.\n"
    "     EVIDENCE: src/melder/aether/aether.py:175-251\n",
    "     this fixed order: `Crystallizer`, `AetherUtilitySystem`, `LoadGate`, the\n"
    "     aetheric `Mediator` plane, `MutationResearch`, `Nexus`, then\n"
    "     `ReleaseManagedSpell` (0.2.8244). Crystallizer leads because\n"
    "     MutationResearch and Nexus read it out of the host as they construct.\n"
    "     All seven are EAGER. MutationResearch was lazy once and was made\n"
    "     eager by owner ruling (2026-08-03): a bare `MutationResearch()` before\n"
    "     its first touch raised instead of returning the hosted root.\n"
    "     `ReleaseManagedSpell` comes last: root stores register their pools in\n"
    "     it only once frames exist, and it reads no other hosted root. No\n"
    "     `AethericFrame` is constructed at boot.\n"
    "     EVIDENCE: src/melder/aether/aether.py:186-266\n",
)

# ---- meld sequence ---------------------------------------------------------------------------------------------
insert_after(
    "   holder's owner, not in the meld's innermost scope (0.2.8235).\n",
    "   A managed site leases instead (0.2.8245): the plan pops an idle object from the version's pool inline - a plan\n"
    "   constant on an automatic root, a per-creation read of the owner store's pool elsewhere - and only an empty pool\n"
    "   calls the site's miss, which reserves a place first, builds the children, then the object, and records the\n"
    "   object's disposal-bearing `many` children with it. Each injection is its own lease.\n",
)

# ---- transfer sequence -----------------------------------------------------------------------------------------
insert_after(
    "   - Marks lineage disabled (transfer_in_progress) and flips registries under lock.\n",
    "   - Stamps every member that carries an owner stamp onto the target root - the active one in the flip, the\n"
    "     parked ones as they migrate - registering each stamp-back first, so a failed transfer stamps them back and\n"
    "     discards the empty managed pools its stamps composed (0.2.8246).\n",
)
replace_once(
    "   - With `move_creations=True` (the default since 0.2.8239) moves the source store's instances of every index\n"
    "     member into the target's store, a holder's adopted `many` children with it (0.2.8238); with `False` takes\n"
    "     the active member's instances out of the source store, neither moved nor disposed. Lineage instances stay\n"
    "     where they were resolved. A transfer disposes nothing.\n",
    "   - With `move_creations=True` (the default since 0.2.8239) moves the source store's instances of every index\n"
    "     member into the target's store, a holder's adopted `many` children with it (0.2.8238) and a managed\n"
    "     version's pool with its idle objects and count; with `False` takes the active member's instances (its pool\n"
    "     among them) out of the source store, neither moved nor disposed. Lineage instances stay where they were\n"
    "     resolved. A transfer disposes nothing.\n",
)

# ---- cleanup sequence ------------------------------------------------------------------------------------------
replace_once(
    "3. `Aether.cleanup()` cleans frames, resets singleton state, cleans logger.\n",
    "3. `Aether.cleanup()` cleans frames, then `ReleaseManagedSpell` (the frames' root stores have unregistered their\n"
    "   pools), then the other hosted roots, resets singleton state, cleans logger.\n",
)
insert_after(
    "   SpellSpace teardowns above it finish the same way and raise its groups last.\n",
    "   A root store cleans its managed pools first, newest first - their idle objects and the `many` children\n"
    "   recorded with every pooled object, out ones included - before its disposable registry, because a pool is\n"
    "   composed at conjure, before the uniques its objects hold; their failures join the same group (0.2.8243).\n",
)

# ---- operational invariants ------------------------------------------------------------------------------------
insert_after(
    "## Operational Invariants\n",
    """- Managed pools follow an ownership transfer's owner stamps (2026-10-15, 0.2.8246): a spell version's owner stamp -
  root id, name and store, dynamic flag, gate controller and the Book's caching posture, written by
  `Spell._add_owned_conduit` - follows the transfer's lineage both ways. The flip stamps the active member and
  `_migrate_inactive_members` every parked member that carries a stamp, through `TransferOfOwnership._restamp`, which
  registers the stamp-back to the source before stamping and, for a managed version whose pool the target store did
  not hold, the discard of the pool its stamp composed (`Creations.discard_managed_quantity`: an identity-checked
  pop under the store lock, unregistered after it, never cleaned there). Rollback runs newest first, so the rows go
  back before the stamps; a discarded pool is empty because the lineage is disabled for the whole transfer. A notch
  never re-stamps (`_apply_notch`), so the stamp must follow the transfer: until 0.2.8246 a parked version kept its
  source store (a `unique` stored its object there after a notch on the target, a managed meld found no pool) and a
  failed transfer left the active member on the target's store. A version staged with `bind_inactive` before conjure
  carries no stamp and moves as before. Stamps run under both conduit locks and outside the Book locks (conduit ->
  spell -> store leaf -> registry leaf); rollbacks take no conduit lock.
  EVIDENCE: `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:TransferOfOwnership._restamp`,
  `TransferOfOwnership._stamp_owner`, `TransferOfOwnership._discard_composed_pool`,
  `TransferOfOwnership._migrate_inactive_members` and
  `src/melder/aether/conduit/creations/creations.py:Creations.discard_managed_quantity`.
- Managed leases in emitted plans (2026-10-15, 0.2.8245): a managed site is per path - both sharedness predicates
  answer False for it, as for `many` - so each injection is its own lease. A LEASING site (no winning override key on
  its own parameters) is placed like a shared site and feeds exactly one consumer. Its value is an inline pop of the
  pool's idle deque - a plan constant when the owner is automatic, its store set and the pool present at emission,
  else a per-creation read of `spells[i]._owner_creations._managed_quantities[sid]` that raises the missing-pool
  MeldExecutionError - and only an empty pool calls its `_miss{i}`, which checks unresolved inputs, reserves a place
  (`reserve()` may serve an idle object at once), builds the children and the object inside a `try` whose handler
  gives the place back and disposes the children built (`abandon`), then records the object's disposal-bearing `many`
  children with it (`adopt`). A FRESH site (winning keys on its own parameters) is built like a `many` step and never
  pooled, counted or registered. Every lease taken for a consumer goes back to its pool when anything between the
  first lease and the consumer's construction - its guard, recheck and publication for a shared consumer - raises,
  and a shared consumer that loses its cold race returns its unused leases. Route "managed" maps onto the `many` door
  templates (so `created` is True on every lease and the activation hooks run for reused objects), solo discovery
  declines a managed model, the generalized manifest takes the route key and the singleton specializer keeps the
  plain door for any graph with a managed row. Plans without a managed step are byte-identical (4,461 emitted shapes
  compared), and no cache generation moves: plans are emitted at hydration. The warm path takes no lock.
  EVIDENCE: `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:SitePlanEmission._emit_leased_region`,
  `SitePlanEmission._emit_leasing_miss`, `SitePlanEmission._managed_pool_constant`,
  `SitePlanRuntimeHelpers.return_leases`,
  `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/compilers/generalized_manifest_no_overrides_compiler.py:rows_contain_managed_step`
  and `src/melder/aether/conduit/conduit.py:Conduit.managed_spell_meld`.
- ReleaseManagedSpell (2026-10-15, 0.2.8244): a process singleton with the hosted roots' shape - a double-checked
  `__new__` under a class lock, a once-only `__init__(*, aether=...)` that refuses a first construction without its
  host, `cleanup()` and `_reset_singleton_for_tests()` - built last by `Aether.__init__` and cleaned by
  `Aether.cleanup` right after the frames. It keeps two copy-on-write maps, `_pools_by_class` (class object -> tuple
  of pools) and `_registrations` (`id(pool)` -> class and holding root id), republished whole under a leaf lock and
  read without it. Creations registers a pool when a store takes it (ensure, restore) and unregisters it when the
  store gives it up (extract, discard, cleanup), outside the store lock, so the registry holds exactly the pools live
  root stores hold. `release(obj)` is one dict get by `type(obj)` and `put_back` when exactly one pool matches and no
  filter is given; otherwise the cold resolver filters by `spell_id` and by `conduit`'s root, prefers the version its
  index selects and raises a ValueError naming every candidate when one pool does not remain. Releasing needs
  neither a conduit nor Aether. `ManagedSpellLease` releases once; its `with` releases on exit and never suppresses.
  EVIDENCE: `src/melder/aether/conduit/creations/release_managed_spell.py:ReleaseManagedSpell.release`,
  `ReleaseManagedSpell._resolve_pool`, `ReleaseManagedSpell.register`, `ReleaseManagedSpell.unregister`,
  `src/melder/aether/conduit/creations/managed_spell_lease.py:ManagedSpellLease` and
  `src/melder/aether/aether.py:Aether.__init__`.
- Managed spell pools (2026-10-15, 0.2.8241-0.2.8243): `Existence.managed_spell_quantity` (the seventh member,
  appended, so the six keep their values) binds classes only and ranks 0 with `unique` in Phase 6 (it may depend on
  unique, managed and many spells; any holder may depend on it). Its four bind options are normalized once in
  `Bind._normalize_managed_options` and hashed into the spell id only for managed bindings, so no other spell id
  moves; the crystal records them (RecordVersion 4.2.0) and restore and graft replay them. Every stamped managed
  version owns one `ManagedSpellQuantity` (an `AbstractElasticPool`) in its owner root's Creations, in
  `_managed_quantities` beside `_creations`, so resolution, the live probes and purge never read a pool as an object;
  conduit purge returns 0 for a managed spell and a spellspace refuses it. elastic keeps a baseline of min(20, limit)
  idle and at most the limit, with the kernel pools' stretch and decay; limited_quantity and queue are fixed at their
  limit, and `count` (built and alive, changed only under the pool lock) never exceeds it. The pool keeps no
  reference to an object that is out. A release runs the reset names outside every lock and appends; disposal runs
  only when the pool destroys an object (an elastic trim, a raising reset, teardown). `Creations.cleanup` cleans its
  pools before its disposable registry, and extract/restore carry a pool as a `managed` row.
  EVIDENCE: `src/melder/aether/conduit/creations/managed_spell_quantity.py:ManagedSpellQuantity`,
  `src/melder/aether/conduit/creations/creations.py:Creations.ensure_managed_quantity`, `Creations.cleanup`,
  `src/melder/aether/spellbook/bind/bind.py:Bind._normalize_managed_options` and
  `src/melder/aether/spellbook/spell_compiler/system/validation/scope_ordering_strategy.py:ScopeOrderingStrategy`.
""",
)

# ---- failure modes ---------------------------------------------------------------------------------------------
insert_after(
    "## Failure Modes and Error Paths\n",
    """- A managed meld can refuse (0.2.8243-0.2.8245): `ManagedSpellExhaustedError`, a `MeldExecutionError` exported at the
  package root, before anything is built - limited_quantity "Managed spell '<name>' (limited_quantity, limit <N>) has
  all <N> objects out. Release one with ReleaseManagedSpell().release(obj) before melding another, or bind it with a
  higher managed_spell_limit."; queue, after waiting its timeout, "Managed spell '<name>' (queue, limit <N>) had no
  object free within <T> s. ...". A version with no pool to lease from - its owner root torn down, or a version staged
  with `bind_inactive` before conjure and notched in after it - raises MeldExecutionError "Managed spell '<name>' has
  no pool to lease from: ...". `Conduit.managed_spell_meld` of another existence raises ValueError
  "managed_spell_meld leases a managed spell; '<name>' is <existence>. ..." before melding anything.
  EVIDENCE: `src/melder/utilities/custom_exceptions/managed_spell_exhausted_error.py:ManagedSpellExhaustedError`,
  `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py:SitePlanRuntimeHelpers.raise_missing_managed_pool`
  and `src/melder/aether/conduit/conduit.py:Conduit.managed_spell_meld`.
- `ReleaseManagedSpell().release(obj)` raises ValueError "<Type> is not a managed spell class in any live root: ..."
  for a class no live root pools; ValueError "<Type> is managed by <k> pools: ... Pass spell_id=... or conduit=... to
  pick one." when several pools match (two binding names, two roots or frames, or a parked version notched in on the
  new owner after a no-move transfer); ValueError "No pool of managed class <Type> matches ..." for filters no pool
  matches; and TypeError for a filter of the wrong type (0.2.8244). A release after the pool's root was torn down
  raises RuntimeError "The pool of managed spell '<name>' was torn down with its root conduit; the object is yours to
  dispose." A reset that raises destroys the object (its disposal methods and recorded children run), frees its
  place and propagates (an ExceptionGroup when the disposal failed too). A release racing a transfer of its spell can
  meet the gap between extract and restore and raises the not-managed ValueError for that call.
  EVIDENCE: `src/melder/aether/conduit/creations/release_managed_spell.py:ReleaseManagedSpell._resolve_pool` and
  `src/melder/aether/conduit/creations/managed_spell_quantity.py:ManagedSpellQuantity.put_back`.
- Bind refuses a managed binding before any registry change (0.2.8242): a `managed_spell_*` option on another
  existence (ValueError); a function, method, lambda or existing object (TypeError: classes only); an unknown mode; a
  limit that is not an int >= 1, or missing for limited_quantity or queue; a timeout given for elastic or
  limited_quantity, or missing or not positive for queue; reset names that are not a list or tuple of names of
  callable attributes of the class (TypeError or ValueError, each message naming the remedy).
  EVIDENCE: `src/melder/aether/spellbook/bind/bind.py:Bind._normalize_managed_options`.
- An ownership transfer no longer leaves an owner stamp naming the wrong store (fixed in 0.2.8246). A version parked
  before the transfer kept the old owner's store, so after `notch_spell` to it on the new owner its `unique` object
  was stored in the old owner's store and a managed meld raised the missing-pool error; a transfer that failed after
  the flip left the active version on the new owner's store, so the old owner's next meld built a second `unique`
  object there, and a managed meld raised missing-pool or leased from an empty pool left in the new owner.
  EVIDENCE: `src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py:TransferOfOwnership._restamp`.
- A version staged with `bind_inactive` before `conjure` is never owner-stamped (conjure stamps the Book's active
  spells only, and a notch stamps nothing), so after a notch to it its first meld raises RuntimeError "Spell has no
  configured CreationContextFactory." for every existence, and a managed consumer raises the missing-pool error. Stage
  versions after conjure. Stamping parked versions at conjure is open for the owner's decision; unchanged.
  EVIDENCE: `src/melder/aether/spellbook/spellbook_creation_system.py:SpellbookCreationSystem.define_conduit_into_spells`,
  `src/melder/aether/spellbook/spellbook.py:Spellbook._apply_notch` and
  `src/melder/aether/spellbook/spell.py:Spell._get_or_build_creation_context`.
""",
)

# ---- the code map ----------------------------------------------------------------------------------------------
notes = {
    "src/melder/__init__.py": "; the four managed-spell root exports (0.2.8244).",
    "src/melder/aether/spellbook/spellbook.py": "; bind and bind_inactive take the four `managed_spell_*` options (0.2.8242).",
    "src/melder/aether/spellbook/spellbinder.py": "; `as_managed_spell_quantity` (0.2.8242).",
    "src/melder/aether/spellbook/bind/bind.py": "; normalizes and fingerprints the managed options (`_normalize_managed_options`, 0.2.8242).",
    "src/melder/aether/spellbook/bind/scan.py": "; `scan_bind` takes the managed options, 28 reserved metadata keys (0.2.8242).",
    "src/melder/aether/spellbook/bind/spell_index.py": "; `_is_selected_unless_cleaned`, the release registry's selected-version probe (0.2.8244).",
    "src/melder/aether/spellbook/spell.py": "; the four managed fields; `_add_owned_conduit` ensures a managed version's pool (0.2.8242-0.2.8243).",
    "src/melder/aether/spellbook/existence/existence.py": "; `managed_spell_quantity`, the seventh member (0.2.8241).",
    "src/melder/aether/spellbook/spell_compiler/codegen_creation_system/shared_assets/site_plan_lowering.py":
        "; the managed site kinds - leasing and fresh, the inline pop, the reserve-first miss, the lease return (0.2.8245).",
    "src/melder/aether/aether.py": "; builds `ReleaseManagedSpell` last and cleans it after the frames (0.2.8244).",
    "src/melder/crystallizer/crystals/spell_crystal.py": "; records the managed options (RecordVersion 4.2.0, 0.2.8242).",
    "src/melder/crystallizer/crystal_loader_system/restore_engine.py": "; replays the managed options through bind (0.2.8242).",
    "src/melder/crystallizer/crystal_loader_system/graft_runner.py": "; replays the managed options (0.2.8242).",
    "src/melder/nexus/rift/frame_viewer/static_frame_viewer.py": "; treats a managed spell like `many` (0.2.8243).",
    "src/melder/nexus/rift/command_system/static_command_system.py": "; treats a managed spell like `many` (0.2.8243).",
    "src/melder/aether/conduit/conduit.py": "; `managed_spell_meld` (0.2.8245) and the managed options on its bind facades (0.2.8242).",
    "src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py":
        "; the owner stamp follows the lineage both ways (`_restamp`, 0.2.8246).",
    "src/melder/aether/conduit/meld/meld.py": "; the live probes' managed-pool answer (0.2.8243).",
    "src/melder/aether/conduit/creations/creations.py":
        "; the managed pool map, `ensure_managed_quantity`, `discard_managed_quantity`, pools cleaned first, the `managed` row (0.2.8243-0.2.8246).",
}
a = text.index("## C1 Code Map (Core Only)\n")
b = text.index("## Diagrams\n")
section = text[a:b]
entry = re.compile(
    r"- path: `(?P<path>[^`]+)`\n  start_line: 1\n  end_line: (?P<end>\d+)\n  loc: (?P<loc>\d+)\n"
    r"  verified_at: (?P<ver>\S+)\n(?P<note>  note: .*\n(?:    .*\n)*)?"
)
changed = []


def remeasure(m: re.Match) -> str:
    path = m.group("path")
    lines = len(pathlib.Path(path).read_text(encoding="utf-8").splitlines())
    if lines == int(m.group("end")):
        return m.group(0)
    changed.append(path)
    note = m.group("note")
    out = f"- path: `{path}`\n  start_line: 1\n  end_line: {lines}\n  loc: {lines}\n  verified_at: {now}\n"
    if path in notes and note:
        body = note[len("  note: "):].rstrip("\n")
        flat = " ".join(part.strip() for part in body.split("\n"))
        flat = flat.rstrip(".") + notes[path]
        words, lines_out, current = flat.split(" "), [], "  note:"
        for word in words:
            if len(current) + 1 + len(word) > 118:
                lines_out.append(current)
                current = "    " + word
            else:
                current = current + " " + word
        lines_out.append(current)
        out += "\n".join(lines_out) + "\n"
    elif note:
        out += note
    return out


section = entry.sub(remeasure, section)
new_entries = {
    "Resolution and creations:\n\n": [
        ("src/melder/aether/conduit/creations/managed_spell_quantity.py",
         "the managed pool: an `AbstractElasticPool` of one managed version's idle objects, its count, reserve, put_back,\n"
         "    abandon, adopt, destroy and cleanup (0.2.8243)."),
        ("src/melder/aether/conduit/creations/release_managed_spell.py",
         "the Aether-owned release registry: class-keyed copy-on-write maps, release, managed, release_all,\n"
         "    describe and the cold resolver (0.2.8244)."),
        ("src/melder/aether/conduit/creations/managed_spell_lease.py",
         "one leased managed object and its pool; releases once, `with` releases on exit (0.2.8244)."),
    ],
}
for anchor, rows in new_entries.items():
    assert section.count(anchor) == 1, anchor
    block = ""
    for path, note in rows:
        n = len(pathlib.Path(path).read_text(encoding="utf-8").splitlines())
        block += f"- path: `{path}`\n  start_line: 1\n  end_line: {n}\n  loc: {n}\n  verified_at: {now}\n  note: {note}\n"
    section = section.replace(anchor, anchor + block)
for anchor_path, path, note in (
    ("src/melder/aether/spellbook/existence/existence.py", "src/melder/aether/spellbook/existence/managed_spell_mode.py",
     "`ManagedSpellMode`: elastic, limited_quantity, queue (0.2.8242)."),
    ("src/melder/utilities/helpers/init_helpers.py", "src/melder/utilities/custom_exceptions/managed_spell_exhausted_error.py",
     "`ManagedSpellExhaustedError`, a MeldExecutionError raised before a refused managed meld builds\n"
     "    anything (0.2.8243)."),
):
    m = re.search(r"- path: `" + re.escape(anchor_path) + r"`\n(?:  .*\n)+", section)
    assert m, anchor_path
    n = len(pathlib.Path(path).read_text(encoding="utf-8").splitlines())
    block = f"- path: `{path}`\n  start_line: 1\n  end_line: {n}\n  loc: {n}\n  verified_at: {now}\n  note: {note}\n"
    section = section[: m.end()] + block + section[m.end():]
text = text[:a] + section + text[b:]

# ---- information sources ---------------------------------------------------------------------------------------
insert_after(
    "- `src/melder/aether/conduit/creations/creations.py`\n",
    "- `src/melder/aether/conduit/creations/managed_spell_quantity.py`\n"
    "- `src/melder/aether/conduit/creations/release_managed_spell.py`\n"
    "- `src/melder/aether/conduit/creations/managed_spell_lease.py`\n",
)
insert_after(
    "- `src/melder/aether/spellbook/existence/existence.py`\n",
    "- `src/melder/aether/spellbook/existence/managed_spell_mode.py`\n",
)
insert_after(
    "- `src/melder/utilities/custom_exceptions/spell_space_scope_error.py`\n",
    "- `src/melder/utilities/custom_exceptions/managed_spell_exhausted_error.py`\n",
)

# ---- diagram ---------------------------------------------------------------------------------------------------
replace_once(
    "\n### ASCII Context Diagram (C4)\n",
    """
### Managed Lease and Release
```text
meld or injection -> plan: pop the pool's idle deque -> hit: the object (no lock)
                                                     -> empty: miss: reserve -> children -> object -> adopt children
                                                        (refused: ManagedSpellExhaustedError; raised: abandon)
holder -> ReleaseManagedSpell().release(obj) -> type(obj) -> pool.put_back: resets -> append (-> trim, notify)
root teardown -> Creations.cleanup: pools first (idle objects + recorded children) -> unregistered
ownership transfer -> rows carry the pool; the owner stamp follows; a failed one stamps back, discards composed pools
```

```mermaid
flowchart LR
  M[Meld or injection] --> P{Idle object in the pool?}
  P -->|yes| O[Leased object]
  P -->|no| R[Miss: reserve a place]
  R -->|refused| X[ManagedSpellExhaustedError]
  R --> B[Build children, then the object]
  B -->|raises| A[Abandon: place back, children disposed]
  B --> O
  O --> H[Holder uses it]
  H --> L[ReleaseManagedSpell.release]
  L --> S[Resets, then back to the idle deque]
  S --> P
  T[Root teardown] --> C[Pools cleaned before the store's registry]
```

### ASCII Context Diagram (C4)
""",
)

# ---- handoff ---------------------------------------------------------------------------------------------------
insert_after(
    "## Context / Handoff Summary\n\n",
    "2026-10-15 managed spells (0.2.8241-0.2.8246; promoted at the end of their lane): `Existence.managed_spell_quantity`\n"
    "leases objects from a pool its owning root keeps per version and takes them back through `ReleaseManagedSpell` -\n"
    "the member and its Phase 6 rank (0.2.8241), the four bind options and their record (0.2.8242), the pool in the\n"
    "root's Creations (0.2.8243), the Aether-owned registry and the lease (0.2.8244), leases through the emitted plans\n"
    "and `Conduit.managed_spell_meld` (0.2.8245), and the owner stamp following an ownership transfer (0.2.8246). The\n"
    "glossary, the boundary list, the guardrails, the boot, meld, transfer and cleanup sequences, four operational\n"
    "invariants, five failure modes, the code map (five new modules; every changed file remeasured, and\n"
    "`spell_system_states.py`, three lines stale since 2026-10-04), the sources and a diagram carry it; the component\n"
    "map carries the per-component contracts. Open for the owner: stamping versions staged before conjure.\n\n",
)

added = [l for l in text.splitlines() if l not in before]
long = [l for l in added if len(l) > 120 and "`src/" not in l and "src/melder" not in l]
assert not long, long
DOC.write_text(text, encoding="utf-8")
print("src_architecture updated:", len(before), "->", len(text.splitlines()), "lines; remeasured:", len(changed))
for c in changed:
    print("  ", c)
