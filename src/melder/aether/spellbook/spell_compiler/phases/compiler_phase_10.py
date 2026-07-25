import threading
from typing import TYPE_CHECKING, ClassVar

from melder.utilities.general_base.cleanable import Cleanable

if TYPE_CHECKING:
    from melder.aether.spellbook.spell import Spell
    from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_planner import (
        SpellCodegenPlanner,
    )
    from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
        SpellCompilerArtifact,
    )


class CompilerPhase10(Cleanable):
    """
    Live compiler phase-10 wrapper over `SpellCodegenPlanner`.

    Purpose:
        Make the live phase-10 surface explicitly planner-backed instead of
        continuing to expose the old patch-map phase implementation as if it
        were still the current path.

    Contract:
        - Owns one `SpellCodegenPlanner`.
        - Consumes the artifact after processor work completed.
        - Publishes `SpellCodegenPlan` onto the artifact as
          `_spell_codegen_plan`.
        - Uses the processor-owned model as its only planning input.
        - Does not emit runtime-ready creation artifacts.

    Threading:
        Reusable facade with no per-call mutable state beyond the owned
        planner facade.

    Lifecycle:
        Owns only the planner facade it delegates to.
    """

    __slots__ = Cleanable.__slots__ + [
        "_codegen_planner",
    ]

    # Lazy-import guard shared across instances (rare path: first plan build
    # in the process). The planner module subtree (~11ms import) is deferred
    # so cache full-hit conjures, which never run phase 10, never load it.
    _lazy_import_lock: ClassVar[threading.Lock] = threading.Lock()

    def __init__(self) -> None:
        """
        Build the live phase-10 wrapper.

        Contract:
            - Defers planner construction (and the codegen_planner module
              import) to the first `run(...)` call so phase objects stay free
              to construct on conjure paths that skip plan phases.
        """
        super().__init__()
        self._codegen_planner: "SpellCodegenPlanner | None" = None

    def cleanup(self) -> None:
        """
        Deterministically release phase-10 owned state.
        """
        if self._cleaned:
            return
        self._cleaned = True
        if self._codegen_planner is not None:
            self._codegen_planner.cleanup()
        del self._codegen_planner

    def run(
            self,
            spell: "Spell",
            artifact: "SpellCompilerArtifact",
    ) -> None:
        """
        Execute the planner-backed live phase 10.

        Purpose:
            Build the planner-owned execution-semantics artifact from the
            processor-owned model already stored on the compiler artifact.

        Contract:
            - Delegates directly to `SpellCodegenPlanner.build(...)`.
            - Treats the `spell` parameter as compatibility-only for the
              current public phase signature.

        Args:
            spell:
                Legacy phase argument retained so the public compiler method
                shape stays stable while this wrapper substitutes the live
                implementation.
            artifact:
                Compiler artifact receiving `SpellCodegenPlan`.

        Returns:
            None.
        """
        _ = spell
        planner = self._codegen_planner
        if planner is None:
            with CompilerPhase10._lazy_import_lock:
                planner = self._codegen_planner
                if planner is None:
                    from melder.aether.spellbook.spell_compiler.codegen_planner.spell_codegen_planner import (
                        SpellCodegenPlanner,
                    )

                    planner = SpellCodegenPlanner()
                    self._codegen_planner = planner
        planner.build(artifact)
