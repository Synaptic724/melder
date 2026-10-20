"""Turn in STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool (melder_0, 2026-10-18).

The owner's word (chat 2026-10-18): "lets hit that up next turn in anything you completed and leave notes on things
you left open since we went into this direction". Part A landed at 0.2.8254; part B is superseded by
EPIC-2026-10-18-spell_identity_is_the_code. This script edits the story in place (final notes, completion summary,
status, transition, checklists, handoff, archived patch paths) and the six patch docs' status lines. The moves
(story to completed/, patch folder to completed/) are done by `mv -n` after it. Usage: s6_closure.py <NOW>
"""
import pathlib
import re
import sys

NOW = sys.argv[1]
STORY = pathlib.Path("tickets/stories/2026-10-17_release_routes_parked_version_objects_to_active_pool_story.md")
PATCH_DIR = pathlib.Path("system_docs/patches/active/managed_settings_spell_id_2026_10_17")
EPIC = "EPIC-2026-10-18-spell_identity_is_the_code"


def replace_once(text: str, old: str, new: str) -> str:
    """Replace exactly one occurrence or stop."""
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected one occurrence, found {count}: {old[:80]!r}")
    return text.replace(old, new, 1)


NOTES = f"""- DATETIME: {NOW}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The code-hash prototype reads the code inside a method, not only its outline (the owner asked, chat
    2026-10-18: "the internal code inside the methods not just the superficial shit ... is that part of your
    equation?"). One method holding a constant, a call, a comparison, a lambda, a nested function and a
    comprehension, changed one thing at a time: the constant, the method called, the comparison, the lambda's body,
    the nested function's body, the comprehension, two statements swapped and a local renamed each give a different
    prototype id and the same spell_id today; a comment inside the nested function gives the same id in both. The
    hashed stream is the instructions with resolved operands (e.g. LOAD_FAST_BORROW 'x', LOAD_SMALL_INT 2,
    BINARY_OP 5, STORE_FAST 'total'). Byte-identical with PYTHONHASHSEED 1 and 2, GIL off and on.
  EVIDENCE:
  - context_compass/artifacts/correctness_defects_20261017/probes/probe_code_hash_internals.py:1-251
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_code_hash_internals_gil0_seed1.txt:1-22
  - context_compass/artifacts/correctness_defects_20261017/runs/probe_code_hash_internals_gil1_seed2.txt:1-22
  IMPACT: The identity the owner wants is buildable from the class object bind already holds; it is the first story
    of {EPIC}.
  NEXT: Record the owner's direction and turn this story in.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

- DATETIME: {NOW}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's direction (chat 2026-10-18), which ends this story: a spell's identity is the registered object's
    code - "the bind signature shouldn't impact the spells identity", "you could register the same object n number
    of times for each existence this is a correctness bug big time", "we only want to read the object registered its
    methods, its actual code not its docstrings or comments" - and the bind signature gets "its own hash signature we
    could put into a manifest associated with an object and I think if that hash changes we should revalidate the
    object". Implementation goes to a new epic ("please make an epic, document your stories for it and lets hit that
    up next turn") and this story is turned in ("in anything you completed and leave notes on things you left open
    since we went into this direction"). So {EPIC} is opened with five stories, and this story closes with part A
    delivered and part B not built.
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md
  IMPACT: Part B's staging refusal is superseded: under the new identity one object cannot be registered twice at all.
  NEXT: Turn this story in; open the epic and its stories.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: {NOW}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Turned in on the owner's word. Delivered: part A at 0.2.8254 - a managed spell's four settings left the
    spell_id, `ManagedSpellQuantity._rebind_spell` gives a same-spell_id rebind the new settings, cache generation 22 -
    with the whole tree green with the GIL off and on, the release note, the system documents, the graph and the
    rebuild last with both checks OK (MEASURE notes of 01:28:45Z, 02:05:06Z and 02:14:40Z). Not built: part B (refuse a
    second managed version of one class in one SpellIndex). Left open and moved to {EPIC}: one registration per object
    (STORY-2026-10-18-one_registration_per_object covers part B's case and every other second registration); a legacy
    record holding one object twice (STORY-2026-10-18-spell_id_migration); the whole bind signature leaving the
    spell_id as a binding manifest (STORY-2026-10-18-binding_manifest_hash, STORY-2026-10-18-revalidate_on_binding_change);
    and, unproven, a disposed spell's pool left beside a new root's pool when the same object is registered again in
    another root (the epic's Open Questions; the owner set pool routing aside). The release resolver is unchanged.
    The patch docs are archived (part A's promoted at 0.2.8254; part B's not built).
  EVIDENCE:
  - context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md
  - src/melder/__version__.py:12-12
  IMPACT: Nothing of this story stays active; its open items live in the epic's stories.
  NEXT: None here; {EPIC}.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

"""

SUMMARY = f"""- Completed: {NOW}
- Summary: part A landed 0.2.8254 - a managed spell's four settings (mode, limit, queue timeout, reset names) left the
  spell_id, a rebind under the same spell_id gives its pool the new settings, creation cache generation 22. Whole tree
  green in both GIL modes; release note, system documents, graph, rebuild checks OK. Part B (the staging refusal) was
  not built: superseded by {EPIC} (one object, one spell). Turned in on the owner's word (2026-10-18).

"""

HANDOFF_OLD_START = "- Scope: the managed settings leave the spell_id (the owner's ruling); a same-id rebind re-composes its pool; the\n"
HANDOFF_NEW = f"""- Scope: the managed settings leave the spell_id (the owner's ruling); a same-id rebind re-composes its pool; the
  notch and cache generation 22 retire old bundles. Defect proven on 0.2.8252 (Notes); probes and runs in Artifact
  Links.
- State: done (turned in {NOW} on the owner's word). Part A landed at 0.2.8254 - the fingerprint, the pool's
  rebind, cache generation 22 - with the whole tree green with the GIL off and on, the release note, the system
  documents and the graph, rebuilt last with both checks OK (MEASURE notes). Part B was not built: the owner's
  identity direction (2026-10-18) replaces it.
- Open, moved to {EPIC}: one registration per object (part B's case and every other second registration); a legacy
  record holding one object twice (its migration story); the whole bind signature leaving the spell_id as a binding
  manifest; and, unproven, a disposed spell's pool beside a new root's pool after a re-registration elsewhere (its
  Open Questions).
- Next: none here; the epic.

"""


def edit_story() -> None:
    """All edits of the story, in one pass."""
    text = STORY.read_text(encoding="utf-8")
    title_end = text.index("\n\n## Metadata")
    text = text[:title_end] + "\n\n" + SUMMARY.rstrip("\n") + text[title_end:]
    text = replace_once(text, "- Status: in_progress\n", "- Status: done\n")
    text, count = re.subn(r"^- Updated: [0-9TZ:-]+$", f"- Updated: {NOW}", text, count=1, flags=re.M)
    assert count == 1
    text = replace_once(
        text,
        "- from_state: ready\n- to_state: in_progress\n- transition_reason: the owner chose the direction (chat 2026-10-17): "
        "the bind call's settings must not change the\n  spell_id, and the version is notched for the cache (DECISION note). "
        "Filed draft -> ready at 2026-10-17T21:07:53Z.\n",
        f"- from_state: in_progress\n- to_state: done\n- transition_reason: turned in on the owner's word (chat 2026-10-18: "
        f"\"lets hit that up next turn in anything you\n  completed and leave notes on things you left open since we went "
        f"into this direction\"); part A landed at 0.2.8254\n  with every EXIT_GATE item recorded in the Notes; part B "
        f"superseded by {EPIC}.\n- prior: ready -> in_progress (2026-10-17T23:50:39Z): the owner chose the direction "
        f"(chat 2026-10-17): the bind\n  call's settings must not change the spell_id, and the version is notched for "
        f"the cache (DECISION note). Filed\n  draft -> ready at 2026-10-17T21:07:53Z.\n",
    )
    text = replace_once(
        text,
        "- [ ] Task: part B after melder_1 releases spellbook.py.\n- [ ] Enforce Ticket Microcycle across all linked tasks.\n"
        "- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.\n",
        f"- [ ] Task: part B after melder_1 releases spellbook.py - not built here: superseded by {EPIC}\n"
        f"  (STORY-2026-10-18-one_registration_per_object).\n- [x] Enforce Ticket Microcycle across all linked tasks.\n"
        f"- [x] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.\n",
    )
    text = replace_once(
        text,
        "- Open, for the talk after part A: part B's staging refusal; a legacy record holding two settings-only versions of\n"
        "  one class in one index (with no extra code its restore fails whole on the collision); whether anything more of\n"
        "  the bind call leaves the spell_id.\n",
        f"- Moved (owner, 2026-10-18) to {EPIC}: part B's staging refusal (one registration per object), the legacy\n"
        f"  record (its migration story) and the bind call (all of it leaves the spell_id as a binding manifest).\n",
    )
    text = replace_once(
        text,
        "\n## Artifact Links (Optional)",
        f"- {NOW}: the owner's identity direction moved part B and the open questions to {EPIC}; turned in on\n"
        f"  his word (DECISION note).\n\n## Artifact Links (Optional)",
    )
    text = text.replace("system_docs/patches/active/managed_settings_spell_id_2026_10_17/",
                        "system_docs/patches/completed/managed_settings_spell_id_2026_10_17/")
    text = replace_once(
        text,
        "- CLEANUP_TRIGGER: the probes are re-run at the fix and kept as the defect's reproducers; the patch docs are\n"
        "  promoted into the system documents at landing and archived under system_docs/patches/completed/\n",
        f"- CLEANUP_TRIGGER: applied at closure ({NOW}): the probes and runs stay as the defect's reproducers, rowed\n"
        f"  under EPIC-2026-10-17-correctness_defects; the patch docs were promoted at 0.2.8254 and are archived under\n"
        f"  system_docs/patches/completed/; the identity probes (fingerprint, prototype, internals) are rowed under {EPIC}\n",
    )
    text = replace_once(text, "\n## Closure Confirmation\n", "\n" + NOTES.rstrip("\n") + "\n\n## Closure Confirmation\n")
    text = replace_once(
        text,
        "## Closure Confirmation\n- [ ] Work walkthrough shared with user\n"
        "- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded\n"
        "- [ ] Applicable anti-pattern checks are clear or escalated with evidence.\n",
        "## Closure Confirmation\n- [x] Work walkthrough shared with user (2026-10-18T02:15Z, the part A report; the identity talk, "
        "2026-10-18)\n- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded\n"
        "- [x] Applicable anti-pattern checks are clear or escalated with evidence.\n",
    )
    start = text.index(HANDOFF_OLD_START)
    end = text.index("## Project-Specific Additions")
    text = text[:start] + HANDOFF_NEW + text[end:]
    STORY.write_text(text, encoding="utf-8")


def set_status(path: pathlib.Path, status: str) -> None:
    """Replace a patch doc's Status entry (with its continuation lines) and its Updated line."""
    lines = path.read_text(encoding="utf-8").split("\n")
    index = next(i for i, line in enumerate(lines) if line.startswith("- Status:"))
    end = index + 1
    while end < len(lines) and lines[end].startswith("  "):
        end += 1
    words, wrapped, current = status.split(" "), [], "- Status:"
    for word in words:
        if len(current) + 1 + len(word) > 116:
            wrapped.append(current)
            current = "  " + word
        else:
            current += " " + word
    wrapped.append(current)
    lines[index:end] = wrapped
    for i, line in enumerate(lines):
        if line.startswith("- Updated:"):
            lines[i] = f"- Updated: {NOW}"
            break
    path.write_text("\n".join(lines), encoding="utf-8")


def edit_patches() -> None:
    """Archive statuses for the six patch docs."""
    archived = (f"archived at the story's closure ({NOW}): landed at 0.2.8254 and promoted to the system documents and "
                f"the graph")
    set_status(PATCH_DIR / "architecture_patch.md",
               f"archived at the story's closure ({NOW}): part A landed at 0.2.8254 and was promoted to the system "
               f"documents and the graph; part B was not built - superseded by {EPIC} (one object, one spell)")
    for name in ("component_patch_binding_fingerprint.md", "component_patch_managed_pool_rebind.md",
                 "code_description_patch_managed_pool_rebind.md", "component_patch_creation_cache_generation.md"):
        set_status(PATCH_DIR / name, archived)
    set_status(PATCH_DIR / "component_patch_staging_refusal.md",
               f"not built; superseded by {EPIC} (one object, one spell; owner, 2026-10-18); archived with the story "
               f"({NOW})")


if __name__ == "__main__":
    edit_story()
    edit_patches()
    print("ok", NOW)
