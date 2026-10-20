"""
Add S3's entry to the running release note (EPIC-2026-10-18-managed_spell_examples_and_docs).

Run from the repository root (any Python 3.10+), and only after melder_0's rebuild-done NOTICE
(M0-201: melder_0 holds release_docs/next_version_release.md until its rebuild):

    python context_compass/artifacts/managed_spell_examples_20261018/scripts/apply_s3_release_note.py

Inserts one bullet into `## Packaging and documentation`, directly above the closing rebuild line
("- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for ..."), so the
entry reads after every entry that landed before it. The lane changes no source, so it takes no
notch and leaves the header and the rebuild line as they are. A second run refuses before it
changes anything, because the bullet must be absent and the anchor must occur exactly once.
"""
import sys
from pathlib import Path


def main() -> None:
    """Insert the documentation bullet above the rebuild line; refuse a second run."""
    note = Path.cwd() / "release_docs" / "next_version_release.md"
    raw = note.read_bytes()
    marker = b"docs/intermediate/managed-spells.md"
    if marker in raw:
        raise SystemExit("release_docs/next_version_release.md already names the managed spell chapter; nothing applied.")
    section = b"\n## Packaging and documentation\n"
    if raw.count(section) != 1:
        raise SystemExit(f"expected one '## Packaging and documentation' section, found {raw.count(section)}.")
    anchor = b"\n- Agent documentation metadata and the whole-repository LLM bundles are rebuilt for "
    if raw.count(anchor) != 1:
        raise SystemExit(f"expected one rebuild line, found {raw.count(anchor)}.")
    if raw.index(anchor) < raw.index(section):
        raise SystemExit("the rebuild line sits above '## Packaging and documentation'; nothing applied.")
    eol = b"\r\n" if b"\r\n" in raw else b"\n"
    lines = [
        "- The documentation site's intermediate level gains a chapter on managed spell pools",
        "  (`docs/intermediate/managed-spells.md`): binding a managed spell, the three modes and their refusals,",
        "  leasing by meld, injection and `managed_spell_meld`, giving objects back, reset methods, inspecting a",
        "  pool, request scopes and root teardown, and changing settings or moving a pool. Seven runnable",
        "  intermediate lessons back it, one per mode and lifecycle step (42-48 in",
        "  `UX_and_AIX_experiences/02_intermediate/`), with 34 contract probes in",
        "  `UX_and_AIX_experiences/pytest_examples/test_managed_spell_probes.py`; the scopes guide links the chapter",
        "  from its purge table.",
    ]
    block = b"".join(eol + line.encode("utf-8") for line in lines)
    position = raw.index(anchor)
    note.write_bytes(raw[:position] + block + raw[position:])
    sys.stdout.write("applied: release_docs/next_version_release.md (## Packaging and documentation)\n")


if __name__ == "__main__":
    main()
