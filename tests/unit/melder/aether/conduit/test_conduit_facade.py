from unittest.mock import MagicMock, call

import pytest

from melder.aether.conduit.conduit import Conduit
from melder.aether.conduit.conduit_ward.permissions.permissions import Permissions
from melder.spellbook.bind.spell_index import SpellIndex
from melder.spellbook.existence.existence import Existence


def _make_spell(
    spell_id: str,
    *,
    permissions: Permissions = Permissions.create,
) -> MagicMock:
    """
    Create a minimal spell double with identifier and permissions.

    Args:
        spell_id (str): Version identifier to attach to the spell.
        permissions (Permissions): Permissions enum for the spell.

    Returns:
        MagicMock: Spell-like object with spell_id and permissions attributes.
    """
    spell = MagicMock()
    spell.spell_id = spell_id
    spell.permissions = permissions
    return spell


def test_create_binder_forwards_defaults(
    conduit_lesser: Conduit,
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify create_binder forwards default arguments to Spellbook.

    Contract:
        - Default existence and permissions are passed through.
        - The Spellbook return value is returned to the caller.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.
        spellbook_stub (MagicMock): Spellbook stub bound to the conduit.

    Raises:
        AssertionError: If forwarding or return behavior is incorrect.
    """
    sentinel = object()
    spellbook_stub.create_binder.return_value = sentinel

    result = conduit_lesser.create_binder()

    spellbook_stub.create_binder.assert_called_once_with(
        default_existence=Existence.unique,
        default_permissions="create",
    )
    assert result is sentinel


def test_create_binder_forwards_custom_args(
    conduit_lesser: Conduit,
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify create_binder forwards custom arguments to Spellbook.

    Contract:
        - Provided defaults override the standard defaults.
        - Return value is passed through unchanged.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.
        spellbook_stub (MagicMock): Spellbook stub bound to the conduit.

    Raises:
        AssertionError: If forwarding or return behavior is incorrect.
    """
    sentinel = object()
    spellbook_stub.create_binder.return_value = sentinel

    result = conduit_lesser.create_binder(
        default_existence=Existence.many,
        default_permissions="read",
    )

    spellbook_stub.create_binder.assert_called_once_with(
        default_existence=Existence.many,
        default_permissions="read",
    )
    assert result is sentinel


def test_bind_raises_for_lesser_conduit(
    conduit_lesser: Conduit,
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify bind is blocked on lesser conduits.

    Contract:
        - Lesser conduits cannot bind spells.
        - Spellbook.bind is not called when blocked.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.
        spellbook_stub (MagicMock): Spellbook stub bound to the conduit.

    Raises:
        AssertionError: If bind succeeds or forwards on a lesser conduit.
    """
    spellbook_stub.bind = MagicMock()
    with pytest.raises(RuntimeError, match="Only normal conduits can bind spells"):
        conduit_lesser.bind(spell=object(), existence=Existence.unique)
    assert spellbook_stub.bind.called is False


def test_bind_forwards_to_spellbook_for_normal_conduit(
    conduit_normal: Conduit,
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify bind forwards registrations to the Spellbook for normal conduits.

    Contract:
        - The bind call is forwarded with the provided arguments.
        - The Spellbook return value is returned.

    Args:
        conduit_normal (Conduit): Normal conduit instance.
        spellbook_stub (MagicMock): Spellbook stub bound to the conduit.

    Raises:
        AssertionError: If bind does not forward or return correctly.
    """
    spell = object()
    extra = object()
    spellbook_stub.bind.return_value = "spell-id"

    result = conduit_normal.bind(
        spell=spell,
        existence=Existence.unique,
        permissions="read",
        spellframe="frame",
        binding_name="main",
        extra=extra,
    )

    spellbook_stub.bind.assert_called_once_with(
        spell=spell,
        existence=Existence.unique,
        spellframe="frame",
        binding_name="main",
        permissions="read",
        extra=extra,
    )
    assert result == "spell-id"


def test_inspect_spell_delegates_to_spellbook(
    conduit_lesser: Conduit,
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify inspect_spell delegates to Spellbook.inspect_spell.

    Contract:
        - The Spellbook return value is passed through.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.
        spellbook_stub (MagicMock): Spellbook stub bound to the conduit.

    Raises:
        AssertionError: If delegation does not occur.
    """
    target = object()
    spellbook_stub.inspect_spell.return_value = "spell-id"

    result = conduit_lesser.inspect_spell(target, aetheric_frame="frame-1")

    spellbook_stub.inspect_spell.assert_called_once_with(target, "frame-1")
    assert result == "spell-id"


def test_find_spell_id_translates_missing_index_error(
    conduit_lesser: Conduit,
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify find_spell_id translates Spellbook lookup errors.

    Contract:
        - Spellbook.find_spell_index RuntimeError is re-raised as ValueError.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.
        spellbook_stub (MagicMock): Spellbook stub bound to the conduit.

    Raises:
        AssertionError: If error translation does not occur.
    """
    spellbook_stub.find_spell_index.side_effect = RuntimeError("not found")

    with pytest.raises(ValueError, match="Spell 'Missing' not found"):
        conduit_lesser.find_spell_id("frame", "Missing", "bind")


def test_find_spell_id_raises_when_spell_missing(
    conduit_lesser: Conduit,
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify find_spell_id raises when SpellIndex resolves but spell is absent.

    Contract:
        - Missing spell after index resolution produces ValueError.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.
        spellbook_stub (MagicMock): Spellbook stub bound to the conduit.

    Raises:
        AssertionError: If missing spell does not raise.
    """
    spellbook_stub.find_spell_index.return_value = SpellIndex("sha-1")
    spellbook_stub._find_spell.return_value = None

    with pytest.raises(ValueError, match="not found"):
        conduit_lesser.find_spell_id("frame", "Spell", "bind")


def test_find_spell_id_returns_spell_id(
    conduit_lesser: Conduit,
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify find_spell_id returns the spell's current version id.

    Contract:
        - SpellIndex and spell resolution returns spell.spell_id.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.
        spellbook_stub (MagicMock): Spellbook stub bound to the conduit.

    Raises:
        AssertionError: If the resolved spell_id is not returned.
    """
    spellbook_stub.find_spell_index.return_value = SpellIndex("sha-1")
    spellbook_stub._find_spell.return_value = _make_spell("sha-1")

    result = conduit_lesser.find_spell_id("frame", "Spell", "bind")

    assert result == "sha-1"


def test_find_spell_key_raises_when_missing(
    conduit_lesser: Conduit,
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify find_spell_key raises when the spellbook returns no key.

    Contract:
        - Absence of a key is reported as ValueError.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.
        spellbook_stub (MagicMock): Spellbook stub bound to the conduit.

    Raises:
        AssertionError: If missing key does not raise.
    """
    spellbook_stub.find_spell_key.return_value = None

    with pytest.raises(ValueError, match="not found"):
        conduit_lesser.find_spell_key("frame", "Spell", "bind")


def test_find_spell_key_returns_key(
    conduit_lesser: Conduit,
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify find_spell_key returns the spellbook key tuple.

    Contract:
        - The Spellbook key is passed through unchanged.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.
        spellbook_stub (MagicMock): Spellbook stub bound to the conduit.

    Raises:
        AssertionError: If the key is not returned correctly.
    """
    key = ("frame", "Spell", "bind")
    spellbook_stub.find_spell_key.return_value = key

    result = conduit_lesser.find_spell_key("frame", "Spell", "bind")

    assert result == key


def test_get_spell_permissions_returns_name(
    conduit_lesser: Conduit,
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify get_spell_permissions resolves the permission name for a spell.

    Contract:
        - The permissions enum name is returned for a matching version id.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.
        spellbook_stub (MagicMock): Spellbook stub bound to the conduit.

    Raises:
        AssertionError: If permissions are not resolved.
    """
    spell_index = SpellIndex("sha-1")
    spellbook_stub._spells = {spell_index: _make_spell("sha-1", permissions=Permissions.create)}

    result = conduit_lesser.get_spell_permissions("sha-1")

    assert result == "create"


def test_get_spell_permissions_raises_when_missing(
    conduit_lesser: Conduit,
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify get_spell_permissions raises when the spell id is absent.

    Contract:
        - Missing spell ids raise RuntimeError.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.
        spellbook_stub (MagicMock): Spellbook stub bound to the conduit.

    Raises:
        AssertionError: If missing spell id does not raise.
    """
    spell_index = SpellIndex("sha-2")
    spellbook_stub._spells = {spell_index: _make_spell("sha-2", permissions=Permissions.read)}

    with pytest.raises(RuntimeError, match="not found"):
        conduit_lesser.get_spell_permissions("sha-1")


def test_get_conduit_by_spell_id_delegates_to_aether(
    conduit_normal: Conduit,
    aether_stub: MagicMock,
) -> None:
    """
    Verify get_conduit_by_spell_id delegates to Aether.

    Contract:
        - The Aether return value is returned to the caller.

    Args:
        conduit_normal (Conduit): Normal conduit instance.
        aether_stub (MagicMock): Aether stub used for delegation.

    Raises:
        AssertionError: If the Aether result is not returned.
    """
    sentinel = object()
    aether_stub._get_conduit_by_spell_id.return_value = sentinel

    result = conduit_normal.get_conduit_by_spell_id("sha-1", aetheric_frame_name="frame-1")

    aether_stub._get_conduit_by_spell_id.assert_called_once_with("sha-1", "frame-1")
    assert result is sentinel


def test_check_spell_id_returns_bool(
    conduit_normal: Conduit,
    aether_stub: MagicMock,
) -> None:
    """
    Verify check_spell_id reports presence using boolean semantics.

    Contract:
        - Truthy Aether responses yield True.

    Args:
        conduit_normal (Conduit): Normal conduit instance.
        aether_stub (MagicMock): Aether stub used for delegation.

    Raises:
        AssertionError: If the boolean result is incorrect.
    """
    aether_stub._check_for_spell.return_value = "sha-1"

    result = conduit_normal.check_spell_id("sha-1", aetheric_frame_name="frame-1")

    aether_stub._check_for_spell.assert_called_once_with("sha-1", "frame-1")
    assert result is True


def test_get_spell_by_id_returns_none_when_owner_missing(
    conduit_normal: Conduit,
    aether_stub: MagicMock,
) -> None:
    """
    Verify get_spell_by_id returns None when no owner conduit is found.

    Contract:
        - Absence of an owner returns None without raising.

    Args:
        conduit_normal (Conduit): Normal conduit instance.
        aether_stub (MagicMock): Aether stub used for lookup.

    Raises:
        AssertionError: If the result is not None.
    """
    aether_stub._get_conduit_by_spell_id.return_value = None

    result = conduit_normal.get_spell_by_id("sha-1")

    assert result is None


def test_get_spell_by_id_returns_owner_spell(
    conduit_normal: Conduit,
    aether_stub: MagicMock,
) -> None:
    """
    Verify get_spell_by_id resolves a spell from the owning spellbook.

    Contract:
        - The owning spellbook is scanned for a SpellIndex that has the version.
        - The matching spell instance is returned.

    Args:
        conduit_normal (Conduit): Normal conduit instance.
        aether_stub (MagicMock): Aether stub used for lookup.

    Raises:
        AssertionError: If the spell is not returned.
    """
    spell = _make_spell("sha-1")
    spell_index = SpellIndex("sha-1")
    owner = MagicMock()
    owner._spellbook = MagicMock()
    owner._spellbook._spells = {spell_index: spell}
    aether_stub._get_conduit_by_spell_id.return_value = owner

    result = conduit_normal.get_spell_by_id("sha-1")

    assert result is spell


def test_find_contracted_spell_returns_none_when_empty(
    conduit_lesser: Conduit,
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify find_contracted_spell returns None when no contracts exist.

    Contract:
        - Empty contracted spell map yields None.
        - Spellbook helper is not called when there are no peers.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.
        spellbook_stub (MagicMock): Spellbook stub bound to the conduit.

    Raises:
        AssertionError: If the result or calls are incorrect.
    """
    spellbook_stub._contracted_spells = {}
    spellbook_stub._find_contracted_spell_by_id = MagicMock(return_value=None)

    result = conduit_lesser.find_contracted_spell("sha-1")

    assert result is None
    assert spellbook_stub._find_contracted_spell_by_id.called is False


def test_find_contracted_spell_returns_first_match(
    conduit_lesser: Conduit,
    spellbook_stub: MagicMock,
) -> None:
    """
    Verify find_contracted_spell returns the first matching contracted spell.

    Contract:
        - Iterates peer conduits in order and returns the first match.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.
        spellbook_stub (MagicMock): Spellbook stub bound to the conduit.

    Raises:
        AssertionError: If ordering or return semantics are incorrect.
    """
    contracted = {"conduit-1": {}, "conduit-2": {}}
    spellbook_stub._contracted_spells = contracted
    match = _make_spell("sha-1")
    spellbook_stub._find_contracted_spell_by_id = MagicMock(
        side_effect=[None, match]
    )

    result = conduit_lesser.find_contracted_spell("sha-1")

    assert result is match
    assert spellbook_stub._find_contracted_spell_by_id.call_args_list == [
        call("sha-1", "conduit-1"),
        call("sha-1", "conduit-2"),
    ]


def test_meld_requires_identifier(conduit_lesser: Conduit) -> None:
    """
    Verify meld requires at least one identifier input.

    Contract:
        - Calling meld without spell_name, spell, or spellframe raises ValueError.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.

    Raises:
        AssertionError: If missing identifiers do not raise.
    """
    with pytest.raises(ValueError, match="requires at least one"):
        conduit_lesser.meld()


def test_meld_forwards_non_string_spell_name(conduit_lesser: Conduit) -> None:
    """
    Verify meld forwards non-string spell_name values to Meld.

    Contract:
        - Conduit does not type-validate spell_name.
        - spell_name is delegated unchanged to Meld.meld.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.

    Raises:
        AssertionError: If forwarding behavior is incorrect.
    """
    conduit_lesser._meld = MagicMock()
    conduit_lesser._meld.meld.return_value = "result"

    result = conduit_lesser.meld(spell_name=123)

    assert result == "result"
    conduit_lesser._meld.meld.assert_called_once_with(
        spell_name=123,
        spell=None,
        spellframe=None,
        binding_name=None,
        spell_override=None,
    )


def test_meld_forwards_non_string_binding_name(conduit_lesser: Conduit) -> None:
    """
    Verify meld forwards non-string binding_name values to Meld.

    Contract:
        - Conduit does not type-validate binding_name.
        - binding_name is delegated unchanged to Meld.meld.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.

    Raises:
        AssertionError: If forwarding behavior is incorrect.
    """
    conduit_lesser._meld = MagicMock()
    conduit_lesser._meld.meld.return_value = "result"

    result = conduit_lesser.meld(spell="sha-1", binding_name=5)

    assert result == "result"
    conduit_lesser._meld.meld.assert_called_once_with(
        spell_name=None,
        spell="sha-1",
        spellframe=None,
        binding_name=5,
        spell_override=None,
    )


def test_meld_delegates_to_meld_instance(conduit_lesser: Conduit) -> None:
    """
    Verify meld delegates to the underlying Meld.meld call.

    Contract:
        - Arguments are forwarded.
        - The return value is passed through.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.

    Raises:
        AssertionError: If delegation or return behavior is incorrect.
    """
    conduit_lesser._meld = MagicMock()
    conduit_lesser._meld.meld.return_value = "result"

    result = conduit_lesser.meld(
        spell_name="Spell",
        spell="sha-1",
        spellframe="frame",
        binding_name="bind",
        spell_override={"k": "v"},
    )

    conduit_lesser._meld.meld.assert_called_once_with(
        spell_name="Spell",
        spell="sha-1",
        spellframe="frame",
        binding_name="bind",
        spell_override={"k": "v"},
    )
    assert result == "result"


def test_meld_does_not_fire_conduit_level_meld_hooks(
    conduit_lesser: Conduit,
) -> None:
    """
    Verify Conduit.meld does not dispatch conduit-level meld hook names.

    Contract:
        - Registering local conduit hooks named ``on_meld_*`` does not create
          conduit-side meld hook dispatch.
        - Meld delegation still executes and returns normally.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.

    Raises:
        AssertionError: If conduit-level hook callbacks fire.
    """
    events: list[tuple[str, Conduit]] = []

    def pre_hook(conduit: Conduit) -> None:
        """
        Record a pre-resolve hook invocation.

        Args:
            conduit (Conduit): Conduit instance passed to the hook.

        Returns:
            None: Hook does not return a value.
        """
        events.append(("pre", conduit))

    def post_hook(conduit: Conduit) -> None:
        """
        Record a post-resolve hook invocation.

        Args:
            conduit (Conduit): Conduit instance passed to the hook.

        Returns:
            None: Hook does not return a value.
        """
        events.append(("post", conduit))

    conduit_lesser._meld = MagicMock()
    conduit_lesser._meld.meld.return_value = "result"
    conduit_lesser.register_conduit_hooks(
        {
            "on_meld_pre_resolve": pre_hook,
            "on_meld_post_resolve": post_hook,
        }
    )

    result = conduit_lesser.meld(spell="sha-1")

    assert result == "result"
    assert events == []


def test_meld_skips_conduit_hook_dispatch_when_no_meld_hooks(
    conduit_lesser: Conduit,
) -> None:
    """
    Verify conduit meld bypasses hook dispatch when no meld hooks exist.

    Contract:
        - The no-hook meld path does not call _fire_conduit_hooks.
        - Meld delegation still executes and returns normally.

    Args:
        conduit_lesser (Conduit): Lesser conduit instance.

    Raises:
        AssertionError: If hook dispatch is used on the no-hook path.
    """
    conduit_lesser._meld = MagicMock()
    conduit_lesser._meld.meld.return_value = "result"
    conduit_lesser._conduit_hooks = {}
    conduit_lesser._local_conduit_hooks = {}
    conduit_lesser._fire_conduit_hooks = MagicMock()

    result = conduit_lesser.meld(spell="sha-1")

    assert result == "result"
    conduit_lesser._fire_conduit_hooks.assert_not_called()


def test_dynamic_meld_skips_conduit_hook_dispatch_when_no_meld_hooks(
    conduit_dynamic_normal: Conduit,
) -> None:
    """
    Verify dynamic meld bypasses hook dispatch when no meld hooks exist.

    Contract:
        - Dynamic meld no-hook path does not call _fire_conduit_hooks.
        - Ticket tracking still drains to zero after the call.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.

    Raises:
        AssertionError: If hook dispatch is used or ticket cleanup fails.
    """
    conduit_dynamic_normal._meld = MagicMock()
    conduit_dynamic_normal._meld.meld.return_value = "result"
    conduit_dynamic_normal._conduit_hooks = {}
    conduit_dynamic_normal._local_conduit_hooks = {}
    conduit_dynamic_normal._fire_conduit_hooks = MagicMock()

    result = conduit_dynamic_normal.meld(spell="sha-1")

    assert result == "result"
    conduit_dynamic_normal._fire_conduit_hooks.assert_not_called()
    assert conduit_dynamic_normal._creation_gate.active_ticket_count() == 0


def test_dynamic_meld_waits_then_rechecks_closed_before_ticket_registration(
    conduit_dynamic_normal: Conduit,
) -> None:
    """
    Verify dynamic meld re-checks terminal closure after wait and before tickets.

    Contract:
        - Gate closure after wait raises RuntimeError.
        - Ticket registration does not occur when post-wait close is observed.
        - Meld delegation is not executed on post-wait closure.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.

    Raises:
        AssertionError: If post-wait closure handling regresses.
    """
    conduit_dynamic_normal._meld = MagicMock()
    conduit_dynamic_normal._meld.meld.return_value = "result"
    gate = MagicMock()
    gate.enabled = False
    gate.is_closed.side_effect = [False, True]
    conduit_dynamic_normal._creation_gate = gate

    with pytest.raises(RuntimeError, match="CreationGate is closed"):
        conduit_dynamic_normal.meld(spell="sha-1")

    gate.wait.assert_called_once_with()
    gate.register_ticket.assert_not_called()
    gate.unregister_ticket.assert_not_called()
    conduit_dynamic_normal._meld.meld.assert_not_called()


def test_dynamic_meld_enabled_path_skips_wait_and_tracks_ticket(
    conduit_dynamic_normal: Conduit,
) -> None:
    """
    Verify dynamic meld enabled-path skips wait and still tracks tickets.

    Contract:
        - Enabled gate bypasses wait.
        - Ticket register/unregister pair wraps delegated meld call.
        - Meld result is passed through unchanged.

    Args:
        conduit_dynamic_normal (Conduit): Dynamic normal conduit instance.

    Raises:
        AssertionError: If enabled-path gate flow regresses.
    """
    conduit_dynamic_normal._meld = MagicMock()
    conduit_dynamic_normal._meld.meld.return_value = "result"
    gate = MagicMock()
    gate.enabled = True
    gate.is_closed.return_value = False
    conduit_dynamic_normal._creation_gate = gate

    result = conduit_dynamic_normal.meld(spell="sha-1")

    assert result == "result"
    gate.wait.assert_not_called()
    gate.register_ticket.assert_called_once_with()
    gate.unregister_ticket.assert_called_once_with()
    conduit_dynamic_normal._meld.meld.assert_called_once()


def test_get_conduit_by_id_rejects_non_string_frame(
    conduit_normal: Conduit,
) -> None:
    """
    Verify get_conduit_by_id enforces aetheric_frame type.

    Contract:
        - Non-string aetheric_frame raises TypeError.

    Args:
        conduit_normal (Conduit): Normal conduit instance.

    Raises:
        AssertionError: If non-string frame does not raise.
    """
    with pytest.raises(TypeError, match="aetheric_frame"):
        conduit_normal.get_conduit_by_id("peer", aetheric_frame=123)


def test_get_conduit_by_id_defaults_frame(
    conduit_normal: Conduit,
    aether_stub: MagicMock,
) -> None:
    """
    Verify get_conduit_by_id maps "default" to the conduit frame.

    Contract:
        - Aether receives the conduit's frame when aetheric_frame="default".

    Args:
        conduit_normal (Conduit): Normal conduit instance.
        aether_stub (MagicMock): Aether stub used for delegation.

    Raises:
        AssertionError: If frame mapping is incorrect.
    """
    conduit_normal._aetheric_frame = "frame-1"
    sentinel = MagicMock()
    aether_stub._get_conduit_by_id.return_value = sentinel

    result = conduit_normal.get_conduit_by_id("peer", aetheric_frame="default")

    aether_stub._get_conduit_by_id.assert_called_once_with("peer", "frame-1")
    assert result is sentinel


def test_get_conduit_by_name_rejects_non_string_frame(
    conduit_normal: Conduit,
) -> None:
    """
    Verify get_conduit_by_name enforces aetheric_frame type.

    Contract:
        - Non-string aetheric_frame raises TypeError.

    Args:
        conduit_normal (Conduit): Normal conduit instance.

    Raises:
        AssertionError: If non-string frame does not raise.
    """
    with pytest.raises(TypeError, match="aetheric_frame"):
        conduit_normal.get_conduit_by_name("peer", aetheric_frame=123)


def test_get_conduit_by_name_defaults_frame(
    conduit_normal: Conduit,
    aether_stub: MagicMock,
) -> None:
    """
    Verify get_conduit_by_name maps "default" to the conduit frame.

    Contract:
        - Aether receives the conduit's frame when aetheric_frame="default".

    Args:
        conduit_normal (Conduit): Normal conduit instance.
        aether_stub (MagicMock): Aether stub used for delegation.

    Raises:
        AssertionError: If frame mapping is incorrect.
    """
    conduit_normal._aetheric_frame = "frame-1"
    sentinel = MagicMock()
    aether_stub._get_conduit_by_name.return_value = sentinel

    result = conduit_normal.get_conduit_by_name("peer", aetheric_frame="default")

    aether_stub._get_conduit_by_name.assert_called_once_with("peer", "frame-1")
    assert result is sentinel
