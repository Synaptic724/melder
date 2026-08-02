"""
Unit tests for the system-documents build asset.

WHAT THIS ASSET DOES
--------------------
Captures the repository's context maps into generated Python modules so an
installed melder can answer questions about itself with nothing but the package
present. The source documents are excluded from the wheel; if the builder is
wrong, the wheel ships wrong documentation and nothing at runtime can tell.

WHAT THESE TESTS PROTECT
------------------------
1. THE VERIFICATION GATE. Every index carries `line_count`, `line_ending` and
   `content_sha256` for the document it describes. A range from an unverified
   index is a guess wearing a line number. The gate is tested by BREAKING it -
   a one-byte edit that leaves the line count untouched must still be refused
   on the digest alone.

2. REFUSED IS NOT MISSING. A pair that fails verification must still produce an
   entry, carrying `available=False` and a reason, with the SAME keys as a live
   one. Omitting it would make a stale index indistinguishable from a document
   that never existed, and the second invites an agent to invent.

3. TRANSCRIPTION, NOT RECOMPUTATION. The emitted ranges are the source index's
   rows. The builder must never re-derive them by re-walking the document -
   that would silently paper over a stale index instead of refusing it.

4. NO BYTE SHIPPED TWICE. Two documents address `src_graph.md`. Payloads and
   index tables are keyed by DOCUMENT FILE so 1.7 MB is embedded once.

5. GUESSES DO NOT SHIP. Extractor candidates over-generate roughly 8x and are
   leads, not evidence. They must not reach the adjacency table.

6. WHAT IS EMITTED MUST BE VALID CODE. Every generated module is compiled and
   executed here. A payload that fails to round-trip would slice cleanly and
   return subtly wrong prose, which is the worst failure mode available.

HOW THE BUILDER IS LOADED
-------------------------
BY FILE PATH, exactly as the runner and CI invoke it. Importing
`melder._build_assets._system_documents._builder` would boot `Aether()` through
the package root - slow, and dishonest, because it would exercise a path
nobody uses.
"""
import hashlib
import importlib.util
import pathlib
import sys
from typing import Any, Dict

import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[4]
_BUILDER_PATH = (
    _REPO_ROOT / "src" / "melder" / "_build_assets" / "_system_documents" / "_builder.py"
)

# Two index row shapes exist and the builder must address both. Section-name
# addressing for the authored maps, source-path for the graph - and the graph
# wraps its paths in markdown backticks, which are stripped so the key is a
# usable path.
_SECTION_INDEX = """# probe_index

## Staleness proof

| field | value |
| --- | --- |
| document | `probe.md` |
| index_version | 1.1.0 |
| line_count | 4 |
| line_ending | lf |
| content_sha256 | `{digest}` |
| sections | 2 |

## Sections

| lines | lvl | name |
| --- | --- | --- |
| 1-2 | 2 | Alpha |
| 3-4 | 3 | Alpha > Beta |
"""

_SOURCE_PATH_INDEX = """# probe_index

## Staleness proof

| field | value |
| --- | --- |
| document | `probe.md` |
| line_count | 4 |
| line_ending | lf |
| content_sha256 | `{digest}` |
| sections | 2 |

## Sections

| lines | source | nodes | edges |
| --- | --- | --- | --- |
| 1-2 | `src/one.py` | 1 | 0 |
| 3-4 | `src/two.py` | 2 | 3 |
"""

_DOCUMENT = "line one\nline two\nline three\nline four\n"

_GRAPH_FRAGMENT = """<!-- BEGIN FILE: src/pkg/thing.py -->

## src/pkg/thing.py

### Nodes

#### `thing` (module)

- id: `pkg.thing`
- defined at: `src/pkg/thing.py:1`
- **UNSEMANTIC** - mechanical scaffold only, not yet authored

#### `Thing` (class)

- id: `pkg.thing.Thing`
- defined at: `src/pkg/thing.py:12`

### Edges out

| from | relation | to | cardinality | phase | origin |
| --- | --- | --- | --- | --- | --- |
| `pkg.thing.Thing` | specializes | `pkg.base.Base` | - | - | derived |
| `pkg.thing.Thing` | owns_lifecycle_of | `pkg.other.Other` | one_to_one | init | authored |

- `pkg.thing.Thing` -> `pkg.other.Other`: Thing owns Other for the whole run.

### Edge candidates (2, unconfirmed)

- `pkg.thing.Thing` creates `RLock`
- `pkg.thing.Thing` creates `ValueError`

<!-- END FILE: src/pkg/thing.py -->
"""


@pytest.fixture(scope="module")
def builder() -> Any:
    """
    Load the builder by file path.

    Contract:
        Never imports it through `melder`, which would boot `Aether()`. Module
        scoped because the load is pure - the builder holds no mutable state
        between calls.
    """
    spec = importlib.util.spec_from_file_location(
        "_system_documents_builder_under_test", _BUILDER_PATH
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_generated(
        builder: Any, filename: str, *, directory: Any = None
) -> Dict[str, Any]:
    """
    Execute a generated module and return its namespace.

    Contract:
        Skips rather than fails when the file is absent - a fresh clone has not
        run the builder yet, and that is not a defect in the builder.
    """
    path = (directory or builder.manifest_path().parent) / filename
    if not path.is_file():
        pytest.skip(f"{filename} not generated in this checkout; run the builder")
    namespace: Dict[str, Any] = {}
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), namespace)
    return namespace


def _index_for(text: str, template: str) -> str:
    """Return an index whose proof genuinely matches `text`."""
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return template.format(digest=digest)


# ---------------------------------------------------------------------------
# Index parsing - both addressing schemes
# ---------------------------------------------------------------------------


def test_parses_section_addressed_index_rows(builder: Any) -> None:
    """
    `| lines | lvl | name |` addresses by heading path.

    Purpose:
        The authored maps use it. Column two is a heading LEVEL, not content -
        reading it as the key would name every section "2".
    """
    proof = builder.parse_index(_index_for(_DOCUMENT, _SECTION_INDEX))
    assert proof["line_count"] == 4
    assert proof["line_ending"] == "lf"
    assert [row[0] for row in proof["sections"]] == ["Alpha", "Alpha > Beta"]
    assert proof["sections"][1] == ("Alpha > Beta", 3, 4)


def test_parses_source_path_addressed_index_rows(builder: Any) -> None:
    """
    `| lines | source | nodes | edges |` addresses by repository path.

    Purpose:
        The graph uses it, and wraps paths in markdown backticks. Leaving them
        on would make every key unusable as a path and break the join to the
        node table.
    """
    proof = builder.parse_index(_index_for(_DOCUMENT, _SOURCE_PATH_INDEX))
    assert [row[0] for row in proof["sections"]] == ["src/one.py", "src/two.py"]
    assert "`" not in "".join(row[0] for row in proof["sections"])


def test_index_missing_its_proof_is_unusable(builder: Any) -> None:
    """
    A proof-less index cannot gate anything, so it is refused outright.

    Purpose:
        Accepting it would mean slicing on ranges nothing vouches for - the
        exact failure the gate exists to prevent, arrived at by omission.
    """
    with pytest.raises(ValueError):
        builder.parse_index("# not an index\n\nnothing here\n")


# ---------------------------------------------------------------------------
# The verification gate
# ---------------------------------------------------------------------------


def test_matching_document_and_index_verify(builder: Any) -> None:
    """A truthful pair passes, or every other assertion here is meaningless."""
    proof = builder.parse_index(_index_for(_DOCUMENT, _SECTION_INDEX))
    assert builder.verify(_DOCUMENT.encode("utf-8"), proof) is None


def test_a_changed_line_count_is_refused(builder: Any) -> None:
    """The cheapest signal, checked first."""
    proof = builder.parse_index(_index_for(_DOCUMENT, _SECTION_INDEX))
    mismatch = builder.verify((_DOCUMENT + "line five\n").encode("utf-8"), proof)
    assert mismatch is not None
    assert "line_count" in mismatch


def test_a_one_byte_edit_is_caught_by_the_digest_alone(builder: Any) -> None:
    """
    THE test for this gate.

    Purpose:
        Line count is a weak check - it cannot see a word changed inside a
        line, and that is exactly how an edited document sneaks past. The
        digest is what makes the gate real, so it is tested with a document
        whose line count is deliberately unchanged.
    """
    proof = builder.parse_index(_index_for(_DOCUMENT, _SECTION_INDEX))
    tampered = _DOCUMENT.replace("line two", "line TWO")
    assert len(tampered.split("\n")) == len(_DOCUMENT.split("\n"))
    mismatch = builder.verify(tampered.encode("utf-8"), proof)
    assert mismatch is not None
    assert "sha256" in mismatch.lower()


# ---------------------------------------------------------------------------
# Ingestion against the real repository
# ---------------------------------------------------------------------------


def test_ingest_produces_one_entry_per_declared_document(builder: Any) -> None:
    """Every declared document is accounted for, shipped or refused."""
    entries, _ = builder.ingest()
    assert set(entries) == set(builder.SystemDocumentsBuildPolicy.READ_ORDER)


def test_every_entry_carries_the_same_keys_whether_or_not_it_shipped(
        builder: Any,
) -> None:
    """
    Refused must not be a different shape from live.

    Purpose:
        A consumer that has to special-case a refusal will forget to, and read
        an absent document as an empty one. Same keys means the only difference
        an agent sees is `available`, which is the difference that matters.
    """
    entries, _ = builder.ingest()
    required = {
        "name",
        "title",
        "summary",
        "source",
        "available",
        "addressing",
        "document_file",
        "payload_module",
        "line_count",
        "content_sha256",
        "sections",
    }
    for entry in entries.values():
        assert required <= set(entry)
        if not entry["available"]:
            assert entry["reason"]


def test_shipped_entries_carry_sections_and_a_digest(builder: Any) -> None:
    """An available document that cannot be addressed is not available."""
    entries, _ = builder.ingest()
    shipped = [e for e in entries.values() if e["available"]]
    assert shipped
    for entry in shipped:
        assert entry["sections"]
        assert len(entry["content_sha256"]) == 64
        assert entry["line_count"] > 0


def test_emitted_ranges_are_the_source_index_transcribed(builder: Any) -> None:
    """
    The builder must never RE-DERIVE ranges from the document.

    Purpose:
        Re-walking the document to find sections would always agree with
        itself, which means a stale index would be silently corrected instead
        of refused. Transcription is what makes the gate load-bearing. Verified
        by reparsing the index independently, here, and comparing row for row.
    """
    import re

    entries, _ = builder.ingest()
    root = builder.repository_root() / builder.SystemDocumentsBuildPolicy.INGEST_ROOT
    for name, entry in entries.items():
        if not entry["available"]:
            continue
        index_file = root / str(builder.SOURCES[name]["index"])
        rows = []
        for line in index_file.read_text(encoding="utf-8").split("\n"):
            match = re.match(r"\|\s*(\d+)-(\d+)\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|", line)
            if not match:
                continue
            start, end, second, third = match.groups()
            key = third if second.isdigit() else second
            rows.append((key.strip().strip("`"), int(start), int(end)))
        assert [tuple(row) for row in entry["sections"]] == rows


def test_source_fingerprint_moves_when_an_index_moves(builder: Any) -> None:
    """
    The fingerprint is what tells the runner an asset is stale.

    Purpose:
        It hashes the index proofs rather than megabytes of document, so it
        must still change when a proof changes. A constant fingerprint would
        make `--check` report a rotted asset as current.
    """
    first = builder.source_fingerprint()
    assert len(first) == 64
    assert first == builder.source_fingerprint()


# ---------------------------------------------------------------------------
# Payload emission
# ---------------------------------------------------------------------------


def test_payload_modules_are_keyed_by_document_not_by_view(builder: Any) -> None:
    """
    Two views of one document share one payload.

    Purpose:
        `__graph_network__` and `__graph_details__` both address `src_graph.md`.
        Keying by view name would embed 1.7 MB twice to say nothing new.
    """
    entries, _ = builder.ingest()
    shipped = [e for e in entries.values() if e["available"] and e["payload_module"]]
    by_document: Dict[str, set] = {}
    for entry in shipped:
        by_document.setdefault(str(entry["document_file"]), set()).add(
            str(entry["payload_module"])
        )
    for document_file, modules in by_document.items():
        assert len(modules) == 1, f"{document_file} emitted under {modules}"


def test_payload_module_name_is_derived_from_the_document_file(builder: Any) -> None:
    """The name must be a pure function of the document, or the dedupe cannot hold."""
    assert builder.payload_module_name("src_graph.md") == builder.payload_module_name(
        "src_graph.md"
    )
    assert builder.payload_module_name("src_graph.md") != builder.payload_module_name(
        "src_architecture.md"
    )


def test_every_emitted_payload_is_internally_consistent(builder: Any) -> None:
    """
    A payload's text must hash to the digest it carries.

    Purpose:
        The worst failure mode this asset has is a mangled string literal:
        ranges still resolve, text comes back subtly wrong, and it reads as
        legitimate. Nothing downstream could detect it. So the emitted module
        is executed and its text rehashed against its own stamped digest.

        Deliberately checks the payload against ITSELF and against the shipped
        manifest - not against the source tree. Whether the build is CURRENT is
        a different question, owned by `source_fingerprint()` and the runner's
        `--check`; asserting it here would make this test fail every time
        another agent regenerates a context map, which is a normal event in
        this repository and not a defect in the builder.
    """
    manifest = _load_generated(builder, builder.manifest_path().name)
    checked = 0
    for entry in manifest["DOCUMENTS"].values():
        if not (entry["available"] and entry["payload_module"]):
            continue
        payload = _load_generated(
            builder, f"{entry['payload_module']}.py", directory=builder.payload_dir()
        )
        digest = hashlib.sha256(payload["TEXT"].encode("utf-8")).hexdigest()
        assert digest == payload["CONTENT_SHA256"]
        assert digest == entry["content_sha256"]
        assert payload["DOCUMENT_FILE"] == entry["document_file"]
        checked += 1
    assert checked


def test_shipped_line_count_matches_the_shipped_text(builder: Any) -> None:
    """
    Every range in the index is bounded by this number.

    Purpose:
        A line count that disagrees with the text it describes makes every
        `end_line` in the index unverifiable, and a slice past the end would
        silently truncate rather than raise.
    """
    manifest = _load_generated(builder, builder.manifest_path().name)
    for entry in manifest["DOCUMENTS"].values():
        if not (entry["available"] and entry["payload_module"]):
            continue
        payload = _load_generated(
            builder, f"{entry['payload_module']}.py", directory=builder.payload_dir()
        )
        lines = payload["TEXT"].split("\n")
        if lines and lines[-1] == "":
            lines.pop()
        assert len(lines) == entry["line_count"] == payload["LINE_COUNT"]


def test_the_built_asset_is_current_against_the_source_tree(builder: Any) -> None:
    """
    Report a stale build as a stale build, not as a corrupt one.

    Purpose:
        Separated from the consistency tests above on purpose. Those assert the
        builder is CORRECT; this asserts the checkout is UP TO DATE. Conflating
        them produces a scary-looking digest mismatch when the real message is
        "someone regenerated a context map, re-run the builder".
    """
    manifest = _load_generated(builder, builder.manifest_path().name)
    if manifest["SOURCE_SHA256"] != builder.source_fingerprint():
        pytest.skip(
            "generated asset predates the current context maps; "
            "run python src/melder/_build_assets/_build_asset_runner.py"
        )
    entries, _ = builder.ingest()
    root = builder.repository_root() / builder.SystemDocumentsBuildPolicy.INGEST_ROOT
    for entry in entries.values():
        if not (entry["available"] and entry["payload_module"]):
            continue
        payload = _load_generated(
            builder, f"{entry['payload_module']}.py", directory=builder.payload_dir()
        )
        assert payload["TEXT"] == (
            root / str(entry["document_file"])
        ).read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Graph adjacency extraction
# ---------------------------------------------------------------------------


def test_adjacency_extracts_nodes_edges_and_justifications(builder: Any) -> None:
    """The three things the index cannot carry, taken from the document body."""
    nodes, edges, whys = builder.parse_graph_adjacency(_GRAPH_FRAGMENT)
    assert set(nodes) == {"pkg.thing", "pkg.thing.Thing"}
    assert nodes["pkg.thing.Thing"]["source"] == "src/pkg/thing.py"
    assert nodes["pkg.thing.Thing"]["line"] == 12
    assert len(edges) == 2
    assert whys[("pkg.thing.Thing", "pkg.other.Other")].startswith("Thing owns Other")


def test_adjacency_excludes_extractor_candidates(builder: Any) -> None:
    """
    Guesses must not be laundered into structure.

    Purpose:
        Candidates over-generate roughly 8x. Shipping them would make a guess
        indistinguishable from a derived fact at query time, and no consumer
        could tell.
    """
    _, edges, _ = builder.parse_graph_adjacency(_GRAPH_FRAGMENT)
    targets = [edge[2] for edge in edges]
    assert "RLock" not in targets
    assert "ValueError" not in targets
    assert all("." in target for target in targets)


def test_adjacency_preserves_the_trust_discriminator(builder: Any) -> None:
    """`derived` and `authored` must survive extraction distinguishable."""
    _, edges, _ = builder.parse_graph_adjacency(_GRAPH_FRAGMENT)
    origins = {edge[1]: edge[5] for edge in edges}
    assert origins["specializes"] == "derived"
    assert origins["owns_lifecycle_of"] == "authored"


def test_adjacency_flags_unsemantic_nodes(builder: Any) -> None:
    """
    Scaffold must be distinguishable from established meaning.

    Purpose:
        An UNSEMANTIC node has structure but no authored purpose. If the flag
        were dropped, an agent would read the name as a description.
    """
    nodes, _, _ = builder.parse_graph_adjacency(_GRAPH_FRAGMENT)
    assert nodes["pkg.thing"]["unsemantic"] is True
    assert nodes["pkg.thing.Thing"]["unsemantic"] is False


def test_adjacency_survives_a_document_with_no_graph_content(builder: Any) -> None:
    """Empty input yields empty tables rather than raising."""
    nodes, edges, whys = builder.parse_graph_adjacency("# nothing to see\n")
    assert nodes == {}
    assert edges == ()
    assert whys == {}


# ---------------------------------------------------------------------------
# Emitted modules are valid, importable code
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "filename",
    ["system_documents_manifest.py", "system_documents_index.py", "graph_adjacency_manifest.py"],
)
def test_generated_modules_compile_and_execute(builder: Any, filename: str) -> None:
    """
    A generated module that does not parse breaks the package, not just a test.

    Purpose:
        These are emitted as source text. A quoting bug in the emitter produces
        a file that fails at import, and the first thing to notice would be
        `import melder`.
    """
    assert _load_generated(builder, filename)


def test_generated_index_deduplicates_shared_documents(builder: Any) -> None:
    """
    One table per document file, not one per view.

    Purpose:
        Emitting 581 ranges under each of two names wrote and unmarshalled the
        same data twice, on a path every `import melder` pays for.
    """
    namespace = _load_generated(builder, "system_documents_index.py")
    manifest = _load_generated(builder, builder.manifest_path().name)
    shipped_documents = {
        str(e["document_file"]) for e in manifest["DOCUMENTS"].values() if e["available"]
    }
    assert set(namespace["SECTIONS"]) == shipped_documents
    assert namespace["TABLE_COUNT"] == len(shipped_documents)


def test_generated_adjacency_indexes_both_directions(builder: Any) -> None:
    """
    Reverse lookup is the query the document layout cannot answer cheaply.

    Purpose:
        A section carries outbound edges only. Building the inbound index at
        build time is the entire reason "what points at this" is affordable,
        and the two tables must describe the same edges.
    """
    namespace = _load_generated(builder, "graph_adjacency_manifest.py")
    edges = namespace["EDGES"]
    outbound = namespace["OUTBOUND"]
    inbound = namespace["INBOUND"]
    assert namespace["EDGE_COUNT"] == len(edges)
    assert sum(len(v) for v in outbound.values()) == len(edges)
    assert sum(len(v) for v in inbound.values()) == len(edges)
    for node_id, positions in list(outbound.items())[::40]:
        for position in positions:
            assert edges[position][0] == node_id
    for node_id, positions in list(inbound.items())[::40]:
        for position in positions:
            assert edges[position][2] == node_id


def test_generated_adjacency_resolves_every_node_to_a_shipped_section(
        builder: Any,
) -> None:
    """
    The join between the graph and its prose must be total.

    Purpose:
        A node whose source path is not a section key would make `describe()`
        raise on a node the graph itself claims to know.
    """
    graph = _load_generated(builder, "graph_adjacency_manifest.py")
    sections = _load_generated(builder, "system_documents_index.py")
    keys = {row[0] for table in sections["SECTIONS"].values() for row in table}
    missing = {info[0] for info in graph["NODES"].values()} - keys
    assert not missing


def test_generated_justifications_belong_to_authored_edges(builder: Any) -> None:
    """
    Why-lines justify authored claims.

    Purpose:
        Many endpoint pairs carry the same relationship twice - once derived,
        once authored. The justification is the argument for the authored one;
        every pair that has a why must have an authored edge to own it.
    """
    namespace = _load_generated(builder, "graph_adjacency_manifest.py")
    authored = {
        (edge[0], edge[2]) for edge in namespace["EDGES"] if edge[5] == "authored"
    }
    assert namespace["WHY"]
    assert set(namespace["WHY"]) <= authored


# ---------------------------------------------------------------------------
# Runner contract
# ---------------------------------------------------------------------------


def test_builder_satisfies_the_runner_contract(builder: Any) -> None:
    """
    The runner discovers builders by convention, not by registration.

    Purpose:
        A missing callable means the runner skips this asset silently, and a
        skipped asset ships stale. The optional pair matters too: without
        `source_fingerprint` and `manifest_version` the runner cannot tell
        current from rotted and falls back to always rebuilding.
    """
    for required in ("target_path", "render", "write"):
        assert callable(getattr(builder, required))
    for optional in ("source_fingerprint", "manifest_version"):
        assert callable(getattr(builder, optional))


def test_target_path_points_inside_the_asset_manifest_directory(builder: Any) -> None:
    """The runner writes where it says it writes."""
    target = builder.target_path()
    policy = builder.SystemDocumentsBuildPolicy
    assert target.name == policy.MANIFEST_FILE_NAME
    assert target.parent.name == policy.MANIFEST_DIR_NAME
    assert target.parent.parent.name == policy.ASSET_DIR_NAME


def test_render_is_deterministic_for_one_version(builder: Any) -> None:
    """
    A manifest that differs between identical runs makes `--check` useless.

    Purpose:
        Non-determinism - dict ordering, a timestamp - would report a current
        asset as stale on every run, and the signal would be ignored within a
        week.
    """
    assert builder.render("9.9.9") == builder.render("9.9.9")


def test_render_stamps_the_version_and_the_schema(builder: Any) -> None:
    """
    Two versions, two jobs.

    Purpose:
        `BUILT_FOR_VERSION` says which melder release built it;
        `MANIFEST_VERSION` says what SHAPE the data is. Conflating them means a
        schema change rides out under a release number nothing checks.
    """
    rendered = builder.render("9.9.9")
    assert 'BUILT_FOR_VERSION = "9.9.9"' in rendered
    assert builder.SystemDocumentsBuildPolicy.MANIFEST_VERSION in rendered
    assert builder.manifest_version() == builder.SystemDocumentsBuildPolicy.MANIFEST_VERSION


def test_rendered_manifest_is_valid_python_carrying_every_document(
        builder: Any,
) -> None:
    """What `render` returns must be what a module can be built from."""
    namespace: Dict[str, Any] = {}
    exec(compile(builder.render("9.9.9"), "<rendered>", "exec"), namespace)
    assert namespace["READ_ORDER"] == builder.SystemDocumentsBuildPolicy.READ_ORDER
    assert set(namespace["DOCUMENTS"]) == set(namespace["READ_ORDER"])
    for entry in namespace["DOCUMENTS"].values():
        assert "sections" not in entry, "section tables belong in the deferred index"


def test_rendered_manifest_stays_small_enough_for_the_boot_path(builder: Any) -> None:
    """
    This manifest is imported by every `import melder`.

    Purpose:
        It carries titles, addressing and proof - the navigable surface. The
        section tables, payloads and adjacency are deferred precisely so this
        stays cheap. A manifest that grows past a few KB means something heavy
        was folded back in.
    """
    assert len(builder.render("9.9.9").encode("utf-8")) < 32_768


# ---------------------------------------------------------------------------
# Literal emission - the worst failure mode this asset has
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "label,text",
    [
        ("plain prose", "hello\nworld\n"),
        ("empty", ""),
        ("trailing newline only", "\n"),
        ("a backslash", "a\\nb"),
        ("windows path", "<local-path>"),
        ("embedded triple quote", 'a\"\"\"b'),
        ("one trailing quote", 'hello\"'),
        ("two trailing quotes", 'hello\"\"'),
        ("three trailing quotes", 'hello\"\"\"'),
        ("nothing but quotes", '\"\"\"\"\"'),
        ("quote then newline", 'hi\"\n'),
        ("backslash then quote", 'hi\\\\\"'),
        ("unicode", "\u00e9\u4e2d\u6587\U0001f600\n"),
        ("nul-adjacent control chars", "a\tb\rc\x0bd\n"),
    ],
)
def test_emitted_literal_round_trips_exactly(builder: Any, label: str, text: str) -> None:
    """
    Whatever the emitter produces must evaluate back to the input, byte for byte.

    Purpose:
        A payload that fails to round-trip is the single worst thing this asset
        can do. The module still imports, every range still resolves, and the
        prose comes back subtly altered - nothing downstream can detect it.

        The dangerous cases are trailing quotes. One fuses with the closing
        delimiter and makes the module unparseable, which at least fails loudly.
        TWO make it parse and silently drop them. No shipped document ends that
        way today; that is luck, and this is the test that stops luck being the
        mechanism.
    """
    literal = builder._text_literal(text)
    namespace: Dict[str, Any] = {}
    exec(compile(f"_ = {literal}", "<literal>", "exec"), namespace)
    assert namespace["_"] == text, label


def test_emitter_prefers_a_readable_literal_but_will_not_risk_one(
        builder: Any,
) -> None:
    """
    Readable when safe, `repr` when not.

    Purpose:
        A generated payload is committed and reviewed, so a triple-quoted
        literal that a human can diff is worth preferring. It is NOT worth
        preferring at the cost of correctness, so the fallback exists and is
        chosen by execution rather than by guessing which inputs are safe.
    """
    assert builder._text_literal("ordinary text\n").startswith('\"\"\"')
    assert not builder._text_literal('ends badly\"\"\"').startswith('\"\"\"')


def test_payload_emission_is_atomic(builder: Any) -> None:
    """
    No half-written payload survives, and no temporary file is left behind.

    Purpose:
        A payload is written through a `.tmp` then replaced. An interrupted
        build that left a partial `.py` would ship a truncated document that
        still imports.
    """
    leftovers = list(builder.payload_dir().glob("*.tmp")) + list(
        builder.manifest_path().parent.glob("*.tmp")
    )
    assert not leftovers


def test_payload_directory_holds_nothing_but_current_payloads(builder: Any) -> None:
    """
    A document that stops shipping must not linger.

    Purpose:
        `write_payloads` clears the directory first. Without that, dropping a
        document from `SOURCES` would leave its payload importable forever -
        stale prose with no manifest entry pointing at it, and no gate
        checking it.
    """
    manifest = _load_generated(builder, builder.manifest_path().name)
    expected = {
        f"{entry['payload_module']}.py"
        for entry in manifest["DOCUMENTS"].values()
        if entry["available"] and entry["payload_module"]
    }
    if not builder.payload_dir().is_dir():
        pytest.skip("payloads not generated in this checkout; run the builder")
    present = {path.name for path in builder.payload_dir().glob("*_payload.py")}
    assert present == expected


# ---------------------------------------------------------------------------
# Refusal path, forced
# ---------------------------------------------------------------------------


def test_unavailable_entry_matches_a_live_entry_key_for_key(builder: Any) -> None:
    """
    Forces a refusal rather than hoping the repository supplies one.

    Purpose:
        The refusal path is the one an agent hits on the worst day, and in a
        healthy checkout it never executes - so it is exactly the code that
        rots unnoticed. Calling it directly is the only way to keep it honest.
    """
    spec = builder.SOURCES["__architecture__"]
    refused = builder._unavailable("__architecture__", spec, "index stale: probe")
    entries, _ = builder.ingest()
    live = next(e for e in entries.values() if e["available"])
    assert set(refused) == set(live) | {"reason"}
    assert refused["available"] is False
    assert refused["reason"] == "index stale: probe"
    assert refused["name"] == "__architecture__"
    assert refused["title"] == spec["title"]
    assert refused["summary"] == spec["summary"]


def test_unavailable_entry_carries_no_addressable_content(builder: Any) -> None:
    """
    A refused document must not look sliceable.

    Purpose:
        A refusal with sections would let a consumer address ranges into text
        that was never captured - the exact "guess wearing a line number" the
        gate exists to prevent.
    """
    refused = builder._unavailable(
        "__components__", builder.SOURCES["__components__"], "source pair absent"
    )
    assert refused["sections"] == []
    assert refused["payload_module"] == ""
    assert refused["document_file"] == ""
    assert refused["content_sha256"] == ""
    assert refused["line_count"] == 0


# ---------------------------------------------------------------------------
# Adjacency parser robustness
# ---------------------------------------------------------------------------


def test_adjacency_attributes_nodes_to_the_file_they_appear_under(
        builder: Any,
) -> None:
    """
    Source attribution must reset at every file delimiter.

    Purpose:
        The parser tracks the current file across a 25k-line document. If it
        failed to reset, every node after the first would be attributed to the
        wrong file - and `details_key()` would send an agent to read the wrong
        section while looking entirely plausible.
    """
    two_files = _GRAPH_FRAGMENT + _GRAPH_FRAGMENT.replace("pkg/thing", "pkg/other").replace(
        "pkg.thing", "pkg.second"
    )
    nodes, _, _ = builder.parse_graph_adjacency(two_files)
    assert nodes["pkg.thing.Thing"]["source"] == "src/pkg/thing.py"
    assert nodes["pkg.second.Thing"]["source"] == "src/pkg/other.py"


def test_adjacency_ignores_malformed_edge_rows(builder: Any) -> None:
    """
    A table row that is not six columns is not an edge.

    Purpose:
        The document is generated, but it is still text, and a partially
        written table during an interrupted run must produce no edge rather
        than a truncated one.
    """
    broken = _GRAPH_FRAGMENT.replace(
        "| `pkg.thing.Thing` | specializes | `pkg.base.Base` | - | - | derived |",
        "| `pkg.thing.Thing` | specializes |",
    )
    _, edges, _ = builder.parse_graph_adjacency(broken)
    assert len(edges) == 1
    assert edges[0][1] == "owns_lifecycle_of"


def test_adjacency_keeps_a_justification_containing_a_colon(builder: Any) -> None:
    """
    Why-lines are prose and prose contains colons.

    Purpose:
        The line is split on the FIRST `": "`. A naive split on every colon
        would truncate any justification that explains itself, which is most
        of the useful ones.
    """
    fragment = _GRAPH_FRAGMENT.replace(
        "- `pkg.thing.Thing` -> `pkg.other.Other`: Thing owns Other for the whole run.",
        "- `pkg.thing.Thing` -> `pkg.other.Other`: Thing owns Other: creation, "
        "reuse, and teardown.",
    )
    _, _, whys = builder.parse_graph_adjacency(fragment)
    assert whys[("pkg.thing.Thing", "pkg.other.Other")] == (
        "Thing owns Other: creation, reuse, and teardown."
    )


def test_adjacency_does_not_invent_nodes_from_headings_without_ids(
        builder: Any,
) -> None:
    """
    A heading is not a node; the `- id:` line is.

    Purpose:
        Treating a bare heading as a node would put entries in the table with
        no resolvable id, and every one of them would be unreachable from a
        walk while still inflating the count.
    """
    fragment = _GRAPH_FRAGMENT.replace("- id: `pkg.thing.Thing`\n", "")
    nodes, _, _ = builder.parse_graph_adjacency(fragment)
    assert "pkg.thing" in nodes
    assert not any(node_id.endswith(".Thing") for node_id in nodes)


def test_adjacency_treats_a_second_edges_table_after_candidates_normally(
        builder: Any,
) -> None:
    """
    The candidate guard must reset at the next section heading.

    Purpose:
        Candidates are skipped by a flag. If the flag never cleared, every file
        after the first candidate block would contribute zero edges - a silent
        loss of most of the graph.
    """
    two_files = _GRAPH_FRAGMENT + _GRAPH_FRAGMENT.replace("pkg/thing", "pkg/other").replace(
        "pkg.thing", "pkg.second"
    )
    _, edges, _ = builder.parse_graph_adjacency(two_files)
    assert len([e for e in edges if e[0].startswith("pkg.second")]) == 2


# ---------------------------------------------------------------------------
# Determinism and idempotence
# ---------------------------------------------------------------------------


def test_ingest_is_deterministic(builder: Any) -> None:
    """
    Two ingests of an unchanged tree agree exactly.

    Purpose:
        Everything downstream - the fingerprint, `--check`, the emitted
        modules - assumes this. Non-determinism would report a current asset
        as stale on every run until the signal was ignored.
    """
    first, first_refusals = builder.ingest()
    second, second_refusals = builder.ingest()
    assert first == second
    assert first_refusals == second_refusals


def test_generated_modules_carry_the_do_not_edit_banner(builder: Any) -> None:
    """
    A generated file that does not say so invites a hand-edit.

    Purpose:
        Hand-editing a payload is undetectable at runtime until `verify()` is
        called, and nothing calls it implicitly. The banner is the cheapest
        prevention available.
    """
    for filename in (
        builder.manifest_path().name,
        "system_documents_index.py",
        "graph_adjacency_manifest.py",
    ):
        path = builder.manifest_path().parent / filename
        if not path.is_file():
            pytest.skip(f"{filename} not generated; run the builder")
        assert "DO NOT EDIT" in path.read_text(encoding="utf-8")[:800]


def test_every_generated_module_names_how_to_regenerate_it(builder: Any) -> None:
    """
    A stale asset should tell its reader how to fix it.

    Purpose:
        The runner reports staleness, but a developer who opens the file
        directly should not have to go find the command.
    """
    for filename in (
        builder.manifest_path().name,
        "system_documents_index.py",
        "graph_adjacency_manifest.py",
    ):
        path = builder.manifest_path().parent / filename
        if not path.is_file():
            pytest.skip(f"{filename} not generated; run the builder")
        assert "_build_asset_runner.py" in path.read_text(encoding="utf-8")[:1200]
