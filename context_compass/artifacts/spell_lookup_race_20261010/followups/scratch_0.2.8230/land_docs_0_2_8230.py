"""Land the 0.2.8230 docs: src_architecture, src_components, release note. Exact anchors; keeps EOL. usage: <repo>"""
import datetime, pathlib, re, sys

REPO = pathlib.Path(sys.argv[1])
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
CHANGED = [
    "src/melder/aether/spellbook/spellbook.py",
    "src/melder/aether/spellbook/spellbook_creation_system.py",
    "src/melder/aether/spellbook/bind/spell_index.py",
    "src/melder/aether/conduit/conduit.py",
    "src/melder/aether/conduit/conduit_ward/transfer/transfer_of_ownership.py",
    "src/melder/nexus/rift/command_system/command_system.py",
]
LOC = {rel: len((REPO / rel).read_bytes().decode("utf-8").splitlines()) for rel in CHANGED}


def edit(rel, ops):
    path = REPO / rel
    data = path.read_bytes().decode("utf-8")
    crlf = "\r\n" in data
    text = data.replace("\r\n", "\n")
    for kind, anchor, payload in ops:
        if kind == "codemap":
            pattern = re.compile(r"(- path: `" + re.escape(anchor) + r"`\n  start_line: 1\n  end_line: )\d+(\n  loc: )\d+"
                                 r"(\n  verified_at: )\S+\n")
            text, n = pattern.subn(lambda m: f"{m.group(1)}{payload}{m.group(2)}{payload}{m.group(3)}{NOW}\n", text)
            if n != 1:
                raise SystemExit(f"{rel}: code map entry x{n} for {anchor}")
            continue
        if text.count(anchor) != 1:
            raise SystemExit(f"{rel}: anchor x{text.count(anchor)}: {anchor[:70]!r}")
        if kind == "before":
            text = text.replace(anchor, payload + anchor, 1)
        elif kind == "after":
            text = text.replace(anchor, anchor + payload, 1)
        elif kind == "replace":
            text = text.replace(anchor, payload, 1)
    path.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
    print(f"{rel}: {len(ops)} edits ({'CRLF' if crlf else 'LF'})")


ARCH_INVARIANT = """- Spell-map walks (2026-10-11, 0.2.8230): every writer of `Spellbook._spells`, `_lookup_spells`, `_spells_by_id`
  and `_spell_id_pool` holds the Book lock - bind now publishes all four inside one `with self._lock` block (its
  frame lookup claim and its callbacks stay outside), as removal, notch, index destruction and ownership transfer
  already did - so a walk that holds the Book lock never meets a resize. A walk that cannot hold it iterates a
  one-call snapshot (`list(...)`, exact under concurrent writers on 3.14t, where a comprehension or
  `next(iter(...))` over the live view is not): the book-wide phase factories and the resolution cleanup pass,
  which public `Conduit.validate_resolution` runs with no Book lock, `inspect_spell` over another Book, the
  contracted-spell lookup and the transfer impact walk. `Conduit.get_spell_permissions` and
  `CommandSystem.get_spell_by_id` resolve lineages through `Spellbook.find_spell_by_id` instead of walking.
  `SpellIndex.has_spell` repeats its cleaned check under the index lock, so a racing cleanup raises the documented
  RuntimeError, never AttributeError; walks over indexes the caller neither owns nor locks (contracted maps,
  contract details) probe with `SpellIndex._has_spell_unless_cleaned`, which answers False for a cleaned index.
  No reader-side Book lock was added (conjure holds that lock while phase workers and hooks run).
  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook.bind`, `Spellbook._find_contracted_spell_by_id`,
  `src/melder/aether/spellbook/bind/spell_index.py:SpellIndex.has_spell`, `SpellIndex._has_spell_unless_cleaned`,
  `src/melder/aether/conduit/conduit_ward/contract/details.py:Detail.has_spell`, `IndexDetail.has_spell` and
  `src/melder/aether/spellbook/spellbook_creation_system.py:SpellbookCreationSystem.cleanup_phase_artifacts_after_resolution`.
"""

ARCH_FAILURE = """- Concurrent binds and removals no longer make `Conduit.validate_resolution`, `Conduit.get_spell_permissions`, the
  Rift command surface's spell lookup, `inspect_spell`, contract lookups or the transfer impact check raise
  RuntimeError "dictionary changed size during iteration", and a walk under the Book lock no longer meets bind's
  insert mid-walk (fixed in 0.2.8230). `SpellIndex.has_spell` racing the index's cleanup raises its documented
  RuntimeError "SpellIndex has already been cleaned." instead of AttributeError "... has no attribute
  '_spells_in_index'", and a contract detail over an index its owner cleaned answers False instead of raising.
  EVIDENCE: `src/melder/aether/spellbook/bind/spell_index.py:SpellIndex.has_spell` and
  `src/melder/aether/spellbook/spellbook.py:Spellbook.bind`.
- `Conduit.get_spell_by_id` and `Conduit.get_conduit_by_spell_id` raise ValueError "Spell version <id> not found in
  any conduit." for an id no conduit in the frame claims - unknown or removed, bound in another frame, its owner
  cleaned, or a lineage between owners while an ownership transfer runs - and "Aetheric frame '<name>' does not
  exist." for an unknown frame. They always did; until 0.2.8230 their docstrings said they return None. A `get_*`
  lookup raises on a miss and a `find_*` lookup returns None (owner decision 2026-10-11).
  EVIDENCE: `src/melder/aether/aether.py:Aether._get_conduit_by_spell_id` and
  `src/melder/aether/spellbook/spellbook.py:Spellbook._get_conduit_by_spell_id`.
"""

ARCH_HANDOFF = """2026-10-11 spell-map walks (0.2.8230): bind publishes its four maps under the Book lock; the walks of a Book's spells
that cannot hold that lock (the `validate_resolution` phases and cleanup pass, foreign-Book inspection, contracted
lookups, the transfer impact walk) take one-call snapshots; `get_spell_permissions` and the command surface's spell
lookup read the id maps; `SpellIndex.has_spell` re-checks cleaned under its lock and contract details probe through
the new `SpellIndex._has_spell_unless_cleaned`. `Conduit.get_spell_by_id` and `get_conduit_by_spell_id` document
the ValueError they raise for an unclaimed id (owner decision: `get_*` raises, `find_*` returns None). The
operational invariants, the failure modes and the code map carry it; the component map carries the per-component
rules.

"""

COMP_CORE_THREADING = """- Every writer of `_spells`, `_lookup_spells`, `_spells_by_id` and `_spell_id_pool` holds `_lock` (0.2.8230):
  `bind` publishes the four maps inside one `with self._lock` block after its frame lookup claim - the block
  re-enters the lock `_register_owned_spell_id` always took there, so no lock-order edge is new - and the bind
  callbacks stay outside it. A walk under `_lock` (`_find_spell`, `_find_spell_index_by_index_id`,
  `_check_all_spells`, `_apply_notch`, the transfer and cluster walks) therefore never meets a resize. Walks without
  `_lock` take a one-call snapshot (`list(...)`, exact under concurrent writers on 3.14t; a comprehension or
  `next(iter(...))` over the live view is not): `inspect_spell` over another Book, `_find_contracted_spell_by_id`
  (which probes with `SpellIndex._has_spell_unless_cleaned`) and the book-wide factories and resolution cleanup pass
  of `SpellbookCreationSystem`. The factories need it because public `Conduit.validate_resolution` runs
  `_run_structural_phases` and `_run_resolution_phases_for_conduit` without `_lock`, although both document a
  caller-held lock.
"""

COMP_CORE_FAILURE = """- `_get_conduit_by_spell_id` raises the Aether lookup's ValueError for an id no conduit in the frame claims; it is
  annotated `Conduit` and, until 0.2.8230, its docstring promised None, so the None checks of its internal callers
  never fire. `_get_spell_by_id_via_aether` returns None only when the owner's `find_spell_by_id` misses.
"""

COMP_BINDING_THREADING = """- `SpellIndex.has_spell` checks `_cleaned`, takes `_lock` and checks again (0.2.8230): `cleanup` marks the index
  cleaned and deletes `_spells_in_index` under that lock, so a cleanup landing between the first check and the
  acquire surfaces as the documented RuntimeError, not AttributeError. `SpellIndex._has_spell_unless_cleaned` reads
  the flag and the member set under the same lock and answers False for a cleaned index; it is the probe for walks
  over indexes the caller neither owns nor locks (`Spellbook._find_contracted_spell_by_id`, `Detail.has_spell`,
  `IndexDetail.has_spell`).
"""

COMP_BINDING_FAILURE = """- RuntimeError "SpellIndex has already been cleaned." from `has_spell` on a cleaned index, also when the cleanup
  races the call (0.2.8230; that race raised AttributeError).
"""

COMP_CONDUIT_THREADING = """- `get_spell_permissions` takes no conduit lock and resolves through `Spellbook.find_spell_by_id` (0.2.8230); it used
  to walk the Book's live index map under the conduit lock, which a bind or removal on another thread could resize
  mid-walk.
"""

COMP_CONDUIT_FAILURE = """- ValueError from `get_spell_by_id` and `get_conduit_by_spell_id` for an id no conduit in the frame claims, or for
  an unknown frame. Both search one frame (this conduit's Book frame unless another is named) and raise on a miss,
  as `get_*` lookups do; they always raised, and their docstrings say so since 0.2.8230 (owner decision
  2026-10-11; they promised None).
"""

COMP_WARD_THREADING = """- `Detail.has_spell` and `IndexDetail.has_spell` read membership through `SpellIndex._has_spell_unless_cleaned`
  (0.2.8230): the index belongs to the Book that owns the lineage, which can clean it while a contract still holds
  it, and the old unlocked read of `_spells_in_index` raised AttributeError when that cleanup won. A cleaned index
  answers False, so `_get_spell_in_contracts` and `_find_governing_index_link` pass over it.
"""

COMP_COMMAND_THREADING = """- `get_spell_by_id` resolves the spell in the owner's Book through `Spellbook.find_spell_by_id` (0.2.8230); it used
  to walk that Book's live index map, which a bind or removal on another thread could resize mid-walk.
"""

COMP_HANDOFF = """2026-10-11 spell-map walks (0.2.8230): Spellbook Core carries the rule that every writer of the four spell maps
holds `_lock` (bind's publication included) and which unlocked walks take snapshots and why (`validate_resolution`
runs the book-wide phases without the lock); the Binding Pipeline carries `has_spell`'s re-check and the
cleanup-safe probe; ConduitWard and Contracts carries the detail probes; the Conduit Runtime and the command surface
carry the id-map lookups and the documented ValueError of the Conduit spell lookups; the code map extents of the
changed files are remeasured.

"""

RELEASE_ADDITION = """The same fix reaches the other places that walked a Book's spells while other threads changed them (0.2.8230).
`Conduit.get_spell_permissions` and the Rift command surface's spell lookup now answer from the id maps too;
`Conduit.validate_resolution`, `Spellbook.inspect_spell` searching the frame's other Books, contract lookups and
the ownership-transfer impact check walk a snapshot; and a `bind` on another thread now waits for a walk that holds
the Book's lock instead of resizing the map under it. None of them can raise
`RuntimeError: dictionary changed size during iteration` any more. `SpellIndex.has_spell` racing the index's
cleanup raises its documented `RuntimeError: SpellIndex has already been cleaned.` instead of `AttributeError`, and
a contract lookup that meets an index its owner has cleaned treats it as holding nothing instead of raising.
Answers on a quiet Book are unchanged.

`Conduit.get_spell_by_id` and `Conduit.get_conduit_by_spell_id` keep raising `ValueError` for an id no conduit in
the frame claims, as `get_*` lookups do (a `find_*` lookup returns `None`); their docstrings said they return
`None`, and now document the raise. `get_conduit_by_spell_id` is annotated as returning a `Conduit`.

"""

edit("context_compass/system_docs/src_architecture.md", [
    ("before", "- Lookup by version id (2026-10-11, 0.2.8229):", ARCH_INVARIANT),
    ("before", "- `Spellbook.find_spell_by_id`, and `Conduit.get_spell_by_id` through it, no longer fail", ARCH_FAILURE),
    ("codemap", CHANGED[0], LOC[CHANGED[0]]),
    ("codemap", CHANGED[1], LOC[CHANGED[1]]),
    ("codemap", CHANGED[2], LOC[CHANGED[2]]),
    ("codemap", CHANGED[3], LOC[CHANGED[3]]),
    ("codemap", CHANGED[4], LOC[CHANGED[4]]),
    ("codemap", CHANGED[5], LOC[CHANGED[5]]),
    ("replace", "  note: Spellbook core and conjure pipeline; `find_spell_by_id` answers from the id maps (0.2.8229).\n",
     "  note: Spellbook core and conjure pipeline; `find_spell_by_id` answers from the id maps (0.2.8229); bind\n"
     "    publishes its spell maps under the Book lock (0.2.8230).\n"),
    ("replace", "    the recorded world stamp (0.2.8220).\n",
     "    the recorded world stamp (0.2.8220); the book-wide factories and the cleanup pass walk snapshots (0.2.8230).\n"),
    ("replace", "  note: stable index that categorizes/targets spells and holds the active\n    selected spell.\n",
     "  note: stable index that categorizes/targets spells and holds the active\n    selected spell; `has_spell` re-checks"
     " cleaned under its lock and `_has_spell_unless_cleaned`\n    is the cleanup-safe probe (0.2.8230).\n"),
    ("before", "2026-10-11 lookup by version id (0.2.8229): `Spellbook.find_spell_by_id` answers from the Book's id maps",
     ARCH_HANDOFF),
])

edit("context_compass/system_docs/src_components.md", [
    ("before", "\nInvariants/Guarantees:\n- Conjure allowed once per Spellbook instance", COMP_CORE_THREADING),
    ("before", "- RuntimeError \"... requires the SpellbookConfiguration to be finalized BEFORE the first bind\"",
     COMP_CORE_FAILURE),
    ("before", "\nInvariants/Guarantees:\n- SpellIndex hash identity is stable and never changes.", COMP_BINDING_THREADING),
    ("after", "- ValueError if method/lambda spells are bound with non-unique existence.\n", COMP_BINDING_FAILURE),
    ("after", "  and a per-gate ticket deque for active meld tracking and close-and-drain.\n", COMP_CONDUIT_THREADING),
    ("after", "- Meld calls block while the local `CreationGate` is disabled.\n", COMP_CONDUIT_FAILURE),
    ("before", "\nInvariants/Guarantees:\n- Ward owns and cleans all lesser conduits it links.", COMP_WARD_THREADING),
    ("after", "- `Workstation` and `CommandSystem` each use an instance `RLock`.\n", COMP_COMMAND_THREADING),
    ("codemap", CHANGED[0], LOC[CHANGED[0]]),
    ("codemap", CHANGED[2], LOC[CHANGED[2]]),
    ("codemap", CHANGED[3], LOC[CHANGED[3]]),
    ("codemap", CHANGED[4], LOC[CHANGED[4]]),
    ("codemap", CHANGED[5], LOC[CHANGED[5]]),
    ("before", "2026-10-11 lookup by version id (0.2.8229): Spellbook Core carries why", COMP_HANDOFF),
])

edit("release_docs/next_version_release.md", [
    ("replace", "# Melder 0.2.8229\n", "# Melder 0.2.8230\n"),
    ("replace", "## `Spellbook.find_spell_by_id` no longer fails while other spells change\n",
     "## Spell lookups and validation no longer fail while other spells change\n"),
    ("before", "## Packaging and documentation\n", RELEASE_ADDITION),
    ("before", "- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for 0.2.8229.",
     "- The packaged system documents describe the Book-lock rule for the spell maps' writers, the snapshot rule for\n"
     "  walks that cannot hold that lock, the cleanup-safe membership probe and the documented ValueError of the\n"
     "  Conduit spell lookups.\n"),
    ("replace", "LLM bundles are rebuilt for 0.2.8229.", "LLM bundles are rebuilt for 0.2.8230."),
])
print("LOC", LOC, "NOW", NOW)
