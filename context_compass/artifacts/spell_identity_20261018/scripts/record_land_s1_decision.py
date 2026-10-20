"""Record the owner's word to land S1 with S2, duplicates strictly refused, S6 parked (melder_0, 2026-10-18).

Run from context_compass/. Writes the timestamp to /tmp/m0_mq/T2.txt.
"""
import pathlib
import re
import subprocess
import sys
from datetime import datetime, timezone

T = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
EPIC = pathlib.Path("tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md")
S1 = pathlib.Path("tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md")
S2 = pathlib.Path("tickets/stories/2026-10-18_binding_manifest_hash_story.md")
S6_OLD = pathlib.Path("tickets/stories/2026-10-18_explicit_duplicate_binding_story.md")
S6 = pathlib.Path("tickets/stories/backlog/2026-10-18_explicit_duplicate_binding_story.md")
BOARD = pathlib.Path("attention_board.md")
MAIL = pathlib.Path("mailbox_board.md")


def once(text, old, new, label):
    n = text.count(old)
    if n != 1:
        sys.exit(f"anchor {label}: {n} matches")
    return text.replace(old, new)


def regex_once(text, pattern, new, label):
    matches = list(re.finditer(pattern, text, re.S))
    if len(matches) != 1:
        sys.exit(f"pattern {label}: {len(matches)} matches")
    m = matches[0]
    return text[:m.start()] + m.expand(new) + text[m.end():]


OWNER = ("\"I'm not sure right now for now just land the first thing we agreed on and then we'll talk about the\n"
         "    rest later with duplication if a user changes how an object is initialized maybe we're fine with things\n"
         "    being strictly unique lets try it for now but allow different kinds of binding patterns and caching\n"
         "    patterns later so users can change how it behaves\"")

NOTE = """- DATETIME: {T}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner (chat 2026-10-18), answering the STRATEGY_DISCUSSION note: {OWNER}. So S1 lands now - the
    spell_id is the object's code - in the one landing the architecture patch plans for it (Migration step 5):
    S1 with S2, whose binding hash keys the creation cache beside the spell_id, so a cache built for one binding
    is never replayed for another under one spell_id (invariant 7); each with its notch. Duplicates are strictly
    refused for now: S6 is parked in the backlog unbuilt, and the corrected refusal names no duplicate option.
    Binding and caching patterns users can choose come later (EPIC-2026-10-18-identity_and_caching_configurables).
    His word to land is the approval of S1's patches, which are updated for decision B (installed packages named
    by version) and strict uniqueness; S2's component patch is written before its code. S3, S4 and S5 follow,
    each after its own patch (Migration step 6).
  EVIDENCE:
  - context_compass/system_docs/patches/active/spell_identity_is_the_code_2026_10_18/architecture_patch.md:77-111
  - context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md:463-523
  IMPACT: S1 and S2 move to implementation; S6 leaves the landing; spell.py and spellbook.py are claimed from
    melder_1 by message (M0-196) before either is edited.
  NEXT: Update S1's patches for B and strict uniqueness; write S2's component patch; the blast-radius run in a /tmp
    mirror.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
""".replace("{T}", T).replace("{OWNER}", OWNER)


def record_epic():
    t = EPIC.read_text(encoding="utf-8")
    t = regex_once(t, r"- Updated: 2026-10-18T14:33:32Z\n", f"- Updated: {T}\n", "epic updated")
    t = once(t, "is refused\n  unless the bind says so explicitly (S6).\n",
             "is refused\n  (strictly for now, the owner, 2026-10-18; an explicit duplicate bind, S6, is parked).\n",
             "epic goal")
    t = once(t, "more than once,\n  its scope recorded; lands with S1 (S6).\n",
             "more than once,\n  its scope recorded (S6; parked in the backlog by the owner, 2026-10-18).\n", "epic S6")
    t = once(t, "- [ ] Milestone 2: the code hash, the binding manifest and the explicit duplicate bind landed (S1, S2, "
                "S6).\n", "- [ ] Milestone 2: the code hash and the binding manifest landed (S1, S2).\n", "epic milestone")
    t = once(t, "- All six stories accepted; the prototype's cases are regression tests in the suite; no object registers "
                "twice\n  unless the bind says so (S6); a binding change revalidates;",
             "- S1-S5 accepted (S6 parked by the owner); the prototype's cases are regression tests in the suite; no "
             "object\n  registers twice; a binding change revalidates;", "epic acceptance")
    t = regex_once(t, r"- Stories land S1 -> S2 -> S3 -> S4 -> S5 \(S1 and S2 may land together.*?running release note\.\n",
                   "- Stories land S1 -> S2 -> S3 -> S4 -> S5 (S1 and S2 land together, so the caches never see a "
                   "spell_id without\n  its binding hash; S6 is parked, so a second registration of one object is "
                   "strictly refused); one notch\n  per landed source change; the identity change is one Breaking "
                   "entry in the running release note.\n", "epic rollout")
    t = regex_once(t, r"- The explicit duplicate bind \(S6, STORY-2026-10-18-explicit_duplicate_binding\): four forms.*?"
                      r"it lands with S1\.\n",
                   "- The explicit duplicate bind (S6, STORY-2026-10-18-explicit_duplicate_binding): parked by the owner "
                   "(DECISION\n  note of " + T + "); one object is strictly one spell for now; the four forms stay in "
                   "the\n  STRATEGY_DISCUSSION note of 2026-10-18T14:33:32Z.\n", "epic open question")
    t = once(t, "\n## Artifact Links (Optional)\n",
             f"- {T}: the owner's word - land S1 with S2's cache keys now, duplicates strictly refused, S6 parked;\n"
             "  binding and caching patterns later (DECISION note).\n\n## Artifact Links (Optional)\n",
             "epic decision log")
    t = once(t, "\n## Closure Confirmation\n", "\n" + NOTE + "\n## Closure Confirmation\n", "epic note")
    handoff = (
        "- State: in_progress (melder_0), implementation. The owner's word (DECISION note of " + T + "): land S1\n"
        "  with S2's cache keys now, duplicates strictly refused (S6 parked in the backlog), binding and caching\n"
        "  patterns later (EPIC-2026-10-18-identity_and_caching_configurables). His earlier calls and decisions\n"
        "  stand (DECISION notes of 2026-10-18T12:15:14Z, 13:06:51Z, 14:14:10Z). S1 and S2 in_progress; S3-S5\n"
        "  draft, each after its own patch; nothing in src/ yet. melder_1 holds spellbook.py and spell.py for S9 of\n"
        "  EPIC-2026-10-17-correctness_defects (M1-33); both are asked for by M0-196. The next notch is above\n"
        "  0.2.8255, or above S9's.\n"
        "- Next: (1) S1's patches updated for B and strict uniqueness, S2's component patch; (2) the blast-radius run\n"
        "  in a /tmp mirror; (3) the landing pass - red tests, src, green, the moved tests, the whole tree with the\n"
        "  GIL off and on, docs, notches, the rebuild last.\n"
    )
    t = regex_once(t, r"- State: in_progress \(melder_0\), discovery\. The owner made all five calls and three decisions.*?"
                      r"back from melder_1 after S9 lands\.\n", handoff, "epic handoff")
    EPIC.write_bytes(t.encode("utf-8"))


def record_s1():
    t = S1.read_text(encoding="utf-8")
    t = regex_once(t, r"- Updated: 2026-10-18T14:33:32Z\n", f"- Updated: {T}\n", "s1 updated")
    t = once(t, "- STORY-2026-10-18-explicit_duplicate_binding (S6; lands with this story)\n",
             "- STORY-2026-10-18-explicit_duplicate_binding (S6; parked in the backlog by the owner, 2026-10-18)\n",
             "s1 deps")
    t = once(t, "  code-description) - written 2026-10-18, the owner's approval pending.\n",
             "  code-description) - written 2026-10-18; approved by the owner's word to land (" + T + "),\n"
             "  updated for decision B and strict uniqueness.\n", "s1 task")
    t = regex_once(t, r"- With the owner: the form of the explicit duplicate bind, which lands with this story.*?"
                      r"the one bind input in the id\.\n",
                   "- The explicit duplicate bind (S6) is parked by the owner (the epic's DECISION note of " + T + "):\n"
                   "  one object is strictly one spell for now, and the corrected refusal names no duplicate option.\n",
                   "s1 open question")
    t = once(t, "  duplicate bind lands with this story as S6 (the epic's DECISION note).\n\n## Artifact Links (Optional)\n",
             "  duplicate bind lands with this story as S6 (the epic's DECISION note).\n"
             f"- {T}: the owner's word to land this story now, with S2's cache keys; duplicates strictly refused, S6\n"
             "  parked (the epic's DECISION note).\n\n## Artifact Links (Optional)\n", "s1 decision log")
    t = regex_once(t, r"- State: in_progress \(melder_0\), discovery: the design docs are written; the owner decided B.*?"
                      r"until S9 lands \(M1-33\)\.\n",
                   "- State: in_progress (melder_0), implementation: the owner's word to land it now with S2 (the "
                   "epic's DECISION\n  note of " + T + "); the patches are updated for B and strict uniqueness "
                   "before the code. spellbook.py\n  and spell.py are melder_1's for S9 and asked for (M0-196).\n",
                   "s1 state")
    t = regex_once(t, r"- Next: the owner's choice of S6's form; the patches updated for B and S6; his approval; the "
                      r"blast-radius run\n  in a /tmp mirror; then S2's patches\.\n",
                   "- Next: the patches updated for B and strict uniqueness; the blast-radius run in a /tmp mirror; "
                   "the landing\n  pass with S2.\n", "s1 next")
    S1.write_bytes(t.encode("utf-8"))


def record_s2():
    t = S2.read_text(encoding="utf-8")
    t = once(t, "- Status: ready\n", "- Status: in_progress\n", "s2 status")
    t = once(t, "- Updated: 2026-10-18T12:15:14Z\n", f"- Updated: {T}\n", "s2 updated")
    t = regex_once(t, r"## State Transition Event\n- from_state: draft\n- to_state: ready\n.*?open questions named\.\n",
                   "## State Transition Event\n- from_state: ready\n- to_state: in_progress\n- transition_reason: the "
                   "owner's word to land S1 now, which lands with this story's cache keys (the\n  epic's DECISION note "
                   "of " + T + "); his confirmation of the conduit-manifest reading (DECISION note\n  of "
                   "2026-10-18T14:14:10Z).\n", "s2 transition")
    t = once(t, "- The owner's \"conduit manifest\" (chat 2026-10-18), read as: the binding hash recorded in what the "
                "conduit\n  builds and caches the spell from; sent for his confirmation (the epic's DECISION note of "
                "2026-10-18T12:15:14Z).\n",
             "- The owner's \"conduit manifest\" reading is confirmed (the epic's DECISION note of "
             "2026-10-18T14:14:10Z): the\n  binding hash is recorded in what the conduit builds and caches the spell "
             "from.\n", "s2 open question")
    t = once(t, "  no longer waits on a release.\n\n## Artifact Links (Optional)\n",
             "  no longer waits on a release.\n- 2026-10-18T14:14:10Z: the conduit-manifest reading confirmed by the "
             "owner (the epic's DECISION note).\n"
             f"- {T}: in_progress on the owner's word to land S1 with this story (the epic's DECISION note).\n"
             "\n## Artifact Links (Optional)\n", "s2 decision log")
    t = once(t, "- State: ready (melder_0); waiting on S1's patch (melder_1's files are free since M1-28).\n"
                "- Next: the component patch with S1's.\n",
             "- State: in_progress (melder_0), discovery: lands with S1 on the owner's word (the epic's DECISION "
             "note of\n  " + T + "); spell.py is melder_1's for S9 and asked for (M0-196).\n"
             "- Next: the inventory of spell_id-keyed caches and stores; the component patch; then the landing with "
             "S1.\n", "s2 handoff")
    S2.write_bytes(t.encode("utf-8"))


def park_s6():
    if S6.exists():
        sys.exit("S6 already in the backlog")
    subprocess.run(["mv", "-n", str(S6_OLD), str(S6)], check=True)
    if not S6.exists() or S6_OLD.exists():
        sys.exit("S6 move did not happen")
    t = S6.read_text(encoding="utf-8")
    t = once(t, "- Updated: 2026-10-18T14:33:32Z\n", f"- Updated: {T}\n", "s6 updated")
    t = once(t, "- from_state: draft\n- to_state: draft\n- transition_reason: filed from the owner's direction (the "
                "epic's DECISION note of 2026-10-18T14:14:10Z); the form\n  is with him.\n",
             "- from_state: draft\n- to_state: draft\n- transition_reason: parked in the backlog by the owner (the "
             "epic's DECISION note of " + T + "):\n  duplicates are strictly refused for now; talked through later.\n",
             "s6 transition")
    t = regex_once(t, r"- DECISION_REQUEST \(owner\): the form - .*?defaulting to the scope \(recommended\)\.\n",
                   "- Parked by the owner (the epic's DECISION note of " + T + "), open until he takes it up: the\n"
                   "  form - (1) an option whose scope joins the spell_id (recommended), (2) `duplicate=True` with the "
                   "address in\n  the spell_id, (3) a scoped block, (4) a Book setting (the epic's STRATEGY_DISCUSSION "
                   "note of\n  2026-10-18T14:33:32Z); the option's name; the binding name defaulting to the scope.\n",
                   "s6 open question")
    t = once(t, "  2026-10-18T14:14:10Z); four forms with him (the epic's STRATEGY_DISCUSSION note).\n\n",
             "  2026-10-18T14:14:10Z); four forms with him (the epic's STRATEGY_DISCUSSION note).\n"
             f"- {T}: parked in tickets/stories/backlog/ on the owner's word; S1 lands strictly unique (the epic's\n"
             "  DECISION note).\n\n", "s6 decision log")
    t = regex_once(t, r"- State: draft \(melder_0\)\. Four forms are with the owner.*?the implementation with S1\.\n",
                   "- State: draft, parked in the backlog (the owner, 2026-10-18): S1 lands with one object strictly "
                   "one spell.\n- Next: (1) the owner takes it up; (2) the four forms (the epic's STRATEGY_DISCUSSION "
                   "note of\n  2026-10-18T14:33:32Z) and his choice; (3) the design in the identity epic's patch "
                   "folder.\n", "s6 handoff")
    S6.write_bytes(t.encode("utf-8"))


def record_boards():
    b = BOARD.read_text(encoding="utf-8")
    b = regex_once(b, r"\| spell_identity_is_the_code \| in_progress \| discovery \|(.*?)\| The owner's choice of the explicit "
                      r"duplicate form \(S6\); then S1's patches for decision B and S6\. \|(.*?)\| The six stories land with "
                      r"notches, docs and the rebuild, or the owner redirects\. \|(.*?)\| 2026-10-18T14:33:32Z \| REQUIRED \|",
                   "| spell_identity_is_the_code | in_progress | implementation |\\1| Land S1 with S2's cache keys on the "
                   "owner's word: patches, the blast-radius run, the landing pass. |\\2| S1-S5 land with notches, docs "
                   "and the rebuild (S6 parked), or the owner redirects. |\\3| " + T + " | REQUIRED |", "board epic row")
    b = regex_once(b, r"\| spell_id_code_hash \| in_progress \| discovery \|(.*?)\| S1's patches updated for decision B and S6's "
                      r"form once the owner picks it; then his approval\. \|(.*?)\| 2026-10-18T14:33:32Z \| REQUIRED \|\n",
                   "| spell_id_code_hash | in_progress | implementation |\\1| Update S1's patches for decision B and strict "
                   "uniqueness; then the blast-radius run in a /tmp mirror. |\\2| " + T + " | REQUIRED |\n"
                   "| binding_manifest_hash | in_progress | discovery | claude | melder_0 | none | Inventory the spell_id-keyed "
                   "caches and stores; write S2's component patch. | The bind signature a binding manifest with its own "
                   "SHA256, in the creation cache's keys beside the spell_id. | S2 lands with S1 (tests, docs, notch, "
                   "rebuild), or the owner redirects. | tickets/stories/2026-10-18_binding_manifest_hash_story.md | "
                   + T + " | REQUIRED |\n", "board s1 row and s2 row")
    b = once(b, "  SWITCH_TRIGGER: The six stories land with notches, docs and the rebuild, or the owner redirects.\n",
             "  SWITCH_TRIGGER: S1-S5 land with notches, docs and the rebuild (S6 parked), or the owner redirects.\n",
             "board epic detail")
    b = once(b, "    - tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md\n",
             "    - tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md\n"
             "- WORK_ITEM: binding_manifest_hash\n"
             "  SWITCH_TRIGGER: S2 lands with S1 (tests, docs, notch, rebuild), or the owner redirects.\n"
             "  RESUME_HIERARCHY:\n"
             "    - tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md\n"
             "    - tickets/stories/2026-10-18_binding_manifest_hash_story.md\n", "board s2 detail")
    b = once(b, "<!-- END USER-DEFINED: alerts -->",
             f"- NEW MESSAGE for melder_1 (from melder_0, {T})\n<!-- END USER-DEFINED: alerts -->", "board alert")
    BOARD.write_bytes(b.encode("utf-8"))


def send_mail(note_range):
    m = MAIL.read_text(encoding="utf-8")
    msg = (
        "- TO: melder_1\n  FROM: melder_0\n  DATETIME: " + T + "\n  TYPE: QUESTION\n"
        "  CLAIM: M0-196. The owner's word (chat 2026-10-18): land S1 of EPIC-2026-10-18-spell_identity_is_the_code now\n"
        "    - the spell_id is the object's code - with S2's binding hash in the creation cache's keys, duplicates\n"
        "    strictly refused. It edits spell.py (a binding-manifest field on Spell, its describe and cleanup, the\n"
        "    spell_id docstrings) and spellbook.py (the bind, bind_inactive and conjure-integrity refusal texts and\n"
        "    inspect_spell's stage-3 text), both yours for S9; it touches neither cleanup_and_remove_spell nor\n"
        "    Spell.cleanup's Raises entry. Can you release both until S1 lands, or tell me when S9 lands? I prepare\n"
        "    everything else meanwhile (patches, a /tmp mirror, the new digest module, bind.py, the caches, tests) and\n"
        "    edit neither file before your answer. Whoever lands second notches above the first.\n"
        "  EVIDENCE: context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md:" + note_range + "\n"
        "  ACK_REQUESTED: true\n"
    )
    m = once(m, "<!-- END USER-DEFINED: messages -->", msg + "<!-- END USER-DEFINED: messages -->", "mail")
    MAIL.write_bytes(m.encode("utf-8"))


def note_range(path, datetime_line):
    lines = path.read_text(encoding="utf-8").split("\n")
    starts = [i for i, line in enumerate(lines) if line == datetime_line]
    if len(starts) != 1:
        sys.exit(f"note {datetime_line!r}: {len(starts)} matches")
    start = starts[0]
    end = next(i for i in range(start, len(lines)) if lines[i].startswith("  SCORE_0_TO_10:"))
    return f"{start + 1}-{end + 1}"


if __name__ == "__main__":
    record_epic()
    record_s1()
    record_s2()
    park_s6()
    record_boards()
    send_mail(note_range(EPIC, f"- DATETIME: {T}"))
    pathlib.Path("/tmp/m0_mq/T2.txt").write_text(T, encoding="utf-8")
    print("recorded at", T, "decision note", note_range(EPIC, f"- DATETIME: {T}"))
