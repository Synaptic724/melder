"""
System documents: template source and committed-manifest builder.

WHAT IT OWNS
------------
The four package-root document surfaces melder publishes - `__architecture__`,
`__components__`, `__graph_network__`, `__graph_details__` - as one committed
manifest holding each document's minified JSON hardcopy.

Read order for an agent is architecture -> components -> graph network ->
graph details, and that ordering is data here (`READ_ORDER`) rather than prose,
so tooling can follow it without parsing English.

WHY THIS ASSET HAS NO CACHE
---------------------------
The other two build assets hydrate through `asset_cache` into a `.melc` bundle.
This one deliberately does not, for two reasons:

  1. There is nothing to amortise. A cache pays off when hydration costs real
     COMPUTATION - the bind guard builds a 582-element frozenset, the agent
     documentation builds four containers. A system document is already a
     string; "hydrating" it is a dict lookup.

  2. It would defeat the laziness. `melder/__init__.py` imports all four
     documents at package scope. A cache read at import would pull every
     payload into memory for the majority of processes that never ask a
     document anything - the exact cost `StaticSystemDocument` defers by
     building its line index on first read.

CURRENT STATE: TEMPLATES
------------------------
The payloads below are STRUCTURED PLACEHOLDERS, not the real documents. Each
carries the section skeleton its final content will fill, so the shape is
reviewable and the wiring is exercisable now, and populating one later is a
content change in this file rather than a plumbing change anywhere else.

The real sources are the ~1.9 MB under `context_compass/system_docs/`
(`src_architecture.md` 118 KB, `src_components.md` 282 KB, `src_graph.json`
750 KB, `readable_src_graph.json` 758 KB). They are NOT inlined yet: at that
size the decision of what actually ships in the wheel is a product call, and
`src_graph.json` in particular is a single 750 KB line that only the reader's
character budget can bound.
"""
import hashlib
import json
import pathlib
from typing import Dict, List, Tuple


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
        MARKDOWN_KEY: The hardcopy envelope's markdown key. `StaticSystemDocument`
            validates its presence at construction, so it is fixed here.
        READ_ORDER: The documents in the order an agent should read them.
        MANIFEST_VERSION: SCHEMA version of the manifest's shape, separate from
            the melder release it was built for.
    """

    BUILD_ASSETS_DIR_NAME: str = "_build_assets"
    ASSET_DIR_NAME: str = "_system_documents"
    MANIFEST_DIR_NAME: str = "manifest"
    MANIFEST_FILE_NAME: str = "system_documents_manifest.py"

    # Payloads live in their OWN modules, one per document, and the manifest
    # holds only metadata. This is not tidiness - it is the difference between
    # `import melder` costing four bytes of metadata and costing 1.9 MB.
    #
    # The manifest is imported eagerly through
    # `__init__.py -> __architecture__ -> system_documents -> manifest`. Inlining
    # the real documents there would load ALL FOUR on every process start,
    # defeating the laziness `StaticSystemDocument` exists to provide - it defers
    # INDEXING, and cannot defer a module-scope import it does not control.
    #
    # Splitting them means the loader imports one payload module the first time
    # a document's body is actually asked for, and never for the other three.
    PAYLOAD_DIR_NAME: str = "payloads"

    # Where ingested content comes from. NOT shipped in the wheel
    # (`context_compass*` is excluded), which is exactly why the builder INLINES
    # the bytes at build time rather than reading them at runtime: the source of
    # truth stays a single reviewed file in the repo, and the wheel stays
    # self-contained.
    INGEST_ROOT: str = "context_compass/system_docs"

    MARKDOWN_KEY: str = "m"

    READ_ORDER: Tuple[str, ...] = (
        "__architecture__",
        "__components__",
        "__graph_network__",
        "__graph_details__",
    )

    # 1.0.0: `{name: {"title", "summary", "source", "populated", "json"}}`.
    MANIFEST_VERSION: str = "1.0.0"


TEMPLATES: Dict[str, Dict[str, str]] = {
    "__architecture__": {
        "title": "Melder Architecture",
        "summary": (
            "C4-level system document. Boundaries, entrypoints, boot and "
            "configuration sequencing, execution lifecycle."
        ),
        "source": "context_compass/system_docs/src_architecture.md",
        "body": """# Melder Architecture

> TEMPLATE. Structure is final; content is not yet populated.
> Source of record: `context_compass/system_docs/src_architecture.md`.

Read order: architecture -> components -> graph network -> graph details.

## 1. System Boundary

What is inside melder, what is the caller's, and what is neither.

## 2. Entrypoints

`Aether()`, `Spellbook`, `conjure(...)`, `Nexus`, `Crystallizer`,
`MutationResearch` - what each one is the door to.

## 3. Boot Sequence

What `import melder` does, in order, and what it deliberately does not do.
Frames are NOT created at boot; the first Spellbook births the frame it names.

## 4. Configuration Sequencing

Which configuration must be frozen before which verb, and why activation is a
distinct step from construction.

## 5. Execution Lifecycle

bind -> conjure -> meld -> cleanup, and where each phase can refuse.

## 6. Concurrency Posture

What free-threaded 3.14t changes, which objects are shared, and which are
per-caller.
""",
    },
    "__components__": {
        "title": "Melder Components",
        "summary": (
            "Subsystem inventory. What each component owns, what it hands off "
            "to, and which are guarded kernel machinery."
        ),
        "source": "context_compass/system_docs/src_components.md",
        "body": """# Melder Components

> TEMPLATE. Structure is final; content is not yet populated.
> Source of record: `context_compass/system_docs/src_components.md`.

Each entry answers: what does it own, what does it hand off to, and may an
agent drive it directly?

## Aether

The global singleton root and the hidden substrate it boots.

## Spellbook

The binding authority. Registration, validation, and the single conjure.

## Conduit

The runtime scope. Resolution, child scopes, request scope, dynamic linking.

## Nexus / Rift

The public AR surface over the substrate: rooms, viewers, ACL, codegen.

## Crystallizer

Persistence: capture, checkpoint, restore, and the external mesh seam.

## MutationResearch

Version lanes, research sets, and derived diffs over recorded material.

## Utilities

Synchronization primitives, weak containers, caching, and the AI-native
support tools.
""",
    },
    "__graph_network__": {
        "title": "Melder Graph Network",
        "summary": (
            "The dependency graph's shape: nodes, edges, and how a resolution "
            "walk traverses it."
        ),
        "source": "context_compass/system_docs/src_graph.json",
        "body": """# Melder Graph Network

> TEMPLATE. Structure is final; content is not yet populated.
> Source of record: `context_compass/system_docs/src_graph.json`.

NOTE for whoever populates this: the source is MINIFIED - one line of roughly
750,000 characters. Line-based paging cannot bound it, so any reader over this
document must set a character budget. `readable_src_graph.json` is the
line-shaped variant of the same data.

## Node Kinds

What a node represents and what identity it carries.

## Edge Kinds

Normal DI sockets versus late-bound contract sockets.

## Traversal

How a resolution walk orders the graph, and where it can refuse.
""",
    },
    "__graph_details__": {
        "title": "Melder Graph Details",
        "summary": (
            "Per-node detail: sockets, existence, permissions, and the "
            "compiled resolution plan."
        ),
        "source": "context_compass/system_docs/readable_src_graph.json",
        "body": """# Melder Graph Details

> TEMPLATE. Structure is final; content is not yet populated.
> Source of record: `context_compass/system_docs/readable_src_graph.json`.

## Per-Node Detail

Sockets, existence, permissions, and spellframe for one node.

## Compiled Plan

What the compiler produced for a node and which strategy family claimed it.

## Diagnostics

Where to look when a node refuses to resolve.
""",
    },
}


# Documents whose real content is READY to be ingested from `INGEST_ROOT`.
#
# Per-document on purpose, not a global switch: `src_architecture.md` and
# `src_components.md` are hand-maintained prose that stabilises on a different
# schedule from the two graph documents, and `src_graph.json` in particular is a
# single 750,000-character line that only a character budget can page. Flipping
# one document on must not drag the others in before they are ready.
#
# Adding a name here is the ENTIRE population step: the builder reads the source,
# inlines it, sets `populated=True`, and the fingerprint moves so `--check`
# catches it. Nothing else changes.
READY_TO_INGEST: Tuple[str, ...] = ()


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
        `<repo>/src/melder` -> `<repo>`. Only used at BUILD time to ingest
        document sources; nothing at runtime resolves this path, because the
        content is inlined into the generated payloads.

    Returns:
        pathlib.Path: The repository root.
    """
    return package_root().parent.parent


def payload_dir() -> pathlib.Path:
    """
    Return the directory holding the generated per-document payload modules.

    Returns:
        pathlib.Path: `<asset dir>/payloads`.
    """
    return (
        package_root()
        / SystemDocumentsBuildPolicy.BUILD_ASSETS_DIR_NAME
        / SystemDocumentsBuildPolicy.ASSET_DIR_NAME
        / SystemDocumentsBuildPolicy.PAYLOAD_DIR_NAME
    )


def payload_module_name(document_name: str) -> str:
    """
    Return the module basename for one document's payload.

    Args:
        document_name: A dunder-shaped document name, e.g. `__architecture__`.

    Returns:
        str: Payload module basename, e.g. `architecture_payload`.
    """
    return f"{document_name.strip('_')}_payload"


def resolve_body(document_name: str) -> Tuple[str, bool]:
    """
    Return one document's body and whether it is real content or a template.

    Contract:
        A document listed in `READY_TO_INGEST` is read from its source under
        `INGEST_ROOT` and marked populated. Anything else - including a document
        listed as ready whose source file is ABSENT - falls back to its template
        and is marked NOT populated.

        The missing-source case falls back rather than raising on purpose: a
        trimmed checkout or a wheel build from an sdist has no `context_compass/`
        at all, and refusing to build there would make the package unbuildable
        outside a full clone. The `populated` flag carries the truth instead, so
        a caller can always tell what it actually got.

    Args:
        document_name: The document to resolve.

    Returns:
        Tuple[str, bool]: The body text and its populated flag.
    """
    template = TEMPLATES[document_name]
    if document_name not in READY_TO_INGEST:
        return template["body"], False
    source = repository_root() / template["source"]
    if not source.is_file():
        return template["body"], False
    return source.read_text(encoding="utf-8"), True


def manifest_path() -> pathlib.Path:
    """
    Return the full path of the committed manifest module.

    Returns:
        pathlib.Path: The generated manifest module's absolute path.
    """
    return (
        package_root()
        / SystemDocumentsBuildPolicy.BUILD_ASSETS_DIR_NAME
        / SystemDocumentsBuildPolicy.ASSET_DIR_NAME
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


def source_fingerprint() -> str:
    """
    SHA256 over the document payloads this builder would emit.

    Contract:
        Hashes the TEMPLATES in this file rather than any external source,
        because the templates ARE the input - nothing under
        `context_compass/system_docs/` is read yet. When a real document is
        inlined, its text lands in `TEMPLATES` and the digest moves with it, so
        `--check` keeps working unchanged.

        Deliberately hashes the rendered payload rather than the file, so a
        comment or docstring edit in this builder does not force a rebuild of
        four documents that did not change.

    Returns:
        str: Hex digest over every document payload, in read order.
    """
    digest = hashlib.sha256()
    for name in SystemDocumentsBuildPolicy.READ_ORDER:
        template = TEMPLATES[name]
        digest.update(name.encode("utf-8"))
        for key in ("title", "summary", "source", "body"):
            digest.update(template[key].encode("utf-8"))
    return digest.hexdigest()


def build_documents() -> Dict[str, Dict[str, object]]:
    """
    Assemble every document entry, hardcopy envelope included.

    Contract:
        The envelope is minified JSON carrying the markdown under key `m`,
        which is what `StaticSystemDocument` validates at construction. Building
        it HERE rather than in the loader means a malformed envelope is a build
        failure, not an import-time crash in a user's process.

        `populated` is False while the body is a template. It is data, not
        prose, so a caller can tell placeholder from real content without
        pattern-matching the text - the distinction the previous
        "CURRENT STATE: the payload is a PLACEHOLDER" docstring could only
        state to human readers.

    Returns:
        Dict[str, Dict[str, object]]: Document name -> entry.

    Raises:
        ValueError: When a template is missing a required field.
    """
    documents: Dict[str, Dict[str, object]] = {}
    for name in SystemDocumentsBuildPolicy.READ_ORDER:
        template = TEMPLATES[name]
        for key in ("title", "summary", "source", "body"):
            if not template.get(key):
                raise ValueError(f"document {name!r} is missing template field {key!r}")
        body = template["body"]
        documents[name] = {
            "title": template["title"],
            "summary": template["summary"],
            "source": template["source"],
            "populated": False,
            "line_count": len(body.splitlines()) or 1,
            "char_count": len(body),
            "json": json.dumps(
                {SystemDocumentsBuildPolicy.MARKDOWN_KEY: body},
                separators=(",", ":"),
            ),
        }
    return documents


def render_from_documents(documents: Dict[str, Dict[str, object]], version: str) -> str:
    """
    Render the committed manifest module from already-built documents.

    Contract:
        PURE and DETERMINISTIC - emitted in `READ_ORDER`, not dict order, so the
        text does not vary between runs.

    Args:
        documents: The assembled document entries.
        version: The melder version to stamp.

    Returns:
        str: Complete manifest module source, newline-terminated.
    """
    lines: List[str] = [
        '"""',
        "GENERATED BUILD ASSET - DO NOT EDIT MANUALLY.",
        "",
        "The four package-root system documents melder publishes, as minified",
        "JSON hardcopy envelopes. Consumed by",
        "`_build_assets/_system_documents/system_documents.py`, which builds one",
        "`StaticSystemDocument` per entry.",
        "",
        "`POPULATED` reports which documents carry real content and which are",
        "still structured templates. Check it rather than pattern-matching prose.",
        "",
        "There is NO .melc cache for this asset - see the builder for why.",
        "",
        "Regenerate with:",
        "    python src/melder/_build_assets/_build_asset_runner.py",
        '"""',
        "",
        f'MANIFEST_VERSION = "{SystemDocumentsBuildPolicy.MANIFEST_VERSION}"',
        f'BUILT_FOR_VERSION = "{version}"',
        f'SOURCE_SHA256 = "{source_fingerprint()}"',
        f"DOCUMENT_COUNT = {len(documents)}",
        "",
        "READ_ORDER = (",
    ]
    lines.extend(f"    {name!r}," for name in SystemDocumentsBuildPolicy.READ_ORDER)
    lines.extend([")", ""])

    lines.append("POPULATED = {")
    for name in SystemDocumentsBuildPolicy.READ_ORDER:
        lines.append(f"    {name!r}: {documents[name]['populated']!r},")
    lines.extend(["}", ""])

    lines.append("DOCUMENTS = {")
    for name in SystemDocumentsBuildPolicy.READ_ORDER:
        entry = documents[name]
        lines.append(f"    {name!r}: {{")
        for key in ("title", "summary", "source", "populated", "line_count", "char_count"):
            lines.append(f"        {key!r}: {entry[key]!r},")
        lines.append(f"        'json': {entry['json']!r},")
        lines.append("    },")
    lines.extend(["}", ""])
    return "\n".join(lines)


def write_manifest(version: str) -> Tuple[pathlib.Path, int]:
    """
    Build every document and write the committed manifest atomically.

    Contract:
        Builds ONCE and threads the result through, rather than rendering and
        then re-deriving the count from a second build.

    Args:
        version: The melder version to stamp into the manifest.

    Returns:
        Tuple[pathlib.Path, int]: The written path and document count.
    """
    documents = build_documents()
    target = manifest_path()
    target.parent.mkdir(parents=True, exist_ok=True)

    temporary = target.with_suffix(".py.tmp")
    temporary.write_text(render_from_documents(documents, version), encoding="utf-8")
    temporary.replace(target)
    return target, len(documents)


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
    return render_from_documents(build_documents(), version)


def write(version: str) -> Tuple[pathlib.Path, int]:
    """
    Write the artifact to disk.

    Args:
        version: The melder version to stamp into the artifact.

    Returns:
        Tuple[pathlib.Path, int]: The written path and the document count.
    """
    return write_manifest(version)
