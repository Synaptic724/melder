"""Record S1's design docs (melder_0, 2026-10-18): S1's Requirements corrected to the design, its MEASURE (D probe)
and PLAN (mapping) notes, the epic's DECISION_REQUEST note, Artifact Links, and the board rows. Exact-anchor edits;
each anchor must occur once."""
import datetime
import pathlib
import sys

ROOT = pathlib.Path.home() / "mnt/melder_private/context_compass"
TS = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
EPIC = "tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md"
STORY = "tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md"
PATCH = "system_docs/patches/active/spell_identity_is_the_code_2026_10_18"


def edit(path: str, pairs: list) -> None:
    p = ROOT / path
    text = p.read_text(encoding="utf-8")
    for old, new in pairs:
        count = text.count(old)
        if count != 1:
            sys.exit(f"{path}: anchor found {count} times: {old[:90]!r}")
        text = text.replace(old, new)
    p.write_text(text, encoding="utf-8")


story_notes = f"""- DATETIME: {TS}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The design-edge probe (D1-D10; 3.14.7t, hash seed 1, GIL 0 and 1, the same verdicts): a dataclass
    default_factory change moves the id (D1, through the generated __init__'s closure); a decorator's wrapper body
    and the decorated body each move it, the same decorated source twice does not (D2-D4); two packaging Version
    objects differ (D5); two C objects without Python-visible state (yaml's Mark) collide under the prototype and
    under today's repr rule alike (D6: their repr is the address-stripped default), so the design keeps today's repr
    rule for such a target; a class-level reference to another class and a module-level helper a method calls are
    named, not hashed (D7, D8); a class over pygments' PythonLexer costs 2.6-3.2 ms cold and 1.9 ms warm against
    0.03 ms for a plain class (D9: class namespaces are encoded at every bind); equal-data objects are one spell (D10).
  EVIDENCE:
  - context_compass/artifacts/spell_identity_20261018/probes/probe_code_digest_design_edges.py:1-111
  - context_compass/artifacts/spell_identity_20261018/runs/probe_code_digest_design_edges_gil0_seed1.txt:1-13
  - context_compass/artifacts/spell_identity_20261018/runs/probe_code_digest_design_edges_gil1_seed1.txt:1-17
  IMPACT: The code-description patch states rule 2e (today's repr rule for an object without Python-visible
    state), the decorator rule (the wrapper with its closure, not `inspect.unwrap`) and the third-party decision
    with its measured cost; the Requirements are corrected in place.
  NEXT: The owner's approval of the patches.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: {TS}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Patch section -> implementation -> validation, for after the owner's approval. (1) Code-description
    patch, steps 1-8 and the value table -> spell_code_digest.py (class SpellCodeDigest, its tables as class
    attributes) -> test_spell_code_digest.py, one test per rule (its Validation Focus Points), red first.
    (2) Binding Pipeline patch, Target boundary and State deltas -> bind.py (the `_spell_code_digest` slot,
    `__init__`, `cleanup`, `_bind_logic`'s id, `spell_id_inspector(spell)`, the three removals) -> test_bind.py,
    test_bind_managed_spell_options.py and the other files that name the fingerprint (14) moved to the new rule.
    (3) Spell Examination Profiles patch -> binding_profile.py and binding_profile_strategy.py ->
    test_binding_profile_strategy.py. (4) Architecture patch, the S1 rows of its statements table -> spell.py,
    lookup_container.py, aether.py, aether_configuration.py, the three meld docstrings, and spellbook.py's
    inspect_spell and remedy texts once melder_1 releases spellbook.py -> a docstring audit. (5) Interface
    deltas -> the F1 loop, the refusal and inspect_spell stage 3 as integration tests. (6) Architecture step 2 ->
    the blast-radius run before any of this. (7) S2's patches land in the same pass, with their own mapping.
  EVIDENCE:
  - context_compass/{PATCH}/architecture_patch.md:1-187
  - context_compass/{PATCH}/component_patch_binding_pipeline.md:1-107
  - context_compass/{PATCH}/component_patch_spell_examination_profiles.md:1-61
  - context_compass/{PATCH}/code_description_patch_spell_code_digest.md:1-164
  IMPACT: The consumption mapping the patch gate requires is in place before any code.
  NEXT: The owner's approval; then the blast-radius run.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Closure Confirmation"""

edit(STORY, [
    ("- Updated: 2026-10-18T13:06:51Z\n", f"- Updated: {TS}\n"),
    ("""- A class's spell_id hashes its module and qualname and, for the class and every class it inherits from (its
  MRO; `object` and classes without Python code by qualified name only; owner, 2026-10-18: a change in a base
  class is a change), every function its body defines - methods, the constructor, static and class methods,
  property accessors - by signature text (parameters, defaults, annotations; memory addresses removed) and
  instruction stream with each operand resolved to its value, nested code (functions, lambdas, comprehensions)
  the same way, and every value assigned in its body (class-level values; owner: "a change anywhere is a
  change").
- Line numbers, docstrings (the constant 3.14 flags with CO_HAS_DOCSTRING), comments and unused constants never
  enter it; raw bytecode is not hashed, because a docstring shifts every constant index in it.
- A function or lambda hashes its module, qualname, signature and instructions; a decorated function hashes the
  function it wraps (`inspect.unwrap`).
- An existing object hashes its class's code plus its data - the values it holds (its `__dict__` and slots), each
  by value, recursively and cycle-safe (owner, 2026-10-18).
""",
     f"""- The spell_id is the SHA256 of `v5-code`, the interpreter's cache tag and the target's encoding; the contract
  is the code-description patch ({PATCH}/code_description_patch_spell_code_digest.md; corrected here
  {TS}).
- A class: its module, qualname, metaclass and bases, and the namespace of the class and of every class it
  inherits from outside the standard library (owner, 2026-10-18: a change in a base class is a change) - each
  function by its code (the instruction stream with each loaded constant by value, argument counts, flags, name
  tables, exception table), its defaults, its annotations' code, its closure values and type parameters, nested
  code the same way, and every value assigned in its body (class-level values; owner: "a change anywhere is a
  change").
- Line numbers, docstrings, comments and unused constants never enter it: constants are read by value in the order
  the instructions first load them, because in 3.14 a docstring takes or shifts slot 0 of the constant table.
- A function or lambda: its module, qualname and code as above. A decorated function is the wrapper itself, whose
  closure holds the function it wraps, so the decorator's code and the wrapped body both count (D2-D4).
- An existing object: its class's code plus its data - its slots and `__dict__`, each by value, recursively and
  cycle-safe (owner, 2026-10-18); an object with no Python-visible state keeps today's rule (type and
  address-free repr).
"""),
    ("""- No source-file read at bind; the digest is computed once per class object (a class object's code does not
  change) and reused.
""",
     """- No source-file read at bind; code-object digests are memoized per Bind (code objects are immutable), class
  and object encodings are computed at each bind (classes and objects are mutable).
"""),
    ("- [ ] Task: the owner's calls (the epic's Open Questions).\n",
     "- [x] Task: the owner's calls (the epic's Open Questions; all five made 2026-10-18).\n"),
    ("- [ ] Task: the component patch (Binding Pipeline: the code digest; the hash domain).\n",
     f"- [x] Task: the patches (architecture; Binding Pipeline and Spell Examination Profiles component;\n"
     f"  code-description) - written {TS}, the owner's approval pending.\n"),
    ("""- A closure's captured values are not code: decide with the owner if a factory-made class counts.
- Bind's cost: memoize per class object; measure.
""",
     """- A closure's captured values count (derived from calls 2-3; stated for the owner in the architecture patch):
  two classes a factory makes with different captured values are two spells.
- Bind's cost: code digests memoized; a class over a large third-party base costs milliseconds (D9); measured on
  the gauntlet at landing.
"""),
    ("""- To confirm in the design docs: two existing objects of one class holding equal data are one spell, so the
  second bind is refused as the same spell.
""",
     """- Stated in the architecture patch for the owner: two existing objects of one class with equal data are one
  spell (D10), so the second bind is refused as the same spell.
- DECISION_REQUEST (owner): third-party code and objects - A, digested like the application's (recommended), or
  B, named with the distribution's version (architecture patch).
"""),
    ("- 2026-10-18T13:06:51Z: the owner's call 4 - a renamed local variable counts (the epic's DECISION note).\n",
     "- 2026-10-18T13:06:51Z: the owner's call 4 - a renamed local variable counts (the epic's DECISION note).\n"
     f"- {TS}: the design docs written for the owner's approval; Requirements corrected to them (MEASURE and\n"
     "  PLAN notes).\n"),
    ("  - artifacts/spell_identity_20261018/runs/ (four runs of each: hash seeds 1 and 2, GIL 0 and 1)\n"
     "- DISPOSITION: retain_as_reference\n",
     "  - artifacts/spell_identity_20261018/runs/ (four runs of each: hash seeds 1 and 2, GIL 0 and 1)\n"
     "  - artifacts/spell_identity_20261018/probes/probe_code_digest_design_edges.py (D1-D10, two runs)\n"
     f"  - {PATCH}/architecture_patch.md\n"
     f"  - {PATCH}/component_patch_binding_pipeline.md\n"
     f"  - {PATCH}/component_patch_spell_examination_profiles.md\n"
     f"  - {PATCH}/code_description_patch_spell_code_digest.md\n"
     "- DISPOSITION: retain_as_reference (the probes); promote_to_documentation (the patch docs, at landing)\n"),
    ("## Closure Confirmation", story_notes),
    ("""- State: in_progress (melder_0), discovery: the design docs; all five of the owner's calls are made (renames
  count). spellbook.py is melder_1's until S8 lands (M1-31; the epic's FACT note).
""",
     """- State: in_progress (melder_0), discovery: the design docs are written and wait for the owner's approval;
  all five of his calls are made and three decisions are with him (the epic's DECISION_REQUEST note).
  spellbook.py is melder_1's until S8 lands (M1-31; the epic's FACT note).
"""),
    ("""- Next: the architecture patch, the Binding Pipeline and Spell Examination Profiles component patches and the
  code-description patch, for the owner's approval.
""",
     """- Done since: the four patch docs in system_docs/patches/active/spell_identity_is_the_code_2026_10_18/, the D
  probe (MEASURE note) and the mapping (PLAN note).
- Next: the owner's approval and decisions; the blast-radius run in a /tmp mirror; then S2's patches.
"""),
])

epic_note = f"""- DATETIME: {TS}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: S1's design docs are written ({PATCH}/: the architecture patch, the
    Binding Pipeline and Spell Examination Profiles component patches, the code-description patch) and wait for
    the owner's approval with three decisions: (1) the "conduit manifest" reading (S2; asked 2026-10-18);
    (2) third-party code and objects - A (recommended): digested like the application's, an upgrade moves the ids
    and a third-party object with per-process state makes its holder's id per-process; B: named by qualified name
    and distribution version, bounded, blind to settings kept inside library objects; (3) a legacy record holding
    one object twice restores the first and files a shortfall per dropped duplicate (recommended), or refuses
    whole. Stated for him: one object binds once per process by default (call 5), so a second Book that binds the
    same class is refused and shares it instead; closures count; equal-data objects are one spell; code a spell
    only names is not hashed.
  EVIDENCE:
  - context_compass/{PATCH}/architecture_patch.md:1-187
  - context_compass/artifacts/spell_identity_20261018/runs/probe_code_digest_design_edges_gil0_seed1.txt:1-13
  IMPACT: No src/ edit before his approval; S2's patches follow his answer on (1).
  NEXT: Report the docs to the owner; on approval, the blast-radius run in a /tmp mirror.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation"""

edit(EPIC, [
    ("- Updated: 2026-10-18T13:06:51Z\n", f"- Updated: {TS}\n"),
    ("- [ ] Task: the owner's calls on the open edges (Open Questions).\n",
     "- [x] Task: the owner's calls on the open edges (Open Questions; all five made 2026-10-18).\n"),
    ("- [ ] Task: the architecture patch for the epic; a component patch per story before its code.\n",
     "- [ ] Task: the architecture patch for the epic; a component patch per story before its code (the architecture\n"
     f"  patch and S1's written {TS}; the owner's approval pending).\n"),
    ("- For S3: which binding fields revalidate and which only rebind",
     "- Third-party code and objects (S1): A, digested like the application's (recommended), or B, named by qualified\n"
     "  name and distribution version (architecture patch).\n"
     "- A record made before the change that holds one object twice (S5): restore the first and file a shortfall per\n"
     "  dropped duplicate (recommended), or refuse the restore whole.\n"
     "- For S3: which binding fields revalidate and which only rebind"),
    ("  lands (FACT note).\n",
     "  lands (FACT note).\n"
     f"- {TS}: S1's design docs written; three decisions with the owner (DECISION_REQUEST note).\n"),
    ("  - artifacts/spell_identity_20261018/ (the epic's scripts)\n",
     "  - artifacts/spell_identity_20261018/ (the epic's scripts)\n"
     f"  - {PATCH}/ (the architecture patch; S1's component and code-description patches)\n"),
    ("## Closure Confirmation", epic_note),
    ("""- Next: (1) S1's design docs - the architecture patch, the Binding Pipeline and Spell Examination Profiles
  component patches and the code-description patch - for the owner's approval; (2) his word on the "conduit
  manifest" reading; (3) S2's component patches; (4) claim spellbook.py back from melder_1 before S1's src edit.
""",
     """- Next: (1) the owner's approval of the architecture patch and S1's patches (written 2026-10-18) and his three
  decisions - the "conduit manifest" reading, third-party code, legacy duplicates; (2) the blast-radius run in a
  /tmp mirror; (3) S2's component patches; (4) claim spellbook.py back from melder_1 before S1's src edit.
"""),
])

# attention board rows
ab = ROOT / "attention_board.md"
lines = ab.read_text(encoding="utf-8").split("\n")
new_next = {
    "spell_identity_is_the_code": "The owner's approval of S1's patches and his three decisions (conduit manifest, third-party code, legacy duplicates).",
    "spell_id_code_hash": "The owner's approval of the patches; then the blast-radius run in a /tmp mirror.",
}
for index, line in enumerate(lines):
    cells = line.split(" | ")
    key = cells[0][2:] if line.startswith("| ") else None
    if key in new_next and len(cells) == 12:
        cells[6] = new_next[key]
        cells[10] = TS
        lines[index] = " | ".join(cells)
ab.write_text("\n".join(lines), encoding="utf-8")

# artifact board rows
edit("artifact_board.md", [
    ("record_s1_measure.py and sync_s1_artifact_rows.py (S1's MEASURE note and rows); probes/ and runs/ are rowed under S1. | 2026-10-18T12:45:46Z |",
     f"record_s1_measure.py and sync_s1_artifact_rows.py (S1's MEASURE note and rows), record_s1_design_docs.py (S1's design docs, notes and rows); probes/ and runs/ are rowed under S1. | {TS} |"),
    ("and the src/melder corpus and cost probe (probe_code_digest_corpus.py), with their runs under runs/ (hash seeds 1 and 2, GIL 0 and 1); S1's tests start here. | 2026-10-18T12:45:46Z | REQUIRED |",
     f"the src/melder corpus and cost probe (probe_code_digest_corpus.py) and the design edges D1-D10 (probe_code_digest_design_edges.py), with their runs under runs/ (hash seeds 1 and 2, GIL 0 and 1); S1's tests start here. | {TS} | REQUIRED |\n"
     f"| tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md | {PATCH}/ | patch_doc | active | promote_to_documentation | The epic's architecture patch and S1's Binding Pipeline, Spell Examination Profiles and code-description patches; the owner's approval before any src edit; S2-S5 add theirs. | {TS} | REQUIRED |"),
])
print("TS", TS)
