from threading import RLock
from types import SimpleNamespace
from typing import Any, Optional

import pytest

from melder.aether.conduit.meld.creation_context.creation_context import CreationContext
from melder.aether.conduit.meld.creation_context.creation_context_builder import (
    CreationContextBuilder,
)
from melder.aether.conduit.meld.creation_context.creation_context_factory import (
    CreationContextFactory,
)
from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)
from melder.aether.spellbook.existence.existence import Existence
from melder.utilities.synchronization.counter_switch import CounterSwitch
from melder.utilities.synchronization.creation_gate_controller import (
    CreationGateController,
)


class _CompilerArtifactStub:
    """
    Minimal compiler-artifact container required by CreationContextBuilder.
    """

    def __init__(self) -> None:
        """
        Initialize default no-overrides/overrides codegen artifacts.
        """
        self._phase12_no_overrides_executor = lambda _context: "built"
        self._execution_plan_phase11_no_overrides = SimpleNamespace(
            fast_transient_plan=None,
        )
        self._override_patch_map_phase10 = None
        self._root_blueprint_phase5 = None
        self._codegen_ir = None


_DEFAULT_ARTIFACT = object()


class _CachedContextStub:
    """
    Simple spell-owned context cache stub with cleanup tracking.
    """

    def __init__(self, *, cleaned: bool = False) -> None:
        """
        Initialize one cached-context stub.
        """
        self._cleaned = cleaned
        self.cleanup_calls = 0

    @property
    def is_cleaned(self) -> bool:
        """
        Return whether this cached context is already cleaned.
        """
        return self._cleaned

    def cleanup(self) -> None:
        """
        Mark the stub as cleaned and count cleanup calls.
        """
        self.cleanup_calls += 1
        self._cleaned = True


class _SpellStub:
    """
    Minimal spell stub exposing the contract used by builder/factory tests.
    """

    def __init__(
            self,
            *,
            spell_id: str = "spell-1",
            existence: Existence = Existence.unique,
            is_existing_creation: bool = False,
            has_mutation_override: bool = False,
            artifact: Any = _DEFAULT_ARTIFACT,
            creation_context: Optional[Any] = None,
    ) -> None:
        """
        Initialize a spell-shaped object for CreationContext tests.
        """
        self.spell_id = spell_id
        self.spell_name = spell_id
        self.spell_index = SimpleNamespace(
            current=spell_id,
            id=f"lineage-{spell_id}",
        )
        self.existence = existence
        self.is_existing_creation = is_existing_creation
        self.user_created_object = object() if is_existing_creation else None
        self.has_mutation_override = has_mutation_override
        self.execution_plan_dispatch_route = None

        self._owner_creations = SimpleNamespace(_creations={}, _lock=RLock())
        self._spellbook = SimpleNamespace(_spell_id_pool={})
        if artifact is _DEFAULT_ARTIFACT:
            self._compiler_artifact = _CompilerArtifactStub()
        else:
            self._compiler_artifact = artifact
        if creation_context is not None and creation_context.is_cleaned:
            self._creation_context = None
        else:
            self._creation_context = creation_context
        if self._creation_context is None:
            self._creation_context_switch = CounterSwitch(state=0)
        else:
            self._creation_context_switch = CounterSwitch(state=2)
        self._lock = RLock()
        self._cleaned = False

    def check_cleaned(self) -> None:
        """
        Enforce the owned spell cleaned contract.
        """
        if self._cleaned:
            raise RuntimeError("Spell has been cleaned.")


def test_build_for_spell_returns_creation_context_instance() -> None:
    """
    Verify factory build returns a spell-bound CreationContext.

    Contract:
        - build_for_spell returns a CreationContext instance.
        - The returned context is bound to the same spell.
    """
    spell = _SpellStub()
    factory = CreationContextFactory(
        creation_gate_controller=CreationGateController(),
    )
    context = factory.build_for_spell(spell)
    try:
        assert isinstance(context, CreationContext)
        assert context._spell is spell
        assert context._spell_id == spell.spell_id
    finally:
        context.cleanup()
        factory.cleanup()


def test_get_or_build_for_spell_publishes_and_reuses_context() -> None:
    """
    Verify get-or-build publishes to spell and reuses cached context.

    Contract:
        - First call builds and publishes spell._creation_context.
        - Second call returns the same published context.
    """
    spell = _SpellStub()
    factory = CreationContextFactory(
        creation_gate_controller=CreationGateController(),
    )
    context_a = factory.get_or_build_for_spell(spell)
    context_b = factory.get_or_build_for_spell(spell)
    try:
        assert spell._creation_context is context_a
        assert context_b is context_a
    finally:
        context_a.cleanup()
        factory.cleanup()


def test_get_or_build_for_spell_replaces_cleaned_cache_entry() -> None:
    """
    Verify get-or-build replaces cleaned spell-owned contexts.

    Contract:
        - Cleaned cached context is treated as cache miss.
        - Newly built context is published onto the spell.
    """
    stale_context = _CachedContextStub(cleaned=True)
    spell = _SpellStub(creation_context=stale_context)
    factory = CreationContextFactory(
        creation_gate_controller=CreationGateController(),
    )
    new_context = factory.get_or_build_for_spell(spell)
    try:
        assert new_context is not stale_context
        assert spell._creation_context is new_context
    finally:
        new_context.cleanup()
        factory.cleanup()


def test_build_and_bind_for_spell_replaces_previous_context() -> None:
    """
    Verify build-and-bind replaces and cleans prior spell-owned context.

    Contract:
        - Existing context is cleaned during replacement.
        - Spell ends up owning the newly built context.
    """
    previous_context = _CachedContextStub(cleaned=False)
    spell = _SpellStub(creation_context=previous_context)
    factory = CreationContextFactory(
        creation_gate_controller=CreationGateController(),
    )
    new_context = factory.build_and_bind_for_spell(spell)
    try:
        assert previous_context.cleanup_calls == 1
        assert spell._creation_context is new_context
    finally:
        new_context.cleanup()
        factory.cleanup()


@pytest.mark.parametrize(
    "existence, expected",
    (
        (Existence.unique, CreationContext.ROUTE_SHARED),
        (Existence.unique_per_conduit, CreationContext.ROUTE_UNIQUE_PER_CONDUIT),
        (Existence.unique_per_spell_space, CreationContext.ROUTE_SPELLSPACE),
        (Existence.many, CreationContext.ROUTE_MANY),
    ),
)
def test_builder_resolve_route_key_maps_existence_variants(
        existence: Existence,
        expected: str,
) -> None:
    """
    Verify builder route-key mapping matches spell existence policy.
    """
    spell = _SpellStub(existence=existence)
    assert CreationContextBuilder._resolve_route_key(spell) == expected


def test_builder_requires_compiler_artifact_for_non_existing_creation() -> None:
    """
    Verify builder rejects non-existing-creation spells without compiler artifacts.

    Contract:
        - build raises RuntimeError when compiler artifacts are missing.
    """
    builder = CreationContextBuilder()
    spell = _SpellStub(artifact=None)
    spell.is_existing_creation = False
    with pytest.raises(RuntimeError, match="Cannot build CreationContext"):
        builder.build(spell)



def test_factory_build_for_spell_dynamic_attaches_lineage_gate() -> None:
    """
    Verify dynamic factory build injects shared spell-index gate metadata.

    Contract:
        - Built context stores dynamic mode.
        - Built context stores shared spell-index gate reference.
        - Built context stores spell-index id used by runtime gate diagnostics.
    """
    spell = _SpellStub(spell_id="spell-dynamic")
    controller = CreationGateController()
    factory = CreationContextFactory(
        dynamic_environment=True,
        creation_gate_controller=controller,
    )
    context = factory.build_for_spell(spell)
    try:
        index_id = spell.spell_index.id
        assert context._dynamic_environment is True
        assert context._creation_gate_index_id == index_id
        assert context._creation_gate is controller.get_spell_index_gate(index_id)
    finally:
        context.cleanup()
        factory.cleanup()

