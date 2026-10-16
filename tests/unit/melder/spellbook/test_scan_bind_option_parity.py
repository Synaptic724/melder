"""
scan_bind option parity and own-declaration discovery.

Purpose:
    Pin the contract that `scan_bind` declares everything `Spellbook.bind` accepts for a target -
    `resolvable`, per-target `disposal_method_names` and application metadata keywords - and that a
    scan replays the declaration through the one bind pipeline, so a scanned registration matches a
    direct bind of the same target. Pin the discovery rules: only an object's own declaration makes it
    a scan target, and each object is bound once per scan.
"""
import annotationlib
import inspect
import re
import types
import uuid
from collections.abc import Iterator
from typing import Any, Optional, Protocol

import pytest

from melder.aether.aether import Aether
from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.aether.spellbook.bind.bind import Bind
from melder.aether.spellbook.bind.scan import ScanBindMetadata, scan_bind
from melder.aether.spellbook.configuration.spellbook_configuration import SpellbookConfiguration
from melder.aether.spellbook.existence.existence import Existence
from melder.aether.spellbook.spell import Spell
from melder.aether.spellbook.spellbook import Spellbook
from tests._frame_posture_test_support import configure_frame_posture_for_spellbook_configuration


@pytest.fixture(autouse=True)
def isolated_scan_parity_world() -> Iterator[None]:
    """
    Purpose:
        Give every case a fresh Aether so frames and registries never leak between tests.
    Contract:
        Resets the Aether singleton before and after the test and rebinds the class-level handles.
    Yields:
        None while the test runs.
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


def _make_book(*, book_disposal: Optional[list[str]] = None, priority: bool = False) -> Spellbook:
    """
    Purpose:
        Build a dynamic Book in a fresh frame, optionally with Book-level disposal candidates.
    Contract:
        Disposal names and priority are set before defaults because the names are idempotent once set.
    Args:
        book_disposal: Book-wide disposal candidates, or None for none.
        priority: Value of `enforce_priority_disposal_methods`.
    Returns:
        Spellbook: A new pre-conjure Book that the caller cleans up.
    """
    frame = f"scan_parity_{uuid.uuid4().hex}"
    configuration = SpellbookConfiguration(frame)
    if book_disposal is not None:
        configuration.set_property("disposal_method_names", list(book_disposal))
    configuration.set_property("enforce_priority_disposal_methods", priority)
    configuration.with_defaults()
    configure_frame_posture_for_spellbook_configuration(configuration, dynamic=True)
    configuration.set_property("phase_scheduler_workers_per_spellbook", 1)
    return Spellbook(aetheric_frame=frame, configuration=configuration)


def _fresh_resource_class() -> type:
    """
    Purpose:
        Return a new class per call so one test's decoration never leaks into another test.
    Returns:
        type: A class with close/flush/stop disposal candidates and no constructor side effects.
    """

    class Resource:
        """Class target with three disposal candidates."""

        def close(self) -> None:
            """Disposal candidate shared with the Book configuration in the overlap cases."""

        def flush(self) -> None:
            """Second Book disposal candidate."""

        def stop(self) -> None:
            """Per-target-only disposal candidate."""

    return Resource


def _module_with(name: str, **members: Any) -> types.ModuleType:
    """
    Purpose:
        Build a module that owns each member, as if the member had been defined in it.
    Args:
        name: Module name.
        **members: Attribute name to class or function; each gets `__module__ = name`.
    Returns:
        types.ModuleType: The module.
    """
    module = types.ModuleType(name)
    for attribute, member in members.items():
        member.__module__ = name
        setattr(module, attribute, member)
    return module


def _module_from_source(name: str, source: str) -> types.ModuleType:
    """
    Purpose:
        Execute module source in a fresh module so every object it defines reports that module.
    Args:
        name: Module name.
        source: Python source; `scan_bind` is imported for it.
    Returns:
        types.ModuleType: The executed module.
    """
    module = types.ModuleType(name)
    exec("from melder import scan_bind\n" + source, module.__dict__)
    return module


def _declaration(target: Any) -> ScanBindMetadata:
    """
    Purpose:
        Read the declaration the target itself carries (its own namespace, never an inherited one).
    Returns:
        ScanBindMetadata: The stored declaration.
    """
    metadata = vars(target)["__melder_scan_bind__"]
    assert isinstance(metadata, ScanBindMetadata)
    return metadata


def _registration_facts(spell: Spell) -> dict[str, Any]:
    """
    Purpose:
        Snapshot what a direct bind and a scan must agree on, before the Book's cleanup clears it.
    Returns:
        dict[str, Any]: Spell id, lifetime, permissions, address, profile kind, capability,
        resolved disposal order and a copy of the metadata (values kept by identity).
    """
    return {
        "spell_id": spell.spell_id,
        "existence": spell.existence,
        "permissions": spell.permissions,
        "spellframe": spell.spellframe,
        "binding_name": spell.binding_name,
        "profile": type(spell.profile).__name__,
        "resolvable": spell.resolvable,
        "disposal_method_names": list(spell.disposal_method_names),
        "metadata": dict(spell.metadata),
    }


def _registered(book: Spellbook, spell_id: str) -> Spell:
    """Return the published Spell for `spell_id`, failing the test if it was not registered."""
    spell = book.find_spell_by_id(spell_id)
    assert spell is not None
    return spell


def _direct_facts(target: Any, book_options: dict[str, Any], **bind_options: Any) -> dict[str, Any]:
    """Bind `target` directly in a fresh Book and return its registration facts."""
    book = _make_book(**book_options)
    try:
        return _registration_facts(_registered(book, book.bind(spell=target, **bind_options)))
    finally:
        book.cleanup()


def _scanned_facts(module: types.ModuleType, book_options: dict[str, Any]) -> dict[str, Any]:
    """Scan a one-target module in a fresh Book and return the registration's facts."""
    book = _make_book(**book_options)
    try:
        spell_id, = book.scan(module)
        return _registration_facts(_registered(book, spell_id))
    finally:
        book.cleanup()


# ---------------------------------------------------------------------------
# Decoration contract
# ---------------------------------------------------------------------------

def test_new_options_default_exactly_like_direct_bind() -> None:
    """
    Purpose:
        An undecorated option means what Spellbook.bind's default means, and nothing registers yet.
    Contract:
        resolvable defaults to True, disposal names to None, metadata to empty; the target is returned.
    """
    resource = _fresh_resource_class()
    decorated = scan_bind(existence="unique", permissions="create")(resource)
    metadata = _declaration(resource)
    bind_parameters = inspect.signature(
        Spellbook.bind, annotation_format=annotationlib.Format.FORWARDREF,
    ).parameters
    assert decorated is resource
    assert metadata.resolvable is bind_parameters["resolvable"].default
    assert metadata.disposal_method_names is bind_parameters["disposal_method_names"].default
    assert dict(metadata.spell_metadata) == {}


def test_resolvable_is_stored_as_given_without_coercion() -> None:
    """
    Purpose:
        The decorator never turns a configuration mistake into a different policy by truthiness.
    Contract:
        A non-bool value is stored unchanged; Bind refuses it at scan time (covered below).
    """
    resource = _fresh_resource_class()
    scan_bind(existence="unique", permissions="create", resolvable=0)(resource)
    stored = _declaration(resource).resolvable
    assert stored == 0 and type(stored) is int


def test_disposal_names_and_metadata_are_snapshotted_at_decoration() -> None:
    """
    Purpose:
        Mutating the caller's list or dictionary after decoration changes nothing that is replayed.
    Contract:
        Disposal names are kept as a tuple; metadata is a read-only shallow copy.
    """
    names = ["stop"]
    caller_metadata: dict[str, Any] = {"owner_team": "tools"}
    resource = _fresh_resource_class()
    scan_bind(
        existence="unique", permissions="create", disposal_method_names=names, **caller_metadata,
    )(resource)
    names.append("close")
    caller_metadata["owner_team"] = "changed"
    caller_metadata["late"] = True
    metadata = _declaration(resource)
    assert metadata.disposal_method_names == ("stop",)
    assert dict(metadata.spell_metadata) == {"owner_team": "tools"}
    scanned = _scanned_facts(_module_with("scan_parity_snapshot", Resource=resource), {})
    assert scanned["disposal_method_names"] == ["stop"]
    assert scanned["metadata"] == {"owner_team": "tools"}


@pytest.mark.parametrize(
    "invalid",
    ["close", ("close", 1), [None], {"close"}],
    ids=["bare_string", "tuple_with_int", "list_with_none", "set"],
)
def test_disposal_names_must_be_a_list_or_tuple_of_strings(invalid: Any) -> None:
    """
    Purpose:
        A malformed disposal group fails at decoration instead of sitting on the object until scan.
    Contract:
        A bare string, which direct bind would iterate per character, is refused like a bad hook list.
    """
    with pytest.raises(TypeError, match="disposal_method_names must be a list or tuple of"):
        scan_bind(existence="unique", permissions="create", disposal_method_names=invalid)


# Reserved names that are not scan_bind parameters, so only **metadata could carry them. The drift
# test below proves this list is exactly the reserved set minus scan_bind's own parameters.
METADATA_REACHABLE_RESERVED_KEYS: list[str] = [
    "_lifecycle_hooks", "aetheric_frame", "configured_disposal_method_names",
    "enforce_priority_disposal_methods", "existing_object", "implemented_protocols", "self", "spell",
    "spell_id", "spell_index", "spell_name", "spell_type", "spellbook", "spellframe_kind",
]


@pytest.mark.parametrize("reserved", METADATA_REACHABLE_RESERVED_KEYS)
def test_reserved_metadata_keys_are_refused_at_decoration(reserved: str) -> None:
    """
    Purpose:
        Application metadata can never collide with or shadow a native bind argument.
    Contract:
        Each reserved key raises TypeError naming it before any decoration happens.
    """
    with pytest.raises(TypeError, match=f"reserved.*{re.escape(reserved)}"):
        scan_bind(existence="unique", permissions="create", **{reserved: "value"})


def test_reserved_metadata_error_names_every_offending_key_in_order() -> None:
    """The refusal lists all reserved keys it found, sorted, so one fix covers the declaration."""
    with pytest.raises(TypeError, match="reserved.*aetheric_frame, spell_id"):
        scan_bind(existence="unique", permissions="create", spell_id="x", aetheric_frame="y", ok=1)


def test_reserved_metadata_keys_are_exactly_the_native_bind_parameters() -> None:
    """
    Purpose:
        Guard the reserved set against drift when Spellbook.bind, Bind or Spell gains a parameter.
    Contract:
        Reserved keys = every named parameter on the bind chain plus the three hook keys.
    """
    native: set[str] = {"pre_hooks", "activation_hooks", "post_hooks"}
    for callable_on_chain in (Spellbook.bind, Bind.bind, Bind._bind_logic, Spell.__init__):
        signature = inspect.signature(
            callable_on_chain, annotation_format=annotationlib.Format.FORWARDREF,
        )
        for name, parameter in signature.parameters.items():
            if parameter.kind not in (parameter.VAR_POSITIONAL, parameter.VAR_KEYWORD):
                native.add(name)
    assert ScanBindMetadata.RESERVED_SPELL_METADATA_KEYS == frozenset(native)
    scan_bind_parameters = set(
        inspect.signature(scan_bind, annotation_format=annotationlib.Format.FORWARDREF).parameters
    )
    reachable = sorted(ScanBindMetadata.RESERVED_SPELL_METADATA_KEYS - scan_bind_parameters)
    assert reachable == METADATA_REACHABLE_RESERVED_KEYS


def test_declaration_cannot_be_changed_after_decoration() -> None:
    """
    Purpose:
        A decorated object carries a stable registration contract from import to scan.
    Contract:
        Attributes cannot be set, added or deleted, and the metadata mapping is read-only.
    """
    resource = _fresh_resource_class()
    scan_bind(existence="unique", permissions="create", owner_team="tools")(resource)
    metadata = _declaration(resource)
    with pytest.raises(AttributeError):
        metadata.resolvable = False
    with pytest.raises(AttributeError):
        metadata.extra = True
    with pytest.raises(AttributeError):
        del metadata.profile
    with pytest.raises(TypeError):
        metadata.spell_metadata["owner_team"] = "changed"
    assert metadata.resolvable is True
    assert metadata.spell_metadata["owner_team"] == "tools"


def test_to_bind_kwargs_hands_every_bind_fresh_metadata_entries() -> None:
    """
    Purpose:
        Each bind receives its own dict, so nothing a Spell does to its metadata reaches the declaration.
    Contract:
        Hooks are copied as lists, profile is always present, metadata values keep their identity.
    """
    payload = object()

    def post_hook() -> None:
        """Construction hook that the payload must carry as a fresh list."""

    resource = _fresh_resource_class()
    scan_bind(existence="unique", permissions="create", post_hooks=[post_hook], payload=payload)(resource)
    metadata = _declaration(resource)
    first = metadata.to_bind_kwargs()
    second = metadata.to_bind_kwargs()
    assert first == second == {"post_hooks": [post_hook], "profile": "general", "payload": payload}
    assert first is not second
    assert first["payload"] is payload
    first["payload"] = "changed"
    assert metadata.spell_metadata["payload"] is payload


# ---------------------------------------------------------------------------
# Parity with a direct bind of the same target
# ---------------------------------------------------------------------------

PARITY_CASES: dict[str, dict[str, Any]] = {
    "native_policy": {
        "existence": Existence.many, "permissions": "read", "spellframe": "parity",
        "binding_name": "named", "profile": "detailed",
    },
    "not_resolvable": {"existence": "unique", "permissions": "create", "resolvable": False},
    "per_target_disposal": {
        "existence": "unique", "permissions": "create", "disposal_method_names": ["stop", "close"],
    },
    "metadata": {"existence": "unique", "permissions": "create", "owner_team": "tools", "tier": 3},
}


@pytest.mark.parametrize("case", sorted(PARITY_CASES))
def test_scanned_registration_matches_a_direct_bind(case: str) -> None:
    """
    Purpose:
        A scan and a direct bind with the same options produce the same registration.
    Contract:
        Same spell_id, lifetime, permissions, address, profile kind, capability, disposal order and
        metadata; each side runs in its own Book so the shared fingerprint never collides.
    """
    options = PARITY_CASES[case]
    resource = _fresh_resource_class()
    scan_bind(**options)(resource)
    module = _module_with(f"scan_parity_{case}", Resource=resource)
    assert _scanned_facts(module, {}) == _direct_facts(resource, {}, **options)


@pytest.mark.parametrize("priority", [False, True], ids=["book_last", "book_first"])
@pytest.mark.parametrize(
    "per_target, expected_default, expected_priority",
    [
        (None, ["close", "flush"], ["close", "flush"]),
        ([], ["close", "flush"], ["close", "flush"]),
        (["flush", "stop", "missing", "stop"], ["stop", "close", "flush"], ["close", "flush", "stop"]),
    ],
    ids=["omitted", "empty", "overlap_missing_duplicate"],
)
def test_scanned_disposal_order_follows_the_book_policy_like_direct_bind(
        priority: bool,
        per_target: Optional[list[str]],
        expected_default: list[str],
        expected_priority: list[str],
) -> None:
    """
    Purpose:
        Per-target disposal names reach Bind, where Book overlap and priority rules stay central.
    Contract:
        An empty group keeps the Book names; shared names belong to the Book block; missing names are
        skipped and duplicates kept once; the Book block goes last by default and first with priority.
    """
    options: dict[str, Any] = {"existence": "unique", "permissions": "create"}
    if per_target is not None:
        options["disposal_method_names"] = per_target
    resource = _fresh_resource_class()
    scan_bind(**options)(resource)
    module = _module_with("scan_parity_disposal", Resource=resource)
    book_options: dict[str, Any] = {"book_disposal": ["close", "flush"], "priority": priority}
    scanned = _scanned_facts(module, book_options)
    direct = _direct_facts(resource, book_options, **options)
    assert scanned["disposal_method_names"] == (expected_priority if priority else expected_default)
    assert scanned["disposal_method_names"] == direct["disposal_method_names"]
    assert scanned["spell_id"] == direct["spell_id"]


def test_scanned_subclass_keeps_an_inherited_disposal_candidate() -> None:
    """An inherited callable is a valid per-target disposal name on the scan path, as on direct bind."""

    class ClosingBase:
        """Base class that supplies close() to its subclasses."""

        def close(self) -> None:
            """Inherited disposal candidate."""

    class Closing(ClosingBase):
        """Decorated subclass whose only disposal method is inherited."""

    options: dict[str, Any] = {
        "existence": "unique", "permissions": "create", "disposal_method_names": ["close"],
    }
    scan_bind(**options)(Closing)
    scanned = _scanned_facts(_module_with("scan_parity_inherited", Closing=Closing), {})
    assert scanned["disposal_method_names"] == ["close"]
    assert scanned == _direct_facts(Closing, {}, **options)


def test_metadata_keeps_value_identity_and_never_reaches_native_fields() -> None:
    """
    Purpose:
        Metadata is application data: it lands in Spell.metadata only, by reference.
    Contract:
        Keys named like Spell attributes that are not constructor parameters stay in metadata.
    """
    payload = object()
    resource = _fresh_resource_class()
    scan_bind(
        existence="unique", permissions="create", payload=payload, timeout=5, tags="label",
    )(resource)
    book = _make_book()
    try:
        spell_id, = book.scan(_module_with("scan_parity_identity", Resource=resource))
        spell = _registered(book, spell_id)
        assert spell.metadata == {"payload": payload, "timeout": 5, "tags": "label"}
        assert spell.metadata["payload"] is payload
        assert spell.timeout is None
        assert spell.tags == []
        assert spell.resolvable is True
    finally:
        book.cleanup()


def test_metadata_survives_the_cleanup_of_an_earlier_book() -> None:
    """
    Purpose:
        Spell cleanup clears its metadata dict in place; the declaration must not be that dict.
    Contract:
        A second scan of the same module, after the first Book was cleaned, forwards the full metadata.
    """
    resource = _fresh_resource_class()
    scan_bind(existence="unique", permissions="create", owner_team="tools")(resource)
    module = _module_with("scan_parity_survives", Resource=resource)
    first = _scanned_facts(module, {})
    second = _scanned_facts(module, {})
    assert first["metadata"] == second["metadata"] == {"owner_team": "tools"}


def test_protocol_definition_scans_when_declared_not_resolvable() -> None:
    """A Protocol registers through scan as a descriptive definition, exactly as with direct bind."""

    class RenderContract(Protocol):
        """Application Protocol registered without an implementation."""

        def render(self) -> str:
            """Return the implementation's representation."""

    scan_bind(existence="unique", permissions="create", resolvable=False)(RenderContract)
    module = _module_with("scan_parity_protocol", RenderContract=RenderContract)
    scanned = _scanned_facts(module, {})
    assert scanned["resolvable"] is False
    assert scanned == _direct_facts(
        RenderContract, {}, existence="unique", permissions="create", resolvable=False,
    )


def test_protocol_left_resolvable_is_refused_at_scan_by_bind() -> None:
    """The decorator adds no Protocol rule; Bind's refusal is what a resolvable Protocol meets."""

    class RenderContract(Protocol):
        """Application Protocol that cannot be a concrete provider."""

        def render(self) -> str:
            """Return the implementation's representation."""

    scan_bind(existence="unique", permissions="create")(RenderContract)
    book = _make_book()
    try:
        with pytest.raises(TypeError, match="Cannot bind Protocol"):
            book.scan(_module_with("scan_parity_protocol_true", RenderContract=RenderContract))
        assert len(book.spells) == 0
    finally:
        book.cleanup()


@pytest.mark.parametrize("invalid", [None, 0, 1, "false"])
def test_non_bool_resolvable_is_refused_by_bind_at_scan_time(invalid: Any) -> None:
    """A non-bool capability fails with the normal binding policy and registers nothing."""
    resource = _fresh_resource_class()
    scan_bind(existence="unique", permissions="create", resolvable=invalid)(resource)
    book = _make_book()
    try:
        with pytest.raises(TypeError, match="resolvable must be a bool"):
            book.scan(_module_with("scan_parity_non_bool", Resource=resource))
        assert len(book.spells) == 0
    finally:
        book.cleanup()


def test_scan_keeps_bind_rejections_for_concrete_frames_and_callable_lifetimes() -> None:
    """New options relax no binding rule: a concrete-class frame and a non-unique function still fail."""

    class ConcreteFrame:
        """A concrete class, which is not a valid spellframe."""

    resource = _fresh_resource_class()
    scan_bind(existence="unique", permissions="create", spellframe=ConcreteFrame)(resource)

    def factory() -> str:
        """Callable target whose lifetime must be unique."""
        return "built"

    scan_bind(existence="many", permissions="create", resolvable=False)(factory)
    book = _make_book()
    try:
        with pytest.raises(TypeError, match="spellframe must be a string category or a Protocol"):
            book.scan(_module_with("scan_parity_concrete_frame", Resource=resource))
        with pytest.raises(ValueError, match="Method and lambda spells must use Existence.unique"):
            book.scan(_module_with("scan_parity_factory", factory=factory))
        assert len(book.spells) == 0
    finally:
        book.cleanup()


# ---------------------------------------------------------------------------
# Discovery: own declarations only, one bind per object per scan
# ---------------------------------------------------------------------------

def _scan_targets(module: types.ModuleType) -> list[Any]:
    """Scan `module` in a fresh Book and return the registered objects in returned-id order."""
    book = _make_book()
    try:
        return [_registered(book, spell_id).spell for spell_id in book.scan(module)]
    finally:
        book.cleanup()


def test_undecorated_subclass_of_a_decorated_class_is_not_a_target() -> None:
    """Inheriting a declaration is not declaring: only the decorated parent registers."""
    module = _module_from_source(
        "scan_discovery_subclass",
        "@scan_bind(existence='unique', permissions='create')\n"
        "class Parent:\n    pass\n"
        "class Child(Parent):\n    pass\n",
    )
    assert getattr(module.Child, "__melder_scan_bind__", None) is not None
    assert _scan_targets(module) == [module.Parent]


def test_explicitly_decorated_subclass_registers_with_its_own_declaration() -> None:
    """A subclass with its own decorator is a target and uses only its own options."""
    module = _module_from_source(
        "scan_discovery_own_subclass",
        "@scan_bind(existence='unique', permissions='create', binding_name='parent')\n"
        "class Parent:\n    pass\n"
        "@scan_bind(existence='many', permissions='read', binding_name='child', owner_team='kids')\n"
        "class Child(Parent):\n    pass\n",
    )
    book = _make_book()
    try:
        parent_id, child_id = book.scan(module)
        parent, child = _registered(book, parent_id), _registered(book, child_id)
        assert (parent.spell, child.spell) == (module.Parent, module.Child)
        assert parent.binding_name == "parent" and parent.metadata == {}
        assert child.binding_name == "child" and child.existence is Existence.many
        assert child.permissions is Permissions.read and child.metadata == {"owner_team": "kids"}
    finally:
        book.cleanup()


def test_module_level_instance_of_a_decorated_class_is_not_a_target() -> None:
    """An instance reads its class's declaration through getattr; it must not register (or collide)."""
    module = _module_from_source(
        "scan_discovery_instance",
        "@scan_bind(existence='unique', permissions='create')\n"
        "class Service:\n    pass\n"
        "default_service = Service()\n",
    )
    assert _scan_targets(module) == [module.Service]


def test_directly_decorated_instance_registers_as_an_existing_object_and_must_be_unique() -> None:
    """
    Purpose:
        An instance decorated itself carries its own declaration, so it is a scan target, bound as an
        existing object; Bind's unique-only rule for existing objects holds on the scan path.
    Contract:
        With `existence="unique"` the instance, not its class, registers with its metadata. With
        `existence="many"` Bind refuses it and nothing is registered.
    """
    module = _module_from_source(
        "scan_discovery_existing_object",
        "class Settings:\n    pass\n"
        "settings = Settings()\n"
        "scan_bind(existence='unique', permissions='create', owner_team='ops')(settings)\n",
    )
    book = _make_book()
    try:
        spell_id, = book.scan(module)
        spell = _registered(book, spell_id)
        assert spell.is_existing_creation
        assert spell.spell is module.settings
        assert spell.metadata == {"owner_team": "ops"}
    finally:
        book.cleanup()
    many_module = _module_from_source(
        "scan_discovery_existing_object_many",
        "class Settings:\n    pass\n"
        "settings = Settings()\n"
        "scan_bind(existence='many', permissions='create')(settings)\n",
    )
    book = _make_book()
    try:
        with pytest.raises(ValueError, match="Existing-object spells must use Existence.unique"):
            book.scan(many_module)
        assert len(book.spells) == 0
    finally:
        book.cleanup()


def test_metaclass_declaration_does_not_make_its_classes_targets() -> None:
    """A class seeing a declaration through its metaclass has not declared anything itself."""
    owner = _module_from_source(
        "scan_discovery_meta_owner",
        "@scan_bind(existence='unique', permissions='create')\n"
        "class Meta(type):\n    pass\n",
    )
    product = owner.Meta("Product", (), {"__module__": "scan_discovery_meta_user"})
    module = types.ModuleType("scan_discovery_meta_user")
    module.Product = product
    assert getattr(product, "__melder_scan_bind__", None) is not None
    assert _scan_targets(module) == []


@pytest.mark.parametrize("slotted", [False, True], ids=["with_dict", "slotted"])
def test_object_answering_every_attribute_is_ignored(slotted: bool) -> None:
    """A __getattr__ proxy neither aborts the scan as 'corrupted' nor becomes a target."""
    proxy_source = (
        "class Proxy:\n"
        + ("    __slots__ = ()\n" if slotted else "")
        + "    def __getattr__(self, name):\n        return 'anything'\n"
    )
    module = _module_from_source(
        "scan_discovery_proxy",
        proxy_source
        + "proxy = Proxy()\n"
        + "@scan_bind(existence='unique', permissions='create')\n"
        + "class Real:\n    pass\n",
    )
    assert _scan_targets(module) == [module.Real]


def test_alias_binds_the_object_once_and_keeps_module_order() -> None:
    """A second name for an object this scan already bound adds no registration and no collision."""
    module = _module_from_source(
        "scan_discovery_alias",
        "@scan_bind(existence='unique', permissions='create')\n"
        "class Thing:\n    pass\n"
        "Alias = Thing\n"
        "@scan_bind(existence='unique', permissions='create', binding_name='other')\n"
        "class Other:\n    pass\n",
    )
    assert _scan_targets(module) == [module.Thing, module.Other]


def test_distinct_targets_sharing_a_binding_key_still_raise_with_an_alias_present() -> None:
    """Identity de-duplication never hides a real collision between two different objects."""
    module = _module_from_source(
        "scan_discovery_alias_collision",
        "@scan_bind(existence='unique', permissions='create', spellframe='dup', binding_name='same')\n"
        "class Thing:\n    pass\n"
        "Alias = Thing\n"
        "@scan_bind(existence='unique', permissions='create', spellframe='dup', binding_name='same')\n"
        "class Twin:\n    pass\n",
    )
    book = _make_book()
    try:
        with pytest.raises(RuntimeError, match="Binding signature already active"):
            book.scan(module)
        assert [spell.spell for spell in book.spells.values()] == [module.Thing]
    finally:
        book.cleanup()


def test_rescanning_a_module_with_an_alias_still_raises() -> None:
    """De-duplication is per scan: a second scan of the same module collides as before."""
    module = _module_from_source(
        "scan_discovery_alias_rescan",
        "@scan_bind(existence='unique', permissions='create')\n"
        "class Thing:\n    pass\n"
        "Alias = Thing\n",
    )
    book = _make_book()
    try:
        assert len(book.scan(module)) == 1
        with pytest.raises(RuntimeError):
            book.scan(module)
    finally:
        book.cleanup()


def test_wraps_based_wrapper_keeps_its_own_copy_of_the_declaration() -> None:
    """functools.wraps copies the wrapped __dict__, so the wrapper is a target with the same metadata."""
    module = _module_from_source(
        "scan_discovery_wraps",
        "import functools\n"
        "def _wrap(func):\n"
        "    @functools.wraps(func)\n"
        "    def wrapper(*args, **kwargs):\n"
        "        return func(*args, **kwargs)\n"
        "    return wrapper\n"
        "@_wrap\n"
        "@scan_bind(existence='unique', permissions='create', binding_name='wrapped', owner_team='tools')\n"
        "def wrapped():\n"
        "    return 'wrapped'\n",
    )
    assert "__melder_scan_bind__" in vars(module.wrapped)
    book = _make_book()
    try:
        spell_id, = book.scan(module)
        spell = _registered(book, spell_id)
        assert spell.spell is module.wrapped
        assert spell.metadata == {"owner_team": "tools"}
    finally:
        book.cleanup()
