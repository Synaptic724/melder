"""
Report the drift between the src_components C1 core set and the union of the C3 Key Files lists.

Purpose:
    The authoring contract defines the core set as the deduplicated union of every `Key Files (C1)` list in
    the C3 catalog. This script measures how far `## C1 Code Map (Core)` is from that union.

Contract:
    - Key Files are read from the C3 and C2 catalogs (each `## ... Catalog` up to the next H2) - the union of
      every `Key Files (C1)` list, as the document's own core-set invariant states it - both the inline form
      (`- Key Files (C1): `a`, `b``) and the list form (`Key Files (C1):` then `- `path`` items; a prose item
      inside the list does not end it), globs and path-less tokens dropped.
    - Core entries are the `- path:` lines between `## C1 Code Map (Core)` and its
      `### Full Package Inventory` subsection.
    - Read-only; prints KEY-ONLY (named by a component, no core entry) and CORE-ONLY (core entry named by no
      component) paths, each with whether the file exists.

Usage:
    python core_set_drift.py <repo root> <src_components.md>
"""

import pathlib
import re
import sys
from typing import List, Set, Tuple


class DriftPolicy:
    """
    Markers that bound the two sets.

    Attributes:
        CATALOG_HEADING: H2 that opens the C3 catalog.
        SUBCATALOG_HEADING: H2 that opens the C2 catalog.
        CORE_HEADING: H2 that opens the core code map.
        INVENTORY_PREFIX: H3 prefix that ends the core list.
        KEY_FILES_LABEL: Field label of a component's key files.
        PATH_PATTERN: A backticked path token.
    """

    CATALOG_HEADING: str = "## C3 Components Catalog"
    SUBCATALOG_HEADING: str = "## C2 Subcomponents Catalog"
    CORE_HEADING: str = "## C1 Code Map (Core)"
    INVENTORY_PREFIX: str = "### Full Package Inventory"
    KEY_FILES_LABEL: str = "Key Files (C1):"
    PATH_PATTERN: str = r"`([^`]+)`"


def section(lines: List[str], heading: str) -> List[Tuple[int, str]]:
    """
    Return the numbered lines of one H2 section, heading excluded.

    Args:
        lines: Document lines.
        heading: Exact H2 heading text.

    Returns:
        List[Tuple[int, str]]: 1-based line numbers with text, up to the next H2.
    """
    start = lines.index(heading)
    out: List[Tuple[int, str]] = []
    for number in range(start + 1, len(lines)):
        if lines[number].startswith("## "):
            break
        out.append((number + 1, lines[number]))
    return out


def key_files(catalog: List[Tuple[int, str]]) -> Set[str]:
    """
    Collect every path a C3 entry lists under `Key Files (C1)`.

    Args:
        catalog: Numbered lines of the C3 catalog.

    Returns:
        Set[str]: Cited paths, globs excluded.
    """
    found: Set[str] = set()
    in_list = False
    for _, text in catalog:
        stripped = text.strip()
        if DriftPolicy.KEY_FILES_LABEL in stripped:
            tail = stripped.split(DriftPolicy.KEY_FILES_LABEL, 1)[1]
            found.update(re.findall(DriftPolicy.PATH_PATTERN, tail))
            in_list = not tail.strip()
            continue
        if in_list:
            # A list runs until a blank line or a line that is neither a list item nor an indented
            # continuation; prose items inside it (a bullet that names no path) do not end it.
            if stripped and (text.startswith("- ") or text.startswith(" ")):
                if stripped.startswith("- `") or stripped.startswith("`"):
                    found.update(re.findall(DriftPolicy.PATH_PATTERN, stripped))
                continue
            in_list = False
    return {path for path in found if "*" not in path and "?" not in path and "/" in path}


def core_entries(core: List[Tuple[int, str]]) -> Set[str]:
    """
    Collect the `- path:` entries of the core list, stopping at the inventory.

    Args:
        core: Numbered lines of the core code map section.

    Returns:
        Set[str]: Core entry paths.
    """
    found: Set[str] = set()
    for _, text in core:
        if text.startswith(DriftPolicy.INVENTORY_PREFIX):
            break
        match = re.match(r"^- path: `([^`]+)`", text)
        if match:
            found.add(match.group(1))
    return found


def main(argv: List[str]) -> int:
    """
    Print the drift between the two sets.

    Args:
        argv: `<repo root> <src_components.md>`.

    Returns:
        int: 0 when the sets agree, else 1.
    """
    repo = pathlib.Path(argv[0])
    lines = pathlib.Path(argv[1]).read_text(encoding="utf-8").split("\n")
    keys = key_files(section(lines, DriftPolicy.CATALOG_HEADING)) | key_files(
        section(lines, DriftPolicy.SUBCATALOG_HEADING))
    core = core_entries(section(lines, DriftPolicy.CORE_HEADING))
    print(f"key files {len(keys)}, core entries {len(core)}, union {len(keys | core)}")
    for path in sorted(keys - core):
        print(f"KEY-ONLY  exists={(repo / path).is_file()} {path}")
    for path in sorted(core - keys):
        print(f"CORE-ONLY exists={(repo / path).is_file()} {path}")
    return 0 if keys == core else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
