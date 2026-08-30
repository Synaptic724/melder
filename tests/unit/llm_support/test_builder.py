"""Contract tests for the deterministic repository LLM support builder."""

import pathlib
import subprocess
from typing import Sequence

import pytest

from llm_support import _builder as subject


def _git(repository: pathlib.Path, arguments: Sequence[str]) -> None:
    """
    Run one Git setup command against a temporary repository.

    Args:
        repository: Temporary working-tree root.
        arguments: Git arguments after the executable.

    Returns:
        None.
    """
    subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=True,
        capture_output=True,
    )


def _write(repository: pathlib.Path, relative_path: str, text: str) -> pathlib.Path:
    """
    Write one UTF-8/LF test input beneath a temporary repository.

    Args:
        repository: Temporary working-tree root.
        relative_path: POSIX-style repository path.
        text: Complete file text.

    Returns:
        Created path.
    """
    path = repository / pathlib.PurePosixPath(relative_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def _repository(tmp_path: pathlib.Path) -> pathlib.Path:
    """
    Create one staged three-corpus Git repository for end-to-end tests.

    Args:
        tmp_path: Pytest temporary directory.

    Returns:
        Initialized repository root.
    """
    _git(tmp_path, ["init", "--quiet"])
    _write(tmp_path, "src/pkg/a.py", "VALUE = 1\n")
    _write(tmp_path, "tests/test_a.py", "def test_a():\n    assert True\n")
    _write(tmp_path, "README.md", "# Example\n")
    _git(tmp_path, ["add", "src/pkg/a.py", "tests/test_a.py", "README.md"])
    return tmp_path


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("src/pkg/a.py", ("src", "included")),
        (
            "src/melder/_build_assets/x/manifest/generated.py",
            (None, "generated_src_asset"),
        ),
        ("src/pkg/py.typed", (None, "src_non_code")),
        ("tests/test_a.py", ("tests", "included")),
        ("tests/results/.gitignore", ("tests", "included")),
        ("README.md", ("other", "included")),
        ("context_compass/AGENTS.MD", (None, "context_compass_direct")),
        (
            "context_compass/tickets/tasks/current.md",
            (None, "context_compass_direct"),
        ),
        (
            "context_compass/attention_board.md",
            (None, "context_compass_direct"),
        ),
        (".gitattributes", ("other", "included")),
        ("context_compass/system_docs/graph/a.json", (None, "context_compass_direct")),
        ("architecture_and_design/a.svg", (None, "rendered_or_placeholder_asset")),
        ("context_compass/empty/.gitkeep", (None, "context_compass_direct")),
        ("llm_support/manifest.json", (None, "self_output")),
    ],
)
def test_classify_applies_exact_corpus_and_exclusion_policy(
        path: str,
        expected: tuple[object, str],
) -> None:
    """
    Verify representative tracked paths map to one accepted policy result.

    Args:
        path: Repository path under test.
        expected: Expected corpus/reason tuple.

    Returns:
        None.
    """
    assert subject.LLMSupportPolicy.classify(path) == expected


@pytest.mark.parametrize(
    ("raw", "encoding", "text"),
    [
        (b"alpha\r\nbeta\r", "utf-8", "alpha\nbeta\n"),
        (b"\xef\xbb\xbfalpha", "utf-8-bom", "alpha"),
        ("alpha\n".encode("utf-16-le"), "utf-16-le-bom", "alpha\n"),
        ("alpha\n".encode("utf-16-be"), "utf-16-be-bom", "alpha\n"),
    ],
)
def test_decode_source_supports_declared_encodings(
        raw: bytes,
        encoding: str,
        text: str,
) -> None:
    """
    Verify decoding is strict, explicit, and LF-normalized.

    Args:
        raw: Source bytes without the BOM supplied separately below.
        encoding: Expected encoding label.
        text: Expected normalized content.

    Returns:
        None.
    """
    if encoding == "utf-16-le-bom":
        raw = b"\xff\xfe" + raw
    elif encoding == "utf-16-be-bom":
        raw = b"\xfe\xff" + raw
    assert subject.decode_source(raw, "sample.txt") == (encoding, text)


def test_decode_source_preserves_mixed_utf8_and_cp1252() -> None:
    """
    Verify valid UTF-8 stays decoded while isolated CP1252 bytes are recovered.

    Returns:
        None.
    """
    raw = "quoted “".encode("utf-8") + b" fa\xe7ade"
    encoding, text = subject.decode_source(raw, "mixed.md")
    assert encoding == "mixed-utf8-cp1252"
    assert text == "quoted “ façade"


def test_decode_source_refuses_nul_binary() -> None:
    """
    Verify an eligible NUL-bearing file without a UTF-16 BOM fails loudly.

    Returns:
        None.
    """
    with pytest.raises(ValueError, match="contains NUL bytes"):
        subject.decode_source(b"alpha\x00beta", "binary.txt")


def test_source_file_manifest_uses_normalized_content() -> None:
    """
    Verify file metadata is deterministic and contains value-only JSON fields.

    Returns:
        None.
    """
    source = subject.SourceFile("src/a.py", "utf-8", "a = 1\n")
    entry = source.manifest_entry()
    assert entry["content_lines"] == 1
    assert entry["content_bytes"] == 6
    assert entry["content_sha256"] == subject.sha256_bytes(b"a = 1\n")
    assert entry["source_encoding"] == "utf-8"


def test_line_count_uses_literal_lf_not_unicode_split_boundaries() -> None:
    """
    Verify embedded Unicode/control separators do not move physical LF ranges.

    Returns:
        None.
    """
    assert subject.count_text_lines("alpha\x1cbeta\n") == 1


def test_bundle_and_index_ranges_round_trip(tmp_path: pathlib.Path) -> None:
    """
    Verify generated line ranges resolve first, final, and empty file markers.

    Args:
        tmp_path: Temporary repository root.

    Returns:
        None.
    """
    (tmp_path / ".git").mkdir()
    builder = subject.LLMSupportBuilder(tmp_path)
    files = [
        subject.SourceFile("src/a.py", "utf-8", "a = 1\n"),
        subject.SourceFile("src/empty.py", "utf-8", ""),
    ]
    state = builder.source_state("src", files)
    bundle, ranges = builder.render_bundle(
        "src",
        files,
        str(state["source_fingerprint"]),
    )
    index = builder.render_index("src", state, bundle, ranges)
    output = tmp_path / "llm_support"
    output.mkdir()
    (output / "llm_full_src.txt").write_text(bundle, encoding="utf-8", newline="\n")
    (output / "llm_full_src_index.md").write_text(
        index,
        encoding="utf-8",
        newline="\n",
    )
    builder._validate_index("src", 2)
    parsed = builder._parse_index("src")
    assert parsed[0]["content_start"] is not None
    assert parsed[1]["content_start"] is None


def test_atomic_write_if_changed_is_idempotent(tmp_path: pathlib.Path) -> None:
    """
    Verify identical output is not replaced or timestamp-churned.

    Args:
        tmp_path: Temporary output directory.

    Returns:
        None.
    """
    path = tmp_path / "asset.txt"
    assert subject.atomic_write_if_changed(path, "alpha\n") is True
    first_mtime = path.stat().st_mtime_ns
    assert subject.atomic_write_if_changed(path, "alpha\n") is False
    assert path.stat().st_mtime_ns == first_mtime
    assert subject.atomic_write_if_changed(path, "beta\n") is True


def test_untracked_inputs_require_explicit_bootstrap_flag(tmp_path: pathlib.Path) -> None:
    """
    Verify untracked files are excluded by default and opt in explicitly.

    Args:
        tmp_path: Temporary Git repository.

    Returns:
        None.
    """
    repository = _repository(tmp_path)
    _write(repository, "tests/test_new.py", "def test_new():\n    assert True\n")
    tracked, _ = subject.LLMSupportBuilder(repository).discover()
    bootstrap_builder = subject.LLMSupportBuilder(
        repository,
        include_untracked=True,
    )
    bootstrap, _ = bootstrap_builder.discover()
    assert [item.path for item in tracked["tests"]] == ["tests/test_a.py"]
    assert [item.path for item in bootstrap["tests"]] == [
        "tests/test_a.py",
        "tests/test_new.py",
    ]
    (repository / "README.md").unlink()
    _corpora, excluded = bootstrap_builder.discover()
    assert excluded["working_tree_deleted"] == ["README.md"]


def test_end_to_end_build_check_incremental_tamper_and_slice(
        tmp_path: pathlib.Path,
        capsys: pytest.CaptureFixture[str],
) -> None:
    """
    Verify the full build/check lifecycle and corpus-level write avoidance.

    Args:
        tmp_path: Temporary Git repository.
        capsys: Pytest output capture.

    Returns:
        None.
    """
    repository = _repository(tmp_path)
    builder = subject.LLMSupportBuilder(repository)
    assert builder.build(subject.LLMSupportPolicy.CORPORA) == 0
    assert builder.check(subject.LLMSupportPolicy.CORPORA) == 0
    output = repository / "llm_support"
    test_bundle = output / "llm_full_tests.txt"
    other_bundle = output / "llm_full_other.txt"
    retained = (test_bundle.stat().st_mtime_ns, other_bundle.stat().st_mtime_ns)

    _write(repository, "src/pkg/a.py", "VALUE = 2\n")
    assert builder.build(["src"]) == 0
    assert retained == (test_bundle.stat().st_mtime_ns, other_bundle.stat().st_mtime_ns)
    assert builder.check(subject.LLMSupportPolicy.CORPORA) == 0

    src_bundle = output / "llm_full_src.txt"
    src_bundle.write_text("tampered\n", encoding="utf-8", newline="\n")
    assert builder.check(["src"]) == 1
    assert builder.build(["src"]) == 0
    capsys.readouterr()
    assert builder.slice_file("src", "src/pkg/a.py") == 0
    assert capsys.readouterr().out.endswith("VALUE = 2\n")


def test_generator_change_requires_complete_rebuild(tmp_path: pathlib.Path) -> None:
    """
    Verify partial generation refuses an incompatible global manifest contract.

    Args:
        tmp_path: Temporary Git repository.

    Returns:
        None.
    """
    repository = _repository(tmp_path)
    builder = subject.LLMSupportBuilder(repository)
    builder.build(subject.LLMSupportPolicy.CORPORA)
    manifest_path = repository / "llm_support" / "manifest.json"
    manifest = json_load(manifest_path)
    manifest["generator_sha256"] = "0" * 64
    manifest_path.write_text(
        subject.render_json(manifest),
        encoding="utf-8",
        newline="\n",
    )
    with pytest.raises(ValueError, match="rebuild all corpora"):
        builder.build(["src"])


def test_repository_workflows_separate_source_and_repo_assets() -> None:
    """
    Verify workflow names, gates, permissions, actions, and check commands.

    Returns:
        None.
    """
    root = pathlib.Path(__file__).resolve().parents[3]
    workflows = root / ".github" / "workflows"
    assert not (workflows / "build-assets.yml").exists()
    source = (workflows / "build-src-assets.yml").read_text(encoding="utf-8")
    repository = (workflows / "build-repo-assets.yml").read_text(encoding="utf-8")
    assert "name: build-src-assets" in source
    assert "BUILD_SRC_ASSETS_GATE" in source
    assert "python src/melder/_build_assets/_build_asset_runner.py --check" in source
    assert "name: build-repo-assets" in repository
    assert "BUILD_REPO_ASSETS_GATE" in repository
    assert "permissions:\n  contents: read" in repository
    assert "python llm_support/_builder.py --check" in repository
    assert "actions/checkout@v7" in source and "actions/checkout@v7" in repository
    assert "actions/setup-python@v7" in source and "actions/setup-python@v7" in repository


def json_load(path: pathlib.Path) -> dict[str, object]:
    """
    Load one generated JSON object for focused manifest mutation.

    Args:
        path: JSON path.

    Returns:
        Parsed JSON object.
    """
    import json

    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value
