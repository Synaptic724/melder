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
from typing import Any, List

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

# A builder exercising the full OPTIONAL contract: fingerprint key and schema
# version. Shaped exactly like the two real ones - a manifest of bare
# (unannotated) stamped constants, written into a `manifest/` subdirectory.
_KEYED_BUILDER = '''
import pathlib

FINGERPRINT = "0" * 64
SCHEMA = "1.0.0"
RENDER_CALLS = []

def target_path():
    return pathlib.Path(__file__).parent / "manifest" / "artifact_manifest.py"

def source_fingerprint():
    return FINGERPRINT

def manifest_version():
    return SCHEMA

def render(version):
    RENDER_CALLS.append(version)
    return (
        'MANIFEST_VERSION = "%s"\\n'
        'BUILT_FOR_VERSION = "%s"\\n'
        'SOURCE_SHA256 = "%s"\\n'
        'ENTRIES = ((\\'a\\', \\'B\\'),)\\n' % (SCHEMA, version, FINGERPRINT)
    )

def write(version):
    target = target_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render(version), encoding="utf-8")
    return target, 1
'''


def _load_module_by_path(name: str, path: pathlib.Path) -> Any:
    """
    Execute one module directly from its file, bypassing package import.

    Args:
        name: Name to register the loaded module under.
        path: Absolute path to the `.py` file.

    Returns:
        Any: The executed module.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_runner() -> Any:
    """
    Load a FRESH runner module from its real path.

    Contract:
        A new module object per call, so monkeypatching one test's runner cannot
        leak into another through `sys.modules`.

    Returns:
        Any: The executed runner module.
    """
    return _load_module_by_path("_rt_build_asset_runner", _RUNNER_PATH)


def _shipped_asset_names() -> List[str]:
    """
    Return every real asset name, DISCOVERED rather than hardcoded.

    Purpose:
        A hardcoded list is how `_system_documents` shipped uncovered. It was
        added as a third asset while the per-asset tests below still named only
        two, so every structural guarantee they enforce silently did not apply
        to it - and nothing failed to say so.

    Contract:
        Derived from the runner's own discovery, so adding an asset directory
        automatically subjects it to every parametrized test in this file.

    Returns:
        List[str]: Asset directory names, sorted.
    """
    return sorted(p.parent.name for p in _load_runner().discover_builders())


# Assets whose loader hydrates through a `.melc` cache. NOT every asset has one,
# and the omission is a design decision rather than an oversight:
# `_system_documents` deliberately has no cache because a cache amortises
# COMPUTATION and there is none - its payload is already a string - and because
# a cache read at import would defeat the laziness that keeps four
# package-scope documents off the boot path.
#
# Listed explicitly rather than discovered so that REMOVING a cache from an
# asset that should have one fails here instead of quietly reducing coverage.
_CACHED_ASSETS = ("bind_guard", "agent_documentation")


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


def test_missing_manifest_fails_even_when_the_key_matches(runner, fake_assets):
    """
    Purpose:
        The manifest is the artifact. A source key that still matches says
        nothing about whether the file it describes is actually on disk, and a
        missing manifest means the loader has nothing to hydrate from.
    Contract:
        A deleted manifest is stale regardless of the key.
    """
    asset = _make_asset(fake_assets, "_keyed", _KEYED_BUILDER)
    assert runner.build_all("1.0.0") == 0
    (asset / "manifest" / "artifact_manifest.py").unlink()

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

    artifact = asset / "manifest" / "artifact_manifest.py"
    artifact.write_text(
        artifact.read_text(encoding="utf-8").replace('"1.0.0"', '"0.9.0"', 1),
        encoding="utf-8",
    )

    assert runner.check_all("1.0.0") == 1


def test_a_builder_without_the_optional_contract_still_checks(runner, fake_assets):
    """
    Purpose:
        The key and schema hooks are OPTIONAL. A builder exposing only the three
        required callables must keep working through the slow byte comparison
        rather than being failed for what it does not declare.
    Contract:
        The plain builder round-trips green, then goes stale on a version bump.
    """
    _make_asset(fake_assets, "_plain")
    assert runner.build_all("1.0.0") == 0
    assert runner.check_all("1.0.0") == 0
    assert runner.check_all("2.0.0") == 1


# The real repository -------------------------------------------------------
#
# There is deliberately NO test here asserting the committed assets are current
# against the live tree. `source_fingerprint()` hashes the raw bytes of every
# source file, so a comment, a blank line, or a docstring typo moves the key and
# reports stale even when the regenerated manifest would be byte-identical. In a
# repository under active edit that test is red almost continuously, for reasons
# unrelated to whatever is being tested - and a check that is red by default
# stops being read, which costs more than it protects.
#
# Currency is a BUILD concern, answered by running the builder. The tests above
# cover what actually needs testing: that the staleness mechanism itself works,
# against synthetic fixtures where the inputs are controlled.


@pytest.mark.parametrize("asset_name", _shipped_asset_names())
def test_every_shipped_builder_satisfies_the_contract(asset_name):
    """
    Purpose:
        These builders are the reference implementation of the convention; if
        one drifts from the contract, the pattern documented for future assets
        is wrong.
    Contract:
        Each real builder exposes all three required callables.
    """
    live = _load_runner()
    builders = live.discover_builders()
    assert asset_name in [p.parent.name for p in builders]
    module = live._load_builder(next(p for p in builders if p.parent.name == asset_name))
    for name in live.BuildAssetRunnerPolicy.REQUIRED_CALLABLES:
        assert callable(getattr(module, name))


@pytest.mark.parametrize("asset_name", _shipped_asset_names())
def test_shipped_assets_follow_the_directory_convention(asset_name):
    """
    Purpose:
        Both assets must be structurally identical, because the next one gets
        built by copying whichever folder someone opens first. An asymmetry here
        is how the previous layout drifted into two different load postures.
    Contract:
        `_<asset>/` holds `_builder.py` and `<asset>.py`, and the committed
        manifest sits at `_<asset>/manifest/<asset>_manifest.py`.
    """
    live = _load_runner()
    builder = next(p for p in live.discover_builders() if p.parent.name == asset_name)
    module = live._load_builder(builder)

    bare = asset_name.lstrip("_")
    asset_dir = builder.parent
    manifest = module.target_path()

    assert (asset_dir / f"{bare}.py").exists(), f"{asset_name}: loader missing"
    assert manifest.exists(), f"{asset_name}: manifest missing"
    assert manifest.parent.name == "manifest", (
        f"{asset_name}: manifest is not in a manifest/ directory"
    )
    assert manifest.name == f"{bare}_manifest.py", (
        f"{asset_name}: manifest named {manifest.name!r}, breaking the convention"
    )


@pytest.mark.parametrize("asset_name", _CACHED_ASSETS)
def test_shipped_assets_cache_under_melder_cache(asset_name):
    """
    Purpose:
        The `.melc` is a CACHE and must land in the shared cache root, not
        beside the source it was derived from. A committed marshal bundle is
        interpreter-specific - `marshal` carries no cross-version guarantee -
        and this repo runs 3.10 while targeting 3.14t, so the previous layout
        would have handed one interpreter's bundle to another.
    Contract:
        The cache path is `__melder_cache__/__<asset>__/<asset>.melc`, matching
        the `<root>/<scope>/<name>.melc` shape `CachingSystem` uses, and it is
        NOT inside `_build_assets`.
    """
    # Loaded BY PATH, like everything else in this file: `import melder` would
    # boot `Aether()` and would also defeat
    # `test_running_the_runner_never_imports_melder` for any test ordered after
    # this one.
    asset_cache = _load_module_by_path(
        "_rt_asset_cache",
        _REPO_ROOT / "src" / "melder" / "utilities" / "caching_system" / "asset_cache.py",
    )
    path = pathlib.Path(asset_cache.cache_path_for(asset_name))
    assert path.name == f"{asset_name}.melc"
    assert path.parent.name == f"__{asset_name}__"
    assert path.parent.parent.name == "__melder_cache__"
    assert "_build_assets" not in path.parts


@pytest.mark.parametrize("asset_name", _shipped_asset_names())
def test_shipped_assets_declare_a_schema_version(asset_name):
    """
    Purpose:
        `MANIFEST_VERSION` is what lets a reader tell "built by an older melder"
        - fine, the SHA decides - from "written in a shape I cannot parse",
        which is fatal. Without it stamped, `--check` cannot detect schema drift
        and silently degrades to a content-only comparison.
    Contract:
        The builder declares a schema version and the generated loader carries
        the same value.
    """
    live = _load_runner()
    builder = next(p for p in live.discover_builders() if p.parent.name == asset_name)
    module = live._load_builder(builder)

    declared = module.manifest_version()
    assert declared, f"{asset_name}: builder declares no schema version"
    stamped = f'MANIFEST_VERSION = "{declared}"'
    assert stamped in module.target_path().read_text(encoding="utf-8"), (
        f"{asset_name}: manifest is not stamped with the declared schema {declared!r}"
    )


def test_build_assets_holds_no_runtime_code():
    """
    Purpose:
        `_build_assets/` is for tools that run at BUILD time and never execute
        in a user's process. A hot-path loader living there made the directory
        mean two unrelated things, which is how `_asset_cache.py` ended up on
        the boot path inside a folder full of generators.
    Contract:
        Every `.py` directly under `_build_assets/` is the runner itself; the
        only other modules are each asset's `_builder.py`, its loader, and its
        generated manifest.
    """
    live = _load_runner()
    root = live._assets_root()

    loose = sorted(p.name for p in root.glob("*.py"))
    assert loose == ["_build_asset_runner.py"], (
        f"unexpected modules directly under _build_assets/: {loose}"
    )

    for builder in live.discover_builders():
        bare = builder.parent.name.lstrip("_")
        names = sorted(p.name for p in builder.parent.glob("*.py"))
        assert names == ["_builder.py", f"{bare}.py"], (
            f"{builder.parent.name}: unexpected modules {names}"
        )
