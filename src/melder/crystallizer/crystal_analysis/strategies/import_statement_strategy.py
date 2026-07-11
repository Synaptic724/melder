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

        Args:
            node:
                Current node from the shared walk.
            context:
                Shared per-module accumulator.

        Returns:
            None.
        """
        if not isinstance(node, ast.Import):
            return
        for alias in node.names:
            context.flat_import_targets.append(alias.name)
