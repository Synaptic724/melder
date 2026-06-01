from typing import TYPE_CHECKING, ClassVar, Optional

from melder.__melder_registration_guard__ import __melder_registration_guard__ as _mrg
from melder.aether.spellbook.spell_compiler.spell_analyzer.spell_analyzer import (
    SpellAnalyzer,
)
from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.aether.aetheric_frame.dev_ops.spell_system_states.spell_system_states import (
        SpellSystemStates,
    )
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
        SpellCompilerArtifact,
    )
    from melder.aether.spellbook.spellbook import Spellbook


class CompilerPhase8(Cleanable):
    """
    Live compiler phase-8 wrapper over `SpellAnalyzer`.

    Purpose:
        Make the live phase-8 surface explicitly analyzer-backed instead of
        continuing to pretend that the old occurrence-plan builder is the
        current implementation.

    Contract:
        - Owns one `SpellAnalyzer`.
        - Consumes the existing spell/artifact pair.
        - Publishes analyzer-owned occurrence graph truth onto the artifact as
          `_occurrence_graph_analysis`.
        - Leaves downstream model / plan / creation fitting to phases 9-11.
        - Ignores old spellbook/system-state phase inputs because the analyzer
          already reads through the spell/artifact relationship.
        - Existing-creation spells are permitted through this wrapper; the
          analyzer strategy itself decides whether a graph artifact should be
          produced.

    Threading:
        Reusable facade with no per-call mutable state beyond the owned
        analyzer facade.

    Lifecycle:
        Reusable across many spells and owns only the analyzer facade it
        delegates to.
    """

    __melder_internal__: ClassVar[object] = _mrg.sentinel
    __slots__ = Cleanable.__slots__ + [
        "_spell_analyzer",
    ]

    def __init__(self) -> None:
        """
        Build the live phase-8 wrapper.

        Contract:
            - Owns its analyzer facade directly.
            - Reuses that facade across many spells until cleanup.
        """
        super().__init__()
        self._spell_analyzer = SpellAnalyzer()

    def cleanup(self) -> None:
        """
        Deterministically release phase-8 owned state.
        """
        if self._cleaned:
            return
        self._cleaned = True
        self._spell_analyzer.cleanup()
        del self._spell_analyzer

    def run(
            self,
            spell: "Spell",
            artifact: "SpellCompilerArtifact",
            spellbook: "Spellbook",
            spell_system_states: Optional["SpellSystemStates"],
    ) -> None:
        """
        Execute the analyzer-backed live phase 8.

        Purpose:
            Bridge the live phase scheduler onto the analyzer seam without
            forcing outer compiler callers to know about analyzer strategies or
            analyzer-owned artifact names.

        Contract:
            - Delegates directly to `SpellAnalyzer.analyze_occurrence(...)`.
            - Treats `spellbook` and `spell_system_states` as compatibility
              signature parameters only.
            - Publishes any analyzer output onto the supplied compiler
              artifact.

        Args:
            spell:
                Spell whose occurrence analysis should be computed.
            artifact:
                Compiler artifact receiving analyzer outputs.
            spellbook:
                Legacy phase argument retained only to preserve the current
                compiler call signature while this wrapper substitutes the live
                phase implementation.
            spell_system_states:
                Legacy phase argument retained only to preserve the current
                compiler call signature while this wrapper substitutes the live
                phase implementation.

        Returns:
            None.
        """
        _ = spellbook
        _ = spell_system_states
        self._spell_analyzer.analyze_occurrence(spell, artifact)
