"""Open S6's fix lane on the owner's ruling (chat 2026-10-17): the managed settings leave the spell_id. <NOW>.

Rewrites S6's working sections to the chosen direction (status in_progress, melder_0), updates the epic's question,
log, story line and handoff, adds S6's lane row and detail entry to the attention board (the epic row's next follows),
and rows the same-id staging probe under S6 on the artifact board. Every edit is checked in memory before anything is
written. Notes are appended separately with append_note.py.

Run from context_compass/:  python3 artifacts/correctness_defects_20261017/scripts/open_s6_fix_lane.py <NOW> [--dry-run]
"""
import pathlib
import re
import sys

NOW = sys.argv[1]
DRY = "--dry-run" in sys.argv[2:]
S6 = "tickets/stories/2026-10-17_release_routes_parked_version_objects_to_active_pool_story.md"
EPIC = "tickets/epics/2026-10-17_correctness_defects_epic.md"
BOARD = "attention_board.md"
ART = "artifact_board.md"


def sub(text: str, old: str, new: str) -> str:
    """Replace `old` (exactly once) with `new`; @@NOW@@ becomes NOW."""
    assert text.count(old) == 1, old[:90]
    return text.replace(old, new.replace("@@NOW@@", NOW), 1)


def section(text: str, heading: str, body: str) -> str:
    """Replace the body of `## heading` (up to the next `## `) with `body`."""
    marker = "\n## " + heading + "\n"
    assert text.count(marker) == 1, heading
    start = text.index(marker) + len(marker)
    end = text.index("\n## ", start)
    return text[:start] + body.replace("@@NOW@@", NOW).rstrip("\n") + "\n" + text[end:]


def check(text: str) -> str:
    """Refuse long lines that hold no path."""
    long = [line for line in text.splitlines() if len(line) > 120 and "/" not in line]
    assert not long, long
    return text


texts = {path: pathlib.Path(path).read_text(encoding="utf-8") for path in (S6, EPIC, BOARD, ART)}

# --- S6 -----------------------------------------------------------------------------------------------------------
t = texts[S6]
t = sub(t, "- Status: ready\n- Owner: user\n- Agent Name: unassigned\n- Agent Role: UNKNOWN\n",
        "- Status: in_progress\n- Owner: user\n- Agent Name: melder_0\n- Agent Role: synaptic_python_developer\n")
t = section(t, "User Narrative", """
As an agent iterating on a managed class, I want its bind settings - mode, limit, queue timeout, reset names - to be
settings of the one spell, not a new version of it, so that changing them keeps one pool whose count stays true, and
every object I release goes back to the pool that leased it.
""")
t = section(t, "Value / MRP Alignment", """
A pool's count is structure Melder keeps (owner ruling: structure is the contract). Today the settings are hashed
into the spell_id, so the same class bound again with another limit becomes a second version with its own pool, and
a release after a notch can leave a limited_quantity or queue pool counting an object out that it will never get back
- the version then refuses every lease while nothing is out. The owner ruled the hashing itself the bug (chat
2026-10-17): "the bind call itself shouldn't impact the actual SHA256 thats absurd".
""")
t = section(t, "Ticket Contract", """
- ENTRY_GATE: the owner's direction recorded (DECISION note of @@NOW@@); patch docs for the Binding
  Pipeline and the Managed Spell Pools linked here and approved by the owner; the active board row; melder_1's notch
  (0.2.8253) landed, so this lane notches above it with __version__, the release note and the system documents
  released to it.
- EXECUTION_BOUNDARY: part A (free files) - `Bind.sha256_profile` and `Bind.spell_id_inspector` (the managed part
  leaves the fingerprint; `_normalize_managed_options` stays, the Spell keeps the settings),
  `ManagedSpellQuantity._rebind_spell` (re-compose the settings and retention sizes from the new Spell),
  `Creations.ensure_managed_quantity` (rebind outside the store lock), the cache generation (22); regression tests,
  the managed fingerprint tests moved to the new rule; the system documents with their indexes and the graph; the
  release note; one notch; the rebuild last. Part B (after melder_1 releases spellbook.py): `bind_inactive` and
  `add_to_spell_index` refuse a managed version whose class already backs another managed version of the index; the
  collision error names the settings remedy.
- DEPENDENCIES: EPIC-2026-10-17-correctness_defects; the probes and their runs (Artifact Links); the managed epic's
  rulings (owner, 2026-10-14: notch and cleanup_spell destroy nothing; identity is not tracked); melder_1's landing
  (TASK-2026-10-16-recheck_contract_consumers_when_provider_changes).
- EXIT_GATE: Q2's bindings are one spell (re-staging the other limit is refused, nothing changed); `cleanup_spell` then
  `bind` with limit 2 keeps the spell_id and the pool, count true and the new limit in force, and an object leased
  before it goes back to that pool; non-managed spell ids byte-identical; Q1 and Q3-Q6 unchanged where they apply;
  regression tests pass with the GIL off and on; docs, notch and the rebuild with both checks OK.
- FAILURE_ESCALATION: DECISION_REQUEST if the owner wants existence, disposal names or resolvable out of the spell_id
  too (a larger lane: the creation cache and the stores' disposal records are keyed by spell_id); CONFLICT if a needed
  file is held by another lane.
""")
t = section(t, "Requirements (Functional)", """
- The spell_id of a managed binding does not depend on its managed settings: one class bound managed at one address
  with one disposal list gets one spell_id whatever its mode, limit, timeout or reset names.
- `bind_inactive` of such a binding onto an index already holding that spell_id is refused as the same spell (the
  collision error), with nothing registered.
- A rebind under the same spell_id (`cleanup_spell`, then `bind` or `bind_inactive`) meets the pool the earlier
  definition left, and the pool takes the new Spell's settings: mode, limit, timeout, reset names and the retention
  sizes they imply. Objects alive stay alive and counted; queue waiters re-check against the new settings.
- A release keeps its routing (one pool of the class: the fast path; several: the cold resolver as today).
- Part B: `bind_inactive` and `add_to_spell_index` refuse a managed version whose class already backs another managed
  version of the index (one class at two addresses or with two disposal lists would otherwise keep two pools).
""")
t = section(t, "Requirements (Non-Functional)", """
- The warm lease and the warm release keep their cost; emitted plans are unchanged (no plan reads a managed setting).
- No new lock-order edge: the store lock stays a leaf (the rebind runs after it is released); the pool lock stays a
  leaf, taken under the Spell lock as owner stamping already takes it.
- No identity tracking (owner, 2026-10-14: "we don't care about identity").
""")
t = section(t, "Scope Boundaries", """
- In scope: the managed part of the fingerprint; the pool's re-composition on a same-id rebind; the cache generation;
  part B's staging refusal.
- Out of scope: the address, existence, disposal names and resolvable, which stay in the spell_id (scope with the
  owner for confirmation); the resolver's active-version preference; pools of a disposed version (kept by the
  2026-10-14 ruling).
""")
t = section(t, "State Transition Event", """
- from_state: ready
- to_state: in_progress
- transition_reason: the owner chose the direction (chat 2026-10-17): the bind call's settings must not change the
  spell_id, and the version is notched for the cache (DECISION note). Filed draft -> ready at 2026-10-17T21:07:53Z.
""")
t = section(t, "Tasks (Implementation Checklist)", """
- [x] Task: the owner's answer on the open question (2026-10-17: the managed settings leave the spell_id).
- [ ] Task: the owner's confirmation of the scope (Open Questions).
- [ ] Task: patch docs for the Binding Pipeline and the Managed Spell Pools; the owner's approval.
- [ ] Task: part A with symptom-named regression tests, docs, notch and the rebuild last.
- [ ] Task: part B after melder_1 releases spellbook.py.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.
""")
t = section(t, "Acceptance Criteria", """
- Worker bound managed (limited_quantity, limit 1) and Worker with limit 2 at the same address and disposal list have
  one spell_id; `bind_inactive` of the second onto the first's index is refused and nothing changes.
- `cleanup_spell` of Worker, then `bind` of it with limit 2: the spell_id is the same, the pool is the same object with
  its idle objects and count, it leases up to 2, and releasing an object leased before the rebind keeps the count true.
- Every managed spell_id differs once from the one 0.2.8253 gave; every other spell_id is byte-identical.
- Part B: staging Worker into Worker's index under another binding name is refused.
""")
t = section(t, "Validation / Test Plan", """
- Regression tests named for the symptom, e.g. `test_managed_settings_do_not_change_the_spell_id`,
  `test_restaging_a_settings_only_version_is_refused_as_the_same_spell` and
  `test_rebinding_with_new_managed_settings_recomposes_its_pool`; the managed fingerprint tests moved to the new rule;
  GIL off and on; probes Q1-Q6 and S1-S2 re-run. Not run: no fix exists yet.
""")
t = section(t, "UX / API / Data Notes", """
- **Breaking change:** every managed spell's spell_id moves once (non-managed ids do not), and staging the same class
  with only other settings is refused as the same spell; change settings with `cleanup_spell` and a new `bind`.
- Bundles written before the notch are cold once (the cache admits only its own release; generation 22 records it).
- A record made by 0.2.8242-0.2.8253 restores with mapped ids (restore maps a changed SHA); one holding two
  settings-only versions of one class in one index cannot rebuild both - the patch decides refusal or a shortfall.
- Under process-wide spell ids, two frames binding one managed class at one address now share its spell_id, so the
  second bind is refused as any other duplicate is.
""")
t = section(t, "Risks / Mitigations", """
- A new limit below the live count: nothing is destroyed; the pool builds again only once the count falls below it.
- A mode change with queue waiters: the rebind wakes them so each re-checks under the new settings.
- The restore and graft edge above: decided in the patch docs before code.
""")
t = section(t, "Open Questions", """
- Scope (ALIGNMENT_CHECK with the owner, chat @@NOW@@): only the four managed settings leave the
  spell_id; the address stays (one class under two binding names is two spells), and existence, disposal names and
  resolvable stay (they shape the plan the creation cache keeps under the spell_id). Part B closes the residual
  same-class case by refusing it at staging. Confirm, or say what else leaves the id.
- Answered (owner, 2026-10-17): the earlier options 1-4 - option 2, settings out of the spell_id, as a bug fix
  (DECISION note).
""")
t = sub(t, "- 2026-10-17T23:25:30Z: the open question reframed to options 1-4 with 3 recommended; the earlier (a) withdrawn\n"
           "  (STRATEGY_DISCUSSION note).\n",
        "- 2026-10-17T23:25:30Z: the open question reframed to options 1-4 with 3 recommended; the earlier (a) withdrawn\n"
        "  (STRATEGY_DISCUSSION note).\n"
        "- @@NOW@@: the owner chose option 2 as a bug fix - the bind call's settings must not change\n"
        "  the spell_id; notch the version for the cache; melder_0 takes the lane (DECISION note).\n")
t = sub(t, "  - artifacts/correctness_defects_20261017/runs/probe_managed_release_routing_gil1.txt\n",
        "  - artifacts/correctness_defects_20261017/runs/probe_managed_release_routing_gil1.txt\n"
        "  - artifacts/correctness_defects_20261017/probes/probe_same_id_staging.py (cases S1, S2: the same spell_id staged; a settings change today)\n"
        "  - artifacts/correctness_defects_20261017/runs/probe_same_id_staging_gil0.txt\n"
        "  - artifacts/correctness_defects_20261017/runs/probe_same_id_staging_gil1.txt\n")
t = section(t, "Context / Handoff Summary", """
- Scope: the managed settings leave the spell_id (the owner's ruling); a same-id rebind re-composes its pool; the
  notch and a cache generation bump retire old bundles; part B refuses the residual same-class staging. Defect
  proven on 0.2.8252 (Notes); probes and runs in Artifact Links.
- State: in_progress (melder_0), discovery. The direction is the owner's (DECISION note); the scope is with him for
  confirmation (Open Questions). Part A sits in free files (bind.py, managed_spell_quantity.py, creations.py,
  caching_system.py); part B in spellbook.py (melder_1's until its release). Landing follows melder_1's 0.2.8253.
- Next: (1) the patch docs, linked here, for the owner's approval; (2) part A with its tests, docs, notch and the
  rebuild last; (3) part B after melder_1's release.
""")
texts[S6] = check(t)

# --- epic ---------------------------------------------------------------------------------------------------------
t = texts[EPIC]
t = sub(t, "- [ ] Story: STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool - a release with no filter\n"
           "  sends a parked version's object to the active version's pool and strands its count (sweep A6).\n",
        "- [ ] Story: STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool - a release with no filter\n"
        "  sends a parked version's object to the active version's pool and strands its count (sweep A6). In progress:\n"
        "  the managed settings leave the spell_id (owner, 2026-10-17).\n")
t = section(t, "Open Questions", """
- S6's scope confirmation, with the owner (its direction chosen 2026-10-17: the managed settings leave the spell_id).
  Every other story question is answered (S1, S2, S5, S8) or withdrawn (S10).
""")
t = sub(t, "  notch; S10 withdrawn, its graft side stays in S5; S6 reframed to options 1-4 (DECISION note).\n",
        "  notch; S10 withdrawn, its graft side stays in S5; S6 reframed to options 1-4 (DECISION note).\n"
        "- @@NOW@@: the owner chose S6's direction - the bind call's settings must not change the\n"
        "  spell_id, notch for the cache; melder_0 takes S6's fix lane (DECISION note).\n")
t = sub(t, "  STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool (p2, open question: options 1-4),\n",
        "  STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool (p2; in progress, melder_0: the managed\n"
        "  settings leave the spell_id),\n")
t = sub(t, "  not a defect (DECISION note of 2026-10-17T23:25:30Z); melder_1 told (M0-188). S6 was talked through with him:\n"
           "  the raise-on-ambiguity recommendation is withdrawn and options 1-4 are with him (S6's notes).\n"
           "- Next: (1) the owner's choice on S6 (its Open Questions: options 1-4, 3 recommended); (2) a fourth tranche on\n"
           "  the owner's word; (3) melder_1 carries S1-S4 and S7-S9 with its hand-back.\n",
        "  not a defect (DECISION note of 2026-10-17T23:25:30Z); melder_1 told (M0-188). The owner chose S6's direction\n"
        "  (DECISION note of @@NOW@@): the managed settings leave the spell_id; melder_0 runs its fix lane.\n"
        "- Next: (1) S6's patch docs and the owner's scope confirmation, then its fix after melder_1's notch; (2) a fourth\n"
        "  tranche on the owner's word; (3) melder_1 carries S1-S4 and S7-S9 with its hand-back.\n")
texts[EPIC] = check(t)

# --- attention board ----------------------------------------------------------------------------------------------
t = texts[BOARD]
row = re.compile(r"(?m)^(\| correctness_defects \| in_progress \| handoff \| claude \| melder_0 \| none \| )"
                 r"Owner picks S6's direction \(options 1-4\); then a fourth sweep tranche on the owner's word\."
                 r"( \|.*\| tickets/epics/2026-10-17_correctness_defects_epic\.md \| )\S+( \| REQUIRED \|)$")
t, n = row.subn(lambda m: m.group(1) + "S6's fix lane runs (its own row); then a fourth sweep tranche on the owner's word."
                + m.group(2) + NOW + m.group(3), t)
assert n == 1, n
new_row = ("| managed_settings_spell_id | in_progress | discovery | claude | melder_0 | none | Write S6's patch docs (Binding "
           "Pipeline, Managed Spell Pools) for the owner's approval and confirm the scope with him. | The four managed "
           "settings leave the spell_id; a same-id rebind re-composes its pool; the notch and cache generation 22 retire "
           "old bundles. | The fix lands with tests, docs, notch and rebuild, or the owner redirects. | "
           "tickets/stories/2026-10-17_release_routes_parked_version_objects_to_active_pool_story.md | " + NOW + " | REQUIRED |\n")
t = sub(t, "<!-- END USER-DEFINED: active_items -->", new_row + "<!-- END USER-DEFINED: active_items -->")
t = sub(t, "<!-- END USER-DEFINED: active_attention_details -->",
        "- WORK_ITEM: managed_settings_spell_id\n"
        "  SWITCH_TRIGGER: The fix lands with tests, docs, notch and rebuild, or the owner redirects.\n"
        "  RESUME_HIERARCHY:\n"
        "    - tickets/epics/2026-10-17_correctness_defects_epic.md\n"
        "    - tickets/stories/2026-10-17_release_routes_parked_version_objects_to_active_pool_story.md\n"
        "<!-- END USER-DEFINED: active_attention_details -->")
texts[BOARD] = t

# --- artifact board -----------------------------------------------------------------------------------------------
t = texts[ART]
t = sub(t, "| tickets/stories/2026-10-17_release_routes_parked_version_objects_to_active_pool_story.md | "
           "artifacts/correctness_defects_20261017/probes/probe_managed_release_routing.py | defect_reproducer | ready |",
        "| tickets/stories/2026-10-17_release_routes_parked_version_objects_to_active_pool_story.md | "
        "artifacts/correctness_defects_20261017/probes/probe_managed_release_routing.py | defect_reproducer | in_progress |")
t = sub(t, "<!-- END USER-DEFINED: active_artifacts -->",
        "| tickets/stories/2026-10-17_release_routes_parked_version_objects_to_active_pool_story.md | "
        "artifacts/correctness_defects_20261017/probes/probe_same_id_staging.py | investigation_evidence | in_progress | "
        "retain_as_reference | Cases S1 (re-staging one spell_id is refused) and S2 (a settings change mints a new id "
        "today) with their runs (runs/probe_same_id_staging_gil0.txt, _gil1.txt); re-run at the fix. | " + NOW + " | HELPFUL |\n"
        "<!-- END USER-DEFINED: active_artifacts -->")
texts[ART] = t

if DRY:
    print("dry run OK:", ", ".join(texts))
else:
    for path, text in texts.items():
        pathlib.Path(path).write_text(text, encoding="utf-8")
    print("written:", ", ".join(texts))
