"""Mapping PLAN note, checklist tick, artifact board rows."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "executor_cache_world_stamp_20261003"))
from cc_helpers import now_utc, read_text, write_text, replace_once, check_line_lengths  # noqa: E402

CC = os.path.abspath(os.path.join(HERE, "..", ".."))
TASK_REL = "tickets/tasks/2026-10-03_certify_and_implement_site_store_constants_task.md"
TASK = os.path.join(CC, TASK_REL)
ARTBOARD = os.path.join(CC, "artifact_board.md")
TS = now_utc()
NOTE = f"""- DATETIME: {TS}
  TYPE: PLAN
  CLAIM: Patch docs written and indexed under system_docs/patches/active/flat_warm_body_2026_10_03/ (architecture,
    component SpellCompiler codegen, code description; ENTRY markers; --check OK). Mapping, patch section ->
    implementation step -> validation step: (a) code description steps 1-2 (the eligible-site branch in
    `_emit_shared_hit`, the class-contract bullet) -> lowering edit -> emitter unit tests: automatic unique site
    emits no alias line and binds `c{{i}}` to the owner store (instance published there and reused), dynamic unique
    site keeps the line and binds nothing, unowned provider keeps the line, per-conduit site unchanged;
    (b) architecture migration step 1 (the `_spell` stub) -> test stub gains `_dynamic_environment=False`;
    (c) component validation expectations -> a new component file (automatic: same Service across two melds and
    the captured normal plan has no `spells[i]._owner_creations` line; dynamic: the line is present; a cache
    full hit world behaves the same); (d) harness re-run on the shipped body at landing.
  EVIDENCE:
  - system_docs/patches/active/flat_warm_body_2026_10_03/architecture_patch.md:1-50
  - system_docs/patches/active/flat_warm_body_2026_10_03/component_patch_spellcompiler_codegen.md:1-40
  - system_docs/patches/active/flat_warm_body_2026_10_03/code_description_patch_site_plan_lowering.md:1-35
  IMPACT: Entry gate satisfied for the working-copy implementation.
  NEXT: the anchored apply script (lowering, stub, unit tests, component test) on `$HOME/work/melder_cc`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

"""
bad = check_line_lengths(NOTE, exempt=r"^  - (src|tests|artifacts|system_docs)/")
if bad:
    raise SystemExit(f"lines over cap: {bad}")
text, nl = read_text(TASK)
text = replace_once(text, "\n## Context / Handoff Summary\n", "\n" + NOTE + "## Context / Handoff Summary\n", "handoff")
text = replace_once(text, "- [ ] Patch docs and the mapping note (only when the table says ship).",
                    "- [x] Patch docs and the mapping note (only when the table says ship).", "step3")
text = re.sub(r"^- Updated: .*$", f"- Updated: {TS}", text, count=1, flags=re.MULTILINE)
write_text(TASK, text, nl)
art, nl = read_text(ARTBOARD)
rows = (
    f"| {TASK_REL} | artifacts/flat_warm_body_20261003/ | measurement_and_implementation_evidence | active | "
    "retain_as_reference | The S9 harness extension, the interleaved A/B runs and medians, the micro-benchmark, lane "
    f"scripts and logs. | {TS} | REQUIRED |\n"
    f"| {TASK_REL} | system_docs/patches/active/flat_warm_body_2026_10_03/ | patch_doc | active | "
    "promote_to_documentation | Entry-gate artifacts: owner-store constants (architecture), the shared-site read "
    f"before/after (component), the eligible-site branch (code description). | {TS} | REQUIRED |\n"
)
art = replace_once(art, "<!-- BEGIN USER-DEFINED: active_artifacts -->\n",
                   "<!-- BEGIN USER-DEFINED: active_artifacts -->\n" + rows, "active begin")
write_text(ARTBOARD, art, nl)
print("planned", TS)
