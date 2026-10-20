"""Route TASK-2026-10-16-public_notch_target_for_staged_versions: one attention-board row and detail entry, one
artifact-board row (inserted at the end of their USER-DEFINED regions; line endings kept; re-read right before write).

Run from the context_compass root:
    python artifacts/public_notch_target_20261016/scripts/route_task.py <NOW>
"""
import pathlib
import sys

TICKET = "tickets/tasks/2026-10-16_public_notch_target_for_staged_versions_task.md"


def insert_before(path: pathlib.Path, marker: str, block: str) -> None:
    """Insert `block` (lines joined by the file's newline) right before the line `marker`, which must occur once."""
    text = path.read_bytes().decode("utf-8")
    newline = "\r\n" if "\r\n" in text else "\n"
    anchor = newline + marker
    if text.count(anchor) != 1:
        raise SystemExit(f"{path}: marker {marker!r} found {text.count(anchor)} times")
    text = text.replace(anchor, newline + block.replace("\n", newline) + anchor, 1)
    path.write_bytes(text.encode("utf-8"))
    print(f"{path}: inserted before {marker}")


def main() -> None:
    """Insert the three routing records."""
    now = sys.argv[1]
    row = (
        "| public_notch_target | in_progress | discovery | claude | melder_0 | none | Write the patch lane "
        "public_notch_target_2026_10_16 and the mapping note, then the red tests. | `Conduit.notch_spell(spell_index=..., "
        "spell_id=...)` notches to a staged version on public calls, its target checked before the transaction; the "
        "README and docs loops run as written. | The change lands with tests, docs, the next notch and the rebuild, or "
        f"the owner redirects. | {TICKET} | {now} | REQUIRED |"
    )
    detail = (
        "- WORK_ITEM: public_notch_target\n"
        "  SWITCH_TRIGGER: The change lands with tests, docs, the next notch and the rebuild, or the owner redirects.\n"
        "  RESUME_HIERARCHY:\n"
        f"    - {TICKET}"
    )
    artifact = (
        f"| {TICKET} | artifacts/public_notch_target_20261016/ | investigation_evidence | active | retain_as_reference | "
        "The lane's folder: the note, replace, activation and routing scripts; the probe of today's notch target "
        f"(C1-C5) and its runs; the notes files. | {now} | REQUIRED |"
    )
    insert_before(pathlib.Path("attention_board.md"), "<!-- END USER-DEFINED: active_items -->", row)
    insert_before(pathlib.Path("attention_board.md"), "<!-- END USER-DEFINED: active_attention_details -->", detail)
    insert_before(pathlib.Path("artifact_board.md"), "<!-- END USER-DEFINED: active_artifacts -->", artifact)


if __name__ == "__main__":
    main()
