"""Link S4's patch docs and the A-D preview from the story and the artifact board (melder_1).

(1) The story's ARTIFACT_PATHS gain the patch folder, the M4-M7 probe and the A-D preview, after the lane folder's
line; (2) the artifact board gains a patch_doc row for the folder after the lane row, and the lane row's text and
time are brought current; (3) the architecture patch's non-goals are re-wrapped so no story id is split across
lines. LF only, anchors must occur once, lines within 120 characters except one-token paths, every write read back.
Usage: --check | --apply
"""
import datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
STORY = ROOT / "tickets/stories/2026-10-17_minted_index_missing_from_frame_registry_story.md"
BOARD = ROOT / "artifact_board.md"
PATCH = ROOT / "system_docs/patches/active/minted_index_registry_2026_10_18/architecture_patch.md"
TS = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
STORY_TICKET = "tickets/stories/2026-10-17_minted_index_missing_from_frame_registry_story.md"

LANE_LINE = "  - artifacts/minted_index_registry_20261018/ (melder_1's lane: re-runs, scripts, notes)\n"
NEW_PATHS = (
    "  - system_docs/patches/active/minted_index_registry_2026_10_18/ (the three patch docs)\n"
    "  - artifacts/minted_index_registry_20261018/probes/probe_minted_index_fix_cases.py (cases M4-M7)\n"
    "  - artifacts/minted_index_registry_20261018/runs/s4_preview_0_2_8256_abcd.diff (edits A-D to land)\n"
)
LANE_ROW = re.compile(r"^\| " + re.escape(STORY_TICKET) + r" \| artifacts/minted_index_registry_20261018/ \|.*$",
                      re.M)
LANE_ROW_NEW = ("| %s | artifacts/minted_index_registry_20261018/ | investigation_evidence | active | "
                "retain_as_reference | melder_1's lane: the re-runs of probes M1-M3 and V1-V4 and the new probe M4-M7 "
                "on 0.2.8256, the prototypes of edits A-C, the A-D preview (runs/s4_preview_0_2_8256_abcd.diff), "
                "scripts and notes drafts; the red and green runs, the whole-tree runs and the rebuild logs land "
                "here. | %s | HELPFUL |" % (STORY_TICKET, TS))
PATCH_ROW = ("| %s | system_docs/patches/active/minted_index_registry_2026_10_18/ | patch_doc | active | "
             "promote_to_documentation | The architecture patch and two component patches (the Spellbook seam and "
             "the root's teardown; MutationResearch residency) for edits A-D, on the owner's word (2026-10-18); "
             "promoted to the system documents at landing, archived at turn-in. | %s | REQUIRED |" % (STORY_TICKET, TS))
OLD_NONGOALS = (
    "  binding signature an active version in a minted index takes (STORY-2026-10-17-notch_moves_signature_by_incoming_\n"
    "  key_only); the parked versions Book teardown leaves uncleaned (STORY-2026-10-17-book_teardown_leaves_parked_\n"
    "  versions_uncleaned); a restore or graft of a separated version (STORY-2026-10-17-restore_drops_separated_parked_\n"
    "  version); index-link borrowers (a minted index has none until a link is made to it).\n"
)
NEW_NONGOALS = (
    "  binding signature an active version in a minted index takes\n"
    "  (STORY-2026-10-17-notch_moves_signature_by_incoming_key_only); the parked versions Book teardown leaves uncleaned\n"
    "  (STORY-2026-10-17-book_teardown_leaves_parked_versions_uncleaned); a restore or graft of a separated version\n"
    "  (STORY-2026-10-17-restore_drops_separated_parked_version); index-link borrowers (a minted index has none until a\n"
    "  link is made to it).\n"
)


def read_lf(path: pathlib.Path) -> str:
    """Return the file's text, refusing CRLF."""
    raw = path.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("CRLF in %s" % path.name)
    return raw.decode("utf-8")


def replace_once(text: str, old: str, new: str, what: str) -> str:
    """Replace the one occurrence of `old`, refusing zero or several."""
    if text.count(old) != 1:
        raise SystemExit("%s: anchor found %d times" % (what, text.count(old)))
    return text.replace(old, new)


def check_width(block: str, what: str) -> None:
    """Refuse a line over 120 characters unless it is a single unbreakable token after its bullet."""
    for line in block.split("\n"):
        stripped = line.strip()
        if len(line) > 120 and not (stripped.startswith("- ") and " " not in stripped[2:]):
            raise SystemExit("%s: line over 120 chars (%d): %s" % (what, len(line), line))


def main() -> None:
    """Prepare the three files, then write them with --apply."""
    if len(sys.argv) != 2 or sys.argv[1] not in ("--check", "--apply"):
        raise SystemExit(__doc__)
    apply = sys.argv[1] == "--apply"
    check_width(NEW_PATHS, "story paths")
    check_width(NEW_NONGOALS, "patch non-goals")
    story = replace_once(read_lf(STORY), LANE_LINE, LANE_LINE + NEW_PATHS, "story")
    story, count = re.subn(r"^- Updated: \S+$", "- Updated: " + TS, story, count=1, flags=re.M)
    if count != 1:
        raise SystemExit("story: no Updated line")
    board = read_lf(BOARD)
    rows = LANE_ROW.findall(board)
    if len(rows) != 1:
        raise SystemExit("board: lane row found %d times" % len(rows))
    board = LANE_ROW.sub(lambda _match: LANE_ROW_NEW + "\n" + PATCH_ROW, board)
    patch = replace_once(read_lf(PATCH), OLD_NONGOALS, NEW_NONGOALS, "patch")
    print("story: +3 artifact paths; board: lane row refreshed, patch row added; patch: non-goals re-wrapped")
    if apply:
        for path, text in ((STORY, story), (BOARD, board), (PATCH, patch)):
            path.write_bytes(text.encode("utf-8"))
            if path.read_bytes().decode("utf-8") != text:
                raise SystemExit("read-back mismatch: %s" % path.name)
        print("applied (%s)" % TS)


main()
