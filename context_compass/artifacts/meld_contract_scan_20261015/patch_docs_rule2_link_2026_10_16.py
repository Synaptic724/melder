"""Link rule 2's patch docs: ticket Notes, Artifact Links, checklist, handoff summary, both boards (melder_1).

usage (from context_compass/): python <this script> <UTC now> [--check]
Exact-text edits with asserts; prose lines in the ticket within 120 characters (an evidence line holding one path
may run long); ASCII and LF; refuses a second run.
"""
import pathlib
import sys

NOW = sys.argv[1]
CHECK = "--check" in sys.argv[2:]
TICKET_PATH = "tickets/tasks/2026-10-16_recheck_contract_consumers_when_provider_changes_task.md"
TICKET = pathlib.Path(TICKET_PATH)
ATTENTION = pathlib.Path("attention_board.md")
ARTIFACTS = pathlib.Path("artifact_board.md")
P = "system_docs/patches/active/contract_recheck_on_notch_2026_10_16/"
CP = "context_compass/" + P
DOCS = [
    ("architecture_patch.md", "Objective, non-goals, six changed components with file owners, nine invariants, interface deltas, migration order, rollback, coverage matrix, risks, decision requests D1-D5."),
    ("component_patch_borrower_contracted_maps.md", "The five Spellbook mutators mark the changed active copy's key after their Book lock (melder_0's file: handoff); validation expectations."),
    ("component_patch_meld_gate.md", "The per-meld contract scan and its helpers leave Meld; the structural branch is the recheck; the lost-provider error type; test replacements."),
    ("component_patch_contract_presence_report.md", "Phase 4's snapshot walk (every option); with D1-B the warning's remedy and the renderer showing a gating warning as the reason."),
    ("component_patch_notch_reactivation.md", "With D3, notch_spell reactivates parked copies of the incoming version on linked peers; the grant docstring corrected in every option."),
    ("code_description_patch_contract_recheck.md", "Control flow of a mark, a notch's fan-out and the recheck meld; edge and error semantics; idempotency; lock order; non-goals."),
]


def read(path: pathlib.Path) -> str:
    raw = path.read_bytes()
    assert b"\r" not in raw, path
    return raw.decode("ascii")


ticket = read(TICKET)
assert "TYPE: DECISION_REQUEST\n  CLAIM: The owner decides before any `src/` edit: D1" not in ticket

NOTES = f"""- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Patch section -> implementation step -> validation step, for after the owner's approval (D1-D5 may trim
    it). (1) component_patch_borrower_contracted_maps: `Spellbook._mark_contract_dependents_dirty` and the five
    mutators' marks after their Book lock (spellbook.py, after melder_0's handoff) -> unit tests per mutator on a
    real registry (a mark when conjured, none before conjure or for a parked copy, the Book lock free) and the
    component coverage matrix. (2) component_patch_meld_gate: the scan, its two helpers and their imports removed,
    the docstrings and the ward's comment updated (meld.py, conduit_ward.py) -> the six scan unit tests replaced,
    integration melds after a notch, an index destroy and an uncontract. (3) component_patch_contract_presence_report:
    the strategy's snapshot walk, and with D1-B its message and the renderer -> renderer and strategy unit tests, a
    GIL-off race of melds against notches. (4) component_patch_notch_reactivation, with D3: `_activate_borrowed_spell`
    in `notch_spell` and the grant docstring (conduit.py, conduit_ward.py) -> the anchored notch-back component test.
    (5) code_description_patch_contract_recheck: the lock and ordering points -> a registry double that asserts the
    Book lock is free, and the probes before and after (us per warm meld, passes per change). Then the system docs
    (src_architecture's gate sequence, an invariant, a failure mode and the code map; src_components' Meld,
    Spellbook and Conduit sections; the tests docs), graph descriptors, the release note, the notch above S8's,
    closure, rebuild.
  EVIDENCE:
  - {CP}architecture_patch.md:1-163
  - {CP}code_description_patch_contract_recheck.md:1-95
  IMPACT: The build has a mapped order the moment the owner approves; nothing in `src/` changes before.
  NEXT: The owner's review of the patch docs and decisions D1-D5.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: The owner decides before any `src/` edit: D1 the message for a lost provider - A keep the first meld's
    generic message, B (recommended) SpellbookValidationError shows the gating SPELL_CONTRACT_MISSING_PROVIDER warning,
    with a remedy, as the spell's reason (type and first line unchanged), C a failure-path scan raising
    MeldExecutionError (it changes the first meld's error too; not recommended); D2 keep the provider's dependencies
    out of rule 2 and open a task for the dependency-notch defect, which exists in one Book too (recommended); D3
    wire the notch-back reactivation of parked version-anchored copies that the docstrings describe (recommended),
    and correct the grant docstring either way; D4 a lent consumer's Book-local provider loss to its own task, or
    accepted as is; D5 land after melder_0's S8 (0.2.8248) with melder_0's handoff of spellbook.py. Approving the
    patch as a whole starts the build.
  EVIDENCE:
  - {CP}architecture_patch.md:139-159
  IMPACT: Each answer fixes a part of the change set; without D5 the five mutators cannot be edited.
  NEXT: Present the patch docs and these decisions to the owner and wait for his answer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
"""

anchor = "\n## Context / Handoff Summary\n"
assert ticket.count(anchor) == 1
ticket = ticket.replace(anchor, "\n" + NOTES.rstrip("\n") + "\n" + anchor, 1)

old_summary_start = ticket.index(anchor) + len(anchor)
old_summary_end = ticket.index("\n## Project-Specific Additions\n")
old_summary = ticket[old_summary_start:old_summary_end]
assert old_summary.startswith("In progress (2026-10-16T09:46:14Z): design phase;")
new_summary = f"""Design phase ({NOW}): the patch docs are written and wait for the owner's approval; no `src/` change
before it. The story (owner, 2026-10-16): a satisfied SpellContract is not checked on every meld; a change of the
provider a consumer resolves - a lender's notch above all, since a notched version's `__init__` may differ - marks
the key's consumers `gated` + `contract_unvalidated`, so their next meld re-validates the contract and rebuilds
against the version now active, or fails with the first-meld error; objects already built keep their provider.
Design: the borrower Book's five contracted-map mutators mark through `mark_contract_dependents_dirty` once their
Book lock is released; the meld's per-meld scan goes; the gate's structural branch is the recheck - one 5-11 pass
per change, shared by every conduit, about 2 us a warm meld instead of about 1.5 ms.
Evidence: the Notes from 09:57:21Z on, and the probes and runs in artifacts/meld_contract_scan_20261015/
(probe_rule2_design.py, probe_rule2_lent_consumer.py, probe_in_book_dependency_notch.py).
Patch: {P}
(architecture, three component patches, the notch-reactivation patch, the code description).
Open for the owner: D1 the lost-provider message (B recommended); D2 the dependency notch outside rule 2 (its own
task); D3 the notch-back reactivation of version-anchored copies (recommended); D4 a lent consumer's Book-local
provider loss (its own task); D5 the landing after S8 with melder_0's handoff of spellbook.py.
Next: (1) the owner's approval and decisions; (2) melder_0's handoff of spellbook.py once S8 (0.2.8248) lands;
(3) the build: red tests, the change, green with the GIL off and on, probes, docs, release note, notch, rebuild.
"""
ticket = ticket[:old_summary_start] + new_summary + ticket[old_summary_end:]

old_step = "- [ ] Re-read whole on today's tree: the meld gate's contract check"
assert ticket.count(old_step) == 1
ticket = ticket.replace(old_step, "- [x] Re-read whole on today's tree: the meld gate's contract check", 1)

old_links = """- ARTIFACT_PATHS:
  - artifacts/meld_contract_scan_20261015/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: decided at closure (the patch docs, once written, are promoted to documentation)"""
assert ticket.count(old_links) == 1
paths = "\n".join(f"  - {P}{name}" for name, _ in DOCS)
new_links = f"""- ARTIFACT_PATHS:
  - artifacts/meld_contract_scan_20261015/
{paths}
- DISPOSITION: retain_as_reference (the folder); promote_to_documentation (the patch docs)
- CLEANUP_TRIGGER: at closure the patch docs are promoted into the system docs and archived under
  system_docs/patches/completed/; the folder stays as the lane's evidence"""
ticket = ticket.replace(old_links, new_links, 1)

updated = [l for l in ticket.split("\n") if l.startswith("- Updated: ")]
assert len(updated) == 1
ticket = ticket.replace(updated[0], f"- Updated: {NOW}", 1)
too_long = [l for l in ticket.split("\n") if len(l) > 120 and not (l.startswith("  - ") and " " not in l[4:])]
assert not too_long, too_long
ticket.encode("ascii")

attention = read(ATTENTION)
old_row = ("| meld_contract_scan | in_progress | discovery | claude | melder_1 | none | Re-read the meld's contract check "
           "and every change of a borrower's contracted copy whole, then write the patch docs. |")
assert attention.count(old_row) == 1
row_start = attention.index(old_row)
row_end = attention.index("\n", row_start)
row = attention[row_start:row_end]
assert row.endswith("| 2026-10-16T09:47:39Z | REQUIRED |")
new_row = ("| meld_contract_scan | in_progress | discovery | claude | melder_1 | the owner's approval of the patch docs "
           "(D1-D5) | Present the patch docs and decisions D1-D5 to the owner; on approval, melder_0's spellbook.py "
           "handoff after S8 lands. | A satisfied SpellContract is not checked on every meld; a provider change (a "
           "notch) marks its consumers for a recheck at their next meld. | The owner-approved change lands with tests, "
           f"docs, notch and rebuild, or the owner redirects. | {TICKET_PATH} | {NOW} | REQUIRED |")
attention = attention[:row_start] + new_row + attention[row_end:]
attention.encode("ascii")

artifacts = read(ARTIFACTS)
old_folder = (f"| {TICKET_PATH} | artifacts/meld_contract_scan_20261015/ | investigation_evidence | active | "
              "retain_as_reference | The lane's shared folder: the trace's logs, gate probes and runs; rule 1's "
              "(0.2.8247) apply scripts, probes, suite, mutation and probe runs, doc, graph and release-note scripts "
              "and rebuild logs; the open, closure and board scripts. Rule 2's design evidence starts here "
              "(probe_design_baseline.py: the borrower contract consumer); its probes and runs land beside it. | "
              "2026-10-16T09:47:39Z | REQUIRED |")
assert artifacts.count(old_folder) == 1
new_folder = (f"| {TICKET_PATH} | artifacts/meld_contract_scan_20261015/ | investigation_evidence | active | "
              "retain_as_reference | The lane's shared folder: the trace's logs, gate probes and runs; rule 1's "
              "(0.2.8247) apply scripts, probes, suite, mutation and probe runs, doc, graph and release-note scripts "
              "and rebuild logs; the open, closure and board scripts. Rule 2's design evidence: probe_rule2_design.py, "
              "probe_rule2_lent_consumer.py and probe_in_book_dependency_notch.py with their runs, and the Notes and "
              f"link scripts. | {NOW} | REQUIRED |")
rows = "\n".join(f"| {TICKET_PATH} | {P}{name} | patch_doc | active | promote_to_documentation | {text} | {NOW} | "
                 "REQUIRED |" for name, text in DOCS)
artifacts = artifacts.replace(old_folder, new_folder + "\n" + rows, 1)
artifacts.encode("ascii")
for name, _ in DOCS:
    assert pathlib.Path(P + name).is_file(), name

if not CHECK:
    TICKET.write_bytes(ticket.encode("ascii"))
    ATTENTION.write_bytes(attention.encode("ascii"))
    ARTIFACTS.write_bytes(artifacts.encode("ascii"))
print("checked" if CHECK else "written", len(ticket.split("\n")), "ticket lines")
