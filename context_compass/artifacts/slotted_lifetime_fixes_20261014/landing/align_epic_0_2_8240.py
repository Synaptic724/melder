"""
Align EPIC-2026-10-14-slotted_lifetime_ownership_fixes's body with the owner's rulings (2026-10-14): the framing no
longer states a dispose-everything rule, D3's invalidation half is ruled out, the patch folder is archived. Notes are
append-only and untouched. Run from the repository root; each anchor must match once; the ticket stays LF.
"""
import pathlib

p = pathlib.Path("context_compass/tickets/epics/2026-10-14_slotted_lifetime_ownership_fixes_epic.md")
text = p.read_bytes().decode("utf-8")
assert "\r\n" not in text

PAIRS = [
    ("""The lifetime audit (TASK-2026-10-14-audit_slotted_lifetime_ownership, probe `probe_lifetime_owners.py`, GIL off and
on, 0.2.8235) proved six defect groups against the owner's rule - the object a lifetime names owns the instance and
everything built for it, which lives exactly as long as that object:
""", """The lifetime audit (TASK-2026-10-14-audit_slotted_lifetime_ownership, probe `probe_lifetime_owners.py`, GIL off and
on, 0.2.8235) proved six defect groups where Melder's structure recorded a slotted instance, or the `many` children
built for it, under the wrong owner, or kept registry state an agent cannot get past (aligned 2026-10-15 to the
owner's ruling: correctness lives in the structure, not in the objects Melder hands out; the earlier framing here
was my own paraphrase):
"""),
    ("""- D3 Melder drops stored instances without disposing them: the default ownership transfer and contract invalidation
  both retire instances with `extract_spell_creations`.
""", """- D3 the default ownership transfer took the source's instances out of its store and put them nowhere, so a
  transferred `unique` was rebuilt as a second instance; contract invalidation lets retired consumers go undisposed
  (intended behaviour by the owner's ruling).
"""),
    ("- D6 a lesser upgraded to a root keeps holders whose dependencies the old root disposes (to be re-investigated).\n",
     "- D6 a lesser upgraded to a root keeps holders whose dependencies the old root disposes (re-investigated: no\n"
     "  defect; a docstring paragraph).\n"),
    ("""One rule applied at every point where an owner ends or changes: a slotted instance and the `many` children built for
it are recorded with its owner, move with it, and are disposed with it, exactly once. Melder is a runtime ecosystem
built for agents, not a static library: objects legitimately outlive the operation that made them, so the fixes
change who owns and disposes them, never whether a caller may keep one. The meld paths keep their O(1) shape.
""", """Fix the structure, not the objects: where an owner ends or changes, a slotted instance and the `many` children built
for it are recorded with the object its lifetime names and move with it, and no registry keeps a torn-down root.
Melder's infrastructure disposes what its own stores record when they end; it does not police the objects it hands
out - agents iterate on them, leave them pending and clean them up (owner ruling 2026-10-14, promoted to
src_architecture as "Runtime Model: Structure Is the Contract"). The meld paths keep their O(1) shape.
"""),
    ("""  objects by default (`move_creations=True`), so a `unique` stays one object; contract invalidation as the owner
  rules (pending).
""", """  objects by default (`move_creations=True`), so a `unique` stays one object; contract invalidation stays as it is
  (owner ruling, Decision Log "contract invalidation and the runtime model").
"""),
    ("""  what each value does; a transfer disposes nothing. Contract invalidation's retired consumers: as the owner rules.
""", """  what each value does; a transfer disposes nothing. Contract invalidation is unchanged (owner ruling).
"""),
    ("- The audit probe's eleven cases report no defect (D6 per its re-investigation), GIL off and on.\n",
     "- The audit probe's eleven cases report no defect (D6 per its re-investigation; b7 accepted as intended by the\n"
     "  owner's ruling), GIL off and on.\n"),
    ("""- [ ] Milestone 3: D3, D4 and D5 landed (disposal and holder-owned children). D4/D5 landed as 0.2.8238 and the D3
      transfer default as 0.2.8239; the D3 invalidation half waits for the owner's ruling.
""", """- [x] Milestone 3: D3, D4 and D5 landed. D4/D5 landed as 0.2.8238 and the D3 transfer default as 0.2.8239, its
      handover docstring as 0.2.8240; the D3 invalidation half was ruled out by the owner (no change).
"""),
    ("""- None open; interpretations of the owner's guidance are recorded in the Decision Log.
""", """- D5 as landed (0.2.8238): purging a holder disposes the `many` children recorded with it. Offered to the owner
  (2026-10-14) to revert purge to leaving them registered; kept as landed unless he says otherwise.
"""),
    ("""  `move_creations=True`, so a transferred `unique` stays one object; `move_creations=False` and a move into a slot
  the target already fills keep today's behaviour and are documented; a transfer disposes nothing.
""", """  `move_creations=True`, so a transferred `unique` stays one object; `move_creations=False` and a move into a slot
  the target already fills keep today's behaviour and are documented; a transfer disposes nothing.
- 2026-10-14: contract invalidation and the runtime model. The owner: "no we leave it alone and simply leave it
  default true, its up to the user to break their own shit", then "objects are left as they are the agents can clean
  them up later ... this is an agentic ecosystem its not a fucken normal program", "correctness is in the structure
  and infrastructure not objects that are generated from melder ... even crystallizer just restores infrastructure
  and structure and not the baseline objects" and "the melder infrastructure enforces that but not userland shit".
  Read as: contract invalidation stays as it is (b7, l1, l2 are intended); a defect is wrong or stuck structure;
  objects Melder lets go of stay pending for agents; my "disposed by its owner exactly once" paraphrase is erased.
- 2026-10-14: D4 and the transfer handover. The owner: "moving the many is fine", then "people will need to
  understand that transfer of ownership will likely end in a broken state ... they just need to register to all the
  dependencies so they can make their own version while you throw out the trash" and "update the documents too
  properly so you fully understand next time". Read as: D4 stays as landed (0.2.8238); the transfer docstring, the
  docs page and the release note say a transfer hands over stewardship, not a working setup (0.2.8240); the system
  docs record the runtime model.
"""),
    ("""  - system_docs/patches/active/slotted_lifetime_ownership_2026_10_14/architecture_patch.md
  - system_docs/patches/active/slotted_lifetime_ownership_2026_10_14/component_patch_conduit_clusters.md
  - system_docs/patches/active/slotted_lifetime_ownership_2026_10_14/component_patch_creations.md
  - system_docs/patches/active/slotted_lifetime_ownership_2026_10_14/component_patch_spellcompiler_codegen.md
  - system_docs/patches/active/slotted_lifetime_ownership_2026_10_14/component_patch_ownership_transfer.md
  - system_docs/patches/active/slotted_lifetime_ownership_2026_10_14/component_patch_conduit_ward_contracts.md
  - system_docs/patches/active/slotted_lifetime_ownership_2026_10_14/code_description_patch_cluster_exit.md
  - system_docs/patches/active/slotted_lifetime_ownership_2026_10_14/code_description_patch_holder_children.md
  - system_docs/patches/active/slotted_lifetime_ownership_2026_10_14/code_description_patch_transfer_disposal.md
- DISPOSITION: retain_as_reference (artifacts); promote_to_documentation (patch docs)
- CLEANUP_TRIGGER: patch docs archived to patches/completed at landing; artifacts decided at closure
""", """  - system_docs/patches/completed/slotted_lifetime_ownership_2026_10_14/ (nine patch docs, promoted and archived
    2026-10-15)
- DISPOSITION: retain_as_reference (artifacts); promote_to_documentation (patch docs, done)
- CLEANUP_TRIGGER: patch docs archived to patches/completed at landing (done); artifacts decided at closure
"""),
]

for old, new in PAIRS:
    assert text.count(old) == 1, (old[:70], text.count(old))
    text = text.replace(old, new)
p.write_bytes(text.encode("utf-8"))
print("epic aligned")
