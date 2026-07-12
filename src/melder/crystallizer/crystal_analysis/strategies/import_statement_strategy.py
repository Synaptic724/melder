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
    """

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
