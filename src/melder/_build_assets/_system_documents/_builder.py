"""
System documents: ingest the context-map document/index pairs into melder.

WHAT THIS INGESTS
-----------------
Context Compass emits every context map as a PAIR:

    <name>.md          the document
    <name>_index.md    line ranges into it, plus a staleness proof

The index is the product; the document is the backing store. Measured on this
repo the index is 2-3% of the document's lines and 3-4% of its bytes, which is
what makes "read the index, then slice one range" cost roughly 500x less than
reading the document to answer a question about one section.

EVERYTHING IS EMITTED AS CODE
-----------------------------
This asset mirrors its siblings `_bind_guard` and `_agent_documentation`: repo
data is captured at BUILD time into generated Python modules that ship inside
the package. `context_compass/` is excluded from the wheel, so an installed
melder has no access to it - the bytes must already be in the code, or an agent
consuming the wheel has nothing to read.

    manifest/   the INDEXES plus each document's proof and graph adjacency.
                Small (~150 KB), committed, imported eagerly. This is the
                navigable surface: what exists and where it lives.

    payloads/   one module per document, carrying the document text as a
                string literal. Imported LAZILY, on first slice.

An earlier revision shipped the documents as `.md` package data instead. That
was wrong for this repo: package-data entries are declared separately from the
code and are silently dropped when the declaration drifts - a failure this
session already hit once, when `*.melc` payloads were gitignored while their
loaders stayed tracked. A string literal in a module cannot fail to ship,
because it IS the module.

The cost that buys is a one-time compile of the payload module. `src_graph.md`
is 1.7 MB, so its payload is the expensive one - which is exactly why payloads
are per-document and lazy: nothing pays for the graph text unless it asks for a
graph slice.

THE VERIFICATION GATE - NON-NEGOTIABLE
--------------------------------------
Every index carries `line_count`, `line_ending`, and `content_sha256` for the
document it describes. Per
`agent_onboarding/default/engineer/skills/src_graph_usage.md`:

    On any mismatch the document was hand-edited or the pipeline was
    interrupted. STOP. Do not slice. ... A range from an unverified index is a
    guess wearing a line number.

This builder enforces that at BUILD time - a document that does not match its
index is refused, not ingested - and the generated loader re-checks at RUNTIME
against the shipped copy. Both gates matter: the build gate stops bad data
entering the wheel, the runtime gate stops a hand-edited installed file being
sliced.

That gate is not theoretical. `src_components_index.md` was stale on
2026-08-02 (8,127 claimed against 8,137 actual, SHA mismatch, the document
written six minutes after its index).

TWO ADDRESSING SCHEMES
----------------------
The index row shape differs by document family, so the query surface does too:

    | lines | lvl | name |                architecture, components
        -> address by SECTION NAME        "Boot and Configuration Sequence"

    | lines | source | nodes | edges |    graph
        -> address by SOURCE PATH         "src/melder/aether/conduit/conduit.py"
"""
import hashlib
import json
import pathlib
import re
from typing import Dict, List, Optional, Tuple


class SystemDocumentsBuildPolicy:
    """
    Static namespace for the system-document generator's fixed values.

    Contract:
        Class-level constants rather than module globals, per the repo's module
        scope rule. Nothing here is mutated at runtime.

    Attributes:
        BUILD_ASSETS_DIR_NAME: Package directory holding durable build assets.
        ASSET_DIR_NAME: This asset's directory.
        MANIFEST_DIR_NAME: Directory holding the committed manifest.
        MANIFEST_FILE_NAME: Generated manifest module filename.
        PAYLOAD_DIR_NAME: Directory holding the generated per-document payload
            modules. Code, not package data - see the module docstring.
        INGEST_ROOT: Repo-relative source of the document/index pairs. Not
            shipped (`context_compass*` is excluded from the wheel), which is
            why the bytes are copied in at build time.
        MARKDOWN_KEY: The hardcopy envelope's markdown key, validated by
            `StaticSystemDocument` at construction.
        READ_ORDER: The documents in the order an agent should read them.
        MANIFEST_VERSION: SCHEMA version of the manifest shape.
    """

    BUILD_ASSETS_DIR_NAME: str = "_build_assets"
    ASSET_DIR_NAME: str = "_system_documents"
    MANIFEST_DIR_NAME: str = "manifest"
    MANIFEST_FILE_NAME: str = "system_documents_manifest.py"
    PAYLOAD_DIR_NAME: str = "payloads"

    INGEST_ROOT: str = "context_compass/system_docs"
    MARKDOWN_KEY: str = "m"

    READ_ORDER: Tuple[str, ...] = (
        "__architecture__",
        "__components__",
        "__graph_network__",
        "__graph_details__",
    )

    # 2.0.0: document/index ingestion with a verification gate and section
    # addressing. 1.0.0 was four inline placeholder envelopes with no index,
    # no sections, and no integrity proof - not a shape this can migrate from.
    MANIFEST_VERSION: str = "2.0.0"


SOURCES: Dict[str, Dict[str, object]] = {
    "__architecture__": {
        "title": "Melder Architecture",
        "summary": (
            "C4-level system map. Boundaries, entrypoints, boot and "
            "configuration sequencing, invariants, failure modes. Read this "
            "FIRST - it is orientation, and it is the one document meant to be "
            "read whole."
        ),
        "document": "src_architecture.md",
        "index": "src_architecture_index.md",
        "addressing": "section",
        "ship_document": True,
    },
    "__components__": {
        "title": "Melder Components",
        "summary": (
            "Subsystem inventory - what each component owns, hands off to, and "
            "whether an agent may drive it. A LOOKUP TABLE, not orientation: "
            "read the index, then fetch only the sections your task touches."
        ),
        "document": "src_components.md",
        "index": "src_components_index.md",
        "addressing": "section",
        "ship_document": True,
    },
    "__graph_network__": {
        "title": "Melder Graph Network",
        "summary": (
            "The graph's SHAPE: every source file melder defines, with its node "
            "and edge counts. This is the index itself - enough to see the "
            "network and choose what to open, without opening anything."
        ),
        "document": "src_graph.md",
        "index": "src_graph_index.md",
        "addressing": "source_path",
        # Shares `src_graph.md` with `__graph_details__`. Payload emission is
        # keyed by DOCUMENT file, so pointing both views at it costs nothing -
        # the 1.7 MB is embedded once - and it is what lets the network view
        # resolve a walked node straight into the prose describing it.
        "ship_document": True,
    },
    "__graph_details__": {
        "title": "Melder Graph Details",
        "summary": (
            "Per-source-file detail: nodes, edges out, why-lines, edge "
            "candidates, published aliases. Address by SOURCE PATH. Trust tiers "
            "differ per field - mechanical is derived, authored can be stale, "
            "candidates are guesses."
        ),
        "document": "src_graph.md",
        "index": "src_graph_index.md",
        "addressing": "source_path",
        "ship_document": True,
    },
}


def package_root() -> pathlib.Path:
    """
    Return the `melder` package directory.

    Returns:
        pathlib.Path: Directory containing the melder package.
    """
    return pathlib.Path(__file__).resolve().parent.parent.parent


def repository_root() -> pathlib.Path:
    """
    Return the repository root, which holds `context_compass/`.

    Contract:
        Build-time only. Nothing at runtime resolves this path, because the
        bytes are copied into the package.

    Returns:
        pathlib.Path: The repository root.
    """
    return package_root().parent.parent


def asset_dir() -> pathlib.Path:
    """
    Return this asset's directory.

    Returns:
        pathlib.Path: `<package>/_build_assets/_system_documents`.
    """
    return (
        package_root()
        / SystemDocumentsBuildPolicy.BUILD_ASSETS_DIR_NAME
        / SystemDocumentsBuildPolicy.ASSET_DIR_NAME
    )


def payload_dir() -> pathlib.Path:
    """
    Return the directory holding generated per-document payload modules.

    Returns:
        pathlib.Path: `<asset dir>/payloads`.
    """
    return asset_dir() / SystemDocumentsBuildPolicy.PAYLOAD_DIR_NAME


def payload_module_name(document_file: str) -> str:
    """
    Return the payload module basename for one document file.

    Contract:
        Keyed on the DOCUMENT, not the melder document name, because
        `__graph_network__` and `__graph_details__` share `src_graph.md` and
        must share one payload rather than embedding 1.7 MB twice.

    Args:
        document_file: e.g. `src_graph.md`.

    Returns:
        str: e.g. `src_graph_payload`.
    """
    return document_file[:-3].replace("-", "_") + "_payload"


def manifest_path() -> pathlib.Path:
    """
    Return the full path of the committed manifest module.

    Returns:
        pathlib.Path: The generated manifest module's absolute path.
    """
    return (
        asset_dir()
        / SystemDocumentsBuildPolicy.MANIFEST_DIR_NAME
        / SystemDocumentsBuildPolicy.MANIFEST_FILE_NAME
    )


def manifest_version() -> str:
    """
    Return the SCHEMA version of this manifest's shape.

    Returns:
        str: The manifest shape version, independent of the melder release.
    """
    return SystemDocumentsBuildPolicy.MANIFEST_VERSION


def parse_index(index_text: str) -> Dict[str, object]:
    """
    Parse one context-map index into its proof and its section rows.

    Contract:
        Handles BOTH row shapes, distinguished by the header:

            `| lines | lvl | name |`               -> keyed by section name
            `| lines | source | nodes | edges |`   -> keyed by source path

        Section keys are returned in document order. Duplicate keys keep the
        FIRST occurrence: an architecture map legitimately repeats a heading
        under different parents, and the index disambiguates those with a
        `Parent > Child` name, so a true collision means the index is malformed
        rather than that the later row should win.

    Args:
        index_text: Full text of the `_index.md` file.

    Returns:
        Dict[str, object]: `line_count`, `line_ending`, `content_sha256`,
            `addressing`, and `sections` as an ordered list of
            `(key, start, end)`.

    Raises:
        ValueError: When the staleness proof is missing or unparseable. An
            index without a proof cannot be verified, and an unverifiable index
            is not usable - refusing here is the point.
    """
    def field(name: str, pattern: str) -> str:
        found = re.search(r"\|\s*" + name + r"\s*\|\s*" + pattern + r"\s*\|", index_text)
        if not found:
            raise ValueError(f"index is missing its {name!r} staleness field")
        return found.group(1)

    line_count = int(field("line_count", r"(\d+)"))
    line_ending = field("line_ending", r"(\w+)")
    content_sha256 = field("content_sha256", r"`([0-9a-f]{64})`")

    by_source = "| lines | source |" in index_text
    sections: List[Tuple[str, int, int]] = []
    seen = set()
    for row in re.finditer(r"^\|\s*(\d+)-(\d+)\s*\|\s*([^|]+?)\s*\|(.*)$", index_text, re.MULTILINE):
        start, end = int(row.group(1)), int(row.group(2))
        if by_source:
            key = row.group(3).strip().strip("`")
        else:
            rest = row.group(4).split("|")
            if not rest:
                continue
            key = rest[0].strip()
        if not key or key in seen:
            continue
        seen.add(key)
        sections.append((key, start, end))

    return {
        "line_count": line_count,
        "line_ending": line_ending,
        "content_sha256": content_sha256,
        "addressing": "source_path" if by_source else "section",
        "sections": sections,
    }


def verify(document_bytes: bytes, proof: Dict[str, object]) -> Optional[str]:
    """
    Check one document against its index's staleness proof.

    Contract:
        Recomputes BOTH `line_count` and `content_sha256`, as the usage skill
        requires. A trailing newline does not create a phantom final line,
        matching how the index counts.

    Args:
        document_bytes: Raw document bytes.
        proof: The parsed index proof.

    Returns:
        Optional[str]: `None` when current, else a human-readable mismatch
            naming both claimed and actual values - because "stale" without the
            numbers sends the reader back to recompute them.
    """
    lines = document_bytes.decode("utf-8").split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    actual_count = len(lines)
    actual_hash = hashlib.sha256(document_bytes).hexdigest()

    problems = []
    if actual_count != proof["line_count"]:
        problems.append(f"line_count claimed {proof['line_count']} actual {actual_count}")
    if actual_hash != proof["content_sha256"]:
        problems.append(
            f"content_sha256 claimed {str(proof['content_sha256'])[:16]}... "
            f"actual {actual_hash[:16]}..."
        )
    return "; ".join(problems) if problems else None


def ingest() -> Tuple[Dict[str, Dict[str, object]], List[str]]:
    """
    Read every document/index pair and build the entries, refusing stale pairs.

    Contract:
        A pair whose document does not match its index proof is NOT ingested.
        It is reported and skipped, and the previously-generated entry for that
        document is left untouched, so a stale regeneration upstream cannot
        silently replace good shipped data with unverifiable data.

        A pair whose source files are ABSENT is also skipped rather than
        raising: a trimmed checkout or an sdist build has no `context_compass/`
        at all, and refusing to build there would make the package unbuildable
        outside a full clone. `available` carries the truth instead.

    Returns:
        Tuple[Dict[str, Dict[str, object]], List[str]]: Entries by document
            name, and a list of human-readable refusals.
    """
    root = repository_root() / SystemDocumentsBuildPolicy.INGEST_ROOT
    entries: Dict[str, Dict[str, object]] = {}
    refusals: List[str] = []

    for name in SystemDocumentsBuildPolicy.READ_ORDER:
        spec = SOURCES[name]
        doc_path = root / str(spec["document"])
        idx_path = root / str(spec["index"])

        if not doc_path.is_file() or not idx_path.is_file():
            entries[name] = _unavailable(name, spec, "source pair not present in this checkout")
            continue

        try:
            proof = parse_index(idx_path.read_text(encoding="utf-8"))
        except ValueError as error:
            refusals.append(f"{name}: {spec['index']} unusable - {error}")
            entries[name] = _unavailable(name, spec, f"index unusable: {error}")
            continue

        mismatch = verify(doc_path.read_bytes(), proof)
        if mismatch is not None:
            refusals.append(f"{name}: {spec['document']} does not match its index - {mismatch}")
            entries[name] = _unavailable(name, spec, f"index stale: {mismatch}")
            continue

        entries[name] = {
            "name": name,
            "title": spec["title"],
            "summary": spec["summary"],
            "source": f"{SystemDocumentsBuildPolicy.INGEST_ROOT}/{spec['document']}",
            "available": True,
            "addressing": proof["addressing"],
            "document_file": str(spec["document"]),
            "payload_module": (
                payload_module_name(str(spec["document"])) if spec["ship_document"] else ""
            ),
            "line_count": proof["line_count"],
            "content_sha256": proof["content_sha256"],
            "sections": proof["sections"],
        }
    return entries, refusals


def _unavailable(name: str, spec: Dict[str, object], reason: str) -> Dict[str, object]:
    """
    Build the entry for a document that could not be ingested.

    Contract:
        Carries the SAME keys as a live entry so consumers need no special
        case, with `available=False` and a `reason` an agent can act on. The
        alternative - omitting the document - would make a stale index look
        identical to a document that never existed.

    Args:
        name: Document name.
        spec: Its `SOURCES` entry.
        reason: Why it is unavailable.

    Returns:
        Dict[str, object]: The unavailable entry.
    """
    return {
        "name": name,
        "title": spec["title"],
        "summary": spec["summary"],
        "source": f"{SystemDocumentsBuildPolicy.INGEST_ROOT}/{spec['document']}",
        "available": False,
        "reason": reason,
        "addressing": spec["addressing"],
        "document_file": "",
        "payload_module": "",
        "line_count": 0,
        "content_sha256": "",
        "sections": [],
    }


def source_fingerprint() -> str:
    """
    SHA256 over the ingested document/index pairs.

    Contract:
        Hashes the INDEX proofs rather than the document bytes. The proof
        already contains the document's own `content_sha256`, so hashing it is
        equivalent to hashing 2.13 MB and costs three small reads instead.

    Returns:
        str: Hex digest over every pair, in read order.
    """
    root = repository_root() / SystemDocumentsBuildPolicy.INGEST_ROOT
    digest = hashlib.sha256()
    for name in SystemDocumentsBuildPolicy.READ_ORDER:
        spec = SOURCES[name]
        digest.update(name.encode("utf-8"))
        for key in ("title", "summary", "document", "index", "addressing"):
            digest.update(str(spec[key]).encode("utf-8"))
        digest.update(b"1" if spec["ship_document"] else b"0")
        idx = root / str(spec["index"])
        digest.update(idx.read_bytes() if idx.is_file() else b"<absent>")
    return digest.hexdigest()


def _text_literal(text: str) -> str:
    """
    Render document text as a Python string literal that round-trips exactly.

    Purpose:
        The payload IS a string literal, so getting this wrong is the worst
        failure this asset has: the module still imports, ranges still resolve,
        and the prose comes back subtly altered. Nothing downstream can detect
        that.

    Contract:
        Prefers a triple-quoted literal because a generated payload is
        diffable and a reviewer should be able to read it. Falls back to
        `repr()` - which Python guarantees round-trips - whenever the readable
        form would not.

        The readable form fails on trailing quotes, which fuse with the closing
        delimiter: one makes the module unparseable, and TWO make it parse
        while silently dropping them. No shipped document ends that way today,
        but that is luck rather than a guarantee, and luck is not a thing to
        emit code on.

        Verified by EXECUTION, not by reasoning about escapes. If the readable
        literal does not evaluate back to the input, it is not used.

    Args:
        text: The document text.

    Returns:
        str: A Python expression evaluating to exactly `text`.
    """
    escaped = text.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
    if escaped.endswith('"'):
        trailing = len(escaped) - len(escaped.rstrip('"'))
        escaped = escaped[:-trailing] + '\\"' * trailing
    readable = '"""' + escaped + '"""'
    try:
        namespace: Dict[str, object] = {}
        exec(compile(f"_ = {readable}", "<literal>", "exec"), namespace)
        if namespace["_"] == text:
            return readable
    except SyntaxError:
        pass
    return repr(text)


def write_payloads(entries: Dict[str, Dict[str, object]]) -> int:
    """
    Emit one payload module per shipped document, carrying its text.

    Contract:
        Generated CODE, mirroring how `_bind_guard` and `_agent_documentation`
        emit their manifests. `context_compass/` never reaches the wheel, so
        the text has to live in a module or an installed melder has nothing to
        serve.

        Keyed by DOCUMENT file, not by melder document name: `__graph_network__`
        and `__graph_details__` share `src_graph.md`, and embedding 1.7 MB twice
        to serve two views of one document would be pure waste.

        The text is written as a single triple-quoted `TEXT` literal.
        Backslashes and embedded triple quotes are escaped, and the round trip
        is ASSERTED before the file is written - a mangled payload would slice
        cleanly and return subtly wrong prose, which is the worst failure mode
        available here.

        Stale payloads are cleared first, so a document that stops shipping does
        not linger.

    Args:
        entries: The ingested entries.

    Returns:
        int: Number of payload modules written.

    Raises:
        ValueError: If an emitted literal does not round-trip to the source
            text exactly.
    """
    target = payload_dir()
    target.mkdir(parents=True, exist_ok=True)
    for existing in target.glob("*_payload.py"):
        existing.unlink()

    root = repository_root() / SystemDocumentsBuildPolicy.INGEST_ROOT
    written: Dict[str, bool] = {}
    for name in SystemDocumentsBuildPolicy.READ_ORDER:
        entry = entries[name]
        if not entry["available"] or not entry["document_file"]:
            continue
        document_file = str(entry["document_file"])
        if document_file in written:
            continue

        text = (root / document_file).read_text(encoding="utf-8")
        literal = _text_literal(text)
        module = "\n".join([
            '"""',
            "GENERATED BUILD ASSET - DO NOT EDIT MANUALLY.",
            "",
            f"Verbatim text of `{SystemDocumentsBuildPolicy.INGEST_ROOT}/{document_file}`,",
            "captured at build time so an installed melder can serve it without the",
            "repository present.",
            "",
            "Imported LAZILY - only when something actually slices this document.",
            f"`LINE_COUNT` and `CONTENT_SHA256` are the same proof the index carries,",
            "repeated here so a consumer can verify without loading the manifest.",
            "",
            "Regenerate with:",
            "    python src/melder/_build_assets/_build_asset_runner.py",
            '"""',
            "",
            f'DOCUMENT_FILE = {document_file!r}',
            f'LINE_COUNT = {entry["line_count"]!r}',
            f'CONTENT_SHA256 = {entry["content_sha256"]!r}',
            "",
            f'TEXT = {literal}',
            "",
        ])

        namespace: Dict[str, object] = {}
        exec(compile(module, "<payload>", "exec"), namespace)
        if namespace["TEXT"] != text:
            raise ValueError(f"{document_file}: emitted literal does not round-trip")

        destination = target / f"{payload_module_name(document_file)}.py"
        temporary = destination.with_suffix(".py.tmp")
        temporary.write_text(module, encoding="utf-8")
        temporary.replace(destination)
        written[document_file] = True
    return len(written)


def parse_graph_adjacency(
        text: str,
) -> Tuple[Dict[str, Dict[str, object]], Tuple[Tuple[str, ...], ...], Dict[Tuple[str, str], str]]:
    """
    Extract the node table and edge list from the graph document.

    Purpose:
        The index answers "where is the section for this FILE". It cannot
        answer "what does this NODE point at", because it only carries node and
        edge COUNTS. Walking therefore means parsing prose - 24,730 lines of it
        - which no agent should pay for at query time, and no installed melder
        should have to do repeatedly.

        So the walk is resolved ONCE here, at build time, and shipped as
        literals.

    Contract:
        Parses only what the document states outright:
          - an `id` field beneath a level-four node heading -> a node
          - six-column `Edges out` rows -> an edge

        Edge CANDIDATES are deliberately skipped. `src_graph_usage.md` measures
        them over-generating roughly 8x and calls them "leads, never evidence";
        promoting a guess into a shipped adjacency table would launder it into
        something that looks derived.

        Both directions are built. The usage skill names reverse lookup as
        "the one query this layout does not make cheap" - true of a text
        document read top-down, but a build pass sees every row, so the inbound
        index costs one extra dict append and removes the whole limitation.

    Args:
        text: Full text of the graph document.

    Returns:
        Tuple: (nodes, edges, whys). `nodes` maps node id -> {source, name,
            kind, line, unsemantic}. `edges` is a tuple of
            (from, relation, to, cardinality, phase, origin). `whys` maps
            (from, to) -> the authored justification for that relationship.
    """
    nodes: Dict[str, Dict[str, object]] = {}
    edges: List[Tuple[str, ...]] = []
    whys: Dict[Tuple[str, str], str] = {}
    source = ""
    pending_name = ""
    pending_kind = ""
    pending_line = 0
    in_candidates = False
    last_id = ""

    for line in text.split("\n"):
        if line.startswith("<!-- BEGIN FILE: "):
            source = line[len("<!-- BEGIN FILE: "):].split(" -->")[0].strip()
            in_candidates = False
            continue
        if line.startswith("### Edge candidates"):
            in_candidates = True
            continue
        if line.startswith("### "):
            in_candidates = False
            continue

        if line.startswith("#### `"):
            rest = line[6:]
            pending_name = rest.split("`", 1)[0]
            pending_kind = rest.split("(", 1)[1].split(")", 1)[0] if "(" in rest else ""
            pending_line = 0
            continue
        if line.startswith("- id: `") and pending_name:
            last_id = line[7:].rstrip("`").strip().rstrip("`")
            nodes[last_id] = {
                "source": source,
                "name": pending_name,
                "kind": pending_kind,
                "line": pending_line,
                "unsemantic": False,
            }
            pending_name = ""
            continue
        if line.startswith("- defined at: `") and last_id in nodes:
            tail = line.rstrip("`").rsplit(":", 1)
            if len(tail) == 2 and tail[1].isdigit():
                nodes[last_id]["line"] = int(tail[1])
            continue
        if line.startswith("- **UNSEMANTIC**") and last_id in nodes:
            nodes[last_id]["unsemantic"] = True
            continue

        # Why-lines sit beneath the table: `- \`from\` -> \`to\`: justification`.
        # They are the authored reason for a claim the syntax tree cannot
        # support, and `src_graph_usage.md` says to read one before relying on
        # its edge. Capturing them here is the difference between that being a
        # dict lookup and being a full section slice plus eyeballing.
        if not in_candidates and line.startswith("- `") and "` -> `" in line:
            head, _, why = line.partition(": ")
            left, _, right = head[2:].partition("` -> `")
            if why:
                whys[(left.strip("` "), right.strip("` "))] = why.strip()
            continue

        if in_candidates or not line.startswith("| `"):
            continue
        cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        if len(cells) == 6 and cells[0] and cells[2]:
            edges.append(tuple(cells))

    return nodes, tuple(edges), whys


def write_graph_adjacency(entries: Dict[str, Dict[str, object]], version: str) -> int:
    """
    Emit the resolved graph adjacency as a generated module.

    Contract:
        Lives beside the manifest because it IS manifest-shaped - committed,
        plain literals, diffable in review - but it is imported LAZILY, only
        when a caller actually walks. A process that imports melder and never
        touches `__graph_network__` must not pay for it.

        Emits both directions plus a node -> source map, which is what makes
        cross-document resolution possible: a node id resolves to a source
        path, and that path is the section key `__graph_details__` is addressed
        by. That is the join between the two graph documents.

    Args:
        entries: The ingested entries.
        version: The melder version to stamp into the generated module.

    Returns:
        int: Number of edges emitted, or 0 when the graph document is
            unavailable.
    """
    entry = entries["__graph_details__"]
    target = manifest_path().parent / "graph_adjacency_manifest.py"
    if not entry["available"]:
        nodes, edges, whys = {}, (), {}
    else:
        root = repository_root() / SystemDocumentsBuildPolicy.INGEST_ROOT
        text = (root / str(entry["document_file"])).read_text(encoding="utf-8")
        nodes, edges, whys = parse_graph_adjacency(text)

    outbound: Dict[str, List[int]] = {}
    inbound: Dict[str, List[int]] = {}
    for position, edge in enumerate(edges):
        outbound.setdefault(edge[0], []).append(position)
        inbound.setdefault(edge[2], []).append(position)

    relations = sorted({edge[1] for edge in edges})
    lines: List[str] = [
        '"""',
        "GENERATED BUILD ASSET - DO NOT EDIT MANUALLY.",
        "",
        "Walkable adjacency resolved from the `Edges out` tables of",
        f"`{SystemDocumentsBuildPolicy.INGEST_ROOT}/{entry['document_file']}`.",
        "",
        "Imported LAZILY - only when something actually walks the graph.",
        "",
        "Edge candidates are NOT here. They over-generate roughly 8x and are",
        "leads, not edges; shipping them would launder a guess into structure.",
        "",
        "Regenerate with:",
        "    python src/melder/_build_assets/_build_asset_runner.py",
        '"""',
        "",
        f'BUILT_FOR_VERSION = "{version}"',
        f"NODE_COUNT = {len(nodes)}",
        f"EDGE_COUNT = {len(edges)}",
        f"WHY_COUNT = {len(whys)}",
        f"RELATIONS = {tuple(relations)!r}",
        "",
        "# node id -> (source path, name, kind, defined line, unsemantic)",
        "NODES = {",
    ]
    for node_id in sorted(nodes):
        info = nodes[node_id]
        lines.append(
            f"    {node_id!r}: ({info['source']!r}, {info['name']!r}, "
            f"{info['kind']!r}, {info['line']!r}, {info['unsemantic']!r}),"
        )
    lines += ["}", "", "# (from, relation, to, cardinality, phase, origin)", "EDGES = ("]
    for edge in edges:
        lines.append(f"    {edge!r},")
    lines += [")", "", "# node id -> positions in EDGES", "OUTBOUND = {"]
    for node_id in sorted(outbound):
        lines.append(f"    {node_id!r}: {tuple(outbound[node_id])!r},")
    lines += ["}", "", "# node id -> positions in EDGES (reverse lookup, resolved at build time)", "INBOUND = {"]
    for node_id in sorted(inbound):
        lines.append(f"    {node_id!r}: {tuple(inbound[node_id])!r},")
    lines += ["}", ""]
    lines += [
        "",
        "# (from, to) -> the authored justification for that relationship.",
        "# Keyed by endpoints, not per edge, because the document states one",
        "# reason per pair - storing it per edge would repeat the same prose.",
        "WHY = {",
    ]
    for pair in sorted(whys):
        lines.append(f"    {pair!r}: {whys[pair]!r},")
    lines += ["}", ""]

    temporary = target.with_suffix(".py.tmp")
    temporary.write_text("\n".join(lines), encoding="utf-8")
    temporary.replace(target)
    return len(edges)


def render_from_entries(entries: Dict[str, Dict[str, object]], version: str) -> str:
    """
    Render the committed manifest from already-ingested entries.

    Contract:
        PURE and DETERMINISTIC - emitted in `READ_ORDER` with sections in
        document order, so the text does not vary between runs.

        Carries the INDEXES only. The documents live beside it as `.md` package
        data, which is what keeps this manifest small enough to import eagerly.

    Args:
        entries: The ingested entries.
        version: The melder version to stamp.

    Returns:
        str: Complete manifest module source, newline-terminated.
    """
    lines: List[str] = [
        '"""',
        "GENERATED BUILD ASSET - DO NOT EDIT MANUALLY.",
        "",
        "Indexes for melder's four package-root system documents.",
        "",
        "This module carries the INDEXES - section names or source paths mapped to",
        "line ranges, plus each document's integrity proof. The documents themselves",
        "ship as `.md` package data in `../documents/` and are sliced on demand.",
        "",
        "DOCUMENTS[name]['sections'] is an ordered tuple of (key, start, end), 1-based",
        "and inclusive on both ends, matching the Context Compass index convention.",
        "",
        "`available` is False when a pair could not be verified at build time; the",
        "entry still exists and carries `reason`, so a stale index is distinguishable",
        "from a document that was never there.",
        "",
        "Regenerate with:",
        "    python src/melder/_build_assets/_build_asset_runner.py",
        '"""',
        "",
        f'MANIFEST_VERSION = "{SystemDocumentsBuildPolicy.MANIFEST_VERSION}"',
        f'BUILT_FOR_VERSION = "{version}"',
        f'SOURCE_SHA256 = "{source_fingerprint()}"',
        f"DOCUMENT_COUNT = {len(entries)}",
        "",
        "READ_ORDER = (",
    ]
    lines.extend(f"    {name!r}," for name in SystemDocumentsBuildPolicy.READ_ORDER)
    lines.extend([")", "", "DOCUMENTS = {"])

    for name in SystemDocumentsBuildPolicy.READ_ORDER:
        entry = entries[name]
        lines.append(f"    {name!r}: {{")
        for key in ("name", "title", "summary", "source", "available", "addressing",
                    "document_file", "payload_module", "line_count", "content_sha256"):
            lines.append(f"        {key!r}: {entry[key]!r},")
        if not entry["available"]:
            lines.append(f"        'reason': {entry.get('reason', '')!r},")
        lines.append("    },")
    lines.extend(["}", ""])
    return "\n".join(lines)


def write_index(entries: Dict[str, Dict[str, object]], version: str) -> int:
    """
    Emit the transcribed index as its own generated module.

    Purpose:
        Two separations at once.

        DEDUPLICATION. `__graph_network__` and `__graph_details__` address the
        same 575 sections of `src_graph.md`. Emitting that table under each
        name wrote it twice and unmarshalled it twice - 1,331 tuples where 756
        say everything. Keyed by DOCUMENT FILE, the duplication cannot recur:
        two views of one document resolve to one table.

        DEFERRAL. The four views are built at package scope, so anything the
        manifest carries is paid by every `import melder`. The section tables
        are the bulk of it and are needed only by a caller that actually asks
        `index()` or `get()`. Splitting them out leaves the eagerly imported
        manifest holding titles, addressing, and proof - the part that answers
        "what is here" - while the ranges load on first use.

    Args:
        entries: The ingested entries.
        version: The melder version to stamp into the generated module.

    Returns:
        int: Number of distinct section tables written.
    """
    tables: Dict[str, List[Tuple[str, int, int]]] = {}
    for name in SystemDocumentsBuildPolicy.READ_ORDER:
        entry = entries[name]
        document_file = str(entry["document_file"])
        if document_file and document_file not in tables:
            tables[document_file] = list(entry["sections"])

    lines: List[str] = [
        '"""',
        "GENERATED BUILD ASSET - DO NOT EDIT MANUALLY.",
        "",
        "The INDEX. Section line ranges transcribed verbatim from each document's",
        "`*_index.md`, keyed by DOCUMENT FILE so two views of one document share",
        "one table.",
        "",
        "These ranges are NOT recomputed from the documents - Context Compass's",
        "index is the authority and this is a transcription of it. The only",
        "normalisation is stripping the markdown backticks the graph index wraps",
        "its source paths in.",
        "",
        "Imported LAZILY, on the first `index()` or `get()`. Ranges are 1-based",
        "and inclusive on both ends, exactly as the source index states them.",
        "",
        "Regenerate with:",
        "    python src/melder/_build_assets/_build_asset_runner.py",
        '"""',
        "",
        # Stamped like every other generated manifest. The version gate globs
        # `*/manifest/*.py` and requires each one to carry a stamp - an
        # unstamped module makes that gate silently incomplete.
        f'BUILT_FOR_VERSION = "{version}"',
        f"TABLE_COUNT = {len(tables)}",
        f"SECTION_COUNT = {sum(len(rows) for rows in tables.values())}",
        "",
        "SECTIONS = {",
    ]
    for document_file in sorted(tables):
        lines.append(f"    {document_file!r}: (")
        for key, start, end in tables[document_file]:
            lines.append(f"        ({key!r}, {start}, {end}),")
        lines.append("    ),")
    lines.extend(["}", ""])

    target = manifest_path().parent / "system_documents_index.py"
    temporary = target.with_suffix(".py.tmp")
    temporary.write_text("\n".join(lines), encoding="utf-8")
    temporary.replace(target)
    return len(tables)


def write_manifest(version: str) -> Tuple[pathlib.Path, int]:
    """
    Ingest, copy documents, and write the manifest atomically.

    Contract:
        Ingests ONCE and threads the result through both the document copy and
        the render. Refusals are printed rather than raised: one stale pair
        must not block the other three from shipping.

    Args:
        version: The melder version to stamp into the manifest.

    Returns:
        Tuple[pathlib.Path, int]: The written path and document count.
    """
    entries, refusals = ingest()
    for refusal in refusals:
        print(f"  REFUSED  {refusal}")

    write_index(entries, version)
    write_payloads(entries)
    write_graph_adjacency(entries, version)
    target = manifest_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(".py.tmp")
    temporary.write_text(render_from_entries(entries, version), encoding="utf-8")
    temporary.replace(target)
    return target, len(entries)


# ---------------------------------------------------------------------------
# BUILDER CONTRACT
# ---------------------------------------------------------------------------


def target_path() -> pathlib.Path:
    """
    Return the artifact path this builder owns.

    Returns:
        pathlib.Path: The committed manifest module's absolute path.
    """
    return manifest_path()


def render(version: str) -> str:
    """
    Render the artifact text for one melder version.

    Args:
        version: The melder version to stamp into the artifact.

    Returns:
        str: Complete manifest module source, newline-terminated.
    """
    entries, _ = ingest()
    return render_from_entries(entries, version)


def write(version: str) -> Tuple[pathlib.Path, int]:
    """
    Write the artifact to disk.

    Args:
        version: The melder version to stamp into the artifact.

    Returns:
        Tuple[pathlib.Path, int]: The written path and the document count.
    """
    return write_manifest(version)
