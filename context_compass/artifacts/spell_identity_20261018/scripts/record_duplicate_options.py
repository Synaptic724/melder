"""Record the explicit-duplicate exploration in the identity epic, S1 and the boards (melder_0, 2026-10-18).

Run from context_compass/. Writes the timestamp it used to /tmp/m0_mq/T.txt for the filing script.
"""
import pathlib
import re
import sys
from datetime import datetime, timezone

T = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
EPIC = pathlib.Path("tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md")
S1 = pathlib.Path("tickets/stories/2026-10-18_spell_id_hashes_the_object_code_story.md")
BOARD = pathlib.Path("attention_board.md")
ARTS = pathlib.Path("artifact_board.md")


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


NOTE = """- DATETIME: {T}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: STRATEGY_DISCUSSION
  CLAIM: Registering one object more than once on purpose (the owner, DECISION note of
    2026-10-18T14:14:10Z), for his choice.
    Objective: keep several bindings of the same code - for example `Worker` as a shared `unique` named
    `shared` and as a `many` named `fresh` - each called by name, while an accidental second registration
    stays refused.
    Constraints: identity stays the object's code (S1); the duplication is written in the bind and recorded;
    nothing changes at meld; it lands with S1.
    Known, read on 0.2.8255: the spell_id hashes the binding name today (`Bind._bind_logic` passes it to
    `sha256_profile`), so a class binds once per binding name. bind and bind_inactive refuse an id the Book
    or the process already holds. An active spell also claims its address frame-wide: the spellframe or the
    class name, with the binding name or "__default__". A meld names a spell by spell_id or by that
    address. The record keeps the binding name and restore replays it through `bind`. A parameter typed
    with a class that several spells provide is refused at conjure (AMBIGUOUS_PROVIDER) unless a SpellMap
    default picks one. So from S1 on, the second registration of a class under another name - accepted
    today - meets the collision refusal. Different data needs nothing new: two existing objects of one
    class with different data are two spells under S1 (call 3); the option is for bindings of one class,
    or of equal-data objects.
    Unknowns: none that block; the form, the name and the binding-name default are the owner's.
    Options: (1) an option on the bind verbs, `duplicate_scope="fresh"`: the scope joins the spell_id (the
    SHA256 of the code and the scope; no scope keeps the plain code id); the Spell keeps the scope and the
    plain code id, so the copies of one object list together; the record keeps the scope and restore and
    graft replay it; an unscoped second registration is refused with a message naming the first and the
    option. (2) `duplicate=True`: the address enters the spell_id of an explicit duplicate. (3) a block,
    `with spellbook.duplicate_scope("tenant_a"):`, giving every bind inside it the scope - (1) for a batch,
    held per thread. (4) a Book setting that allows duplicates.
    Tradeoffs: (1) keeps identity and binding apart - the scope is identity, the binding name stays a
    binding field S3 can change; (2) is one flag but puts a binding field back into identity, so renaming a
    duplicate's binding (S3) would make it another spell; (3) suits tenants and can follow (1); (4) is
    explicit per Book, not per bind, against "it has to be explicit". Under every form each active copy
    needs its own address (the frame claim), a class annotation sees every copy (AMBIGUOUS_PROVIDER unless
    a SpellMap default picks one, as two binding names do today) and an unfiltered managed release of two
    managed copies asks for `spell_id=` (as today).
    Recommendation: (1), with the binding name defaulting to the scope when none is given, so
    `bind(spell=Worker, existence="many", duplicate_scope="fresh")` is melded as `meld(spell=Worker,
    binding_name="fresh")`; (3) and a strict switch wait in the parked configurables epic.
    Decision ask: the form, and the name (`duplicate_scope`, from his words, or another). Filed as S6,
    STORY-2026-10-18-explicit_duplicate_binding; the configurables epic is filed in the backlog as
    EPIC-2026-10-18-identity_and_caching_configurables.
  EVIDENCE:
  - src/melder/aether/spellbook/bind/bind.py:795-804
  - src/melder/aether/spellbook/spellbook.py:5405-5419
  - src/melder/aether/spellbook/spellbook.py:5754-5776
  - src/melder/aether/aether.py:2550-2624
  - src/melder/aether/aetheric_frame/aetheric_frame.py:1064-1083
  - src/melder/utilities/helpers/general_helpers.py:365-401
  - src/melder/aether/conduit/meld/meld.py:2067-2149
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2142-2199
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_3.py:628-704
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/ambiguous_provider_strategy.py:71-118
  - src/melder/aether/conduit/creations/release_managed_spell.py:515-580
  - context_compass/system_docs/patches/active/spell_identity_is_the_code_2026_10_18/architecture_patch.md:51-94
  IMPACT: Without S6 at S1's landing, S1 removes today's way to bind one class twice and puts nothing in
    its place. Once the form is chosen, the architecture patch's formula (invariant 1) and its one-object
    rule (invariant 5) gain the explicit exception, and S4's refusal names the option.
  NEXT: The owner's choice of the form and the name; then S1's patches updated for decision B and S6.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
""".replace("{T}", T)


def record_epic():
    t = EPIC.read_text(encoding="utf-8")
    t = once(t, "- Updated: 2026-10-18T14:14:10Z\n- Target Window: 2026-Q4",
             f"- Updated: {T}\n- Target Window: 2026-Q4", "epic updated")
    t = once(t, "- One object is one spell: registering it again, under any name or existence or as a staged version, "
                "is refused.\n",
             "- One object is one spell: registering it again, under any name or existence or as a staged version, "
             "is refused\n  unless the bind says so explicitly (S6).\n", "epic goal")
    t = once(t, "  research history, tests, docs and the release note (S5).\n",
             "  research history, tests, docs and the release note (S5).\n"
             "- [ ] Story: STORY-2026-10-18-explicit_duplicate_binding - a bind that says so registers one object "
             "more than once,\n  its scope recorded; lands with S1 (S6).\n", "epic stories")
    t = once(t, "- [x] Task: the owner's calls on the open edges (Open Questions; all five made 2026-10-18).\n",
             "- [x] Task: the owner's calls on the open edges (Open Questions; all five made 2026-10-18).\n"
             "- [x] Task: the parked configurables epic filed (EPIC-2026-10-18-identity_and_caching_configurables, "
             "backlog).\n", "epic tasks")
    t = regex_once(t, r"- Stories land S1 -> S2 -> S3 -> S4 -> S5 \(S1 and S2 may land together.*?release note\.\n",
                   "- Stories land S1 -> S2 -> S3 -> S4 -> S5 (S1 and S2 may land together, so the caches never "
                   "see a spell_id without\n  its binding hash; S6 lands with S1, so a bind can duplicate an object "
                   "on purpose from the moment an\n  implicit duplicate is refused); one notch per landed source "
                   "change; the identity change is one Breaking\n  entry in the running release note.\n",
                   "epic rollout")
    t = regex_once(t, r"- Exploring: an explicit bind that registers one object more than once.*?it must land with S1\.\n",
                   "- The explicit duplicate bind (S6, STORY-2026-10-18-explicit_duplicate_binding): four forms with "
                   "the owner, (1)\n  recommended - an option whose scope joins the spell_id, the binding name "
                   "defaulting to the scope - and\n  the option's name (STRATEGY_DISCUSSION note of "
                   + T + "); it lands with S1.\n"
                   "- Configurables (how deeply Melder reads objects, installed packages, caching, the duplicates "
                   "policy, presets\n  and advice): parked in EPIC-2026-10-18-identity_and_caching_configurables "
                   "(backlog), on the owner's word.\n",
                   "epic open questions")
    t = once(t, "\n## Artifact Links (Optional)\n",
             f"- {T}: the explicit duplicate bind explored - four forms with the owner, (1) recommended; S6 filed;"
             "\n  the configurables epic filed in the backlog (STRATEGY_DISCUSSION note).\n"
             "\n## Artifact Links (Optional)\n", "epic decision log")
    t = once(t, "\n## Closure Confirmation\n", "\n" + NOTE + "\n## Closure Confirmation\n", "epic note")
    handoff = (
        "- State: in_progress (melder_0), discovery. The owner made all five calls and three decisions (DECISION "
        "notes of\n  2026-10-18T12:15:14Z, 13:06:51Z and 14:14:10Z): the conduit-manifest reading stands (S2, S3), "
        "installed\n  third-party code is named by version (B, S1), an old record holding one object twice "
        "restores the first (S5).\n  S1 is in_progress: its four patch docs are written and wait for the update "
        "to B and S6's form, then his\n  approval. S6 (the explicit duplicate bind) is draft with four forms "
        "before him (STRATEGY_DISCUSSION note of\n  " + T + "). S2 ready, S3-S5 draft; nothing in src/ yet. "
        "Configurables are parked in\n  EPIC-2026-10-18-identity_and_caching_configurables (backlog). melder_1 "
        "holds spellbook.py and spell.py for S9\n  of EPIC-2026-10-17-correctness_defects until it lands (M1-33, "
        "M0-195); S8 is on hold; three correctness\n  stories wait for this epic (Constraints); the next notch is "
        "above 0.2.8255, or above S9's.\n"
        "- Next: (1) the owner's choice of S6's form and name; (2) S1's patches updated for decision B and S6, "
        "then his\n  approval; (3) the blast-radius run in a /tmp mirror; (4) S2's component patches; (5) "
        "spellbook.py and spell.py\n  back from melder_1 after S9 lands.\n"
    )
    t = regex_once(t, r"- State: in_progress \(melder_0\), discovery\. The owner made all five calls.*?"
                      r"back from melder_1 after S9 lands\.\n", handoff, "epic handoff")
    EPIC.write_bytes(t.encode("utf-8"))


def record_s1():
    t = S1.read_text(encoding="utf-8")
    t = once(t, "- Updated: 2026-10-18T13:42:22Z\n", f"- Updated: {T}\n", "s1 updated")
    t = once(t, "- STORY-2026-10-18-binding_manifest_hash (lands with this story)\n",
             "- STORY-2026-10-18-binding_manifest_hash (lands with this story)\n"
             "- STORY-2026-10-18-explicit_duplicate_binding (S6; lands with this story)\n", "s1 deps")
    t = once(t, "- DECISION_REQUEST (owner): third-party code and objects - A, digested like the application's "
                "(recommended), or\n  B, named with the distribution's version (architecture patch).\n",
             "- Decided (the owner, the epic's DECISION note of 2026-10-18T14:14:10Z): installed third-party code "
             "and objects are\n  named by qualified name and distribution version (B); the patches move to B. A "
             "configurable for it is parked\n  in EPIC-2026-10-18-identity_and_caching_configurables.\n"
             "- With the owner: the form of the explicit duplicate bind, which lands with this story (S6; the "
             "epic's\n  STRATEGY_DISCUSSION note of " + T + "). With it, a duplicate's scope is the one bind "
             "input in the id.\n", "s1 open questions")
    t = once(t, "  PLAN notes).\n\n## Artifact Links (Optional)\n",
             "  PLAN notes).\n- 2026-10-18T14:14:10Z: the owner's decisions - installed third-party code by "
             "version (B); the explicit\n  duplicate bind lands with this story as S6 (the epic's DECISION "
             "note).\n\n## Artifact Links (Optional)\n", "s1 decision log")
    t = regex_once(t, r"- State: in_progress \(melder_0\), discovery: the design docs are written and wait.*?"
                      r"\(M1-31; the epic's FACT note\)\.\n",
                   "- State: in_progress (melder_0), discovery: the design docs are written; the owner decided B "
                   "for installed\n  third-party code (the epic's DECISION note of 2026-10-18T14:14:10Z), so they "
                   "move to B, and S6's form joins\n  them once he picks it. spellbook.py and spell.py are "
                   "melder_1's until S9 lands (M1-33).\n", "s1 state")
    t = once(t, "- Next: the owner's approval and decisions; the blast-radius run in a /tmp mirror; then S2's "
                "patches.\n",
             "- Next: the owner's choice of S6's form; the patches updated for B and S6; his approval; the "
             "blast-radius run\n  in a /tmp mirror; then S2's patches.\n", "s1 next")
    S1.write_bytes(t.encode("utf-8"))


def record_boards():
    t = BOARD.read_text(encoding="utf-8")
    t = regex_once(t, r"\| Explore the owner's explicit duplicate bind and bring him options; then S1's patches for "
                      r"decision B\. \|(.*?)\| 2026-10-18T14:14:10Z \| REQUIRED \|",
                   "| The owner's choice of the explicit duplicate form (S6); then S1's patches for decision B and "
                   "S6. |\\1| " + T + " | REQUIRED |", "board epic row")
    t = regex_once(t, r"\| Update S1's patches for decision B and the explicit duplicate path; then the owner's "
                      r"approval\. \|(.*?)\| 2026-10-18T14:14:10Z \| REQUIRED \|",
                   "| S1's patches updated for decision B and S6's form once the owner picks it; then his approval. "
                   "|\\1| " + T + " | REQUIRED |", "board s1 row")
    BOARD.write_bytes(t.encode("utf-8"))
    a = ARTS.read_text(encoding="utf-8")
    a = once(a, "record_s1_design_docs_rest.py (the rest of S1's design-doc record); probes/ and runs/ are rowed "
                "under S1. | 2026-10-18T13:42:22Z |",
             "record_s1_design_docs_rest.py (the rest of S1's design-doc record); record_duplicate_options.py and "
             "file_s6_and_configurables.py (the explicit duplicate options, S6 and the parked configurables "
             "epic); probes/ and runs/ are rowed under S1. | " + T + " |", "artifact scripts row")
    ARTS.write_bytes(a.encode("utf-8"))


if __name__ == "__main__":
    record_epic()
    record_s1()
    record_boards()
    pathlib.Path("/tmp/m0_mq/T.txt").write_text(T, encoding="utf-8")
    print("recorded at", T)
