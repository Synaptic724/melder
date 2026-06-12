from unittest.mock import MagicMock

from melder.aether.conduit.meld.conduit_meld import ConduitMeld
from melder.aether.spellbook.bind.spell_index import SpellIndex
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spell_compiler.spell_compiler_artifact import (
    SpellCompilerArtifact,
)
from melder.aether.spellbook.spell_compiler.spell_compiler import (
    SpellCompiler,
)
from melder.aether.spellbook.spell_compiler.spell_compiler_system import (
    SpellCompilerSystem,
)
from melder.aether.spellbook.spell_types.spell_types import SpellType
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.utilities.general_base.cleanable import Cleanable


class _RecordingStates:
    """Minimal spell-system-state stub for foundation spell tests."""

    def mark_structural_change(self, spell_index, reason=None):
        """Accept structural-change notifications without side effects."""
        return None

    def get_by_index_id(self, index_id):
        """Return a stable dummy state for the supplied lineage id."""
        return "state:{0}".format(index_id)


class _SpellbookStub:
    """Minimal spellbook stub with the surfaces needed by foundation tests."""

    def __init__(self):
        """Initialize empty spellbook maps plus validator/state stubs."""
        self._spell_system_states = _RecordingStates()
        self._spell_validator = MagicMock()
        self._spells = {}
        self._contracted_spells = {}
        self._spells_by_id = {}
        self._contracted_spells_by_id = {}
        self._spell_id_pool = {}
        self._lookup_spells = {}
        self._lookup_contracted_spells = {}
        self.cleanup_calls = []

    def cleanup_and_remove_spell(self, spell):
        """Mirror spellbook-owned spell teardown delegation for the foundation tests."""
        self.cleanup_calls.append(spell)
        spell._spellbook_cleanup = True
        spell.cleanup()
        return None


class _CreationStoreStub:
    """Minimal creations stub for Meld foundation tests."""

    def __init__(self) -> None:
        """Initialize the conduit-owned identity used by ConduitMeld."""
        self.owner_conduit_id = "conduit-1"


class _CleanableArtifact(Cleanable):
    """Track whether cleanup was called by SpellCompilerArtifact cleanup."""

    __slots__ = Cleanable.__slots__ + [
        "_was_cleaned",
    ]

    def __init__(self) -> None:
        """Initialize the recording cleanup artifact."""
        super().__init__()
        self._was_cleaned = False

    def cleanup(self) -> None:
        """Record cleanup and flip the cleaned flag."""
        self._was_cleaned = True
        self._cleaned = True


def _make_spell() -> Spell:
    """Build one minimal live Spell instance for foundation tests."""
    spellbook = _SpellbookStub()
    spell = Spell(
        spell=lambda: None,
        spell_index=SpellIndex("foundation-id"),
        spellframe=None,
        binding_name=None,
        spell_name="FoundationSpell",
        existence=Existence.unique,
        spell_type=SpellType.SPELL,
        spell_id="foundation-fingerprint",
        permissions=Permissions.read,
        aetheric_frame="default",
        spellbook=spellbook,
    )
    return spell


def test_spell_initializes_compiler_artifact_foundation() -> None:
    """Spell should own a SpellCompilerArtifact immediately at construction."""
    spell = _make_spell()

    assert isinstance(spell._compiler_artifact, SpellCompilerArtifact)
    assert spell._compiler_artifact.spell_id == spell.spell_id
    assert spell._compiler_artifact._requirements is None
    assert spell._compiler_artifact._validated_phase4 is False


def test_spell_cleanup_cleans_compiler_artifact_foundation() -> None:
    """Spell cleanup should cleanup the owned compiler artifact foundation."""
    spell = _make_spell()
    attached = _CleanableArtifact()
    spell._compiler_artifact._requirements = attached

    spell.cleanup()

    assert attached._was_cleaned is True
    assert not hasattr(spell, "_compiler_artifact")


def test_spell_compiler_system_owns_spell_compiler() -> None:
    """SpellCompilerSystem should own a concrete SpellCompiler instance."""
    spell = _make_spell()
    compiler_system = SpellCompilerSystem()

    assert isinstance(compiler_system._spell_compiler, SpellCompiler)


def test_meld_creates_spell_compiler_system_on_first_demand() -> None:
    """Meld should lazily create the compiler-system foundation surface."""
    spellbook = _SpellbookStub()
    creations = _CreationStoreStub()

    meld = ConduitMeld(
        creations=creations,
        spellbook=spellbook,
        conduit_id=creations.owner_conduit_id,
        resolution_conduit_id=creations.owner_conduit_id,
    )

    assert meld._spell_compiler_system is None
    compiler_system = meld._get_spell_compiler_system()
    assert isinstance(compiler_system, SpellCompilerSystem)
    assert meld._spell_compiler_system is compiler_system

