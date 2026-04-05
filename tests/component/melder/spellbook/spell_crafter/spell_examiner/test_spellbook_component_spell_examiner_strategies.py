import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.spellbook.existence.existence import Existence
from melder.spellbook.spell_crafter.spell_examiner.profiles.binding_profile import (
    CallableBindingProfile,
    ClassBindingProfile,
    InstanceBindingProfile,
    SpellBindingKind,
)
from melder.spellbook.spell_crafter.spell_examiner.profiles.detailed_profile import (
    SpellDetailedProfile,
)
from melder.spellbook.spell_crafter.spell_examiner.strategies.binding_profile_strategy import (
    BindingProfileStrategy,
)
from melder.spellbook.spell_crafter.spell_examiner.strategies.resolution_profile_strategy import (
    ResolutionProfileStrategy,
)
from melder.spellbook.spellbook import Spellbook
from tests.mocks.spellbook.core_classes import BasicService
from tests.mocks.spellbook.protocols import IService


@pytest.fixture(autouse=True)
def reset_aether_singleton_for_component_examiner_strategies() -> None:
    """
    Purpose:
        Reset the Aether singleton for SpellExaminer strategy component tests.
    Contract:
        - Rebinds Spellbook and Conduit to a fresh Aether instance.
        - Restores a clean singleton after each test.
    Returns:
        None.
    """
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether
    yield
    Aether._reset_singleton_for_tests()
    aether = Aether()
    Spellbook._aether = aether
    Conduit._aether = aether


def _make_spellbook() -> Spellbook:
    """
    Purpose:
        Provide a Spellbook configured for component tests.
    Contract:
        - phase_scheduler_workers_per_spellbook is set to 1.
    Returns:
        Spellbook: Configured Spellbook instance.
    """
    spellbook = Spellbook()
    config = spellbook.get_configuration()
    config.set_property("phase_scheduler_workers_per_spellbook", 1)
    return spellbook


def _get_spell_by_version_id(spellbook: Spellbook, spell_id: str):
    """
    Purpose:
        Retrieve a local Spell by its version id.
    Contract:
        - Returns the first spell whose SpellIndex.current matches spell_id.
    Args:
        spellbook: Spellbook to search.
        spell_id: Version id to match.
    Returns:
        Spell or None: Matching spell instance or None if not found.
    """
    for spell in spellbook._spells.values():
        if spell.spell_index.current == spell_id:
            return spell
    return None


def test_component_binding_strategy_class_profile_filters_dunders() -> None:
    """
    Purpose:
        Validate class binding profiles exclude dunder methods by default.
    Contract:
        - Non-dunder methods are present.
        - __init__ is excluded when show_dunders is False.
    Returns:
        None.
    """
    profile = None

    class Widget:
        def __init__(self) -> None:
            self.value = 1

        def ping(self) -> str:
            return "pong"

    try:
        profile = BindingProfileStrategy(show_dunders=False).build_profile(Widget)
        assert isinstance(profile, ClassBindingProfile)
        assert profile.kind is SpellBindingKind.CLASS
        assert "ping" in profile.method_names
        assert "__init__" not in profile.method_names
    finally:
        if profile is not None:
            profile.cleanup()


def test_component_binding_strategy_class_profile_includes_dunders() -> None:
    """
    Purpose:
        Validate class binding profiles include dunders when enabled.
    Contract:
        - __init__ appears in method_names when show_dunders is True.
    Returns:
        None.
    """
    profile = None

    class Widget:
        def __init__(self) -> None:
            self.value = 1

        def ping(self) -> str:
            return "pong"

    try:
        profile = BindingProfileStrategy(show_dunders=True).build_profile(Widget)
        assert isinstance(profile, ClassBindingProfile)
        assert "__init__" in profile.method_names
        assert "ping" in profile.method_names
    finally:
        if profile is not None:
            profile.cleanup()


def test_component_binding_strategy_callable_profile_captures_signature() -> None:
    """
    Purpose:
        Validate callable binding profiles capture signature metadata.
    Contract:
        - Signature includes parameter names.
        - Parameter summaries include defaults and annotations when provided.
    Returns:
        None.
    """
    profile = None

    def build_service(service: BasicService, count: int = 3) -> BasicService:
        _ = count
        return service

    try:
        profile = BindingProfileStrategy().build_profile(build_service)
        assert isinstance(profile, CallableBindingProfile)
        assert profile.signature is not None
        assert "service" in profile.signature
        assert "count" in profile.signature
        summaries = {param.name: param for param in profile.parameters}
        assert summaries["service"].annotation_repr is not None
        assert summaries["count"].default_repr is not None
    finally:
        if profile is not None:
            profile.cleanup()


def test_component_binding_strategy_instance_profile_for_non_callable() -> None:
    """
    Purpose:
        Validate non-callable instances use InstanceBindingProfile.
    Contract:
        - Profile kind is INSTANCE.
        - type_name matches the instance type.
    Returns:
        None.
    """
    profile = None

    class Holder:
        pass

    instance = Holder()
    try:
        profile = BindingProfileStrategy().build_profile(instance)
        assert isinstance(profile, InstanceBindingProfile)
        assert profile.kind is SpellBindingKind.INSTANCE
        assert profile.type_name == "Holder"
    finally:
        if profile is not None:
            profile.cleanup()


def test_component_binding_strategy_callable_instance_treated_as_callable() -> None:
    """
    Purpose:
        Validate callable instances are treated as callables.
    Contract:
        - Profile kind is CALLABLE.
        - Signature includes the callable parameter.
    Returns:
        None.
    """
    profile = None

    class Factory:
        def __call__(self, value: int) -> int:
            return value

    instance = Factory()
    try:
        profile = BindingProfileStrategy().build_profile(instance)
        assert isinstance(profile, CallableBindingProfile)
        assert profile.kind is SpellBindingKind.CALLABLE
        assert profile.signature is not None
        assert "value" in profile.signature
    finally:
        if profile is not None:
            profile.cleanup()


def test_component_resolution_strategy_builds_requirements_for_class_spell() -> None:
    """
    Purpose:
        Validate resolution profiles build requirements from class spells.
    Contract:
        - DI parameters appear in iter_di_parameters().
        - Required holes appear in iter_required_holes().
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    profile = None

    class Consumer:
        def __init__(self, service: BasicService, count: int) -> None:
            self.service = service
            self.count = count

    try:
        spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        consumer_id = spellbook.bind(
            spell=Consumer,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, consumer_id)
        assert spell is not None

        profile = ResolutionProfileStrategy().build_profile(spell)
        requirements = profile.requirements
        di_names = {param.name for param in requirements.iter_di_parameters()}
        hole_names = {param.name for param in requirements.iter_required_holes()}
        assert "service" in di_names
        assert "count" in hole_names
    finally:
        if profile is not None:
            profile.cleanup()
        spellbook.cleanup()


def test_component_resolution_strategy_populates_spell_metadata() -> None:
    """
    Purpose:
        Validate resolution profiles reflect spell metadata.
    Contract:
        - spell_id, spellframe, and binding_name match the Spell.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    profile = None
    try:
        spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
            spellframe=IService,
            binding_name="primary",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        profile = ResolutionProfileStrategy().build_profile(spell)
        assert profile.spell_id == spell.spell_id
        assert profile.spellframe is IService
        assert profile.binding_name == "primary"
    finally:
        if profile is not None:
            profile.cleanup()
        spellbook.cleanup()


def test_component_resolution_strategy_sets_phase_artifacts_none() -> None:
    """
    Purpose:
        Validate resolution profiles leave phase artifacts unset.
    Contract:
        - symbolic_graph, resolution_frame, and validation are None.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    profile = None
    try:
        spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        profile = ResolutionProfileStrategy().build_profile(spell)
        assert profile.symbolic_graph is None
        assert profile.resolution_frame is None
        assert profile.validation is None
    finally:
        if profile is not None:
            profile.cleanup()
        spellbook.cleanup()


def test_component_resolution_strategy_existing_creation_has_no_parameters() -> None:
    """
    Purpose:
        Validate resolution profiles for existing creations are empty.
    Contract:
        - SpellRequirements has no parameters for existing creations.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    profile = None
    try:
        instance = BasicService(marker="existing")
        spell_id = spellbook.bind(
            spell=instance,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None
        assert spell.is_existing_creation is True

        profile = ResolutionProfileStrategy().build_profile(spell)
        assert profile.requirements.parameters == ()
    finally:
        if profile is not None:
            profile.cleanup()
        spellbook.cleanup()


def test_component_resolution_strategy_tracks_updated_spell_index() -> None:
    """
    Purpose:
        Validate requirements spell_id follows SpellIndex updates.
    Contract:
        - SpellRequirements uses the updated SpellIndex.current.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    profile = None
    try:
        spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        spell.spell_index.update("updated-id")
        profile = ResolutionProfileStrategy().build_profile(spell)
        assert profile.requirements.spell_id == "updated-id"
    finally:
        if profile is not None:
            profile.cleanup()
        spellbook.cleanup()


def test_component_ai_strategy_class_spell_builds_class_profile() -> None:
    """
    Purpose:
        Validate AI profiles include class profiles for class spells.
    Contract:
        - class_profile is populated for class spells.
        - callable_profile is also populated for class spells.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    profile = None
    try:
        spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        profile = SpellDetailedProfile.create_from_target(spell)
        assert profile.class_profile is not None
        assert profile.callable_profile is not None
        assert profile.class_profile.name == "BasicService"
    finally:
        if profile is not None:
            profile.cleanup()
        spellbook.cleanup()


def test_component_ai_strategy_callable_spell_builds_callable_profile() -> None:
    """
    Purpose:
        Validate AI profiles include callable profiles for function spells.
    Contract:
        - callable_profile is populated for function spells.
        - class_profile remains None for function spells.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    profile = None

    def build_service() -> BasicService:
        return BasicService()

    try:
        spell_id = spellbook.bind(
            spell=build_service,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        profile = SpellDetailedProfile.create_from_target(spell)
        assert profile.class_profile is None
        assert profile.callable_profile is not None
        assert profile.callable_profile.name == "build_service"
    finally:
        if profile is not None:
            profile.cleanup()
        spellbook.cleanup()


def test_component_ai_strategy_uses_provided_profiles() -> None:
    """
    Purpose:
        Validate AI profiles use provided binding and resolution profiles.
    Contract:
        - Returned profile references the supplied profile objects.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    profile = None
    binding_profile = None
    resolution_profile = None
    try:
        spell_id = spellbook.bind(
            spell=BasicService,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        profile = SpellDetailedProfile.create_from_target(spell)
        assert profile.binding_profile.original_object is BasicService
        assert profile.resolution_profile.spell_id == spell.spell_index.current
    finally:
        if profile is not None:
            profile.cleanup()
        spellbook.cleanup()


def test_component_ai_strategy_class_profile_includes_method_profile() -> None:
    """
    Purpose:
        Validate class profiles include method profiles for class spells.
    Contract:
        - The named method appears in class_profile.methods.
        - Method signature includes the expected parameter.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    profile = None

    class Worker:
        def run(self, value: int) -> str:
            return f"run:{value}"

    try:
        spell_id = spellbook.bind(
            spell=Worker,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        profile = SpellDetailedProfile.create_from_target(spell)
        class_profile = profile.class_profile
        assert class_profile is not None
        assert "run" in class_profile.methods
        assert class_profile.methods["run"].signature is not None
        assert "value" in class_profile.methods["run"].signature
    finally:
        if profile is not None:
            profile.cleanup()
        spellbook.cleanup()


def test_component_ai_strategy_callable_fallback_for_existing_creation() -> None:
    """
    Purpose:
        Validate callable existing creations use callable inspection fallback.
    Contract:
        - callable_profile is populated when spell.spell is callable.
    Returns:
        None.
    """
    spellbook = _make_spellbook()
    profile = None

    class CallableThing:
        def __call__(self, value: int) -> int:
            return value

    instance = CallableThing()
    try:
        spell_id = spellbook.bind(
            spell=instance,
            existence=Existence.unique,
            permissions="create",
        )
        spell = _get_spell_by_version_id(spellbook, spell_id)
        assert spell is not None

        profile = SpellDetailedProfile.create_from_target(spell)
        assert profile.class_profile is None
        assert profile.callable_profile is not None
        assert profile.callable_profile.signature is not None
        assert "value" in profile.callable_profile.signature
    finally:
        if profile is not None:
            profile.cleanup()
        spellbook.cleanup()


