"""M2 follow-through in tests/unit/melder/aether/test_nexus.py (melder_0, 2026-09-30).

Two tests re-activated the LIVE Nexus singleton with another configuration as setup. An active Nexus now refuses
that (0.2.8210), so each gets a deactivate() first - the documented remedy. What they assert is unchanged. The
file has mixed line endings, so each edit keeps the ending of the line it anchors on.
"""
import pathlib
import sys

PATH = pathlib.Path(sys.argv[1])

EDITS = (
    (
        b"    replacement_configuration.with_denied_target_frame_names(tuple())",
        b"    nexus.activate(replacement_configuration)",
        (
            b"    # An active Nexus refuses another configuration (0.2.8210): deactivate it,",
            b"    # then activate the replacement policy.",
            b"    nexus.deactivate()",
        ),
    ),
    (
        b"    configuration.with_max_nexus_frame_count(2)",
        b"    isolated_nexus.activate(configuration)",
        (
            b"    # Nexus is a singleton: this is the shared Nexus above, still active. An active",
            b"    # Nexus refuses another configuration (0.2.8210), so deactivate it first.",
            b"    isolated_nexus.deactivate()",
        ),
    ),
)

raw = PATH.read_bytes()
for before, target, inserted in EDITS:
    for ending in (b"\r\n", b"\n"):
        anchor = before + ending + target + ending
        if raw.count(anchor) == 1:
            replacement = before + ending + b"".join(line + ending for line in inserted) + target + ending
            raw = raw.replace(anchor, replacement, 1)
            print("inserted before", target.decode().strip(), "(CRLF)" if ending == b"\r\n" else "(LF)")
            break
    else:
        raise SystemExit("anchor not found once: " + target.decode())
PATH.write_bytes(raw)
