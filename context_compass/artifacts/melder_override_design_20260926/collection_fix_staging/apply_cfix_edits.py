"""Apply the collection-member path fix under a repository root.

Line-based and line-ending preserving: each anchor is a run of exact lines (without line endings) that
must occur exactly once; replacement lines take the line ending of the anchor's first line, so mixed
CRLF/LF files keep their endings. Usage: python apply_cfix_edits.py <repo_root> [paths] [cache] (default: both)
"""
import pathlib
import sys

DAG = "src/melder/aether/spellbook/spell_compiler/dag/dag_index.py"
BLUEPRINT = "src/melder/aether/spellbook/spell_compiler/system/spell_system_root_blueprint_builder.py"
ANALYZER = (
    "src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/"
    "spell_occurrence_graph_analyzer_strategy.py"
)
CACHE = "src/melder/utilities/caching_system/caching_system.py"
CACHE_TEST = "tests/integration/melder/spellbook/test_cache_schema_version_integration.py"


def L(text: str) -> list:
    """Split a triple-quoted block into lines, dropping the leading newline."""
    return text[1:].split("\n")[:-1] if text.startswith("\n") else text.split("\n")[:-1]


DAG_EDITS = [
    (L("""
        - extend_path returns the same id for the same (parent, segment) pair.
"""), L("""
        - extend_path returns the same id for the same (parent, segment, member)
          triple; member is None except for collection members (see extend_path).
""")),
    (L("""
        self._child_ids: Dict[Tuple[int, str], int] = {}
"""), L("""
        self._child_ids: Dict[Tuple[int, str, Optional[str]], int] = {}
""")),
    (L("""
    def extend_path(self, parent_id: int, segment: str) -> int:
        \"\"\"
        Extend a parent path id with a single segment.

        Contract:
            - Returns existing ids for repeated (parent_id, segment) pairs.
            - New ids are appended and assigned a depth of parent + 1.

        Args:
            parent_id: PathId of the parent path.
            segment: Path segment to append.

        Returns:
            int: PathId representing parent + segment.
        \"\"\"
"""), L("""
    def extend_path(
            self,
            parent_id: int,
            segment: str,
            *,
            member: Optional[str] = None,
    ) -> int:
        \"\"\"
        Extend a parent path id with a single segment.

        Contract:
            - Returns existing ids for repeated (parent_id, segment, member)
              triples.
            - New ids are appended and assigned a depth of parent + 1.
            - `member` separates the members of one collection parameter. Each
              member gets its own child path id while the stored segment stays
              the parameter name, so paths that differ only by member materialize
              and format to the same string (name-based override keys are
              unchanged) but everything below different members stays a distinct
              occurrence: one `Existence.many` object per member, never one per
              collection. Non-collection edges pass None.

        Args:
            parent_id: PathId of the parent path.
            segment: Path segment (parameter name) to append.
            member: Collection member identity (the member's spell id), or None
                for a non-collection edge.

        Returns:
            int: PathId representing parent + segment (+ member).
        \"\"\"
""")),
    (L("""
        key = (parent_id, segment)
"""), L("""
        key = (parent_id, segment, member)
""")),
    (L("""
            - Returns the root id when segments are empty.
            - Returns None when any segment is unknown.
"""), L("""
            - Returns the root id when segments are empty.
            - Returns None when any segment is unknown.
            - Follows member-less edges only: a path that exists only below a
              collection member (see extend_path) resolves to None.
""")),
    (L("""
            key = (current_id, segment)
"""), L("""
            key = (current_id, segment, None)
""")),
]

BLUEPRINT_EDITS = [
    (L("""
            - PathIds are extended via the blueprint PathRegistry.
"""), L("""
            - PathIds are extended via the blueprint PathRegistry.
            - A socket keeps its member-less path; each member of a collection
              socket is queued on its own member path
              (`extend_path(..., member=target_id)`), exactly as Phase 8 mints
              occurrences, so socket parent ids still equal occurrence paths.
""")),
    (L("""
                for target_id in socket_desc.target_spell_ids:
                    target_key = (target_id, socket_path_id)
"""), L("""
                for target_id in socket_desc.target_spell_ids:
                    # Each collection member gets its own child path so the
                    # many-existence dependencies below different members stay
                    # distinct (Phase 8 mints the same ids).
                    if socket_desc.is_collection:
                        target_path_id = path_registry.extend_path(
                            path_id,
                            param_name,
                            member=target_id,
                        )
                    else:
                        target_path_id = socket_path_id
                    target_key = (target_id, target_path_id)
""")),
]

ANALYZER_EDITS = [
    (L("""
        \"\"\"
        Append dependencies discovered from SpellSystemStates local topology.
        \"\"\"
"""), L("""
        \"\"\"
        Append dependencies discovered from SpellSystemStates local topology.

        Contract:
            - Each target of a socket becomes one child occurrence
              `(target_id, child_path_id)` under the socket's parameter name.
            - A collection socket gives every member its own child path
              (`extend_path(..., member=target_id)`), so dependencies below
              different members are separate occurrences and each member gets its
              own `Existence.many` objects. Phase 5 mints the same ids.
            - Returns False when the spell has no local topology (the caller then
              falls back to DAG metadata).
        \"\"\"
""")),
    (L("""
            for target_id in socket.target_spell_ids:
                child_path_id = path_registry.extend_path(path_id, socket.param_name)
"""), L("""
            for target_id in socket.target_spell_ids:
                if socket.is_collection:
                    child_path_id = path_registry.extend_path(
                        path_id,
                        socket.param_name,
                        member=target_id,
                    )
                else:
                    child_path_id = path_registry.extend_path(path_id, socket.param_name)
""")),
    (L("""
        \"\"\"
        Append dependencies discovered from the DAG metadata.
        \"\"\"
"""), L("""
        \"\"\"
        Append dependencies discovered from the DAG metadata.

        Contract:
            - Used only when the spell has no local topology, so collection-ness
              is not known: a parameter fed by two or more nodes is treated as a
              collection and each node gets its own member path, matching the
              topology rule.
        \"\"\"
""")),
    (L("""
        for param_name, _, parent_node in sorted(parent_entries):
            child_path_id = path_registry.extend_path(path_id, param_name)
"""), L("""
        entry_counts: Dict[str, int] = {}
        for param_name, _, _ in parent_entries:
            entry_counts[param_name] = entry_counts.get(param_name, 0) + 1
        for param_name, parent_id, parent_node in sorted(parent_entries):
            if entry_counts[param_name] > 1:
                child_path_id = path_registry.extend_path(
                    path_id,
                    param_name,
                    member=parent_id,
                )
            else:
                child_path_id = path_registry.extend_path(path_id, param_name)
""")),
]

CACHE_EDITS = [
    (L("""
    # Version 12: a non-full-hit conjure rebuilds the whole bundle from its own
"""), L("""
    # Version 13: each member of a collection parameter gets its own compiler
    # path, so many-existence dependencies below different members are built
    # once per member instead of once per collection (2026-09-26). Version-12
    # bundles carry plans that hand one such object to every member.
    # Version 12: a non-full-hit conjure rebuilds the whole bundle from its own
""")),
    (L("""
        12: "complete_bundle_restage",
"""), L("""
        12: "complete_bundle_restage",
        13: "collection_member_paths",
""")),
]

CACHE_TEST_EDITS = [
    (L("""
    12: "complete_bundle_restage",
"""), L("""
    12: "complete_bundle_restage",
    13: "collection_member_paths",
""")),
]


def apply(path: pathlib.Path, edits: list) -> None:
    """Apply anchored line edits to one file, preserving each anchor's line ending."""
    raw = path.read_bytes().decode("utf-8")
    lines = raw.split("\n")
    bodies = [line[:-1] if line.endswith("\r") else line for line in lines]
    for anchor, replacement in edits:
        width = len(anchor)
        hits = [i for i in range(len(bodies) - width + 1) if bodies[i:i + width] == anchor]
        if len(hits) != 1:
            raise SystemExit(f"{path}: anchor matched {len(hits)} times:\n" + "\n".join(anchor))
        start = hits[0]
        ending = "\r" if lines[start].endswith("\r") else ""
        new_lines = [text + ending for text in replacement]
        lines[start:start + width] = new_lines
        bodies[start:start + width] = replacement
    path.write_bytes("\n".join(lines).encode("utf-8"))
    print(f"edited {path}")


if __name__ == "__main__":
    root = pathlib.Path(sys.argv[1])
    targets = sys.argv[2:] or ["paths", "cache"]
    if "paths" in targets:
        apply(root / DAG, DAG_EDITS)
        apply(root / BLUEPRINT, BLUEPRINT_EDITS)
        apply(root / ANALYZER, ANALYZER_EDITS)
    if "cache" in targets:
        apply(root / CACHE, CACHE_EDITS)
        apply(root / CACHE_TEST, CACHE_TEST_EDITS)
