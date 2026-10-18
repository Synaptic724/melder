"""
Unit: the four managed bind options at the Bind seam (STORY-2026-10-15-managed_bind_options, S2).

`Existence.managed_spell_quantity` bindings carry `managed_spell_mode`, `managed_spell_limit`,
`managed_spell_timeout_seconds` and `managed_spell_reset_methods`. Bind normalizes them once - after the profile,
before the fingerprint - refuses every malformed combination before a Spell exists, hands the normalized values
to the Spell, and never hashes them: they are settings of the one spell, not part of its spell_id (owner ruling,
2026-10-17: "the bind call itself shouldn't impact the actual SHA256"; 0.2.8242-0.2.8253 appended a `managed:`
part, STORY-2026-10-17-release_routes_parked_version_objects_to_active_pool removed it). Every other binding keeps
its spell id byte for byte: the literal ids below were computed on 0.2.8241, before the options existed
(context_compass/artifacts/managed_spell_quantity_20261015/runs/s2_golden_ids_pre.txt).
"""
import hashlib
import math
from typing import Any, Dict, List

import pytest

from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.spellbook.bind.bind import Bind
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.existence.managed_spell_mode import ManagedSpellMode
from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.binding_profile import (
    CallableBindingProfile,
    ClassBindingProfile,
    InstanceBindingProfile,
    SpellBindingKind,
    SpellBindingProfile,
)
from melder.aether.spellbook.spell_compiler.spell_examiner.profiles.general_profile import (
    SpellGeneralProfile,
)


# -------------------------
# Targets and test doubles
# -------------------------


class PooledTarget:
    """
    A managed target: two zero-argument reset methods, a property and a plain class attribute.
    """

    label = "not callable"

    def reset(self) -> None:
        """Zero-argument reset."""

    def clear(self) -> None:
        """A second zero-argument reset."""

    @property
    def size(self) -> int:
        """A property is not a reset method."""
        return 1


class StubSpell:
    """
    Records the keywords Bind constructs a Spell with; counts constructions.
    """

    constructed: List["StubSpell"] = []

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Capture the construction keywords."""
        self.args = args
        self.kwargs = kwargs
        StubSpell.constructed.append(self)


class StubGeneralProfile(SpellGeneralProfile):
    """
    General profile whose completion step records nothing (the stub spell is not a real Spell).
    """

    def complete_with_spell(self, spell: Any) -> None:
        """Accept the stub spell."""
        self.resolution_profile = object()


class StubExaminer:
    """
    Examiner double returning one fixed binding profile for any target.
    """

    def __init__(self, profile: SpellBindingProfile) -> None:
        """Hold the profile to return."""
        self.profile = profile

    def create_profile(self, obj: Any, profile_name: str, show_dunders: bool = False, max_repr: int = 120) -> Any:
        """Return the fixed profile wrapped in a general profile."""
        return StubGeneralProfile(binding_profile=self.profile, resolution_profile=None)

    def cleanup(self) -> None:
        """Nothing to release."""


class StubSpellbook:
    """
    The two Spellbook reads Bind does not make here; Bind only stores the owner.
    """

    def __init__(self) -> None:
        """No configured disposal names."""
        self._configured_disposal_method_names = frozenset()


def golden_class_profile(original_object: Any = PooledTarget) -> ClassBindingProfile:
    """
    The class profile the 0.2.8241 literal ids were computed from (module "golden_mod").
    """
    return ClassBindingProfile(
        kind=SpellBindingKind.CLASS,
        original_object=original_object,
        name="Pooled",
        qualname="Pooled",
        module="golden_mod",
        bases=["object"],
        mro=["Pooled", "object"],
        annotations={"size": int},
        origin_file=None,
        origin_line=None,
        init_signature="(self, size: int = 1)",
        source_preview="",
        is_dataclass=False,
        decorated=False,
        method_names=["reset", "close"],
    )


def golden_callable_profile() -> CallableBindingProfile:
    """The callable profile of the literal ids."""
    return CallableBindingProfile(
        kind=SpellBindingKind.CALLABLE,
        original_object=lambda: None,
        object_id="obj-1",
        name="factory",
        qualname="factory",
        module="golden_mod",
        parameters=[],
        repr_string="<function factory>",
        type_name="function",
        signature="()",
        lambda_function=False,
        builtin_module=False,
        extension_module=False,
    )


def golden_instance_profile() -> InstanceBindingProfile:
    """The existing-object profile of the literal ids."""
    return InstanceBindingProfile(
        kind=SpellBindingKind.INSTANCE,
        original_object=object(),
        type_name="Pooled",
        module="golden_mod",
        repr_string="<Pooled>",
    )


@pytest.fixture(autouse=True)
def patch_bind(monkeypatch: pytest.MonkeyPatch) -> Any:
    """
    Replace Spell with the recording double and neutralize the internal-bind guard.

    raising=True keeps both seams loud: a rename makes this fixture fail instead of patching nothing.
    """
    StubSpell.constructed = []
    monkeypatch.setattr("melder.aether.spellbook.bind.bind.Spell", StubSpell, raising=True)
    monkeypatch.setattr(
        "melder.aether.spellbook.bind.bind.assert_allowed", lambda *a, **k: None, raising=True,
    )
    yield


def bind_with(
        monkeypatch: pytest.MonkeyPatch,
        existence: Existence,
        *,
        profile: Any = None,
        spell: Any = PooledTarget,
        **options: Any,
) -> StubSpell:
    """
    Bind `spell` through a fresh Bind whose examiner returns `profile` (the golden class profile by default).
    """
    chosen = golden_class_profile() if profile is None else profile
    monkeypatch.setattr(
        "melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(chosen), raising=True,
    )
    binder = Bind(StubSpellbook())
    try:
        return binder.bind(Permissions.create, existence, aetheric_frame="f", spell=spell, **options)
    finally:
        binder.cleanup()


def managed_values(spell: StubSpell) -> tuple:
    """The four normalized values Bind handed the Spell."""
    return (
        spell.kwargs["managed_spell_mode"],
        spell.kwargs["managed_spell_limit"],
        spell.kwargs["managed_spell_timeout_seconds"],
        spell.kwargs["managed_spell_reset_methods"],
    )


# -------------------------
# ManagedSpellMode
# -------------------------


def test_managed_spell_mode_has_three_members_whose_str_is_the_bare_name() -> None:
    """The mode vocabulary is elastic, limited_quantity and queue; str() round-trips through the enum by name."""
    assert [member.name for member in ManagedSpellMode] == ["elastic", "limited_quantity", "queue"]
    for member in ManagedSpellMode:
        assert str(member) == member.name
        assert ManagedSpellMode[str(member)] is member


# -------------------------
# Normalization
# -------------------------


def test_managed_binding_without_options_is_elastic_with_256_idle_objects(monkeypatch: pytest.MonkeyPatch) -> None:
    """A managed binding with no options gets the elastic mode, the 256 idle cap, no timeout and no resets."""
    spell = bind_with(monkeypatch, Existence.managed_spell_quantity)
    assert managed_values(spell) == (ManagedSpellMode.elastic, 256, None, ())


@pytest.mark.parametrize("mode", [ManagedSpellMode.limited_quantity, "limited_quantity", "LIMITED_QUANTITY"])
def test_mode_is_accepted_as_member_or_name_in_any_case(monkeypatch: pytest.MonkeyPatch, mode: Any) -> None:
    """The member and its name (any case) select the same mode."""
    spell = bind_with(
        monkeypatch, Existence.managed_spell_quantity, managed_spell_mode=mode, managed_spell_limit=4,
    )
    assert managed_values(spell) == (ManagedSpellMode.limited_quantity, 4, None, ())


def test_elastic_limit_is_the_idle_cap_when_given(monkeypatch: pytest.MonkeyPatch) -> None:
    """An explicit elastic limit replaces the 256 default."""
    spell = bind_with(
        monkeypatch, Existence.managed_spell_quantity, managed_spell_mode="elastic", managed_spell_limit=12,
    )
    assert managed_values(spell) == (ManagedSpellMode.elastic, 12, None, ())


def test_queue_mode_keeps_limit_and_stores_the_timeout_as_float(monkeypatch: pytest.MonkeyPatch) -> None:
    """A queue binding keeps its limit and its timeout in seconds as a float."""
    spell = bind_with(
        monkeypatch,
        Existence.managed_spell_quantity,
        managed_spell_mode=ManagedSpellMode.queue,
        managed_spell_limit=2,
        managed_spell_timeout_seconds=3,
    )
    mode, limit, timeout, resets = managed_values(spell)
    assert (mode, limit, resets) == (ManagedSpellMode.queue, 2, ())
    assert timeout == 3.0 and type(timeout) is float


@pytest.mark.parametrize("names", [["clear", "reset"], ("clear", "reset")])
def test_reset_methods_keep_their_order_as_a_tuple(monkeypatch: pytest.MonkeyPatch, names: Any) -> None:
    """Reset names are kept in the order given, as a tuple, whether a list or a tuple was passed."""
    spell = bind_with(monkeypatch, Existence.managed_spell_quantity, managed_spell_reset_methods=names)
    assert spell.kwargs["managed_spell_reset_methods"] == ("clear", "reset")


@pytest.mark.parametrize("existence", [member for member in Existence if member is not Existence.managed_spell_quantity])
def test_other_existences_carry_no_managed_options(monkeypatch: pytest.MonkeyPatch, existence: Existence) -> None:
    """A binding of any other existence hands the Spell None, None, None and an empty reset tuple."""
    spell = bind_with(monkeypatch, existence)
    assert managed_values(spell) == (None, None, None, ())


@pytest.mark.parametrize(
    "option, value",
    [
        ("managed_spell_mode", "elastic"),
        ("managed_spell_limit", 4),
        ("managed_spell_timeout_seconds", 1.0),
        ("managed_spell_reset_methods", ["reset"]),
        ("managed_spell_reset_methods", []),
    ],
)
def test_an_option_on_another_existence_is_refused(monkeypatch: pytest.MonkeyPatch, option: str, value: Any) -> None:
    """Any managed option on a non-managed binding raises ValueError naming the option and the remedy."""
    with pytest.raises(ValueError, match=option) as caught:
        bind_with(monkeypatch, Existence.unique, **{option: value})
    assert "Existence.managed_spell_quantity" in str(caught.value)
    assert StubSpell.constructed == []


def test_managed_refuses_a_function_or_method(monkeypatch: pytest.MonkeyPatch) -> None:
    """A callable target cannot be managed: TypeError says classes only, before the callable rules run."""
    with pytest.raises(TypeError, match="classes only") as caught:
        bind_with(monkeypatch, Existence.managed_spell_quantity, profile=golden_callable_profile(), spell=print)
    assert "a function or method" in str(caught.value)


def test_managed_refuses_an_existing_object(monkeypatch: pytest.MonkeyPatch) -> None:
    """An existing object cannot be managed: TypeError says classes only."""
    with pytest.raises(TypeError, match="classes only") as caught:
        bind_with(
            monkeypatch, Existence.managed_spell_quantity, profile=golden_instance_profile(), spell=PooledTarget(),
        )
    assert "an existing object" in str(caught.value)


def test_unknown_mode_name_is_refused_with_the_three_names(monkeypatch: pytest.MonkeyPatch) -> None:
    """An unknown mode name raises ValueError listing the valid names."""
    with pytest.raises(ValueError, match="Unknown managed_spell_mode 'pooled'") as caught:
        bind_with(monkeypatch, Existence.managed_spell_quantity, managed_spell_mode="pooled")
    for name in ("elastic", "limited_quantity", "queue"):
        assert name in str(caught.value)


@pytest.mark.parametrize("mode", [1, Existence.unique, object()])
def test_mode_of_another_type_is_refused(monkeypatch: pytest.MonkeyPatch, mode: Any) -> None:
    """A mode that is neither a ManagedSpellMode member nor a string raises TypeError."""
    with pytest.raises(TypeError, match="managed_spell_mode must be a ManagedSpellMode member or its name"):
        bind_with(monkeypatch, Existence.managed_spell_quantity, managed_spell_mode=mode)


@pytest.mark.parametrize("mode", ["limited_quantity", "queue"])
def test_limited_and_queue_modes_require_a_limit(monkeypatch: pytest.MonkeyPatch, mode: str) -> None:
    """limited_quantity and queue have no default limit."""
    with pytest.raises(ValueError, match=f"managed_spell_mode '{mode}' needs managed_spell_limit"):
        bind_with(
            monkeypatch, Existence.managed_spell_quantity, managed_spell_mode=mode,
            managed_spell_timeout_seconds=1.0 if mode == "queue" else None,
        )


@pytest.mark.parametrize("limit", [True, "4", 2.0])
def test_limit_must_be_an_int(monkeypatch: pytest.MonkeyPatch, limit: Any) -> None:
    """A bool, a string or a float limit raises TypeError."""
    with pytest.raises(TypeError, match="managed_spell_limit must be an int"):
        bind_with(monkeypatch, Existence.managed_spell_quantity, managed_spell_limit=limit)


@pytest.mark.parametrize("limit", [0, -3])
def test_limit_must_be_at_least_one(monkeypatch: pytest.MonkeyPatch, limit: int) -> None:
    """A limit below 1 raises ValueError naming it."""
    with pytest.raises(ValueError, match=f"managed_spell_limit must be at least 1, got {limit}"):
        bind_with(
            monkeypatch, Existence.managed_spell_quantity, managed_spell_mode="limited_quantity",
            managed_spell_limit=limit,
        )


@pytest.mark.parametrize("mode", ["elastic", "limited_quantity"])
def test_a_timeout_outside_the_queue_mode_is_refused(monkeypatch: pytest.MonkeyPatch, mode: str) -> None:
    """Only a queue waits, so only a queue takes a timeout."""
    with pytest.raises(ValueError, match="applies only to managed_spell_mode 'queue'"):
        bind_with(
            monkeypatch, Existence.managed_spell_quantity, managed_spell_mode=mode, managed_spell_limit=3,
            managed_spell_timeout_seconds=1.0,
        )


def test_queue_requires_a_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """A queue binding without a timeout raises ValueError."""
    with pytest.raises(ValueError, match="managed_spell_mode 'queue' needs managed_spell_timeout_seconds"):
        bind_with(monkeypatch, Existence.managed_spell_quantity, managed_spell_mode="queue", managed_spell_limit=3)


@pytest.mark.parametrize("timeout", [True, "1"])
def test_queue_timeout_must_be_a_number(monkeypatch: pytest.MonkeyPatch, timeout: Any) -> None:
    """A bool or string timeout raises TypeError."""
    with pytest.raises(TypeError, match="managed_spell_timeout_seconds must be a number of seconds"):
        bind_with(
            monkeypatch, Existence.managed_spell_quantity, managed_spell_mode="queue", managed_spell_limit=3,
            managed_spell_timeout_seconds=timeout,
        )


@pytest.mark.parametrize("timeout", [0, -1.0, math.inf, math.nan])
def test_queue_timeout_must_be_finite_and_positive(monkeypatch: pytest.MonkeyPatch, timeout: float) -> None:
    """Zero, negative, infinite and NaN timeouts raise ValueError."""
    with pytest.raises(ValueError, match="managed_spell_timeout_seconds must be a finite number of seconds > 0"):
        bind_with(
            monkeypatch, Existence.managed_spell_quantity, managed_spell_mode="queue", managed_spell_limit=3,
            managed_spell_timeout_seconds=timeout,
        )


@pytest.mark.parametrize("names", ["reset", {"reset"}])
def test_reset_methods_must_be_a_list_or_tuple(monkeypatch: pytest.MonkeyPatch, names: Any) -> None:
    """A bare string (it would be read per character) or a set raises TypeError with the list remedy."""
    with pytest.raises(TypeError, match=r"Wrap a single name in a list: \['reset'\]"):
        bind_with(monkeypatch, Existence.managed_spell_quantity, managed_spell_reset_methods=names)


def test_reset_method_names_must_be_strings(monkeypatch: pytest.MonkeyPatch) -> None:
    """A non-string element raises TypeError naming its type."""
    with pytest.raises(TypeError, match="found an element of type int"):
        bind_with(monkeypatch, Existence.managed_spell_quantity, managed_spell_reset_methods=["reset", 1])


def test_reset_method_name_must_not_be_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    """An empty name raises ValueError."""
    with pytest.raises(ValueError, match="empty name"):
        bind_with(monkeypatch, Existence.managed_spell_quantity, managed_spell_reset_methods=[""])


@pytest.mark.parametrize("name", ["missing", "label", "size"])
def test_reset_method_must_name_a_method_of_the_class(monkeypatch: pytest.MonkeyPatch, name: str) -> None:
    """A missing name, a plain attribute and a property are not reset methods."""
    with pytest.raises(ValueError, match=f"names '{name}', which is not a method of 'PooledTarget'"):
        bind_with(monkeypatch, Existence.managed_spell_quantity, managed_spell_reset_methods=[name])
    assert StubSpell.constructed == []


# -------------------------
# Fingerprint
# -------------------------

GOLDEN_IDS: Dict[str, str] = {
    "class/unique/True": "e56248c9c9dc835d1e8ba1147cff0e78aa869dccc8d877466efd3d8c72c7f105",
    "class/unique/False": "488c2f0016e85569a55be52a1f15280aac00605ab7c83a751b21f34b66a27684",
    "class/unique_per_conduit/True": "42971e029864daefed89f4d95155e534dff6d41e013624af7e4fe0469a6466fb",
    "class/unique_per_conduit/False": "03c5c2e2dea77686d599299a33ceef037e3dc51e5182d3855ed7acb3d4c246b1",
    "class/many/True": "655f37f0d2d635496994caf8f53904c0ef6091456a3e64d841ab6701f0858952",
    "class/many/False": "02577bc0d949fa426bae0694ead6980d4d61738b14c1456e2a07eb4840e9a9ff",
    "class/unique_per_conduit_cluster/True": "f8258ff9605003458f6a74eccc54098af6045b0b750f7a9ceade2d1b4b808cef",
    "class/unique_per_conduit_cluster/False": "77e993f48c239b018ad8193e2eeb9098b302f330da4f4657feb7d6a6629e6f74",
    "class/unique_per_conduit_lineage/True": "e3b50c0d83a683709cb397039df889186aa886d995bbcdab3e9b3aecd9838919",
    "class/unique_per_conduit_lineage/False": "3a1c2598ea1f96d1a422349b9e8295a3727f189f86013fbaa28f3debd5442daa",
    "class/unique_per_spell_space/True": "c9c5b3ff4bc200f9c1f417d84f3fb2f79024e2bb957ed4e5d95ce924e5efba44",
    "class/unique_per_spell_space/False": "6931380488523d00cffeb50adab7d995b16fc0b51d592473a9578bb89becae92",
}
GOLDEN_FRAME_NAME_DISPOSAL = "fa82947f742dab74f77071edf66222980a8e6efbc3c20a32e27e7624c9c68e20"
GOLDEN_CALLABLE = "927d2a1c98bc5b6499e9510ff831d8673e207014b1802fed735bbf8eee7aea20"
GOLDEN_INSTANCE = "e64a7214e4a752add3492f46c88ceffee612254ac1febe686f041f478eb87d20"
GOLDEN_MANAGED_WITHOUT_PART = "30f9f18d117623b9e5d5f1f801d9cd1e8f7fca3ac8424fcfeaa596be9bf6fb52"


@pytest.mark.parametrize("key", sorted(GOLDEN_IDS))
def test_existing_member_ids_are_byte_identical_to_0_2_8241(key: str) -> None:
    """Every existing member keeps its 0.2.8241 spell id, resolvable or not."""
    _, existence_name, resolvable = key.split("/")
    assert Bind.sha256_profile(
        golden_class_profile(),
        spell_name="Pooled",
        existence=Existence[existence_name],
        resolvable=resolvable == "True",
    ) == GOLDEN_IDS[key]


def test_frame_name_and_disposal_ids_are_byte_identical_to_0_2_8241() -> None:
    """A spellframe, a binding name and disposal names hash exactly as before."""
    assert Bind.sha256_profile(
        golden_class_profile(), spell_name="Pooled", spellframe="pools", binding_name="primary",
        existence=Existence.unique, disposal_method_names=["close"],
    ) == GOLDEN_FRAME_NAME_DISPOSAL


def test_callable_and_existing_object_ids_are_byte_identical_to_0_2_8241() -> None:
    """Callable and existing-object profiles hash exactly as before."""
    assert Bind.sha256_profile(
        golden_callable_profile(), spell_name="factory", existence=Existence.unique,
    ) == GOLDEN_CALLABLE
    assert Bind.sha256_profile(
        golden_instance_profile(), spell_name="Pooled", existence=Existence.unique,
    ) == GOLDEN_INSTANCE


def _managed_key(part: str) -> str:
    """The documented hash input of the golden class bound managed, with `part` as its managed part."""
    parts = [
        "v4-binding", "Pooled", "Pooled", "golden_mod", "object", "Pooled,object", "size", "close,reset",
        "(self, size: int = 1)", "Pooled", "managed_spell_quantity",
    ]
    if part:
        parts.append(part)
    return hashlib.sha256("::".join(parts).encode("utf-8")).hexdigest()


def test_a_managed_binding_hashes_the_inputs_every_binding_hashes() -> None:
    """No settings part: a managed id is the documented key of its profile, name and existence (0.2.8254)."""
    assert Bind.sha256_profile(
        golden_class_profile(), spell_name="Pooled", existence=Existence.managed_spell_quantity,
    ) == _managed_key("") == GOLDEN_MANAGED_WITHOUT_PART


def test_managed_settings_do_not_change_the_spell_id(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mode, limit, timeout and reset names (in any order) give one spell_id: the managed id with no settings."""
    variants = [
        {},
        {"managed_spell_limit": 8},
        {"managed_spell_mode": "limited_quantity", "managed_spell_limit": 8},
        {"managed_spell_mode": "queue", "managed_spell_limit": 8, "managed_spell_timeout_seconds": 1.0},
        {"managed_spell_mode": "queue", "managed_spell_limit": 8, "managed_spell_timeout_seconds": 2.0},
        {"managed_spell_reset_methods": ["reset"]},
        {"managed_spell_reset_methods": ["reset", "clear"]},
        {"managed_spell_reset_methods": ["clear", "reset"]},
    ]
    ids = {bind_with(monkeypatch, Existence.managed_spell_quantity, **variant).kwargs["spell_id"] for variant in variants}
    assert ids == {
        Bind.sha256_profile(golden_class_profile(), spell_name="PooledTarget", existence=Existence.managed_spell_quantity)
    }


def test_equal_timeouts_hash_alike(monkeypatch: pytest.MonkeyPatch) -> None:
    """2 and 2.0 seconds normalize to one value, so they give one id."""
    as_int = bind_with(
        monkeypatch, Existence.managed_spell_quantity, managed_spell_mode="queue", managed_spell_limit=1,
        managed_spell_timeout_seconds=2,
    )
    as_float = bind_with(
        monkeypatch, Existence.managed_spell_quantity, managed_spell_mode="queue", managed_spell_limit=1,
        managed_spell_timeout_seconds=2.0,
    )
    assert as_int.kwargs["spell_id"] == as_float.kwargs["spell_id"]


def test_spell_index_is_minted_with_the_managed_id(monkeypatch: pytest.MonkeyPatch) -> None:
    """The fresh SpellIndex and the Spell share the managed fingerprint."""
    spell = bind_with(monkeypatch, Existence.managed_spell_quantity, managed_spell_limit=7)
    assert spell.kwargs["spell_index"].selected_spell_id == spell.kwargs["spell_id"]


# -------------------------
# Forwarding and the inspector
# -------------------------


def test_decorator_form_forwards_the_options(monkeypatch: pytest.MonkeyPatch) -> None:
    """Bind.bind used as a decorator hands the same normalized options to the Spell."""
    profile = golden_class_profile()
    monkeypatch.setattr(
        "melder.aether.spellbook.bind.bind.SpellExaminer", lambda: StubExaminer(profile), raising=True,
    )
    binder = Bind(StubSpellbook())
    try:
        decorator = binder.bind(
            Permissions.create, Existence.managed_spell_quantity, aetheric_frame="f",
            managed_spell_mode="limited_quantity", managed_spell_limit=5, managed_spell_reset_methods=("reset",),
        )
        decorator(PooledTarget)
    finally:
        binder.cleanup()
    assert managed_values(StubSpell.constructed[-1]) == (ManagedSpellMode.limited_quantity, 5, None, ("reset",))


def test_leftover_keywords_still_flow_beside_the_options(monkeypatch: pytest.MonkeyPatch) -> None:
    """The options are named Spell keywords; leftover bind keywords still reach the Spell's metadata channel."""
    spell = bind_with(monkeypatch, Existence.managed_spell_quantity, managed_spell_limit=3, team="pools")
    assert spell.kwargs["team"] == "pools"
    assert spell.kwargs["managed_spell_limit"] == 3


def test_spell_id_inspector_matches_the_bind_fingerprint_for_a_managed_class() -> None:
    """The read-only inspector checks the settings as bind does and, like bind, does not hash them."""
    profile = SpellGeneralProfile.create_from_target(PooledTarget)
    try:
        expected = Bind.sha256_profile(
            profile.binding_profile, spell_name="PooledTarget", existence=Existence.managed_spell_quantity,
        )
    finally:
        profile.cleanup()
    for settings in (
            {},
            {
                "managed_spell_mode": "queue", "managed_spell_limit": 2, "managed_spell_timeout_seconds": 1.5,
                "managed_spell_reset_methods": ["reset"],
            },
    ):
        assert Bind.spell_id_inspector(
            PooledTarget, spell_name="PooledTarget", existence=Existence.managed_spell_quantity, **settings,
        ) == expected


def test_spell_id_inspector_refuses_what_bind_refuses() -> None:
    """The inspector applies the same refusals: an option on another existence."""
    with pytest.raises(ValueError, match="managed_spell_limit"):
        Bind.spell_id_inspector(PooledTarget, existence=Existence.unique, managed_spell_limit=2)
