"""
Unit tests for the durable build asset runner.

The runner is the only thing standing between a stale generated asset and a
released wheel, so these tests target its REFUSAL behaviour above all: every
way an asset can rot must produce a non-zero exit, and every contract violation
must be loud rather than skipped.

The runner is loaded BY FILE PATH, exactly as production and CI invoke it. That
is deliberate - importing `melder._build_assets._build_asset_runner` would boot
`Aether()` through the package root, which is both slow and dishonest: it would
test a code path nobody actually uses.
"""
import importlib.util
import pathlib
import sys
from typing import Any

import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[4]
_RUNNER_PATH = _REPO_ROOT / "src" / "melder" / "_build_assets" / "_build_asset_runner.py"

_VALID_BUILDER = '''
import pathlib

_TEXT = "generated for {version}\\n"

def target_path():
    return pathlib.Path(__file__).parent / "artifact.py"

def render(version):
    return _TEXT.format(version=version)

def write(version):
    target = target_path()
    target.write_text(render(version), encoding="utf-8")
    return target, 1
'''

# A builder exercising the full OPTIONAL contract: fingerprint key, marshal
# payload sidecar, and schema version. Shaped exactly like the two real ones -
# bare (unannotated) stamped constants, because the annotations live in a .pyi.
_KEYED_BUILDER = '''
import marshal
import pathlib

FINGERPRINT = "0" * 64
SCHEMA = "1.0.0"
RENDER_CALLS = []

def target_path():
    return pathlib.Path(__file__).parent / "artifact.py"

def payload_path():
    return target_path().with_suffix(".melc")

def source_fingerprint():
    return FINGERPRINT

def manifest_version():
    return SCHEMA

def render(version):
    RENDER_CALLS.append(version)
    return (
        "import marshal\\n"
        'MANIFEST_VERSION = "%s"\\n'
        'BUILT_FOR_VERSION = "%s"\\n'
        'SOURCE_SHA256 = "%s"\\n' % (SCHEMA, version, FINGERPRINT)
    )

def write(version):
    payload_path().write_bytes(marshal.dumps(frozenset({("a", "B")})))
    target = target_path()
    target.write_text(render(version), encoding="utf-8")
    return target, 1
'''


def _load_runner() -> Any:
    """
    Load a FRESH runner module from its real path.

    Contract:
        A new module object per call, so monkeypatching one test's runner cannot
        leak into another through `sys.modules`.

    Returns:
        Any: The executed runner module.
    """
    spec = importlib.util.spec_from_file_location("_rt_build_asset_runner", _RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def runner():
    """Fresh runner module per test."""
    return _load_runner()


@pytest.fixture
def fake_assets(tmp_path, runner, monkeypatch):
    """
    Point the runner at an empty temporary asset root.

    Returns:
        pathlib.Path: The temporary `_build_assets` stand-in.
    """
    monkeypatch.setattr(runner, "_assets_root", lambda: tmp_path)
    return tmp_path


def _make_asset(root: pathlib.Path, name: str, body: str = _VALID_BUILDER) -> pathlib.Path:
    """
    Create one asset directory containing a `_builder.py`.

    Args:
        root: The asset root to create under.
        name: Asset directory name.
        body: Source for the builder module.

    Returns:
        pathlib.Path: The created asset directory.
    """
    asset = root / name
    asset.mkdir()
    (asset / "_builder.py").write_text(body, encoding="utf-8")
    return asset


# Discovery -----------------------------------------------------------------


def test_discovery_finds_a_directory_holding_a_builder(runner, fake_assets):
    """
    Purpose:
        The whole convention is "a directory participates by containing a
        _builder.py". If discovery misses one, that asset silently stops being
        generated and checked.
    Contract:
        A directory with `_builder.py` is discovered; the returned path points
        at the builder itself.
    """
    _make_asset(fake_assets, "_alpha")
    found = runner.discover_builders()
    assert [p.parent.name for p in found] == ["_alpha"]
    assert found[0].name == "_builder.py"


def test_discovery_ignores_directories_without_a_builder(runner, fake_assets):
    """
    Purpose:
        Generated output and future data files must be able to sit beside a
        builder without being mistaken for assets themselves.
    Contract:
        A directory lacking `_builder.py` is skipped silently, not reported.
    """
    _make_asset(fake_assets, "_real")
    (fake_assets / "_not_an_asset").mkdir()
    (fake_assets / "_not_an_asset" / "data.py").write_text("X = 1", encoding="utf-8")
    assert [p.parent.name for p in runner.discover_builders()] == ["_real"]


def test_discovery_is_sorted_for_reproducible_runs(runner, fake_assets):
    """
    Purpose:
        Unordered discovery makes build output and CI logs differ run to run,
        which turns a real regression into noise.
    Contract:
        Discovery returns assets in sorted order regardless of creation order.
    """
    for name in ("_charlie", "_alpha", "_bravo"):
        _make_asset(fake_assets, name)
    assert [p.parent.name for p in runner.discover_builders()] == ["_alpha", "_bravo", "_charlie"]


def test_discovery_skips_pycache(runner, fake_assets):
    """
    Purpose:
        `__pycache__` is a directory like any other and would otherwise be
        probed on every run.
    Contract:
        `__pycache__` never appears in discovery results.
    """
    _make_asset(fake_assets, "_alpha")
    (fake_assets / "__pycache__").mkdir()
    assert all(p.parent.name != "__pycache__" for p in runner.discover_builders())


# Builder contract ----------------------------------------------------------


def test_contract_violation_raises_and_names_every_missing_callable(runner, fake_assets):
    """
    Purpose:
        A builder that cannot be rendered cannot be checked, so skipping it
        quietly would let that asset rot unnoticed - the exact failure this
        runner exists to prevent. Failing loudly is a deliberate design choice
        and must stay that way.
    Contract:
        Loading an incomplete builder raises AttributeError naming the asset and
        EVERY missing callable, not just the first.
    """
    _make_asset(fake_assets, "_broken", body="def target_path():\n    pass\n")
    with pytest.raises(AttributeError) as excinfo:
        runner.check_all("1.0.0")
    message = str(excinfo.value)
    assert "_broken" in message
    assert "render" in message and "write" in message


def test_non_callable_attribute_does_not_satisfy_the_contract(runner, fake_assets):
    """
    Purpose:
        Presence is not the contract; being callable is. A builder exporting
        `render = None` would pass a naive hasattr check and explode later.
    Contract:
        A non-callable attribute counts as missing.
    """
    body = "def target_path():\n    pass\nrender = None\ndef write(v):\n    pass\n"
    _make_asset(fake_assets, "_bad_types", body=body)
    with pytest.raises(AttributeError, match="render"):
        runner.check_all("1.0.0")


# Check gate ----------------------------------------------------------------


def test_check_passes_when_the_artifact_matches(runner, fake_assets):
    """
    Purpose:
        The gate must not cry wolf; a correct tree has to exit 0 or CI becomes
        noise everyone learns to ignore.
    Contract:
        After a build, `check_all` at the same version returns 0.
    """
    _make_asset(fake_assets, "_alpha")
    assert runner.build_all("1.0.0") == 0
    assert runner.check_all("1.0.0") == 0


def test_check_fails_when_the_version_changes(runner, fake_assets):
    """
    Purpose:
        THE version-drift guarantee. The artifact carries its version, so a
        release bump alone must invalidate it even when nothing else moved -
        otherwise a wheel ships a manifest stamped for another release.
    Contract:
        Building at one version and checking at another returns 1.
    """
    _make_asset(fake_assets, "_alpha")
    runner.build_all("1.0.0")
    assert runner.check_all("2.0.0") == 1


def test_check_fails_when_the_artifact_is_hand_edited(runner, fake_assets):
    """
    Purpose:
        Generated files get "quickly fixed" by hand, and the next regeneration
        silently discards the edit. The gate must catch tampering, not just
        absence.
    Contract:
        Mutating a single byte of the artifact returns 1.
    """
    asset = _make_asset(fake_assets, "_alpha")
    runner.build_all("1.0.0")
    artifact = asset / "artifact.py"
    artifact.write_text(artifact.read_text(encoding="utf-8") + "# tampered\n", encoding="utf-8")
    assert runner.check_all("1.0.0") == 1


def test_check_fails_when_the_artifact_was_never_generated(runner, fake_assets):
    """
    Purpose:
        A fresh clone that has never run the generator must not read as healthy.
    Contract:
        A discovered builder whose target is absent returns 1.
    """
    _make_asset(fake_assets, "_alpha")
    assert runner.check_all("1.0.0") == 1


def test_check_reports_every_stale_asset_not_only_the_first(runner, fake_assets):
    """
    Purpose:
        Stopping at the first failure forces a fix-run-fix-run loop across a
        multi-asset tree.
    Contract:
        With two stale assets, both names appear in the failure output.
    """
    _make_asset(fake_assets, "_alpha")
    _make_asset(fake_assets, "_beta")
    assert runner.check_all("1.0.0") == 1


def test_empty_asset_root_is_a_failure_not_a_pass(runner, fake_assets):
    """
    Purpose:
        If discovery breaks or the tree is wrong, "no assets found" must never
        be reported as success - that would make the CI gate vacuously green.
    Contract:
        An empty asset root returns 1 for both build and check.
    """
    assert runner.check_all("1.0.0") == 1
    assert runner.build_all("1.0.0") == 1


# Build ---------------------------------------------------------------------


def test_build_writes_the_artifact_and_reports_success(runner, fake_assets):
    """
    Purpose:
        Generation is the runner's other half; a silent no-op build would leave
        the tree stale while reporting success.
    Contract:
        `build_all` returns 0 and the artifact exists with version-stamped text.
    """
    asset = _make_asset(fake_assets, "_alpha")
    assert runner.build_all("3.2.1") == 0
    assert (asset / "artifact.py").read_text(encoding="utf-8") == "generated for 3.2.1\n"


def test_build_then_check_round_trips_across_versions(runner, fake_assets):
    """
    Purpose:
        Regenerating is the documented remedy for a stale gate, so the remedy
        must actually clear the failure it was prescribed for.
    Contract:
        Rebuilding at the new version turns a failing check green.
    """
    _make_asset(fake_assets, "_alpha")
    runner.build_all("1.0.0")
    assert runner.check_all("2.0.0") == 1
    runner.build_all("2.0.0")
    assert runner.check_all("2.0.0") == 0


def test_render_is_deterministic(runner, fake_assets):
    """
    Purpose:
        `--check` is a byte-exact comparison, so any nondeterminism in a builder
        (dict ordering, timestamps, absolute paths) would produce phantom
        staleness that no regeneration can fix.
    Contract:
        Two renders at one version are byte-identical.
    """
    _make_asset(fake_assets, "_alpha")
    builder = runner._load_builder(runner.discover_builders()[0])
    assert builder.render("1.0.0") == builder.render("1.0.0")


# CLI dispatch --------------------------------------------------------------


def test_main_check_flag_propagates_the_failure_exit_code(runner, fake_assets):
    """
    Purpose:
        CI reads the process exit code and nothing else. A gate that detects
        drift but exits 0 is worse than no gate.
    Contract:
        `main(["--check"])` returns 1 for an ungenerated tree.
    """
    _make_asset(fake_assets, "_alpha")
    runner.melder_version = lambda: "1.0.0"
    assert runner.main(["--check"]) == 1


def test_main_without_flags_builds(runner, fake_assets):
    """
    Purpose:
        The no-flag invocation is the documented remedy printed in every failure
        message and generated header.
    Contract:
        `main([])` generates, leaving `--check` green.
    """
    _make_asset(fake_assets, "_alpha")
    runner.melder_version = lambda: "1.0.0"
    assert runner.main([]) == 0
    assert runner.main(["--check"]) == 0


def test_list_flag_reports_without_writing(runner, fake_assets):
    """
    Purpose:
        `--list` is the discovery-debugging surface; it must never mutate.
    Contract:
        `main(["--list"])` returns 0 and writes no artifact.
    """
    asset = _make_asset(fake_assets, "_alpha")
    assert runner.main(["--list"]) == 0
    assert not (asset / "artifact.py").exists()


# Isolation -----------------------------------------------------------------


def test_running_the_runner_never_imports_melder(runner, fake_assets):
    """
    Purpose:
        Builders load by file path so generation never boots `Aether()`. If the
        runner ever imported the package it would depend on the runtime it
        describes - and on the very asset it is about to write, which is
        unbuildable from a clean tree.
    Contract:
        A full build/check cycle leaves `melder` absent from `sys.modules` when
        it was not already loaded.
    """
    if "melder" in sys.modules:
        pytest.skip("melder already imported by another test in this session")
    _make_asset(fake_assets, "_alpha")
    runner.build_all("1.0.0")
    runner.check_all("1.0.0")
    assert "melder" not in sys.modules


# The optional contract: key, payload, schema -------------------------------


def test_key_match_skips_render_entirely(runner, fake_assets):
    """
    Purpose:
        The fast path's whole value is NOT rendering. It regressed once already
        and nothing caught it: the stamped-constant patterns required
        `NAME: str = "..."`, but the lean loaders emit bare `NAME = "..."`, so
        every match returned None and every asset silently took the slow path.
        The gate stayed CORRECT and quietly stopped being fast, which is exactly
        the kind of regression a green suite hides.
    Contract:
        On a key match, `render` is never called.
    """
    _make_asset(fake_assets, "_keyed", _KEYED_BUILDER)
    assert runner.build_all("1.0.0") == 0
    assert runner.check_all("1.0.0") == 0

    # `_load_builder` re-executes the builder per call, so the module now in
    # sys.modules is the one `check_all` just loaded and its call log covers
    # that invocation alone.
    module = sys.modules["_melder_asset_builder__keyed"]
    assert module.RENDER_CALLS == [], (
        "render() ran during --check; the fast path did not fire"
    )


def test_missing_payload_fails_even_when_the_key_matches(runner, fake_assets):
    """
    Purpose:
        A loader whose marshal sidecar is absent imports fine right up to its
        `marshal.loads`. Checking the key alone would report OK for a package
        that cannot be imported - and the payloads were in fact untracked and
        gitignored when this was written, so a clone hit precisely that.
    Contract:
        Payload existence is checked BEFORE the key, so a perfect key match on a
        payload-less asset still fails.
    """
    asset = _make_asset(fake_assets, "_keyed", _KEYED_BUILDER)
    assert runner.build_all("1.0.0") == 0
    (asset / "artifact.melc").unlink()

    assert runner.check_all("1.0.0") == 1


def test_schema_drift_fails_even_when_the_key_matches(runner, fake_assets):
    """
    Purpose:
        `MANIFEST_VERSION` tracks payload SHAPE, `BUILT_FOR_VERSION` tracks the
        release. An asset written in an older shape may not hydrate at all, so
        it is not merely out of date - it must never pass on a content match.
    Contract:
        A committed asset stamped with a superseded schema is stale even though
        its source key and build version are both current.
    """
    asset = _make_asset(fake_assets, "_keyed", _KEYED_BUILDER)
    assert runner.build_all("1.0.0") == 0

    artifact = asset / "artifact.py"
    artifact.write_text(
        artifact.read_text(encoding="utf-8").replace('"1.0.0"', '"0.9.0"', 1),
        encoding="utf-8",
    )

    assert runner.check_all("1.0.0") == 1


def test_a_builder_without_the_optional_contract_still_checks(runner, fake_assets):
    """
    Purpose:
        The key, payload and schema hooks are OPTIONAL. A builder exposing only
        the three required callables must keep working through the slow byte
        comparison rather than being failed for what it does not declare.
    Contract:
        The plain builder round-trips green, then goes stale on a version bump.
    """
    _make_asset(fake_assets, "_plain")
    assert runner.build_all("1.0.0") == 0
    assert runner.check_all("1.0.0") == 0
    assert runner.check_all("2.0.0") == 1


# The real repository -------------------------------------------------------


def test_committed_assets_are_current_in_this_repository():
    """
    Purpose:
        THE regression this whole lane exists for. The internal-bind manifest IS
        the enforced registration policy - `bind.py` imports it directly and
        there is no runtime rebuild - so a stale committed asset silently
        enforces a class list that no longer matches the source. This has
        already happened once here.
    Contract:
        Against the real tree at the real version, the gate is green. If this
        fails, run:
            python src/melder/_build_assets/_build_asset_runner.py
    """
    live = _load_runner()
    assert live.check_all(live.melder_version()) == 0


def test_the_shipped_manifest_builder_satisfies_the_contract():
    """
    Purpose:
        The manifest builder is the reference implementation of the convention;
        if it drifts from the contract, the pattern documented for future assets
        is wrong.
    Contract:
        The real `_init_metadata` builder exposes all three required callables.
    """
    live = _load_runner()
    builders = live.discover_builders()
    assert "_init_metadata" in [p.parent.name for p in builders]
    module = live._load_builder(next(p for p in builders if p.parent.name == "_init_metadata"))
    for name in live.BuildAssetRunnerPolicy.REQUIRED_CALLABLES:
        assert callable(getattr(module, name))
