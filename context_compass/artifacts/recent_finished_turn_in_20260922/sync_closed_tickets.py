"""Synchronize only the five owner-selected recent tickets after native file moves."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys


def replace_region(text: str, region: str, content: str) -> str:
    """Replace one user-owned board region while preserving its managed boundaries."""
    start = f"<!-- BEGIN USER-DEFINED: {region} -->"
    end = f"<!-- END USER-DEFINED: {region} -->"
    left, remaining = text.split(start, 1)
    _old, right = remaining.split(end, 1)
    return left + start + "\n" + content.strip() + "\n" + end + right


def region_text(text: str, region: str) -> str:
    """Return one known user-owned region for a bounded routing update."""
    return text.split(f"<!-- BEGIN USER-DEFINED: {region} -->", 1)[1].split(
        f"<!-- END USER-DEFINED: {region} -->", 1,
    )[0]


def main() -> None:
    """Update references, closure anchors, artifact disposition and a verification receipt."""
    root = Path.cwd()
    compass = root / "context_compass"
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    selected = {
        "tickets/epics/2026-09-21_runtime_hook_lifecycle_and_adjustment_epic.md": "pool_hook_epic",
        "tickets/tasks/2026-09-22_investigate_pooled_conduit_hook_reset_task.md": "pooled_hook_discovery",
        "tickets/tasks/2026-09-22_add_local_hook_setters_and_tracking_task.md": "local_hook_tracking",
        "tickets/tasks/2026-09-20_prepare_0_2_37_to_0_2_42_release_document_task.md": "release_0_2_37_to_0_2_43",
        "tickets/tasks/2026-09-19_repair_benchmark_spell_id_lookup_task.md": "benchmark_spell_id_lookup",
    }
    replacements = {old: str(Path(old).parent / "completed" / Path(old).name).replace("\\", "/")
                    for old in selected}
    patch_old = "system_docs/patches/active/pool_hook_baselines_2026_09_22/"
    patch_new = "system_docs/patches/completed/pool_hook_baselines_2026_09_22/"
    for old, new in replacements.items():
        target = compass / new
        assert not (compass / old).exists() and target.is_file(), (old, new)
        text = target.read_text(encoding="utf-8")
        assert "- Status: done" in text
        for before, after in replacements.items():
            text = text.replace(before, after)
        text = text.replace(patch_old, patch_new)
        text = re.sub(r"(?m)^- (Completed|Updated): .*", lambda match: f"- {match[1]}: {stamp}", text)
        target.write_text(text, encoding="utf-8", newline="\n")

    board_path = compass / "attention_board.md"
    board = board_path.read_text(encoding="utf-8")
    active = [line for line in region_text(board, "active_items").splitlines()
              if not any(old in line for old in replacements)]
    board = replace_region(board, "active_items", "\n".join(active))
    for label in ("pool_hook_epic", "pooled_hook_discovery", "local_hook_tracking", "release_0_2_37_to_0_2_43", "benchmark_spell_id_lookup"):
        board = re.sub(r"(?m)^- " + label + r":[^\n]*\n(?:  [^\n]*\n)*", "", board)
    new_anchors = [f"| {selected[old]} | done | updater_0 | {new} | Owner turn-in; evidence retained, packaging held separately. | {stamp} |"
                   for old, new in replacements.items()]
    old_anchors = [line for line in region_text(board, "closed_anchors").splitlines() if line.startswith("|")]
    board = replace_region(board, "closed_anchors", "\n".join((new_anchors + old_anchors)[:12]))
    assert not any(old in region_text(board, "active_items") for old in replacements)
    board_path.write_text(board, encoding="utf-8", newline="\n")

    artifacts_path = compass / "artifact_board.md"
    artifacts = artifacts_path.read_text(encoding="utf-8")
    retained = []
    cleared = []
    for line in region_text(artifacts, "active_artifacts").splitlines():
        matching = next((old for old in replacements if old in line), None)
        if matching is None:
            retained.append(line)
            continue
        fields = [field.strip() for field in line.split("|")][1:-1]
        artifact = fields[1].replace(patch_old, patch_new)
        cleared.append(f"| {replacements[matching]} | {artifact} | {fields[4]} | Owner accepted; evidence retained or contracts promoted and archived. | {stamp} |")
    # Repair the pre-existing missing disposition cell without changing that other lane.
    retained = [line.replace("| validation | review | Initial scalar-cost", "| validation | review | retain_as_reference | Initial scalar-cost")
                for line in retained]
    artifacts = replace_region(artifacts, "active_artifacts", "\n".join(retained))
    artifacts = replace_region(artifacts, "cleared_artifacts", "\n".join(cleared) + region_text(artifacts, "cleared_artifacts"))
    artifacts_path.write_text(artifacts, encoding="utf-8", newline="\n")

    expected_assets = json.loads((compass / "artifacts/release_0_2_45_20260922/assets_before.json").read_text(encoding="utf-8"))
    changed = [name for name, digest in expected_assets.items()
               if hashlib.sha256((root / name).read_bytes()).hexdigest().lower() != digest.lower()]
    assert not changed, changed
    assert not (compass / patch_old).exists()
    patch_files = list((compass / patch_new).glob("*.md"))
    assert len(patch_files) == 3
    active_rows = [row for row in region_text(board, "active_items").splitlines() if row.startswith("|")]
    for row in active_rows:
        ticket = [cell.strip() for cell in row.split("|")][10]
        assert "/completed/" not in ticket and (compass / ticket).is_file(), ticket
    receipt = {"closed_at": stamp, "closed_tickets": replacements,
               "patch_archive": patch_new, "archived_patch_files": len(patch_files),
               "held_assets_checked": len(expected_assets), "held_assets_changed": changed,
               "closed_anchor_count": len((new_anchors + old_anchors)[:12]),
               "active_ticket_routes_verified": len(active_rows),
               "runtime_tests_rerun": False}
    (Path(__file__).parent / "closure_receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    sys.stdout.write(json.dumps(receipt, indent=2) + "\n")


if __name__ == "__main__":
    main()
