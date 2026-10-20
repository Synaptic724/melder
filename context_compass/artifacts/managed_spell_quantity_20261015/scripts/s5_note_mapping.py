"""Append the S5 patch-section -> implementation -> validation mapping note to the S5 story."""
import datetime
import pathlib
import sys

STORY = pathlib.Path("context_compass/tickets/stories/2026-10-15_managed_dispense_codegen_story.md")
PATCHES = "context_compass/system_docs/patches/active/managed_spell_quantity_2026_10_15"


def main() -> int:
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    note = f"""- DATETIME: {now}
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Patch gate met: component_patch_managed_dispense_codegen.md and code_description_patch_managed_dispense_codegen.md
    written and linked, the architecture patch aligned (no generation 21, door rows on the many templates, invariant
    11 widened), the emission before-image captured (s5_emission_before_0_2_8244.json.gz: 4461 entries - 4342 lowering
    shapes, 28 door bodies, the five harness worlds; two runs identical). Mapping, patch section -> implementation ->
    validation: (1) Sharedness -> both `_is_shared_existence` -> unit: per-path keys and occurrences for managed.
    (2) Discovery -> solo `discover` declines managed counts -> unit: solo declines, generalized claims. (3) Manifest ->
    `_resolve_route_key_from_model` + "managed" -> unit. (4) Door -> "managed" rows on the many templates -> unit:
    selectors return the many templates; component: hooks see created=True. (5) Specializer ->
    `rows_contain_managed_step` + `_install_specializing_door` decline -> unit. (6) Leasing/fresh site, hit, miss,
    placement, return, children (code-description control flow) -> SitePlanEmission (`__init__`, `_place`,
    `_unresolved_check_lines`, `_emit_context`, `_emit_many`, `_emit_miss`, new managed hit/miss/lease-group
    emitters, `_managed_pool_constant`) and three SitePlanRuntimeHelpers -> unit: emitted shapes and runtime on real
    pools (pop, reserve, served, abandon with notes, adopt, F9 and lost-race returns, missing pool). (7)
    `Conduit.managed_spell_meld` -> conduit.py after `meld` -> component. (8) Gate -> the capture rerun equal for
    every non-managed entry. (9) Benchmark -> the warm lease cycle in a plan.
  EVIDENCE:
  - {PATCHES}/component_patch_managed_dispense_codegen.md:1-89
  - {PATCHES}/code_description_patch_managed_dispense_codegen.md:1-107
  - {PATCHES}/architecture_patch.md:30-108
  - context_compass/artifacts/managed_spell_quantity_20261015/scripts/s5_emission_capture.py:1-260
  IMPACT: S5 may edit src/ now; any change outside the mapped seams goes back through the patches first.
  NEXT: Write the red unit tests in test_site_plan_lowering.py and the discovery, predicate, manifest, door and
    specializer tests; run them red in both GIL modes.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

"""
    text = STORY.read_text(encoding="utf-8")
    anchor = "## Closure Confirmation"
    if text.count(anchor) != 1:
        return 1
    text = text.replace(anchor, note + anchor)
    updated = [line for line in text.splitlines() if line.startswith("- Updated: ")]
    text = text.replace(updated[0], f"- Updated: {now}")
    old_task = "- [ ] Read the U7/U8 sites whole; component and code-description patches; mapping note."
    if text.count(old_task) == 1:
        text = text.replace(old_task, "- [x] Read the U7/U8 sites whole; component and code-description patches; mapping note.")
    old_base = "- [ ] Capture the baseline emission over the certification harness worlds before any edit."
    if text.count(old_base) == 1:
        text = text.replace(old_base, "- [x] Capture the baseline emission over the certification harness worlds before any edit.")
    STORY.write_text(text, encoding="utf-8", newline="")
    print("mapping note appended", now, "max", max(len(line) for line in note.splitlines()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
