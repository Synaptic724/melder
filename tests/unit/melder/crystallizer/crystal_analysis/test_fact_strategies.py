"""
Unit tests for the crystal_analysis fact strategies: import extraction
order parity, from-import member probing and relative resolution, export
surfaces, and the topological dependency view.

Runs only on 3.14t (melder package root import chain).
"""
import ast

from melder.crystallizer.crystal_analysis.crystal_analysis_result import (
    CrystalAnalysisResult,
)
from melder.crystallizer.crystal_analysis.strategies.base_strategy import (
    FactContext,
)
from melder.crystallizer.crystal_analysis.strategies.dependency_view_strategy import (
    DependencyViewStrategy,
)
from melder.crystallizer.crystal_analysis.strategies.export_surface_strategy import (
    ExportSurfaceStrategy,
)
from melder.crystallizer.crystal_analysis.strategies.from_import_statement_strategy import (
    FromImportStatementStrategy,
)
from melder.crystallizer.crystal_analysis.strategies.import_statement_strategy import (
    ImportStatementStrategy,
)


def _dispatch(source_text, module_name="probe_module", current_package=""):
    """
    Run one shared-walk dispatch over the source with both import
    strategies, mirroring the analyzer's single AST pass.
    """
    syntax_tree = ast.parse(source_text)
    context = FactContext(
        module_name=module_name,
        current_package=current_package,
        source_text=source_text,
        syntax_tree=syntax_tree,
    )
    import_strategy = ImportStatementStrategy()
    from_strategy = FromImportStatementStrategy()
    try:
        for node in ast.walk(syntax_tree):
            import_strategy.visit_node(node, context)
            from_strategy.visit_node(node, context)
        return (
            list(context.flat_import_targets),
            {
                base: list(members)
                for base, members in context.from_import_targets.items()
            },
        )
    finally:
        import_strategy.cleanup()
        from_strategy.cleanup()
        context.cleanup()


def test_import_extraction_preserves_historical_interleaved_order():
    """
    Contract: candidates appear in visit order - plain imports as written,
    and for each from-import the probed member submodules BEFORE their
    base - byte-compatible with the pre-decomposition extractor.
    """
    flat_targets, from_targets = _dispatch(
        "import zlib\n"
        "from os import path\n"
        "import json\n"
    )
    assert flat_targets == ["zlib", "os.path", "os", "json"]
    assert from_targets == {"os": ["path"]}


def test_from_import_records_plain_members_without_probed_candidates():
    """
    Contract: `from x import name` members that are not importable
    submodules still land in the member map, while only the base becomes
    a dependency candidate.
    """
    flat_targets, from_targets = _dispatch(
        "from json import dumps, loads\n"
    )
    assert flat_targets == ["json"]
    assert from_targets == {"json": ["dumps", "loads"]}


def test_from_import_star_is_mapped_but_never_probed():
    """
    Contract: star imports record `*` in the member map and contribute
    only the base module as a candidate.
    """
    flat_targets, from_targets = _dispatch("from json import *\n")
    assert flat_targets == ["json"]
    assert from_targets == {"json": ["*"]}


def test_relative_import_resolves_against_current_package():
    """
    Contract: relative levels resolve through the package context - the
    resolved base and any importable member submodules become candidates.
    """
    flat_targets, from_targets = _dispatch(
        "from . import abc\n",
        module_name="collections.probe",
        current_package="collections",
    )
    assert flat_targets == ["collections.abc", "collections"]
    assert from_targets == {"collections": ["abc"]}


def test_export_surface_records_static_all_and_public_names():
    """
    Contract: a static `__all__` list resolves verbatim; public top-level
    def/class/assignment names record in first-seen order; underscore and
    dunder names are excluded.
    """
    source_text = (
        "__all__ = [\"Visible\", \"helper\"]\n"
        "_SECRET = 1\n"
        "LIMIT = 10\n"
        "class Visible:\n"
        "    pass\n"
        "def helper():\n"
        "    return LIMIT\n"
        "def _hidden():\n"
        "    return _SECRET\n"
    )
    syntax_tree = ast.parse(source_text)
    context = FactContext(
        module_name="surface_module",
        current_package="",
        source_text=source_text,
        syntax_tree=syntax_tree,
    )
    result = CrystalAnalysisResult()
    strategy = ExportSurfaceStrategy()
    try:
        strategy.analyze_module(context, result)
        surface = result.export_surfaces["surface_module"]
        assert surface["all_declared"] == ["Visible", "helper"]
        assert surface["public_names"] == ["LIMIT", "Visible", "helper"]
    finally:
        strategy.cleanup()
        context.cleanup()
        result.cleanup()


def test_export_surface_underclaims_dynamic_all_honestly():
    """
    Contract: a dynamic `__all__` (not a list/tuple of string constants)
    yields an EMPTY all_declared instead of a guess.
    """
    source_text = (
        "_names = [\"A\"]\n"
        "__all__ = list(_names)\n"
        "class A:\n"
        "    pass\n"
    )
    syntax_tree = ast.parse(source_text)
    context = FactContext(
        module_name="dynamic_module",
        current_package="",
        source_text=source_text,
        syntax_tree=syntax_tree,
    )
    result = CrystalAnalysisResult()
    strategy = ExportSurfaceStrategy()
    try:
        strategy.analyze_module(context, result)
        surface = result.export_surfaces["dynamic_module"]
        assert surface["all_declared"] == []
        assert surface["public_names"] == ["A"]
    finally:
        strategy.cleanup()
        context.cleanup()
        result.cleanup()


def _seed_edges(result, edges):
    """
    Record bare module targets carrying the given dependency edges.
    """
    for module_name, dependency_names in edges.items():
        result.record_module_target(
            module_name=module_name,
            module_path=None,
            module_kind="user_source",
            module_extension=".py",
            direct_dependencies=dependency_names,
            ast_import_targets=list(dependency_names),
            ast_from_import_targets={},
        )


def test_dependency_view_orders_dependencies_before_dependents():
    """
    Contract: the recorded load order is topological - every walked
    dependency appears before its dependents (chain and diamond shapes).
    """
    result = CrystalAnalysisResult()
    strategy = DependencyViewStrategy()
    try:
        _seed_edges(result, {
            "app.root": ["app.left", "app.right"],
            "app.left": ["app.base"],
            "app.right": ["app.base"],
            "app.base": [],
        })
        strategy.finalize(result)
        load_order = result.module_load_order
        assert load_order.index("app.base") < load_order.index("app.left")
        assert load_order.index("app.base") < load_order.index("app.right")
        assert load_order.index("app.left") < load_order.index("app.root")
        assert load_order.index("app.right") < load_order.index("app.root")
        assert result.walk_errors == []
    finally:
        strategy.cleanup()
        result.cleanup()


def test_dependency_view_ignores_unwalked_external_edges():
    """
    Contract: edges pointing outside the walked module set (external
    leaves) never block ordering.
    """
    result = CrystalAnalysisResult()
    strategy = DependencyViewStrategy()
    try:
        _seed_edges(result, {
            "solo.module": ["json", "zlib"],
        })
        strategy.finalize(result)
        assert result.module_load_order == ["solo.module"]
        assert result.walk_errors == []
    finally:
        strategy.cleanup()
        result.cleanup()


def test_dependency_view_breaks_cycles_deterministically_with_honesty():
    """
    Contract: an import cycle cannot topo-sort - the cycle members are
    appended in sorted name order and ONE walk error names them, so the
    order stays usable and the honesty ledger stays honest.
    """
    result = CrystalAnalysisResult()
    strategy = DependencyViewStrategy()
    try:
        _seed_edges(result, {
            "cyc.alpha": ["cyc.beta"],
            "cyc.beta": ["cyc.alpha"],
            "cyc.free": [],
        })
        strategy.finalize(result)
        assert result.module_load_order == [
            "cyc.free",
            "cyc.alpha",
            "cyc.beta",
        ]
        assert len(result.walk_errors) == 1
        assert "cyc.alpha" in result.walk_errors[0]
        assert "cyc.beta" in result.walk_errors[0]
    finally:
        strategy.cleanup()
        result.cleanup()
