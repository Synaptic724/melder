"""Link S6's patch docs and the settings-rebind probe (S6 Artifact Links, tasks, handoff; the artifact board; the
board row's next). <NOW>. Every edit is an exact replacement checked once, in memory, before anything is written.

Run from context_compass/:  python3 artifacts/correctness_defects_20261017/scripts/link_s6_patch_docs.py <NOW> [--dry-run]
"""
import pathlib
import re
import sys

NOW = sys.argv[1]
DRY = "--dry-run" in sys.argv[2:]
S6 = "tickets/stories/2026-10-17_release_routes_parked_version_objects_to_active_pool_story.md"
BOARD = "attention_board.md"
ART = "artifact_board.md"
PATCH = "system_docs/patches/active/managed_settings_spell_id_2026_10_17/"


def sub(text: str, old: str, new: str) -> str:
    """Replace `old` (exactly once) with `new`; @@NOW@@ becomes NOW."""
    assert text.count(old) == 1, old[:90]
    return text.replace(old, new.replace("@@NOW@@", NOW), 1)


texts = {path: pathlib.Path(path).read_text(encoding="utf-8") for path in (S6, BOARD, ART)}

t = texts[S6]
t = sub(t, "- [ ] Task: patch docs for the Binding Pipeline and the Managed Spell Pools; the owner's approval.\n",
        "- [ ] Task: patch docs for the Binding Pipeline and the Managed Spell Pools (written @@NOW@@,\n"
        "  linked below); the owner's approval.\n")
t = sub(t, "  - artifacts/correctness_defects_20261017/runs/probe_same_id_staging_gil1.txt\n",
        "  - artifacts/correctness_defects_20261017/runs/probe_same_id_staging_gil1.txt\n"
        "  - artifacts/correctness_defects_20261017/probes/probe_settings_rebind.py (cases R1-R3: a settings change on the tree and on the prototype)\n"
        "  - artifacts/correctness_defects_20261017/runs/probe_settings_rebind_tree_gil0.txt\n"
        "  - artifacts/correctness_defects_20261017/runs/probe_settings_rebind_tree_gil1.txt\n"
        "  - artifacts/correctness_defects_20261017/runs/probe_settings_rebind_proto_gil0.txt\n"
        "  - artifacts/correctness_defects_20261017/runs/probe_settings_rebind_proto_gil1.txt\n"
        "  - " + PATCH + "architecture_patch.md\n"
        "  - " + PATCH + "component_patch_binding_fingerprint.md\n"
        "  - " + PATCH + "component_patch_managed_pool_rebind.md\n"
        "  - " + PATCH + "code_description_patch_managed_pool_rebind.md\n"
        "  - " + PATCH + "component_patch_creation_cache_generation.md\n"
        "  - " + PATCH + "component_patch_staging_refusal.md\n")
t = sub(t, "- DISPOSITION: retain_as_reference\n- CLEANUP_TRIGGER: the probe is re-run at the fix and kept as the defect's reproducer\n",
        "- DISPOSITION: retain_as_reference (probes and runs); promote_to_documentation (the patch docs)\n"
        "- CLEANUP_TRIGGER: the probes are re-run at the fix and kept as the defect's reproducers; the patch docs are\n"
        "  promoted into the system documents at landing and archived under system_docs/patches/completed/\n")
t = sub(t, "- Next: (1) the patch docs, linked here, for the owner's approval; (2) part A with its tests, docs, notch and the\n"
           "  rebuild last; (3) part B after melder_1's release.\n",
        "- Next: (1) the owner's approval of the patch docs (Artifact Links) and his answers on the scope and the legacy\n"
        "  record; (2) part A after melder_1's notch, with its tests, docs, notch and the rebuild last; (3) part B after\n"
        "  melder_1's release of spellbook.py.\n")
long = [line for line in t.splitlines() if len(line) > 120 and "/" not in line]
assert not long, long
texts[S6] = t

t = texts[BOARD]
row = re.compile(r"(?m)^(\| managed_settings_spell_id \| in_progress \| discovery \| claude \| melder_0 \| none \| )"
                 r"Write S6's patch docs \(Binding Pipeline, Managed Spell Pools\) for the owner's approval and confirm the"
                 r" scope with him\.( \|.*\| )\S+( \| REQUIRED \|)$")
t, n = row.subn(lambda m: m.group(1) + "The owner approves S6's patch docs and answers the scope and the legacy record;"
                " then part A after melder_1's notch." + m.group(2) + NOW + m.group(3), t)
assert n == 1, n
texts[BOARD] = t

t = texts[ART]
t = sub(t, "<!-- END USER-DEFINED: active_artifacts -->",
        "| tickets/stories/2026-10-17_release_routes_parked_version_objects_to_active_pool_story.md | "
        "artifacts/correctness_defects_20261017/probes/probe_settings_rebind.py | investigation_evidence | in_progress | "
        "retain_as_reference | Cases R1-R3 (a settings change by cleanup_spell and bind, a settings-only staging, a mode "
        "change) with their runs on the tree and on the prototype (runs/probe_settings_rebind_tree_gil0.txt, _gil1.txt, "
        "_proto_gil0.txt, _proto_gil1.txt); re-run at the fix. | " + NOW + " | HELPFUL |\n"
        "| tickets/stories/2026-10-17_release_routes_parked_version_objects_to_active_pool_story.md | " + PATCH
        + " | patch_doc | active | promote_to_documentation | Entry-gate docs of S6's fix (architecture, three component "
        "patches for part A, the pool's code description, part B's component patch); for the owner's approval; promote "
        "at landing and archive. | " + NOW + " | REQUIRED |\n"
        "<!-- END USER-DEFINED: active_artifacts -->")
texts[ART] = t

if DRY:
    print("dry run OK:", ", ".join(texts))
else:
    for path, text in texts.items():
        pathlib.Path(path).write_text(text, encoding="utf-8")
    print("written:", ", ".join(texts))
