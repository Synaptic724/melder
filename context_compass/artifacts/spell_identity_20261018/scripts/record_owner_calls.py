"""Record the owner's calls on the epic's open edges (chat 2026-10-18) and route S1's design work (melder_0).

- Epic: in_progress; a DECISION note (calls 1-3 and 5 made, call 4 and the "conduit manifest" reading pending);
  Open Questions, Decision Log and the handoff summary brought current.
- S1: in_progress for its design docs; requirements carry bases, class-level values and an object's data.
- S2: the "conduit manifest" reading as an open question. S4: its scope question withdrawn (owner: not this change).
- attention_board.md: the epic's row in_progress, a row and detail for S1. mailbox_board.md: M1-29 (an ACK) consumed.
Every replacement must match exactly once. Usage (from context_compass/): record_owner_calls.py <NOW>
"""
import pathlib
import re
import sys

NOW = sys.argv[1]
EPIC = pathlib.Path("tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md")
S1 = pathlib.Path("tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md")
S2 = pathlib.Path("tickets/stories/2026-10-18_binding_manifest_hash_story.md")
S4 = pathlib.Path("tickets/stories/2026-10-18_one_registration_per_object_story.md")
EPIC_REF = "context_compass/" + EPIC.as_posix()


def rep(text: str, old: str, new: str) -> str:
    """Replace one exact occurrence; refuse zero or several."""
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected one match, found {count}: {old[:90]!r}")
    return text.replace(old, new)


def section_span(text: str, header: str) -> str:
    """1-based range of a section: its header through the last non-blank line before the next '## '."""
    lines = text.split("\n")
    start = next(i for i, line in enumerate(lines) if line.startswith(header))
    nxt = next(i for i in range(start + 1, len(lines)) if lines[i].startswith("## "))
    end = nxt - 1
    while not lines[end].strip():
        end -= 1
    return f"{start + 1}-{end + 1}"


def epic() -> None:
    """The calls, the epic's state and its current view."""
    text = EPIC.read_text(encoding="utf-8")
    text = rep(text, "- Status: ready\n", "- Status: in_progress\n")
    text = rep(text, "- Updated: 2026-10-18T12:01:17Z\n", f"- Updated: {NOW}\n")
    text = rep(text, "- from_state: draft\n- to_state: ready\n- transition_reason: the owner's direction and his"
               " instruction (chat 2026-10-18) to make an epic with its stories and\n  start next turn; the five stories"
               " are filed with their open questions.\n",
               "- from_state: ready\n- to_state: in_progress\n- transition_reason: the owner made calls 1-3 and 5"
               " (chat 2026-10-18; DECISION note), so S1's design docs\n  start; call 4 and the \"conduit manifest\""
               " reading wait for his word.\n")
    text = rep(text,
               "- The owner's calls before S1's implementation: (1) inherited code - does a change in a base class's"
               " method move its\n  subclasses' spell_ids (the prototype reads bases by name only)? (2) class-level"
               " values (e.g. `retries = 3` on the\n  class) - part of the code? (3) an existing object bound as a spell"
               " - its class's code plus its data? (4) a renamed\n  local variable - a code change (the prototype says"
               " yes)? (5) the scope of one registration - per process (today's\n  default regime) or per frame?\n",
               "- The owner's calls before S1's implementation, made 2026-10-18 (DECISION note): (1) inherited code -"
               " yes, a change\n  in a base class moves its subclasses' spell_ids; (2) class-level values - code (\"a"
               " change anywhere is a change\");\n  (3) an existing object - its class's code plus its data; (5) the"
               " scope of a registration - not part of this\n  change, the existing spell-id regime stands. Open: (4) a"
               " renamed local variable - explained with an example,\n  counting it recommended (the prototype does), his"
               " word pending.\n- The owner's \"conduit manifest\" (chat 2026-10-18), read as: each spell's binding hash"
               " is recorded in what the\n  conduit builds and caches the spell from (its plan, its creation cache), and"
               " a changed hash revalidates and\n  rebuilds that spell; sent for his confirmation.\n")
    text = rep(text, "  (FACT note).\n\n## Artifact Links",
               f"  (FACT note).\n- {NOW}: the owner made calls 1-3 and 5; in_progress for S1's design docs (DECISION"
               " note).\n\n## Artifact Links")
    span = section_span(text, "## Open Questions")
    note = f"""
- DATETIME: {NOW}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's calls on the open edges (chat 2026-10-18). (1) "yes": a change in a base class's code moves its
    subclasses' spell_ids, so a class's code digest includes the code of the classes it inherits from. (2) "class
    level values are code yeah, so a change anywhere is a change": values assigned in a class body enter the digest.
    (3) "yes": an existing object bound as a spell is identified by its class's code plus its data. (5) "this isn't
    related to our change your focus is bind and bindhashing for the conduit manifest": the scope of a registration
    stays the existing spell-id regime and no story decides it; the focus is bind and its hashing (S1) and the
    binding manifest the conduit builds from (S2, with S3's revalidation). (4) Open: he asked what a local variable
    is - the example and the recommendation (count a rename, as answer 2 implies) are sent, with the reading of
    "conduit manifest" for him to confirm. melder_1 ACKed M0-193 (M1-29): it holds no file and claims from melder_0
    by message before it edits one.
  EVIDENCE: {EPIC_REF}:{span}
  IMPACT: S1 can be designed: a class's bases, its class-level values and an existing object's data are inputs of
    the code hash. S4 loses its scope question.
  NEXT: Read Bind's fingerprint and the binding profile whole, extend the prototype to bases, class-level values and
    object data, then write S1's design docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""
    text = rep(text, "  NEXT: The owner's calls on the five edges.\n  REREAD: REQUIRED\n  SCORE_0_TO_10: 8\n",
               "  NEXT: The owner's calls on the five edges.\n  REREAD: REQUIRED\n  SCORE_0_TO_10: 8\n" + note)
    text = rep(text,
               "- State: ready (melder_0), discovery. Five stories filed (S1-S2 ready, S3-S5 draft); nothing in src/ yet."
               " Evidence:\n  the probes in Artifact Links. S6 of the correctness epic is turned in; its part B and open"
               " items live here.\n  melder_1's lane is turned in and its files are free (M1-28); the next notch is"
               " above 0.2.8255.\n- Next: (1) the owner's five calls (Open Questions); (2) the architecture patch and"
               " the S1/S2 component patches;\n  (3) S1 and S2.\n",
               "- State: in_progress (melder_0), discovery. The owner made calls 1-3 and 5 (DECISION note of"
               f" {NOW}); S1 is\n  in_progress (its design docs), S2 ready, S3-S5 draft; nothing in src/ yet. Evidence:"
               " the probes in Artifact\n  Links. S6 of the correctness epic is turned in; its part B and open items"
               " live here. melder_1 holds no file\n  (M1-28, M1-29); the next notch is above 0.2.8255.\n- Next:"
               " (1) S1's design docs - architecture patch, code-hash component patch, code-description patch; (2) the\n"
               "  owner's word on call 4 and the \"conduit manifest\" reading; (3) S2's component patches.\n")
    EPIC.write_text(text, encoding="utf-8")
    print("epic: open questions", span)


def story_s1() -> None:
    """S1 in progress; its requirements carry the owner's calls."""
    text = S1.read_text(encoding="utf-8")
    text = rep(text, "- Status: ready\n", "- Status: in_progress\n")
    text = re.sub(r"^- Updated: \S+$", f"- Updated: {NOW}", text, count=1, flags=re.M)
    text = rep(text, "- ENTRY_GATE: the owner's calls on the epic's open edges (inherited code, class-level values,"
               " existing objects,\n  local renames, scope);",
               "- ENTRY_GATE: the owner's calls on the epic's open edges (made 2026-10-18, local renames pending);")
    text = rep(text,
               "- A class's spell_id hashes its module, qualname and bases (per the owner's inherited-code call) and,"
               " for every\n  function its body defines - methods, the constructor, static and class methods,"
               " property accessors - the\n  signature text (parameters, defaults, annotations; memory addresses"
               " removed) and the instruction stream with each\n  operand resolved to its value; nested code"
               " (functions, lambdas, comprehensions) is hashed the same way.\n",
               "- A class's spell_id hashes its module and qualname and, for the class and every class it inherits from"
               " (its\n  MRO; `object` and classes without Python code by qualified name only; owner, 2026-10-18: a"
               " change in a base\n  class is a change), every function its body defines - methods, the constructor,"
               " static and class methods,\n  property accessors - by signature text (parameters, defaults,"
               " annotations; memory addresses removed) and\n  instruction stream with each operand resolved to its"
               " value, nested code (functions, lambdas, comprehensions)\n  the same way, and every value assigned in"
               " its body (class-level values; owner: \"a change anywhere is a\n  change\").\n")
    text = rep(text, "- An existing object hashes as the owner calls it (its class's code plus its data is the proposal).\n",
               "- An existing object hashes its class's code plus its data - the values it holds (its `__dict__` and"
               " slots), each\n  by value, recursively and cycle-safe (owner, 2026-10-18).\n- Local variable names are"
               " hashed, so a rename is a new version, unless the owner rules otherwise (call 4,\n  pending).\n")
    text = rep(text, "- from_state: draft\n- to_state: ready\n- transition_reason: filed under"
               " EPIC-2026-10-18-spell_identity_is_the_code on the owner's direction (chat\n  2026-10-18); scope and"
               " owner set, the open questions named.\n",
               "- from_state: ready\n- to_state: in_progress\n- transition_reason: the owner made calls 1-3 and 5 (chat"
               " 2026-10-18; the epic's DECISION note), so the\n  design docs start; call 4 (local names) is pending,"
               " counted by default.\n")
    text = rep(text, "- The epic's five calls, foremost inherited code and existing objects.\n",
               "- Call 4 (a renamed local variable): pending; counted by default.\n- To confirm in the design docs:"
               " two existing objects of one class holding equal data are one spell, so the\n  second bind is refused"
               " as the same spell.\n")
    text = rep(text, "(the epic's DECISION note).\n\n## Artifact Links",
               f"(the epic's DECISION note).\n- {NOW}: the owner made calls 1-3 and 5 (the epic's DECISION note);"
               " in_progress for the design docs.\n\n## Artifact Links")
    text = rep(text, "- State: ready (melder_0); waiting on the owner's calls and the patches.\n- Next: the component"
               " patch after the owner's calls.\n",
               "- State: in_progress (melder_0), discovery: the design docs; call 4 pending (counted by default).\n"
               "- Next: read Bind's fingerprint and the binding profile whole; extend the prototype to bases,"
               " class-level\n  values and object data; write the architecture patch, the code-hash component patch"
               " and its code\n  description.\n")
    S1.write_text(text, encoding="utf-8")
    print("S1 in_progress")


def story_s2() -> None:
    """S2 carries the "conduit manifest" reading as an open question."""
    text = S2.read_text(encoding="utf-8")
    text = re.sub(r"^- Updated: \S+$", f"- Updated: {NOW}", text, count=1, flags=re.M)
    text = rep(text, "- Which managed settings belong to the binding hash, or to a pool-only setting (S3's question).\n",
               "- Which managed settings belong to the binding hash, or to a pool-only setting (S3's question).\n- The"
               " owner's \"conduit manifest\" (chat 2026-10-18), read as: the binding hash recorded in what the"
               " conduit\n  builds and caches the spell from; sent for his confirmation (the epic's DECISION note"
               f" of {NOW}).\n")
    S2.write_text(text, encoding="utf-8")
    print("S2 open question")


def story_s4() -> None:
    """S4's scope follows the existing regime; its scope question is withdrawn."""
    text = S4.read_text(encoding="utf-8")
    text = re.sub(r"^- Updated: \S+$", f"- Updated: {NOW}", text, count=1, flags=re.M)
    text = rep(text, "- DEPENDENCIES: S1; the owner's scope call (per process or per frame).\n", "- DEPENDENCIES: S1.\n")
    text = rep(text, "- FAILURE_ESCALATION: DECISION_REQUEST on the scope; CONFLICT if another lane takes spellbook.py.\n",
               "- FAILURE_ESCALATION: CONFLICT if another lane takes spellbook.py.\n")
    text = rep(text, "  already registered in scope - per process by default, per frame under per-frame ids - with"
               " nothing registered.\n",
               "  already registered under the existing spell-id regime - per process by default, per frame under"
               " per-frame ids;\n  the owner: the scope is not part of this change - with nothing registered.\n")
    text = rep(text, "- The scope (per process or per frame) - the epic's call 5.\n",
               "- None: the scope follows the existing spell-id regime (owner, 2026-10-18: not part of this change).\n")
    text = rep(text, "stays draft until S1 lands and the epic's call 5 (scope) is made.\n", "stays draft until S1 lands.\n")
    text = rep(text, "  no longer waits on a release.\n\n## Artifact Links",
               f"  no longer waits on a release.\n- {NOW}: the scope question withdrawn - the existing spell-id regime"
               " stands (owner; the epic's\n  DECISION note).\n\n## Artifact Links")
    S4.write_text(text, encoding="utf-8")
    print("S4 scope withdrawn")


def boards() -> None:
    """The epic's row in progress, S1's row and detail; M1-29 consumed."""
    path = pathlib.Path("attention_board.md")
    text = path.read_text(encoding="utf-8")
    old = re.search(r"^\| spell_identity_is_the_code \| ready \| discovery \|.*$", text, flags=re.M).group(0)
    new = ("| spell_identity_is_the_code | in_progress | discovery | claude | melder_0 | none | The owner's word on call"
           " 4 (local names) and the \"conduit manifest\" reading. | A spell_id that is the object's code; the bind"
           " signature a manifest with its own hash that revalidates; one object, one spell. | The five stories land"
           " with notches, docs and the rebuild, or the owner redirects. |"
           f" tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md | {NOW} | REQUIRED |")
    s1_row = ("| spell_id_code_hash | in_progress | discovery | claude | melder_0 | none | Read Bind's fingerprint and the"
              " binding profile whole; then S1's design docs. | The spell_id is the SHA256 of the registered object's"
              " code - its bases, class-level values and an object's data included; docstrings and comments out. | S1"
              " lands with S2 (tests, docs, notch, rebuild), or the owner redirects. |"
              f" tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md | {NOW} | REQUIRED |")
    text = rep(text, old + "\n", new + "\n" + s1_row + "\n")
    text = rep(text, "    - tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md\n<!-- END USER-DEFINED:"
               " active_attention_details -->",
               "    - tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md\n- WORK_ITEM: spell_id_code_hash\n"
               "  SWITCH_TRIGGER: S1 lands with S2 (tests, docs, notch, rebuild), or the owner redirects.\n"
               "  RESUME_HIERARCHY:\n    - tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md\n"
               "    - tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md\n"
               "<!-- END USER-DEFINED: active_attention_details -->")
    text = rep(text, "- NEW MESSAGE for melder_0 (from melder_1, 2026-10-18T12:10:26Z)\n", "")
    path.write_text(text, encoding="utf-8")
    mb = pathlib.Path("mailbox_board.md")
    text = mb.read_text(encoding="utf-8")
    start = text.index("- TO: melder_0\n  FROM: melder_1\n  DATETIME: 2026-10-18T12:10:26Z\n")
    end = text.index("ACK_REQUESTED: false\n", start) + len("ACK_REQUESTED: false\n")
    if "M1-29" not in text[start:end] or text[start:end].count("- TO: ") != 1:
        raise SystemExit("M1-29 not found as one message")
    text = text[:start] + text[end:]
    pat = re.compile(r"^(\| melder_0 \| claude \| 2026-09-26T22:24:06Z \| )[0-9TZ:-]+( \| active \|)$", re.M)
    if len(pat.findall(text)) != 1:
        raise SystemExit("check-in row not found")
    text = pat.sub(lambda m: m.group(1) + NOW + m.group(2), text)
    mb.write_text(text, encoding="utf-8")
    print("boards: rows, detail, M1-29 consumed")


if __name__ == "__main__":
    epic()
    story_s1()
    story_s2()
    story_s4()
    boards()
