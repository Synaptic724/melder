"""
Fact strategy for plain `import x` statements.

Extracts flat dependency candidates from `ast.Import` nodes in visit order,
preserving the historical extractor's behavior: every dotted name an import
statement mentions becomes a walk candidate exactly as written.

Lane: EPIC-2026-07-09-crystallizer-subsystem-decomposition, story S1.
"""

import ast

from melder.crystallizer.crystal_analysis.strategies.base_strategy import (
    CrystalFactStrategy,
    FactContext,
)
from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg


class ImportStatementStrategy(CrystalFactStrategy):
    """
    Extract flat import targets from `import ...` statements.

    Purpose:
        Contribute `ast.Import` alias names to the module's dependency
        candidates in visit order.

    Contract:
        - Handles `ast.Import` nodes only.
        - Appends alias names verbatim (dotted names included); the
          analyzer owns deduplication on merge.
        - Nested imports (inside functions/classes) are captured because
          the analyzer dispatch walks the full tree, mirroring the
          historical `ast.walk` extraction.
        - Each matching node also appends one value-only memo event with kind
          `import`, relative level zero, no raw module name, and the alias
          names as a tuple. No AST node or alias object enters that event.

    Threading:
        Thread-confined to one analyzer pass; no locks and no instance
        state (`__slots__` is empty). All mutation lands on the caller's
        `FactContext`, which is itself confined to that pass.

    Registration:
        MELDER KERNEL - guarded. Fact strategies are constructed by
        `CrystalAnalyzer` for one analysis, never bound as spells.
        Note the classification split: this concrete leaf IS guarded,
        while its base `CrystalFactStrategy` is deliberately NOT - see
        that class's Registration section for the MRO reasoning.

    Subsystem Context:
        The simplest of the four fact strategies that share the
        analyzer's SINGLE `ast.walk` per module. The analyzer dispatches
        every node to every strategy in registration order; this one acts
        only on `ast.Import`. Its sibling `FromImportStatementStrategy`
        owns the `from ... import ...` half (with relative resolution and
        submodule probing), `ExportSurfaceStrategy` derives what a module
        EXPOSES, and `DependencyViewStrategy` turns the collected edges
        into topological load order after the walk.

    System Context:
        Two properties here are contracts rather than implementation
        details. First, ORDER IS OUTPUT: aliases stay in visit order and
        deduplication is deferred to the analyzer's merge (first-seen
        wins), because that is what keeps manifest ordering
        byte-compatible with the pre-decomposition single-pass extractor.
        A strategy that sorted or deduplicated locally would silently
        change recorded manifests. Second, nested imports inside
        functions and classes ARE captured - not by choice here but
        because the analyzer walks the full tree - which deliberately
        mirrors the historical extractor.
        The dependency edges this pass contributes are what later become
        the `ImpactEngine`'s reverse-import index, so a missed import
        would understate a change's blast radius.
    """
    _ast_helper_access: str = "internal"
    __agent_purpose__: str = (
        "access: internal. Extract flat import targets from `import ...` statements. Melder "
        "kernel machinery: read it to understand the runtime, do not drive it directly."
    )

    __melder_internal__ = _mrg.sentinel
    __slots__ = ()

    @property
    def name(self) -> str:
        """
        Return the stable strategy name.

        Returns:
            str: `import_statement`.
        """
        return "import_statement"

    def visit_node(self, node: ast.AST, context: FactContext) -> None:
        """
        Append `import` alias names to the flat candidate list.

        Purpose:
            Feed both immediate cold-path dependency extraction and the
            ordered value stream used by later memo hits.

        Contract:
            - Non-Import nodes leave the context unchanged.
            - Matching aliases remain in source order, including dotted names.
            - The immutable event is appended before the mutable flat targets,
              preserving one event per AST node.

        Args:
            node:
                Current node from the shared walk.
            context:
                Shared per-module accumulator.

        Returns:
            None.

        Threading:
            Mutates one thread-confined FactContext; no shared cache is touched.

        Lifecycle / Cleanup:
            The context owns both accumulators until the analyzer freezes
            memo values and cleans the context.
        """
        if not isinstance(node, ast.Import):
            return
        alias_names = tuple(alias.name for alias in node.names)
        context.import_events.append(("import", 0, None, alias_names))
        for alias in node.names:
            context.flat_import_targets.append(alias.name)
