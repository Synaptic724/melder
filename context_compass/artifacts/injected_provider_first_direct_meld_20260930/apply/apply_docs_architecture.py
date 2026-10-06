"""
Promote the injected_provider_first_direct_meld patch (0.2.8215) into src_architecture.md and remeasure the
citations into the files the landing touched.

Usage: python apply_docs_architecture.py <repository root>
Every anchor must match exactly once; nothing is written unless all do.
"""
import datetime
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from apply_support import ApplySession

ROOT = sys.argv[1]
DOC = "context_compass/system_docs/src_architecture.md"
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
s = ApplySession(ROOT)

# Meld-time validation sequence.
s.replace(
    DOC,
    "4. Under dynamic ownership every rerun above (and the deferred 8-11 run) first enters the spell's rebuild\n"
    "   window: freeze and drain the spell-index gate, then take `spell._lock`, run the phases, publish the\n"
    "   rebuilt context when its plan is present, reopen the gate (2026-09-26).\n",
    "4. Under dynamic ownership every rerun above (and the deferred lane's run) first enters the spell's rebuild\n"
    "   window: freeze and drain the spell-index gate, then take `spell._lock`, run the phases, publish the\n"
    "   rebuilt context when its plan is present, reopen the gate (2026-09-26).\n"
    "5. A spell flagged `resolution_required` takes the deferred lane (`Meld._ensure_runtime_resolution_ready`)\n"
    "   instead of step 3: 8-11 for its own Phase 5 root or an existing creation, otherwise its full target pass\n"
    "   5-11, which must leave it resolution-valid (0.2.8215). A successful target pass flags each owned dependency\n"
    "   it compiled only inside the target's plan, so that dependency's first direct meld resolves it.\n",
)

# Operational invariants: newest first.
s.insert_before(
    DOC,
    "- Root configuration guards for hosts (2026-09-30, 0.2.8209-0.2.8212): a host that embeds Melder next to another\n",
    "- Injected dependencies resolve on their first direct meld (2026-09-30, 0.2.8215). A target-local resolution pass -\n"
    "  a consumer's first meld after a late bind - publishes root blueprints only to its target (2026-09-19) and its\n"
    "  Phase 6 stamps every node of the target's scope valid, so a dependency first compiled inside the consumer's plan\n"
    "  reads valid with no plan of its own. On success the pass therefore flags each such dependency the Book owns -\n"
    "  resolvable, not an existing creation, with no phase-11 plan, no published CreationContext and no flag yet -\n"
    "  with `resolution_required`, under the dependency's spell lock taken after the target's (the build-lock order).\n"
    "  Every meld door already reads that flag: the deferred lane runs the dependency's own full target pass (5-11)\n"
    "  because it is not its Phase 5 root, checks its verdict, and the rebuild window publishes its context, so the\n"
    "  direct meld returns the instance the consumer's plan stored (unique_per_conduit, unique) or a new one (many).\n"
    "  Verdicts, the Book validation flag, warm melds and the conduit-wide pass are unchanged, and no caller step is\n"
    "  needed.\n"
    "  EVIDENCE:\n"
    "  `src/melder/aether/spellbook/spellbook_creation_system.py:SpellbookCreationSystem.flag_dependencies_without_own_plan`,\n"
    "  `SpellbookCreationSystem.run_resolution_phases_for_target_spell` and\n"
    "  `src/melder/aether/conduit/meld/meld.py:Meld._ensure_runtime_resolution_ready`.\n",
)

# Failure modes: newest first.
s.insert_before(
    DOC,
    "- `Aether.configure(configuration)` and `Aether.activate()` raise RuntimeError while frames exist when the\n",
    "- A spell bound on a live dynamic root after conjure and first built as a consumer's dependency no longer fails its\n"
    "  first direct meld with RuntimeError \"Cannot build CreationContext before spell_codegen_creation exists.\" (fixed\n"
    "  in 0.2.8215; the builder's guard is unchanged). If that dependency's own full target pass leaves it unresolved\n"
    "  for the conduit (a visibility failure), the meld raises SpellbookValidationError and the flag stays set.\n"
    "  EVIDENCE: `src/melder/aether/conduit/meld/meld.py:Meld._raise_unless_resolution_valid`.\n",
)

# Citations into the touched files, checked by symbol against the landed tree.
CITATIONS = [
    ("see `src/melder/aether/spellbook/spellbook.py:3680`, which states the",
     "see `src/melder/aether/spellbook/spellbook.py:3686`, which states the"),
    ("  - src/melder/aether/spellbook/spellbook.py:3835 (`_add_to_spell_index` entry)\n",
     "  - src/melder/aether/spellbook/spellbook.py:3843 (`_add_to_spell_index` entry)\n"),
    ("  - src/melder/aether/spellbook/spellbook.py:3868 (`_apply_add_to_index` seam)\n",
     "  - src/melder/aether/spellbook/spellbook.py:3876 (`_apply_add_to_index` seam)\n"),
    ("EVIDENCE: src/melder/aether/spellbook/spellbook.py:3695-3833.\n",
     "EVIDENCE: src/melder/aether/spellbook/spellbook.py:3701-4136 (the three seams, remeasured 2026-09-30).\n"),
    ("   - src/melder/aether/spellbook/spellbook.py:3695-3833\n"
     "   - src/melder/aether/spellbook/spellbook.py:3868-3962\n"
     "   - src/melder/aether/spellbook/spellbook.py:4043-4128\n",
     "   - src/melder/aether/spellbook/spellbook.py:3701-3841\n"
     "   - src/melder/aether/spellbook/spellbook.py:3876-3970\n"
     "   - src/melder/aether/spellbook/spellbook.py:4051-4136\n"),
    ("  - src/melder/aether/spellbook/spellbook.py:665 (ownership check reads it)\n"
     "  - src/melder/aether/spellbook/spellbook.py:723 (deleted on cleanup)\n",
     "  - src/melder/aether/spellbook/spellbook.py:667 (ownership check reads it)\n"
     "  - src/melder/aether/spellbook/spellbook.py:725 (deleted on cleanup)\n"),
    ("  - src/melder/aether/spellbook/spellbook.py:6502-6545\n"
     "    (`Spellbook._settle_or_inherit_conjure_mode`; in-place settle :6532-6544,\n"
     "    effective-mode return :6545; remeasured 2026-09-30)\n"
     "  - src/melder/aether/spellbook/spellbook.py:6758\n",
     "  - src/melder/aether/spellbook/spellbook.py:6516-6559\n"
     "    (`Spellbook._settle_or_inherit_conjure_mode`; in-place settle :6546-6558,\n"
     "    effective-mode return :6559; remeasured 2026-09-30 at 0.2.8215)\n"
     "  - src/melder/aether/spellbook/spellbook.py:6772\n"),
]
for old, new in CITATIONS:
    s.replace(DOC, old, new)


# C1 code map: remeasure the two touched entries, add the creation system.
def remeasure(path: str) -> None:
    """Rewrite one code-map entry's end_line, loc and verified_at from the file on disk."""
    text = s._load(DOC)
    pattern = re.compile(
        r"- path: `" + re.escape(path) + r"`\n  start_line: 1\n  end_line: \d+\n  loc: \d+\n  verified_at: \S+\n"
    )
    matches = pattern.findall(text)
    if len(matches) != 1:
        raise AssertionError(f"code map entry for {path}: {len(matches)} matches")
    loc = len((pathlib.Path(ROOT) / path).read_bytes().decode("utf-8").splitlines())
    s.replace(
        DOC,
        matches[0],
        f"- path: `{path}`\n  start_line: 1\n  end_line: {loc}\n  loc: {loc}\n  verified_at: {NOW}\n",
    )


for touched in ("src/melder/aether/spellbook/spellbook.py", "src/melder/aether/conduit/meld/meld.py"):
    remeasure(touched)
creation = "src/melder/aether/spellbook/spellbook_creation_system.py"
creation_loc = len((pathlib.Path(ROOT) / creation).read_bytes().decode("utf-8").splitlines())
s.insert_before(
    DOC,
    "- path: `src/melder/aether/spellbook/spellbinder.py`\n",
    f"- path: `{creation}`\n  start_line: 1\n  end_line: {creation_loc}\n  loc: {creation_loc}\n"
    f"  verified_at: {NOW}\n"
    "  note: conjure and target-local resolution orchestration; a successful target pass flags the owned\n"
    "    dependencies it compiled without a plan of their own (0.2.8215).\n",
)

# Information sources.
s.insert_after(
    DOC,
    "- `src/melder/aether/conduit/meld/meld.py`\n",
    "- `src/melder/aether/spellbook/spellbook_creation_system.py`\n"
    "- `src/melder/aether/conduit/meld/creation_context/creation_context_rebuild.py`\n",
)

# Handoff summary.
s.replace(
    DOC,
    "## Context / Handoff Summary\n\n2026-09-30 per-frame spell worlds (0.2.8213-0.2.8214):",
    "## Context / Handoff Summary\n\n"
    "2026-09-30 injected dependencies (0.2.8215): a spell bound after conjure and first built as a consumer's\n"
    "dependency melds directly afterwards - a successful target-local pass flags the owned dependencies it compiled\n"
    "without a plan of their own, and the deferred lane runs a full target pass for a spell that is not its Phase 5\n"
    "root. The meld-time validation sequence, the operational invariants, the failure modes and the code map carry\n"
    "it; the component map carries the mechanics. Citations into spellbook.py were remeasured on the way (several\n"
    "were already 2-14 lines stale).\n\n"
    "2026-09-30 per-frame spell worlds (0.2.8213-0.2.8214):",
)

long_lines = [
    line for line in s.long_added_lines()
    if "`src/melder/aether/spellbook/spellbook_creation_system.py:SpellbookCreationSystem." not in line
]
if long_lines:
    raise SystemExit("long added lines:\n" + "\n".join(long_lines))
for written in s.write():
    print("wrote", written)
