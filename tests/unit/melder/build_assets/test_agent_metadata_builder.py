"""
Unit tests for the agent-metadata harvester.

This builder is the migration's safety net. It has to reproduce 788 hand-written
markers EXACTLY while classes are being emptied out from under it, so the tests
below weight two things above all others: FIDELITY (the harvested value equals
the value the class carries today) and PRECEDENCE (a migrated docstring beats the
legacy attribute, never the other way round).

The builder is loaded by file path, matching how the runner invokes it and
avoiding a package import that would boot `Aether()`.
"""
import importlib.util
import pathlib
import textwrap
from typing import Any

import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[4]
_BUILDER_PATH = (
    _REPO_ROOT / "src" / "melder" / "_build_assets" / "_agent_metadata" / "_builder.py"
)


def _load_builder() -> Any:
    """
    Load a FRESH builder module from its real path.

    Returns:
        Any: The executed builder module.
    """
    spec = importlib.util.spec_from_file_location("_rt_agent_metadata_builder", _BUILDER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def builder():
    """Fresh builder module per test."""
    return _load_builder()


# Grammar -------------------------------------------------------------------


def test_access_marker_is_extracted(builder):
    """
    Purpose:
        The access level decides whether agent tooling surfaces a class at all;
        losing it silently downgrades visibility.
    Contract:
        `AGENT_ACCESS:` yields its value.
    """
    access, _ = builder.parse_docstring_markers("AGENT_ACCESS: public\n")
    assert access == "public"


def test_purpose_block_is_collected_across_lines(builder):
    """
    Purpose:
        Purposes are multi-line prose; a parser that grabbed only the first line
        would silently truncate 416-character entries.
    Contract:
        An indented block under `AGENT_PURPOSE:` is joined into one string.
    """
    doc = textwrap.dedent(
        """
        Some ordinary class documentation.

        AGENT_ACCESS: internal

        AGENT_PURPOSE:
            First line of the purpose.
            Second line continues it.
        """
    )
    access, purpose = builder.parse_docstring_markers(doc)
    assert access == "internal"
    assert purpose == "First line of the purpose. Second line continues it."


def test_purpose_block_stops_at_the_next_title_case_section(builder):
    """
    Purpose:
        THE grammar risk. Every class already carries `Contract:`, `Threading:`,
        `Registration:` sections. If the purpose block swallowed them, 404
        entries would silently absorb unrelated documentation.
    Contract:
        A Title-Case section header terminates the purpose block.
    """
    doc = textwrap.dedent(
        """
        AGENT_PURPOSE:
            The real purpose text.

        Threading:
            Guarded by an RLock and definitely not part of the purpose.
        """
    )
    _, purpose = builder.parse_docstring_markers(doc)
    assert purpose == "The real purpose text."
    assert "RLock" not in purpose


def test_purpose_block_stops_at_a_following_access_marker(builder):
    """
    Purpose:
        Authors may order the two markers either way round.
    Contract:
        `AGENT_ACCESS:` after a purpose block closes it and still parses.
    """
    doc = "AGENT_PURPOSE:\n    Purpose text.\n\nAGENT_ACCESS: public\n"
    access, purpose = builder.parse_docstring_markers(doc)
    assert access == "public"
    assert purpose == "Purpose text."


def test_inline_purpose_on_the_marker_line_is_accepted(builder):
    """
    Purpose:
        Short purposes read better on one line; rejecting that shape would force
        awkward formatting on hundreds of classes.
    Contract:
        Text on the `AGENT_PURPOSE:` line itself is captured.
    """
    _, purpose = builder.parse_docstring_markers("AGENT_PURPOSE: A short purpose.\n")
    assert purpose == "A short purpose."


def test_ordinary_prose_is_never_mistaken_for_a_marker(builder):
    """
    Purpose:
        The whole reason for ALL-CAPS line-anchored markers is that ordinary
        documentation must not trip the parser.
    Contract:
        Prose merely mentioning the concepts yields nothing.
    """
    doc = "This class documents agent access and its purpose in the system.\n"
    assert builder.parse_docstring_markers(doc) == (None, None)


def test_empty_docstring_yields_nothing(builder):
    """
    Purpose:
        Undocumented classes must classify as unmarked, not crash the build.
    Contract:
        Empty input returns `(None, None)`.
    """
    assert builder.parse_docstring_markers("") == (None, None)


# Precedence and fallback ---------------------------------------------------


def test_docstring_wins_over_the_legacy_attribute(builder, tmp_path, monkeypatch):
    """
    Purpose:
        THE migration invariant. As classes are converted, both sources exist at
        once. If the attribute won, a freshly migrated class would keep emitting
        its old value and the codemod would appear to do nothing.
    Contract:
        With both present, the docstring value is harvested.
    """
    pkg = tmp_path / "melder"
    pkg.mkdir()
    (pkg / "sample.py").write_text(
        'class Both:\n'
        '    """\n'
        '    AGENT_ACCESS: public\n\n'
        '    AGENT_PURPOSE: from docstring\n'
        '    """\n'
        '    __ast_helper_access__: str = "internal"\n'
        '    __agent_purpose__: str = "from attribute"\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(builder, "package_root", lambda: pkg)
    access, purpose, source = builder.harvest().marked[("melder.sample", "Both")]
    assert (access, purpose, source) == ("public", "from docstring", "docstring")


def test_legacy_attribute_is_used_when_no_docstring_marker_exists(builder, tmp_path, monkeypatch):
    """
    Purpose:
        Dual-source is what makes the asset correct BEFORE any class is
        migrated, so the codemod can proceed subtree by subtree.
    Contract:
        An unmigrated class still harvests, flagged `attribute`.
    """
    pkg = tmp_path / "melder"
    pkg.mkdir()
    (pkg / "sample.py").write_text(
        'class Legacy:\n'
        '    """Ordinary docs."""\n'
        '    __ast_helper_access__: str = "internal"\n'
        '    __agent_purpose__: str = "legacy prose"\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(builder, "package_root", lambda: pkg)
    assert builder.harvest().marked[("melder.sample", "Legacy")] == (
        "internal",
        "legacy prose",
        "attribute",
    )


# Three-state classification ------------------------------------------------


def test_unmarked_class_outside_an_exempt_subtree_is_pending(builder, tmp_path, monkeypatch):
    """
    Purpose:
        The catalog only has value if genuinely-unfinished work lands in it.
    Contract:
        An unmarked class in a normal path is `pending`.
    """
    pkg = tmp_path / "melder"
    (pkg / "utilities").mkdir(parents=True)
    (pkg / "utilities" / "thing.py").write_text('class Thing:\n    """Docs."""\n', encoding="utf-8")
    monkeypatch.setattr(builder, "package_root", lambda: pkg)
    result = builder.harvest()
    assert ("melder.utilities.thing", "Thing") in result.pending


def test_unmarked_class_inside_the_exempt_subtree_is_exempt(builder, tmp_path, monkeypatch):
    """
    Purpose:
        The owner ruled spell_compiler out wholesale. Without the path rule those
        173 classes would flood the pending catalog and drown real work.
    Contract:
        An unmarked class under the exempt prefix is `exempt`, not `pending`.
    """
    pkg = tmp_path / "melder"
    target = pkg / "aether" / "spellbook" / "spell_compiler"
    target.mkdir(parents=True)
    (target / "thing.py").write_text('class Skipped:\n    """Docs."""\n', encoding="utf-8")
    monkeypatch.setattr(builder, "package_root", lambda: pkg)
    result = builder.harvest()
    key = ("melder.aether.spellbook.spell_compiler.thing", "Skipped")
    assert key in result.exempt
    assert key not in result.pending


def test_a_class_inside_the_exempt_subtree_can_opt_back_in(builder, tmp_path, monkeypatch):
    """
    Purpose:
        A blanket path rule must not become a trap; one agent-facing class inside
        an exempt subtree has to be able to declare itself.
    Contract:
        An explicit marker beats the path exemption.
    """
    pkg = tmp_path / "melder"
    target = pkg / "aether" / "spellbook" / "spell_compiler"
    target.mkdir(parents=True)
    (target / "thing.py").write_text(
        'class OptedIn:\n    """\n    AGENT_ACCESS: public\n\n    AGENT_PURPOSE: visible\n    """\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(builder, "package_root", lambda: pkg)
    result = builder.harvest()
    key = ("melder.aether.spellbook.spell_compiler.thing", "OptedIn")
    assert key in result.marked
    assert key not in result.exempt


def test_explicit_exempt_marker_classifies_as_exempt(builder, tmp_path, monkeypatch):
    """
    Purpose:
        One-off exemptions outside spell_compiler need a way to be recorded as
        DELIBERATE rather than looking unfinished forever.
    Contract:
        `AGENT_ACCESS: exempt` lands in `exempt`, never `marked` or `pending`.
    """
    pkg = tmp_path / "melder"
    pkg.mkdir()
    (pkg / "s.py").write_text('class E:\n    """\n    AGENT_ACCESS: exempt\n    """\n', encoding="utf-8")
    monkeypatch.setattr(builder, "package_root", lambda: pkg)
    result = builder.harvest()
    assert ("melder.s", "E") in result.exempt
    assert ("melder.s", "E") not in result.marked


def test_nested_classes_are_harvested(builder, tmp_path, monkeypatch):
    """
    Purpose:
        Nested classes were invisible to the original hand audit; missing them
        would let real classes escape the catalog entirely.
    Contract:
        A nested class is recorded under its dotted qualname.
    """
    pkg = tmp_path / "melder"
    pkg.mkdir()
    (pkg / "s.py").write_text(
        'class Outer:\n    """Docs."""\n    class Inner:\n        """Docs."""\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(builder, "package_root", lambda: pkg)
    everything = builder.harvest().pending
    assert ("melder.s", "Outer.Inner") in everything


# Build-time validation -----------------------------------------------------


def test_invalid_access_value_fails_the_build(builder, tmp_path, monkeypatch):
    """
    Purpose:
        A bad access value currently surfaces as a RUNTIME raise from
        ClassSurfaceAstDescriber - potentially in production, whenever something
        happens to describe that object. Moving it to build time is the point.
    Contract:
        `render` raises ValueError naming the offending class and value.
    """
    pkg = tmp_path / "melder"
    pkg.mkdir()
    (pkg / "s.py").write_text(
        'class Bad:\n    """\n    AGENT_ACCESS: banana\n\n    AGENT_PURPOSE: x\n    """\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(builder, "package_root", lambda: pkg)
    with pytest.raises(ValueError) as excinfo:
        builder.render("1.0.0")
    assert "banana" in str(excinfo.value) and "Bad" in str(excinfo.value)


def test_render_is_deterministic(builder, tmp_path, monkeypatch):
    """
    Purpose:
        `--check` is a byte comparison, so nondeterminism here (dict ordering,
        set iteration) would produce phantom staleness no rebuild can clear.
    Contract:
        Two renders at one version are byte-identical.
    """
    pkg = tmp_path / "melder"
    pkg.mkdir()
    for name in ("a", "b", "c"):
        (pkg / f"{name}.py").write_text(
            f'class C{name.upper()}:\n    """\n    AGENT_ACCESS: public\n\n'
            f'    AGENT_PURPOSE: purpose {name}\n    """\n',
            encoding="utf-8",
        )
    monkeypatch.setattr(builder, "package_root", lambda: pkg)
    assert builder.render("1.0.0") == builder.render("1.0.0")


def test_base_names_are_captured_for_inherited_purpose_resolution(builder, tmp_path, monkeypatch):
    """
    Purpose:
        The describer builds `inherited_agent_purposes` by walking bases. The
        owner chose build-time precomputation over a runtime MRO walk, so the
        base chain must actually be captured.
    Contract:
        Statically resolvable base names are recorded.
    """
    pkg = tmp_path / "melder"
    pkg.mkdir()
    (pkg / "s.py").write_text('class Base:\n    """D."""\nclass Child(Base):\n    """D."""\n', encoding="utf-8")
    monkeypatch.setattr(builder, "package_root", lambda: pkg)
    assert builder.harvest().bases[("melder.s", "Child")] == ["Base"]


# The real repository -------------------------------------------------------


def test_harvest_reproduces_every_live_class_attribute_exactly():
    """
    Purpose:
        THE fidelity guarantee, and the one that makes the codemod safe. Every
        value the harvester emits must equal the value that class carries in
        source today. If this drifts, the migration silently rewrites 76,200
        characters of authored prose.
    Contract:
        For every class still carrying legacy attributes, the harvested access
        and purpose match the attribute values byte for byte.
    """
    import ast

    live = _load_builder()
    harvested = live.harvest().marked
    root = live.package_root()
    mismatches = []

    for path in root.rglob("*.py"):
        if any(p in {"__pycache__", "_build_assets", "__melder_cache__"} for p in path.parts):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
        module_name = live._module_name_for(path, root)
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            legacy_access, legacy_purpose = live._legacy_attributes(node)
            if legacy_access is None and legacy_purpose is None:
                continue
            entry = harvested.get((module_name, node.name))
            if entry is None:
                mismatches.append(f"{module_name}:{node.name} missing from harvest")
                continue
            if entry[0] != (legacy_access or "") or entry[1] != (legacy_purpose or ""):
                mismatches.append(f"{module_name}:{node.name} value drift")

    assert not mismatches, f"{len(mismatches)} fidelity failures: {mismatches[:5]}"


def test_the_generated_asset_is_current():
    """
    Purpose:
        The committed asset is what downstream will read; a stale one teaches
        wrong metadata.
    Contract:
        The committed file matches a fresh render at the live version.
    """
    live = _load_builder()
    runner_path = _REPO_ROOT / "src" / "melder" / "_build_assets" / "_build_asset_runner.py"
    spec = importlib.util.spec_from_file_location("_rt_runner_for_meta", runner_path)
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    assert live.target_path().read_text(encoding="utf-8") == live.render(runner.melder_version())


def test_package_stays_pending_by_owner_ruling():
    """
    Purpose:
        `Package` is DELIBERATELY parked pending an owner keep-vs-remove call
        (it captures callables well, may be exposed through `melder.__init__`,
        and CommandOps holds a copy to reconcile). A future agent tidying the
        pending list to zero would destroy a recorded decision, so the ruling is
        pinned here rather than living only in a ticket note.
    Contract:
        `Package` is neither marked nor exempt.
    """
    live = _load_builder()
    result = live.harvest()
    key = ("melder.utilities.helpers.package", "Package")
    assert key in result.pending
    assert key not in result.marked and key not in result.exempt
