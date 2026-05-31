from typing import Optional, Sequence

from melder.aether.spellbook.spell_compiler.spell_analyzer.spell_analyzer import (
    SpellAnalyzer,
)
from melder.aether.spellbook.spell_compiler.spell_analyzer.spell_analyzer_strategy import (
    SpellAnalyzerStrategy,
)


class SpellAnalyzerBuilder:
    """
    Build `SpellAnalyzer` instances from an ordered strategy registry.

    Purpose:
        Keep the builder narrow and literal: it owns the ordered
        analyzer-strategy registry and produces configured analyzer instances.

    Contract:
        - Does not consume spell or artifact data directly.
        - Does not perform analysis itself.
        - Preserves supplied strategy order exactly.
        - Produces a `SpellAnalyzer` configured with those strategies.

    Ownership:
        - Owns only the ordered analyzer-strategy registry.
        - Produces configured `SpellAnalyzer` instances.
    """

    __slots__ = [
        "_strategies",
    ]

    def __init__(
            self,
            *,
            strategies: Optional[Sequence[SpellAnalyzerStrategy]] = None,
    ) -> None:
        """
        Build one analyzer builder with an ordered strategy registry.

        Args:
            strategies:
                Optional ordered analyzer strategies to attach to built
                analyzers.
        """
        if strategies is None:
            self._strategies: tuple[SpellAnalyzerStrategy, ...] = ()
        else:
            self._strategies = tuple(strategies)

    def build(self) -> SpellAnalyzer:
        """
        Build one analyzer configured with this builder's strategy registry.

        Returns:
            SpellAnalyzer:
                Analyzer configured with the builder's strategy registry.
        """
        return SpellAnalyzer(
            strategies=self._strategies,
        )
