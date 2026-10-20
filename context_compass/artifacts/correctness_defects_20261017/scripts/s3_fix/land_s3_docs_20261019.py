"""S3's system documents (melder_0, 2026-10-19): src_architecture, src_components, tests_components and
tests_architecture carry `cleanup_spell`'s contract release (0.2.8261), by patch cleanup_releases_contracts_2026_10_19.

src_architecture: an operational invariant and a fixed failure mode; the 0.2.8256 invariant's filed gap marked fixed
and its unchanged doors named; the 0.2.8231 entry's release-first sentence; the code map (three files remeasured); a
handoff entry. src_components: Spellbook Core (a threading bullet, an invariant, a failure), Conduit Runtime (the
cleanup_spell bullet, a failure), ConduitWard and Contracts (a paragraph, a responsibility, the emissions' lock
bullet, the stale `_get_spell_contract_keys` citation), a method-level flow, the code map and a handoff entry. The
tests documents: the two new modules with their records, the recounted inventory and key-file union, handoff
entries. Numeric citations were remapped before this pass (remap_s3_citations.py). All-or-nothing; `--write` flushes.
"""
import ast
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path.home() / "mnt/melder_private/context_compass/artifacts/spell_identity_20261018/scripts"))
from cc_record import Record

ARCH = "system_docs/src_architecture.md"
COMP = "system_docs/src_components.md"
TCOMP = "system_docs/tests_components.md"
TARCH = "system_docs/tests_architecture.md"
CONDUIT = "src/melder/aether/conduit/conduit.py"
BOOK = "src/melder/aether/spellbook/spellbook.py"
WARD = "src/melder/aether/conduit/conduit_ward/conduit_ward.py"
ITEST = "tests/integration/melder/aether/conduit/test_cleanup_releases_contracts_integration.py"
CTEST = "tests/component/melder/spellbook/test_spellbook_component_dispose_spell_releases_contracts_first.py"


class LandS3Docs(Record):
    """The four system documents."""

    def loc(self, rel: str) -> int:
        return len((self.REPO / rel).read_text(encoding="utf-8").splitlines())

    def def_range(self, rel: str, cls: str, meth: str) -> str:
        src = (self.REPO / rel).read_text(encoding="utf-8")
        for node in ast.parse(src).body:
            if isinstance(node, ast.ClassDef) and node.name == cls:
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == meth:
                        return f"{item.lineno}-{item.end_lineno}"
        sys.exit(f"DEF {rel} {cls}.{meth}")

    def tier_counts(self, tier: str) -> tuple:
        base = self.REPO / "tests" / tier
        py = [p for p in base.rglob("*.py") if "__pycache__" not in p.parts]
        return len(py), len([p for p in py if p.name.startswith("test_")])

    def handoff(self, rel: str, entry: str) -> None:
        text = self.read(rel)
        self.stage(rel, self.once(text, "## Context / Handoff Summary\n\n",
                                  "## Context / Handoff Summary\n\n" + entry + "\n\n", f"handoff {rel}"))

    def edit(self, rel: str, old: str, new: str, label: str) -> None:
        self.stage(rel, self.once(self.read(rel), old, new, label))

    # ---- src_architecture ------------------------------------------------------------------------------------
    def architecture(self) -> None:
        invariant = (
            "- A disposed version leaves every contract first (2026-10-19, 0.2.8261;\n"
            "  STORY-2026-10-17-parked_cleanup_leaves_borrower_copies, on the owner's word, chat 2026-10-19: \"check for active\n"
            "  contracts and then cleanup\"): every `cleanup_spell` door - `Conduit.cleanup_spell` on the root conduit or a\n"
            "  lesser of its lineage, and `Spellbook.cleanup_spell`, which a conjured Book routes through its root conduit's -\n"
            "  runs `Spellbook._dispose_spell` with `release_contracts`, the `_emit_spell_disposed` of the Book's ROOT conduit\n"
            "  ward (a lesser's ward holds no contracts). `_dispose_spell` calls it once with the spell_id, after its\n"
            "  Book-locked decision and its refusals and before anything is invalidated or disposed: for every contract whose\n"
            "  owner-side Detail map holds the version - an index link's member Detail or a version grant -\n"
            "  `_uncontract_member_spell` drops the Detail and has the borrower Book remove its entry, active or parked, and\n"
            "  its borrowed id (`Spellbook._remove_contracted_spell`, whose active branch marks the borrower's contract\n"
            "  consumers, rule 2), and the contract's record is emitted again. When the index went with the version,\n"
            "  `_emit_index_destroy(index_id, ())` drops its index links after the disposal, with no member id. A refused call\n"
            "  touches no contract; a raise from the release (a borrower Book holding no entry under an owner-side Detail)\n"
            "  ends the call with nothing disposed and the in-flight mark cleared, so a retry repeats it; an unconjured Book\n"
            "  holds no contract and disposes directly. Locks: the release runs with no Book lock held and takes ward ->\n"
            "  contract -> borrower Book, the order sever and the index emissions take; no lock-order edge is added.\n"
            "  `cleanup_spell` takes no transaction, so a link or grant of the version that lands between the release and the\n"
            "  disposal is not ordered against it (pre-existing). Not changed: `cleanup_and_remove_spell` and a direct\n"
            "  `Spell.cleanup()` release nothing (a direct cleanup of a parked version is refused there, \"Spellbook could not\n"
            "  resolve the requested local spell.\"), and a grant of a parked version still adds every member id of its index\n"
            "  to the borrower's borrowed ids while its removal drops only its own (`_add_inactive_contracted_spell`).\n"
            "  EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit.cleanup_spell`,\n"
            "  `src/melder/aether/spellbook/spellbook.py:Spellbook.cleanup_spell`, `Spellbook._dispose_spell`,\n"
            "  `Spellbook.cleanup_and_remove_spell`, `Spellbook._remove_contracted_spell`,\n"
            "  `Spellbook._add_inactive_contracted_spell` and\n"
            "  `src/melder/aether/conduit/conduit_ward/conduit_ward.py:ConduitWard._emit_spell_disposed`,\n"
            "  `ConduitWard._uncontract_member_spell`, `ConduitWard._emit_index_destroy`.\n")
        self.edit(ARCH, "## Operational Invariants\n", "## Operational Invariants\n" + invariant, "arch invariant")
        failure = (
            "- Fixed in 0.2.8261: a lender's `cleanup_spell` no longer leaves its borrowers a record of the version. A parked\n"
            "  version whose index survived stayed with every index-link borrower - a parked entry holding the cleaned Spell,\n"
            "  its borrowed id and the owner-side member Detail, past the borrower's own `remove_index_from_contract` - and a\n"
            "  version grant, parked or active, stayed on its borrower, whose meld of a disposed active grant raised\n"
            "  AttributeError \"'Spell' object has no attribute '_resolvable'\"; a later notch to the class staged again raised\n"
            "  AttributeError in the borrower fan-out after the lender's switch, leaving the borrower with no active version;\n"
            "  the Spellbook's own `cleanup_spell` told no borrower, not even of a destroyed index, and a lesser conduit's\n"
            "  call reached no contract. Every borrower now drops the version before it is disposed, and a meld of a disposed\n"
            "  granted version raises KeyError \"[MELD] No spell found with spell_id: <id>\" as for a version it never held.\n"
            "  EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit.cleanup_spell` and\n"
            "  `src/melder/aether/conduit/conduit_ward/conduit_ward.py:ConduitWard._emit_spell_disposed`.\n")
        self.edit(ARCH, "## Failure Modes and Error Paths\n", "## Failure Modes and Error Paths\n" + failure, "arch failure")
        self.edit(
            ARCH,
            "  `cleanup_spell` leaves index-link borrowers a copy (STORY-2026-10-17-parked_cleanup_leaves_borrower_copies)\n",
            "  `cleanup_spell` left index-link borrowers a copy (fixed in 0.2.8261;\n"
            "  STORY-2026-10-17-parked_cleanup_leaves_borrower_copies)\n",
            "arch 0.2.8256 gap")
        self.edit(
            ARCH,
            "Not changed: the direct doors send\n"
            "  index-link borrowers no emission. Book teardown retires the parked versions since 0.2.8260\n"
            "  (STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned).\n",
            "Not changed: the direct doors\n"
            "  (`cleanup_and_remove_spell`, a direct `Spell.cleanup()`) send index-link borrowers no emission; `cleanup_spell`,\n"
            "  through a conduit or the Book, releases the version from every contract since 0.2.8261 (entry above).\n"
            "  Book teardown retires the parked versions since 0.2.8260\n"
            "  (STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned).\n",
            "arch 0.2.8256 doors")
        self.edit(
            ARCH,
            "  from its decision under the Book lock. Bind's cross-frame sweep and `_get_all_spell_ids` read\n"
            "  `Aether._aetheric_frame_view`,",
            "  from its decision under the Book lock; since 0.2.8261 it first releases the version from every contract of\n"
            "  the Book's root ward (`_emit_spell_disposed`, under the ward lock). Bind's cross-frame sweep and\n"
            "  `_get_all_spell_ids` read `Aether._aetheric_frame_view`,",
            "arch 0.2.8231")
        # The code map: three files remeasured, their notes extended.
        book_n, conduit_n, ward_n = self.loc(BOOK), self.loc(CONDUIT), self.loc(WARD)
        self.edit(ARCH, "  end_line: 7903\n  loc: 7903\n  verified_at: 2026-10-19T01:22:58Z\n  note: Spellbook core",
                  f"  end_line: {book_n}\n  loc: {book_n}\n  verified_at: {self.now}\n  note: Spellbook core",
                  "arch map spellbook")
        self.edit(ARCH,
                  "    the Book's parked versions and cleans the indexes only they hold (0.2.8260).\n"
                  "- path: `src/melder/aether/spellbook/spellbook_creation_system.py`",
                  "    the Book's parked versions and cleans the indexes only they hold (0.2.8260). `cleanup_spell` goes\n"
                  "    through the root conduit once conjured, and `_dispose_spell` runs the caller's `release_contracts`\n"
                  "    between its decision and its disposal (0.2.8261).\n"
                  "- path: `src/melder/aether/spellbook/spellbook_creation_system.py`",
                  "arch map spellbook note")
        self.edit(ARCH, "  end_line: 7867\n  loc: 7867\n  verified_at: 2026-10-17T23:03:04Z\n",
                  f"  end_line: {conduit_n}\n  loc: {conduit_n}\n  verified_at: {self.now}\n", "arch map conduit")
        self.edit(ARCH,
                  "    `_resolve_transfer_spell` takes the explicit index step (0.2.8253).\n"
                  "- path: `src/melder/aether/conduit/conduit_pool.py`",
                  "    `_resolve_transfer_spell` takes the explicit index step (0.2.8253). `cleanup_spell` releases the version\n"
                  "    from every contract of the Book's root conduit before the disposal and sends the index destroy with no\n"
                  "    member id (0.2.8261).\n"
                  "- path: `src/melder/aether/conduit/conduit_pool.py`",
                  "arch map conduit note")
        self.edit(ARCH, "  end_line: 3999\n  loc: 3999\n  verified_at: 2026-10-17T23:03:04Z\n",
                  f"  end_line: {ward_n}\n  loc: {ward_n}\n  verified_at: {self.now}\n", "arch map ward")
        self.edit(ARCH,
                  "    the grant check and the outbound listing resolve exactly (0.2.8253).\n"
                  "- path: `src/melder/aether/conduit/conduit_ward/policies/policies.py`",
                  "    the grant check and the outbound listing resolve exactly (0.2.8253). `_emit_spell_disposed`, the\n"
                  "    per-contract release of a disposed version (0.2.8261).\n"
                  "- path: `src/melder/aether/conduit/conduit_ward/policies/policies.py`",
                  "arch map ward note")
        self.handoff(ARCH, (
            "2026-10-19 cleanup releases the contracts (0.2.8261; STORY-2026-10-17-parked_cleanup_leaves_borrower_copies, on\n"
            "the owner's word \"check for active contracts and then cleanup\"): every `cleanup_spell` door takes the version\n"
            "out of every contract of the Book's root conduit - an index link's member Detail or a version grant, with the\n"
            "borrower's entry and borrowed id - after the Book's decision and before its disposal, and the Spellbook's own\n"
            "door goes through its root conduit once conjured. A new operational invariant, a fixed failure mode and the code\n"
            "map (three files remeasured) carry it; the 0.2.8256 invariant's filed gap is marked fixed and its unchanged\n"
            "doors are named, and the 0.2.8231 entry says the release comes first; the component map carries the\n"
            "per-component contracts. Numeric citations into conduit.py and spellbook.py past the edits moved 25 and 42\n"
            "lines and were remapped line by line; none into conduit_ward.py moved here."))

    # ---- src_components --------------------------------------------------------------------------------------
    def components(self) -> None:
        self.edit(
            COMP,
            "  short `_lock` section (about 0.1 us on a 20 us disposal, measured).\n",
            "  short `_lock` section (about 0.1 us on a 20 us disposal, measured).\n"
            "- A conjured Book's `cleanup_spell` goes through its root conduit's `cleanup_spell` (0.2.8261), which hands\n"
            "  `_dispose_spell` its `release_contracts` hook - the root ward's `_emit_spell_disposed`. `_dispose_spell` calls\n"
            "  the hook once with the spell_id, first inside its `try`: after the decision's `_lock` section (the in-flight\n"
            "  mark set) and the refusals, with no `_lock` held, before the invalidation and the disposal take `_lock` again.\n"
            "  A refusal raises before the hook; a raise from the hook disposes nothing and the `finally` clears the mark. An\n"
            "  unconjured Book has no conduit and no contract, so its `cleanup_spell` calls `_dispose_spell` with no hook.\n",
            "comp core threading")
        self.edit(
            COMP,
            "- A Book's teardown retires its parked versions (0.2.8260;\n"
            "  STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned): after its loop",
            "- A disposed version leaves every contract first (0.2.8261;\n"
            "  STORY-2026-10-17-parked_cleanup_leaves_borrower_copies): on a conjured Book every `cleanup_spell` releases the\n"
            "  version from every contract of its root conduit before `_dispose_spell` invalidates or disposes it (Conduit\n"
            "  Runtime; ConduitWard and Contracts), and a refused disposal releases nothing. `cleanup_and_remove_spell` and a\n"
            "  direct `Spell.cleanup()` release nothing (not changed).\n"
            "  EVIDENCE: `src/melder/aether/spellbook/spellbook.py:Spellbook.cleanup_spell` and `Spellbook._dispose_spell`.\n"
            "- A Book's teardown retires its parked versions (0.2.8260;\n"
            "  STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned): after its loop",
            "comp core invariant")
        self.edit(
            COMP,
            "  of the same spell runs (0.2.8232; before, both disposed it and one failed part-way).\n",
            "  of the same spell runs (0.2.8232; before, both disposed it and one failed part-way).\n"
            "- An exception from `release_contracts` - RuntimeError \"Spell version <id> not found for conduit ID <lender>.\"\n"
            "  when a borrower Book holds no entry for the version under an owner-side Detail - ends `cleanup_spell` with\n"
            "  nothing disposed and the in-flight mark cleared; a retry repeats the release (0.2.8261).\n",
            "comp core failure")
        self.edit(
            COMP,
            "- `cleanup_spell` takes no lock of its own and reads nothing about the spell before the Book decides (0.2.8231): it\n"
            "  emits `_emit_index_destroy(index_id, (spell_id,))` exactly when `Spellbook._dispose_spell` reports the index it\n"
            "  destroyed. The emission walks the ward's contracts under the ward lock, so a concurrent `link` or `sever_link` of\n"
            "  this conduit waits for it. The old unlocked pre-read of `spell.spell_index` raised AttributeError for a disposed\n"
            "  spell and could disagree with what the Book then did. Of two overlapping calls for one spell the Book disposes it\n"
            "  once and refuses the other (0.2.8232), so the destroy is emitted once.\n",
            "- `cleanup_spell` takes no lock of its own and reads nothing about the spell before the Book decides (0.2.8231). It\n"
            "  takes the ward of the Book's ROOT conduit - the contracts live there; a lesser's ward holds none - and hands its\n"
            "  `_emit_spell_disposed` to `Spellbook._dispose_spell` as `release_contracts`, so every contract drops the version\n"
            "  between the Book's decision and its disposal (0.2.8261); it emits `_emit_index_destroy(index_id, ())` - no\n"
            "  member id, the version having left every contract - exactly when the Book reports the index it destroyed (until\n"
            "  0.2.8261 `(spell_id,)` on the calling conduit's own ward, and nothing else). Both walk the root ward's contracts\n"
            "  under the ward lock, so a concurrent `link` or `sever_link` of the root waits for them. The old unlocked\n"
            "  pre-read of `spell.spell_index` raised AttributeError for a disposed spell and could disagree with what the\n"
            "  Book then did. Of two overlapping calls for one spell the Book disposes it once and refuses the other\n"
            "  (0.2.8232), so each contract drops the version once and the destroy is emitted once.\n",
            "comp conduit threading")
        self.edit(
            COMP,
            "  dispose the parked versions, or move them out with `remove_from_spell_index`).\n- ExceptionGroup from `cleanup()`",
            "  dispose the parked versions, or move them out with `remove_from_spell_index`).\n"
            "- RuntimeError from `cleanup_spell`'s contract release when a borrower Book holds no entry for the version under\n"
            "  an owner-side Detail (\"Spell version <id> not found for conduit ID <lender>.\"): nothing is disposed and a\n"
            "  retry repeats the release (0.2.8261).\n"
            "- ExceptionGroup from `cleanup()`",
            "comp conduit failure")
        self.edit(
            COMP,
            "### Component: ConduitWard and Contracts\nPurpose:\n- Control-plane manager for conduit contracts and lineage links.\n\n",
            "### Component: ConduitWard and Contracts\nPurpose:\n- Control-plane manager for conduit contracts and lineage links.\n\n"
            "Contracts released on a disposal (2026-10-19, 0.2.8261; cleanup_releases_contracts_2026_10_19):\n"
            "`_emit_spell_disposed(spell_id)` is the owner-side emission of a disposed version. Under the ward lock it walks\n"
            "`_contracts`; for each contract whose owner-side Detail map holds the version (read under the contract lock) -\n"
            "an index link's member Detail or a version grant - it calls `_uncontract_member_spell(contract, self, spell_id)`,\n"
            "which drops and cleans the Detail and has the borrower Book remove its entry, active or parked, and its borrowed\n"
            "id (`Spellbook._remove_contracted_spell`; an active entry marks the borrower's contract consumers), then emits\n"
            "each changed contract's record again after the lock. A contract that holds no Detail for the version is\n"
            "untouched, and none is severed (an empty contract is a live link with nothing shared). `Conduit.cleanup_spell`\n"
            "calls it on the Book's root ward through `Spellbook._dispose_spell`, after the Book's decision and before its\n"
            "disposal; an index that dies with the version then leaves its links through `_emit_index_destroy` with no member\n"
            "id. `_uncontract_member_spell` is idempotent on the owner side only: the borrower's removal raises when its Book\n"
            "holds no entry for the version, and the cleanup then disposes nothing.\n"
            "EVIDENCE: `src/melder/aether/conduit/conduit_ward/conduit_ward.py:ConduitWard._emit_spell_disposed`,\n"
            "`ConduitWard._uncontract_member_spell`, `ConduitWard._emit_index_destroy` and\n"
            "`src/melder/aether/conduit/conduit.py:Conduit.cleanup_spell`.\n\n",
            "comp ward paragraph")
        self.edit(COMP, "- Update Spellbook contracted maps when links change.\n",
                  "- Update Spellbook contracted maps when links change.\n"
                  "- Release a disposed version from every contract that holds it (`_emit_spell_disposed`, 0.2.8261).\n",
                  "comp ward responsibility")
        self.edit(
            COMP,
            "- The four owner-side index emissions walk `_contracts` under the ward lock (0.2.8231), the lock link\n"
            "  (`_create_new_contract`) and sever (`_remove_contract`) write it under.",
            "- The four owner-side index emissions and `_emit_spell_disposed` (0.2.8261) walk `_contracts` under the ward lock\n"
            "  (0.2.8231), the lock link (`_create_new_contract`) and sever (`_remove_contract`) write it under.",
            "comp ward threading")
        keys = self.def_range(WARD, "ConduitWard", "_get_spell_contract_keys")
        self.edit(COMP, "  EVIDENCE: src/melder/aether/conduit/conduit_ward/conduit_ward.py:2580-2691.\n",
                  f"  EVIDENCE: src/melder/aether/conduit/conduit_ward/conduit_ward.py:{keys}.\n", "comp keys citation")
        flow = (
            "### Flow: Conduit.cleanup_spell -> Contracts Released -> Spellbook._dispose_spell\n"
            "1. `Conduit.cleanup_spell(spell=...)` on a root or a lesser of its lineage (a conjured Book's\n"
            "   `Spellbook.cleanup_spell` comes here through its root conduit): `ward = self._spellbook._conduit._conduit_ward`.\n"
            "2. `Spellbook._dispose_spell(spell, release_contracts=ward._emit_spell_disposed)`: under `_lock`, refuse an\n"
            "   overlapping call, read ownership, activity and sole membership and mark the spell id; refuse a foreign,\n"
            "   disposed or active multi-member spell with nothing changed.\n"
            "3. Inside the `try`, with no `_lock` held: `release_contracts(spell_id)` -> `ConduitWard._emit_spell_disposed`:\n"
            "   under the ward lock, each contract whose owner-side Detail map holds the version ->\n"
            "   `_uncontract_member_spell` (the Detail dropped; `Spellbook._remove_contracted_spell` on the borrower) ->\n"
            "   the changed contracts' records after the lock.\n"
            "4. The disposal as before: an active version invalidated, then `cleanup_and_remove_spell`; a parked one dropped\n"
            "   from the maps and its index, the index destroyed when emptied; the destroyed index's id or None returned;\n"
            "   the mark cleared in the `finally`.\n"
            "5. When an index id came back: `ConduitWard._emit_index_destroy(index_id, ())` - each borrower untracks the\n"
            "   index and the IndexDetail is dropped.\n"
            "EVIDENCE: `src/melder/aether/conduit/conduit.py:Conduit.cleanup_spell`,\n"
            "`src/melder/aether/spellbook/spellbook.py:Spellbook._dispose_spell` and\n"
            "`src/melder/aether/conduit/conduit_ward/conduit_ward.py:ConduitWard._emit_spell_disposed`.\n\n")
        self.edit(COMP, "### Flow: SpellSpace Scoped Meld\n", flow + "### Flow: SpellSpace Scoped Meld\n", "comp flow")
        book_n, conduit_n, ward_n = self.loc(BOOK), self.loc(CONDUIT), self.loc(WARD)
        self.edit(COMP,
                  "- path: `src/melder/aether/spellbook/spellbook.py`\n  start_line: 1\n  end_line: 7903\n  loc: 7903\n"
                  "  verified_at: 2026-10-19T01:22:58Z\n",
                  f"- path: `src/melder/aether/spellbook/spellbook.py`\n  start_line: 1\n  end_line: {book_n}\n"
                  f"  loc: {book_n}\n  verified_at: {self.now}\n", "comp map spellbook")
        self.edit(COMP,
                  "- path: `src/melder/aether/conduit/conduit.py`\n  start_line: 1\n  end_line: 7867\n  loc: 7867\n"
                  "  verified_at: 2026-10-17T23:12:45Z\n",
                  f"- path: `src/melder/aether/conduit/conduit.py`\n  start_line: 1\n  end_line: {conduit_n}\n"
                  f"  loc: {conduit_n}\n  verified_at: {self.now}\n", "comp map conduit")
        self.edit(COMP,
                  "- path: `src/melder/aether/conduit/conduit_ward/conduit_ward.py`\n  start_line: 1\n  end_line: 3999\n"
                  "  loc: 3999\n  verified_at: 2026-10-17T23:12:45Z\n",
                  f"- path: `src/melder/aether/conduit/conduit_ward/conduit_ward.py`\n  start_line: 1\n  end_line: {ward_n}\n"
                  f"  loc: {ward_n}\n  verified_at: {self.now}\n", "comp map ward")
        self.handoff(COMP, (
            "2026-10-19 cleanup releases the contracts (0.2.8261; STORY-2026-10-17-parked_cleanup_leaves_borrower_copies):\n"
            "Spellbook Core says a conjured Book's `cleanup_spell` goes through its root conduit and `_dispose_spell` runs\n"
            "the `release_contracts` hook between its decision and its disposal, with an invariant and the hook's failure;\n"
            "the Conduit Runtime's `cleanup_spell` bullet names the root ward, the release and the destroy with no member\n"
            "id, with the release's failure; ConduitWard and Contracts gains the `_emit_spell_disposed` paragraph, a\n"
            "responsibility and its place among the ward-locked emissions; a method-level flow follows the call. The code\n"
            "map remeasures conduit.py, spellbook.py and conduit_ward.py. Numeric citations into conduit.py and spellbook.py\n"
            "past the edits were remapped line by line, and the `_get_spell_contract_keys` citation, stale before this\n"
            f"lane, points at the method again ({keys})."))

    # ---- tests documents -------------------------------------------------------------------------------------
    def tests_docs(self) -> None:
        comp_py, comp_t = self.tier_counts("component")
        integ_py, integ_t = self.tier_counts("integration")
        unit_py, unit_t = self.tier_counts("unit")
        total = comp_t + integ_t + unit_t
        if (comp_py, comp_t, integ_py, integ_t) != (170, 168, 185, 178) or total != 860:
            sys.exit(f"COUNTS {comp_py} {comp_t} {integ_py} {integ_t} {unit_py} {unit_t} {total}")
        self.edit(
            TCOMP,
            "  first tear down as before\nKey Files (C1):\n",
            "  first tear down as before\n"
            "- a disposed version leaves every contract first (0.2.8261;\n"
            "  `test_cleanup_releases_contracts_integration.py`, 10 tests): in a dynamic world with English active and\n"
            "  French parked on a lender's index, contracted whole by a linked borrower, the lender's `cleanup_spell(French)`\n"
            "  leaves the borrower no entry, borrowed id or member Detail of French, and the borrower's unlink afterwards\n"
            "  leaves nothing; a notch to French staged again completes for the borrower, which melds it; a grant of parked\n"
            "  French and a grant of Solo, the sole active member of its index, leave with their version (a meld of the\n"
            "  disposed Solo raises KeyError); the Spellbook's own `cleanup_spell` and a lesser conduit's release the root's\n"
            "  contracts, for a parked member and for a sole member whose index link goes too; the borrower drops the\n"
            "  version while it is still live; and a refused cleanup of the active English changes no contract\n"
            "Key Files (C1):\n",
            "tcomp integ protects")
        self.edit(
            TCOMP,
            "- `tests/integration/melder/aether/conduit/test_spell_id_lookup_returns_that_spell_integration.py` (2026-10-17)\n"
            "\n### Subcomponent: Conduit Integration Cluster",
            "- `tests/integration/melder/aether/conduit/test_spell_id_lookup_returns_that_spell_integration.py` (2026-10-17)\n"
            f"- `{ITEST}` (2026-10-19)\n"
            "\n### Subcomponent: Conduit Integration Cluster",
            "tcomp integ key")
        self.edit(
            TCOMP,
            "  cleanup; and a binding changed under one spell_id is another world to the creation cache\nKey Files (C1):\n",
            "  cleanup; and a binding changed under one spell_id is another world to the creation cache\n"
            "- the contracts-first order of a disposal (0.2.8261;\n"
            "  `test_spellbook_component_dispose_spell_releases_contracts_first.py`, 3 tests): `_dispose_spell` runs its\n"
            "  `release_contracts` hook with the spell_id between the decision and the disposal and never for a refused\n"
            "  disposal, and a raising hook disposes nothing, clears the in-flight mark and lets a retry complete\n"
            "Key Files (C1):\n",
            "tcomp comp protects")
        self.edit(
            TCOMP,
            "- `tests/component/melder/spellbook/test_spellbook_component_spell_identity.py` (one object, one spell, 2026-10-18)\n",
            "- `tests/component/melder/spellbook/test_spellbook_component_spell_identity.py` (one object, one spell, 2026-10-18)\n"
            f"- `{CTEST}` (2026-10-19)\n",
            "tcomp comp key")
        self.edit(TCOMP, "- 167 `test_*.py` modules among 169 `.py` files (recounted 2026-10-18)\n",
                  f"- {comp_t} `test_*.py` modules among {comp_py} `.py` files (recounted 2026-10-19)\n", "tcomp comp count")
        self.edit(TCOMP, "- 177 `test_*.py` modules among 184 `.py` files (recounted 2026-10-19);",
                  f"- {integ_t} `test_*.py` modules among {integ_py} `.py` files (recounted 2026-10-19);",
                  "tcomp integ count")
        self.edit(TCOMP, "builders - not every `test_*.py` module beneath it. The 858 test modules of the\n",
                  f"builders - not every `test_*.py` module beneath it. The {total} test modules of the\n", "tcomp total")
        crec = (f"- path: `{CTEST}`\n  start_line: 1\n  end_line: {self.loc(CTEST)}\n  loc: {self.loc(CTEST)}\n"
                f"  verified_at: {self.now}\n"
                "  note: `_dispose_spell` runs `release_contracts` between its decision and its disposal, never for a\n"
                "    refusal; a raising hook disposes nothing and a retry completes (0.2.8261).\n")
        self.edit(TCOMP,
                  "  note: one object, one spell, over real wiring (0.2.8257-0.2.8258).\n"
                  "- path: `tests/component/melder/spellbook/test_conjure_refusal_leaves_frame_unsettled_component.py`",
                  "  note: one object, one spell, over real wiring (0.2.8257-0.2.8258).\n" + crec +
                  "- path: `tests/component/melder/spellbook/test_conjure_refusal_leaves_frame_unsettled_component.py`",
                  "tcomp comp record")
        irec = (f"- path: `{ITEST}`\n  start_line: 1\n  end_line: {self.loc(ITEST)}\n  loc: {self.loc(ITEST)}\n"
                f"  verified_at: {self.now}\n"
                "  note: a lender's cleanup_spell takes the version out of every contract first - index-link members and\n"
                "    version grants, from every door - and a refused cleanup changes none (0.2.8261).\n")
        self.edit(TCOMP,
                  "    `cleanup()` returns afterwards; active-only and disposed-first controls (0.2.8260).\n"
                  "- path: `tests/integration/melder/aether/conduit/test_notch_spell_by_id_integration.py`",
                  "    `cleanup()` returns afterwards; active-only and disposed-first controls (0.2.8260).\n" + irec +
                  "- path: `tests/integration/melder/aether/conduit/test_notch_spell_by_id_integration.py`",
                  "tcomp integ record")
        self.edit(TCOMP,
                  "- `tests/integration/melder/spellbook/test_book_teardown_retires_parked_versions_integration.py`\n"
                  "- direct filesystem inventory of `tests/`",
                  "- `tests/integration/melder/spellbook/test_book_teardown_retires_parked_versions_integration.py`\n"
                  f"- `{ITEST}`\n- `{CTEST}`\n"
                  "- direct filesystem inventory of `tests/`",
                  "tcomp sources")
        union = self.key_file_union()
        if union != 276:
            sys.exit(f"UNION {union}")
        self.edit(TCOMP, "above - 274 paths (recounted 2026-10-19)", f"above - {union} paths (recounted 2026-10-19)",
                  "tcomp union")
        self.handoff(TCOMP, (
            "2026-10-19 cleanup releases the contracts (0.2.8261; STORY-2026-10-17-parked_cleanup_leaves_borrower_copies):\n"
            "the Spellbook Integration Cluster gains `test_cleanup_releases_contracts_integration.py` (10 tests: a parked\n"
            "index-link member and the unlink after it, a notch to the version staged again, a parked and a sole granted\n"
            "version, the Spellbook's own door parked and sole, a lesser conduit's call, the live-version order, a refused\n"
            "cleanup) and the Spellbook Runtime And Binding Component Cluster\n"
            "`test_spellbook_component_dispose_spell_releases_contracts_first.py` (3 tests: the hook's place, never on a\n"
            "refusal, a raising hook), each a key file with a code-map record. Counts are recounted from disk (component\n"
            f"{comp_t} of {comp_py}, integration {integ_t} of {integ_py}; {total} test modules in the three tiers); the core "
            f"key-file union is {union}\npaths."))
        self.edit(TARCH, "- `component/`: 169 `.py` files, 167 of them `test_*.py` (143, 81)\n",
                  f"- `component/`: {comp_py} `.py` files, {comp_t} of them `test_*.py` (143, 81)\n", "tarch comp")
        self.edit(TARCH, "- `integration/`: 184 `.py` files, 177 of them `test_*.py` (149, 88)\n",
                  f"- `integration/`: {integ_py} `.py` files, {integ_t} of them `test_*.py` (149, 88)\n", "tarch integ")
        self.edit(TARCH, "(pycache excluded); the three tiers' 858 `test_*.py`\n",
                  f"(pycache excluded); the three tiers' {total} `test_*.py`\n", "tarch total")
        self.handoff(TARCH, (
            f"2026-10-19 cleanup releases the contracts (0.2.8261): the inventory is recounted from disk (component {comp_py}\n"
            f"`.py`, {comp_t} of them `test_*.py`; integration {integ_py}, {integ_t}; {total} test modules in the three "
            "tiers) - the lane\nadds one component module (the contracts-first order of a disposal) and one integration "
            "module (a disposed\nversion leaving every contract), catalogued in `tests_components`. No tier, conftest, "
            "declared marker or\nshared support module changes, and no extent in this map moves."))
        self.set_field(TCOMP, "Updated")

    def key_file_union(self) -> int:
        lines = self.read(TCOMP).split("\n")
        stop = lines.index("## C1 Code Map (Core)")
        paths = set()
        inside = False
        for line in lines[:stop]:
            if line.startswith("Key Files (C1):"):
                inside = True
                continue
            if inside:
                if line.startswith("- "):
                    match = re.match(r"- `([^`]+)`", line)
                    if match:
                        paths.add(match.group(1))
                    continue
                if line.startswith("  "):
                    continue
                inside = False
        return len(paths)

    def run(self) -> None:
        self.architecture()
        self.components()
        self.tests_docs()
        for rel in (ARCH, COMP, TCOMP, TARCH):
            text = self.read(rel)
            if "\r" in text:
                sys.exit(f"CR {rel}")
            print(rel, len(text.split("\n")))


def main() -> None:
    record = LandS3Docs("land_s3_docs")
    record.run()
    if "--write" not in sys.argv:
        print("CHECK OK", record.now, sorted(record.staged))
        return
    record.flush()


if __name__ == "__main__":
    main()
