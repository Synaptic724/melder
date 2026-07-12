"""
Fact strategy for `from ... import ...` statements.

Ports the historical extractor's from-import behavior exactly: relative
bases resolve through `importlib.util.resolve_name` against the module's
package context; each non-star imported member is probed with `find_spec`
and contributes a submodule candidate when it IS a submodule; the resolved
base itself is appended AFTER its members (order matters - manifest and
walk order are byte-compatible with the pre-decomposition extractor); and
the member map is retained for diagnostics even when members are plain
names rather than submodules.

Lane: EPIC-2026-07-09-crystallizer-subsystem-decomposition, story S1.
"""

import ast
import importlib.util
from typing import List, Optional

from melder.crystallizer.crystal_analysis.strategies.base_strategy import (
    CrystalFactStrategy,
    FactContext,
)


class FromImportStatementStrategy(CrystalFactStrategy):
    """
    Extract dependency candidates and member maps from from-imports.

    Purpose:
        Contribute resolved from-import bases, probed submodule members,
        and the `from ... import ...` diagnostics map for one module.

    Contract:
        - Handles `ast.ImportFrom` nodes only.
        - Relative levels resolve against `context.current_package`;
          unresolvable relative bases are skipped silently (historical
          behavior - the walk stays honest through the unknown bucket).
        - Star imports are recorded in the member map but never probed.
        - Candidate order per node: probed member submodules first (in
          alias order), then the base module.
        - Every matching node first records a raw value event containing its
          relative level, unresolved module name, and alias-name tuple.
          Recording occurs even when the live relative base cannot resolve.
        - Memo replay consumes that raw event and repeats relative resolution
          plus find_spec probing; only source-stable syntax is reused.
        - Events retain no AST node, alias object, module, or spec reference.
    """

    __slots__ = ()

    @property
    def name(self) -> str:
        """
        Return the stable strategy name.

        Returns:
            str: `from_import_statement`.
        """
        return "from_import_statement"

    def visit_node(self, node: ast.AST, context: FactContext) -> None:
        """
        Resolve one from-import node into candidates and member entries.

        Purpose:
            Capture source syntax separately from the live environment
            decisions needed for the current dependency graph.

        Contract:
            - Non-ImportFrom nodes leave the context unchanged.
            - The raw immutable event is appended before resolution.
            - Relative bases and candidate submodules resolve live.
            - A failed find_spec probe means only that the member is not
              promoted to a submodule candidate; the base/member map remains.

        Args:
            node:
                Current node from the shared walk.
            context:
                Shared per-module accumulator.

        Returns:
            None.

        Threading:
            Mutates one thread-confined FactContext. find_spec observes the
            process import environment but no cache lock is held.

        Lifecycle / Cleanup:
            The context owns the event until the analyzer freezes its values.
        """
        if not isinstance(node, ast.ImportFrom):
            return
        context.import_events.append(
            (
                "from",
                node.level,
                node.module,
                tuple(alias.name for alias in node.names),
            )
        )
        if node.level > 0:
            relative_name = "." * node.level
            if node.module:
                relative_name += node.module
            resolved_base = self._resolve_relative_import_target(
                current_package=context.current_package,
                relative_module_name=relative_name,
            )
        else:
            resolved_base = node.module
        if not resolved_base:
            return

        imported_names: List[str] = []
        for alias in node.names:
            imported_names.append(alias.name)
            if alias.name != "*":
                candidate_module_name = "{0}.{1}".format(
                    resolved_base,
                    alias.name,
                )
                try:
                    spec = importlib.util.find_spec(candidate_module_name)
                except Exception:
                    spec = None
                if spec is not None:
                    context.flat_import_targets.append(candidate_module_name)
        context.from_import_targets.setdefault(resolved_base, []).extend(
            imported_names
        )
        context.flat_import_targets.append(resolved_base)

    @staticmethod
    def _resolve_relative_import_target(
            *,
            current_package: str,
            relative_module_name: str,
    ) -> Optional[str]:
        """
        Resolve one relative import target into an absolute module name.

        Purpose:
            Use one historical resolution rule for cold extraction and
            memo-event replay.

        Contract:
            Calls importlib.util.resolve_name with the supplied package.
            Resolution failures are treated as an honest unresolved base and
            return None; no module is imported or retained here.

        Args:
            current_package:
                Package context of the module being parsed.
            relative_module_name:
                Relative import string such as `.helper` or `..pkg.mod`.

        Returns:
            Optional[str]:
                Absolute module name, or None when the relative path
                cannot be resolved safely.

        Threading:
            Stateless resolution; no strategy or memo state is mutated.
        """
        try:
            return importlib.util.resolve_name(
                relative_module_name,
                current_package,
            )
        except Exception:
            return None
