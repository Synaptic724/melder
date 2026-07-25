"""
Agent-metadata harvester and durable asset builder.

WHAT THIS REPLACES
------------------
Melder classes have carried two agent-facing markers in their class bodies -
`__ast_helper_access__` (should agent tooling surface this at all?) and
`__agent_purpose__` (what can an agent do with it?). At 788 assignments across
370 files that is ~115 KB of prose resident in class dicts for the life of every
process, and 788 lines of noise in class bodies, to serve exactly ONE consumer:
`ClassSurfaceAstDescriber`.

This builder harvests the same facts at BUILD time into one generated asset, so
the classes can stop owning them.

WHY DOCSTRINGS ARE SAFE HERE
----------------------------
The sibling epic's docstring proposal was rejected for the registration guard
because `python -OO` strips docstrings and the guard must work at runtime in any
interpreter. That objection does NOT apply to a build-time harvest: `-OO` strips
docstrings from BYTECODE, never from source, and this builder AST-parses source
text. The generated asset carries the prose as ordinary string data, so `-OO` is
irrelevant to every consumer downstream.

THE GRAMMAR
-----------
Line-anchored, ALL-CAPS, deliberately un-prose-like so extraction cannot collide
with the Title-Case sections already in use (`Purpose:`, `Contract:`,
`Threading:`, `Registration:`)::

    AGENT_ACCESS: public

    AGENT_PURPOSE:
        The registration gatekeeper. Internals need NO annotation - the
        generated manifest enumerates them; bind paths call assert_allowed(...).

`AGENT_PURPOSE:` runs until the next line-anchored ALL-CAPS marker, the next
Title-Case section header, or the end of the docstring.

THREE STATES
------------
The point of this asset is that "deliberately excluded" and "nobody has done it
yet" are currently indistinguishable to every tool and every future agent:

    marked   - access + purpose resolved      -> AGENT_METADATA
    exempt   - ruled out, deliberately        -> EXEMPT
    pending  - not done yet, fill in later    -> PENDING

`spell_compiler` is exempt by PATH RULE rather than by stamping 173 files: it is
one coherent subtree under an existing owner ruling (recorded at the OCE epic's
closure as "spell_compiler excluded per owner"). Per-class `AGENT_ACCESS: exempt`
remains available for one-offs.

DUAL-SOURCE MIGRATION
---------------------
Harvest prefers the docstring section and FALLS BACK to the legacy class
attribute. That is what lets the asset be complete and correct from its very
first run, before a single class has been migrated, and lets the codemod proceed
subtree by subtree instead of as one atomic 370-file cutover. When the sweep is
finished and no `attribute` sources remain, the fallback can be deleted.
"""
import ast
import pathlib
import re
from typing import Dict, Iterable, List, Optional, Set, Tuple


class AgentMetadataPolicy:
    """
    Static namespace for the harvester's fixed policy values.

    Contract:
        Class-level constants rather than module globals, per the repo's module
        scope rule. Nothing here is mutated at runtime.

    Attributes:
        ACCESS_MARKER: Line-anchored docstring marker carrying the access level.
        PURPOSE_MARKER: Line-anchored docstring marker opening the purpose block.
        LEGACY_ACCESS_ATTR: Retired class attribute, still read as fallback.
        LEGACY_PURPOSE_ATTR: Retired class attribute, still read as fallback.
        EXEMPT_VALUE: Access value meaning "deliberately not agent-facing".
        VALID_ACCESS: Accepted access values; anything else is a build error.
        EXEMPT_PATH_PREFIXES: Module prefixes (below `melder.`) exempt wholesale.
        ASSET_DIR_NAME: This asset's directory name.
        ASSET_FILE_NAME: Generated asset filename.
        SKIP_DIR_NAMES: Directories excluded from the scan.
    """

    ACCESS_MARKER: str = "AGENT_ACCESS:"
    PURPOSE_MARKER: str = "AGENT_PURPOSE:"

    LEGACY_ACCESS_ATTR: str = "__ast_helper_access__"
    LEGACY_PURPOSE_ATTR: str = "__agent_purpose__"

    EXEMPT_VALUE: str = "exempt"
    VALID_ACCESS: Set[str] = {"public", "internal", "private", "exempt"}

    EXEMPT_PATH_PREFIXES: Tuple[str, ...] = ("aether.spellbook.spell_compiler",)

    ASSET_DIR_NAME: str = "_agent_metadata"
    ASSET_FILE_NAME: str = "agent_metadata.py"

    SKIP_DIR_NAMES: Set[str] = {"__pycache__", "__melder_cache__", "_build_assets"}


def package_root() -> pathlib.Path:
    """
    Return the `melder` package directory.

    Returns:
        pathlib.Path: Directory containing the melder package.
    """
    return pathlib.Path(__file__).resolve().parent.parent.parent


def _iter_source_files(root: pathlib.Path) -> Iterable[pathlib.Path]:
    """
    Yield every scannable Python source file under the package root.

    Args:
        root: The `melder` package directory.

    Returns:
        Iterable[pathlib.Path]: Source files in stable sorted order.
    """
    for path in sorted(root.rglob("*.py")):
        if any(part in AgentMetadataPolicy.SKIP_DIR_NAMES for part in path.parts):
            continue
        yield path


def _module_name_for(path: pathlib.Path, root: pathlib.Path) -> str:
    """
    Derive a file's dotted module name relative to the package root.

    Args:
        path: The source file.
        root: The `melder` package directory.

    Returns:
        str: Dotted module name, always rooted at `melder`.
    """
    parts = list(path.relative_to(root).parts)
    if parts[-1] == "__init__.py":
        parts = parts[:-1]
    else:
        parts[-1] = parts[-1][: -len(".py")]
    return ".".join(["melder", *parts]) if parts else "melder"


def _is_path_exempt(module_name: str) -> bool:
    """
    Return True when a module falls under a wholesale path exemption.

    Contract:
        Prefix match below `melder.`. A per-class `AGENT_ACCESS:` marker still
        wins over the path rule, so a subtree can be exempt while individual
        classes inside it opt back in.

    Args:
        module_name: Dotted module name rooted at `melder`.

    Returns:
        bool: True when the module is inside an exempt subtree.
    """
    suffix = module_name[len("melder.") :] if module_name.startswith("melder.") else ""
    return suffix.startswith(AgentMetadataPolicy.EXEMPT_PATH_PREFIXES)


def _dedent_block(lines: List[str]) -> str:
    """
    Join and normalise an indented docstring block into one prose string.

    Contract:
        Collapses the block to single-spaced prose. Blank lines become paragraph
        breaks so multi-paragraph purposes survive the round trip.

    Args:
        lines: Raw block lines, still indented.

    Returns:
        str: Normalised prose, empty when the block held nothing.
    """
    paragraphs: List[List[str]] = [[]]
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if paragraphs[-1]:
                paragraphs.append([])
            continue
        paragraphs[-1].append(stripped)
    return "\n\n".join(" ".join(p) for p in paragraphs if p).strip()


def parse_docstring_markers(docstring: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract `AGENT_ACCESS` and `AGENT_PURPOSE` from one docstring.

    Contract:
        Markers are LINE-ANCHORED and ALL-CAPS, which is what makes extraction
        unambiguous against the Title-Case sections already in the codebase. The
        purpose block runs until the next line-anchored marker, the next
        Title-Case section header, or the end of the docstring - so authors do
        not have to terminate it explicitly.

    Args:
        docstring: Raw class docstring text.

    Returns:
        Tuple[Optional[str], Optional[str]]: Access value and purpose prose,
            each `None` when its marker is absent.
    """
    if not docstring:
        return None, None

    lines = docstring.splitlines()
    access: Optional[str] = None
    purpose_lines: List[str] = []
    collecting = False

    section_header = re.compile(r"^\s*[A-Z][A-Za-z][A-Za-z /]*:\s*$")

    for line in lines:
        stripped = line.strip()

        if stripped.startswith(AgentMetadataPolicy.ACCESS_MARKER):
            access = stripped[len(AgentMetadataPolicy.ACCESS_MARKER) :].strip() or None
            collecting = False
            continue

        if stripped.startswith(AgentMetadataPolicy.PURPOSE_MARKER):
            inline = stripped[len(AgentMetadataPolicy.PURPOSE_MARKER) :].strip()
            if inline:
                purpose_lines.append(inline)
            collecting = True
            continue

        if collecting:
            # A new marker or a Title-Case section header closes the block.
            if stripped.startswith(AgentMetadataPolicy.ACCESS_MARKER):
                collecting = False
                continue
            if section_header.match(line) and not line.startswith("    " * 2):
                collecting = False
                continue
            purpose_lines.append(line)

    purpose = _dedent_block(purpose_lines) or None
    return access, purpose


def _legacy_attributes(node: ast.ClassDef) -> Tuple[Optional[str], Optional[str]]:
    """
    Read the retired class attributes as a migration fallback.

    Contract:
        Handles both annotated (`x: str = "v"`) and plain (`x = "v"`) forms.
        Non-literal values resolve to `None` rather than raising - a computed
        marker is not harvestable and must surface as unmarked, not as a crash.

    Args:
        node: The class definition being inspected.

    Returns:
        Tuple[Optional[str], Optional[str]]: Legacy access and purpose values.
    """
    access: Optional[str] = None
    purpose: Optional[str] = None
    for stmt in node.body:
        target_name: Optional[str] = None
        value_node: Optional[ast.expr] = None
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            target_name, value_node = stmt.target.id, stmt.value
        elif isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
            target_name, value_node = stmt.targets[0].id, stmt.value
        if target_name is None or value_node is None:
            continue
        try:
            literal = ast.literal_eval(value_node)
        except Exception:
            continue
        if not isinstance(literal, str):
            continue
        if target_name == AgentMetadataPolicy.LEGACY_ACCESS_ATTR:
            access = literal
        elif target_name == AgentMetadataPolicy.LEGACY_PURPOSE_ATTR:
            purpose = literal
    return access, purpose


def _base_names(node: ast.ClassDef) -> List[str]:
    """
    Return statically resolvable base-class names for one class.

    Contract:
        Only names AST can see. Dynamic or computed bases are invisible here and
        are reported through `unresolved_bases` rather than guessed at, so the
        blind spots are named instead of silently wrong.

    Args:
        node: The class definition being inspected.

    Returns:
        List[str]: Base names in declaration order.
    """
    names: List[str] = []
    for base in node.bases:
        if isinstance(base, ast.Name):
            names.append(base.id)
        elif isinstance(base, ast.Attribute):
            names.append(base.attr)
    return names


class HarvestResult:
    """
    Collected harvest output for one scan of the package.

    Contract:
        Plain value container. Holds the three catalogued states plus the
        diagnostics `--check` reports on. Not a dataclass because it carries
        containers rather than scalars, per the repo's dataclass rule.

    Attributes:
        marked: `(module, qualname) -> (access, purpose, source)`.
        exempt: Sorted `(module, qualname)` ruled deliberately out of scope.
        pending: Sorted `(module, qualname)` not yet marked.
        bases: `(module, qualname) -> [base names]` for inherited-purpose resolution.
        invalid_access: Entries whose access value is not in `VALID_ACCESS`.
        access_without_purpose: Marked entries missing prose.
    """

    def __init__(self) -> None:
        """Initialise every collection empty."""
        self.marked: Dict[Tuple[str, str], Tuple[str, str, str]] = {}
        self.exempt: List[Tuple[str, str]] = []
        self.pending: List[Tuple[str, str]] = []
        self.bases: Dict[Tuple[str, str], List[str]] = {}
        self.invalid_access: List[Tuple[str, str, str]] = []
        self.access_without_purpose: List[Tuple[str, str]] = []


def harvest() -> HarvestResult:
    """
    Scan the package and classify every class into the three states.

    Contract:
        Pure AST parsing - imports nothing, so it is cycle-safe and runs against
        a half-built tree. Files are read `utf-8-sig` so a Windows BOM never
        breaks the scan. Resolution order per class is: docstring marker, then
        legacy attribute, then the path exemption, then pending.

    Returns:
        HarvestResult: The classified harvest.

    Raises:
        SyntaxError: If a source file cannot be parsed.
    """
    root = package_root()
    result = HarvestResult()

    for path in _iter_source_files(root):
        tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
        module_name = _module_name_for(path, root)

        stack: List[Tuple[ast.ClassDef, str]] = [
            (n, n.name) for n in tree.body if isinstance(n, ast.ClassDef)
        ]
        while stack:
            node, qualname = stack.pop()
            for child in node.body:
                if isinstance(child, ast.ClassDef):
                    stack.append((child, f"{qualname}.{child.name}"))

            key = (module_name, qualname)
            result.bases[key] = _base_names(node)

            access, purpose = parse_docstring_markers(ast.get_docstring(node) or "")
            source = "docstring"
            if access is None and purpose is None:
                access, purpose = _legacy_attributes(node)
                source = "attribute"

            if access == AgentMetadataPolicy.EXEMPT_VALUE:
                result.exempt.append(key)
                continue

            if access is None and purpose is None:
                if _is_path_exempt(module_name):
                    result.exempt.append(key)
                else:
                    result.pending.append(key)
                continue

            if access is not None and access not in AgentMetadataPolicy.VALID_ACCESS:
                result.invalid_access.append((module_name, qualname, access))
                continue

            if access is not None and purpose is None:
                result.access_without_purpose.append(key)

            result.marked[key] = (access or "", purpose or "", source)

    result.exempt.sort()
    result.pending.sort()
    return result


def target_path() -> pathlib.Path:
    """
    Return the artifact path this builder owns.

    Returns:
        pathlib.Path: `<package>/_build_assets/_agent_metadata/agent_metadata.py`.
    """
    return (
        package_root()
        / "_build_assets"
        / AgentMetadataPolicy.ASSET_DIR_NAME
        / AgentMetadataPolicy.ASSET_FILE_NAME
    )


def render(version: str) -> str:
    """
    Render the artifact text for one melder version.

    Contract:
        PURE and DETERMINISTIC - two calls at one version over one source tree
        return byte-identical text. The runner's `--check` gate is a byte
        comparison, so nondeterminism here would produce phantom staleness.

    Args:
        version: The melder version to stamp into the artifact.

    Returns:
        str: Complete module source, newline-terminated.

    Raises:
        ValueError: When any class declares an access value outside
            `VALID_ACCESS`. This is a BUILD-TIME failure on purpose: the same
            mistake previously surfaced as a runtime raise from
            `ClassSurfaceAstDescriber`, potentially in production.
    """
    result = harvest()

    if result.invalid_access:
        detail = ", ".join(f"{m}:{q}={a!r}" for m, q, a in sorted(result.invalid_access))
        raise ValueError(
            f"invalid AGENT_ACCESS value(s): {detail}. "
            f"Valid values are {sorted(AgentMetadataPolicy.VALID_ACCESS)}."
        )

    lines: List[str] = [
        '"""',
        "GENERATED DURABLE BUILD ASSET - DO NOT EDIT MANUALLY.",
        "",
        "Agent-facing class metadata, harvested from docstrings at build time.",
        "Regenerate with:",
        "    python src/melder/_build_assets/_build_asset_runner.py",
        "",
        "AGENT_METADATA maps (module, qualname) -> (access, purpose).",
        "EXEMPT lists classes deliberately ruled out of agent tooling.",
        "PENDING lists classes not yet marked - fill these in over time.",
        "CLASS_BASES carries statically resolvable base names so inherited",
        "purposes resolve without a runtime MRO walk.",
        '"""',
        "from typing import Dict",
        "from typing import FrozenSet",
        "from typing import Tuple",
        "",
        "",
        f'BUILT_FOR_VERSION: str = "{version}"',
        f"MARKED_COUNT: int = {len(result.marked)}",
        f"EXEMPT_COUNT: int = {len(result.exempt)}",
        f"PENDING_COUNT: int = {len(result.pending)}",
        "",
        "AGENT_METADATA: Dict[Tuple[str, str], Tuple[str, str]] = {",
    ]
    for (module_name, qualname) in sorted(result.marked):
        access, purpose, _source = result.marked[(module_name, qualname)]
        lines.append(
            f'    ("{module_name}", "{qualname}"): ({access!r}, {purpose!r}),'
        )
    lines.append("}")
    lines.append("")
    lines.append("EXEMPT: FrozenSet[Tuple[str, str]] = frozenset((")
    for module_name, qualname in result.exempt:
        lines.append(f'    ("{module_name}", "{qualname}"),')
    lines.append("))")
    lines.append("")
    lines.append("PENDING: FrozenSet[Tuple[str, str]] = frozenset((")
    for module_name, qualname in result.pending:
        lines.append(f'    ("{module_name}", "{qualname}"),')
    lines.append("))")
    lines.append("")
    lines.append("CLASS_BASES: Dict[Tuple[str, str], Tuple[str, ...]] = {")
    for key in sorted(result.bases):
        bases = result.bases[key]
        if bases:
            lines.append(f'    ("{key[0]}", "{key[1]}"): {tuple(bases)!r},')
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def write(version: str) -> Tuple[pathlib.Path, int]:
    """
    Write the artifact to disk atomically.

    Args:
        version: The melder version to stamp into the artifact.

    Returns:
        Tuple[pathlib.Path, int]: The written path and the marked-entry count.

    Raises:
        OSError: If the asset directory is not writable.
    """
    text = render(version)
    target = target_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(".py.tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(target)
    return target, text.count("): (")
