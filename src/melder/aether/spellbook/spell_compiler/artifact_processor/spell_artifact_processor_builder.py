from typing import Optional, Sequence

from melder.aether.spellbook.spell_compiler.artifact_processor.spell_artifact_processor import (
    SpellArtifactProcessor,
)
from melder.aether.spellbook.spell_compiler.artifact_processor.spell_artifact_processor_strategy import (
    SpellArtifactProcessorStrategy,
)


class SpellArtifactProcessorBuilder:
    """
    Build `SpellArtifactProcessor` instances from an ordered strategy registry.

    Purpose:
        Keep the builder's role narrow and literal: it owns the ordered
        processor-strategy registry and produces configured processor
        instances.

    Contract:
        - Does not consume spell/artifact data directly.
        - Does not build the codegen model itself.
        - Preserves the supplied strategy order exactly.
        - Produces a processor configured with those strategies.

    Ownership:
        - Owns only the ordered processor strategy registry.
        - Produces configured `SpellArtifactProcessor` instances.

    Threading:
        - Builder state is immutable after construction.
    """

    __slots__ = [
        "_strategies",
    ]

    def __init__(
            self,
            *,
            strategies: Optional[Sequence[SpellArtifactProcessorStrategy]] = None,
    ) -> None:
        """
        Build one processor builder with an ordered strategy registry.

        Purpose:
            Freeze the ordered processor strategy list so later compiler code
            can ask the builder for processors without reassembling the
            registry each time.

        Contract:
            - `None` becomes an empty deterministic sequence.
            - Supplied strategy order is preserved exactly.

        Args:
            strategies:
                Optional ordered processor strategies to attach to built
                processors.

        Returns:
            None.
        """
        if strategies is None:
            self._strategies: tuple[SpellArtifactProcessorStrategy, ...] = ()
        else:
            self._strategies = tuple(strategies)

    def build(self) -> SpellArtifactProcessor:
        """
        Build one processor configured with this builder's strategy registry.

        Purpose:
            Produce the processor orchestrator that will later consume the
            artifact inputs, build the codegen model, and run the strategies.

        Contract:
            - Processor receives the stored ordered strategy tuple verbatim.
            - Builder does not read spell or artifact data here.

        Returns:
            SpellArtifactProcessor:
                Processor configured with the builder's strategy registry.
        """
        return SpellArtifactProcessor(
            strategies=self._strategies,
        )
