import gc
import types

import pytest

from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbinder import SpellBinder
from melder.utilities.synchronization.sync_weak_ref import SyncWeakRef


_strong_spellbooks = []


class SpellbookStub:
    """
    Minimal Spellbook double to capture bind calls and allow weakref behavior.
    """

    def __init__(self, should_raise: Exception | None = None):
        self.bind_calls: list[dict] = []
        self.should_raise = should_raise
        self.cleaned = False

    def bind(self, **kwargs):
        if self.should_raise:
            raise self.should_raise
        self.bind_calls.append(kwargs)
        return kwargs.get("spell_id", "spell-id")

    def cleanup(self):
        self.cleaned = True


def _binder(spellbook=None, **kwargs) -> SpellBinder:
    sb = spellbook or SpellbookStub()
    _strong_spellbooks.append(sb)
    binder = SpellBinder(sb, **kwargs)
    return binder


def test_bind_sets_core_fields_and_resets_prior_state():
    binder = _binder()
    binder._spell = "old"
    binder._kwargs = {"pre_hooks": ["x"], "other": 1}
    result = binder.bind("spell", existence=Existence.many, permissions="read", spellframe="Frame", binding_name="name",
                         foo=1)
    assert result is binder
    assert binder._spell == "spell"
    assert binder._existence is Existence.many
    assert binder._permissions == "read"
    assert binder._spellframe == "Frame"
    assert binder._binding_name == "name"
    assert binder._kwargs["foo"] == 1
    assert "pre_hooks" not in binder._kwargs  # prior state cleared


def test_constructor_requires_spellbook() -> None:
    with pytest.raises(ValueError, match="SpellBinder requires a valid ISpellbook instance."):
        SpellBinder(None)


@pytest.mark.parametrize(
    "method,expected",
    [
        ("as_unique", Existence.unique),
        ("as_many", Existence.many),
        ("as_unique_per_conduit", Existence.unique_per_conduit),
        ("as_unique_per_conduit_cluster", Existence.unique_per_conduit_cluster),
        ("as_unique_per_conduit_lineage", Existence.unique_per_conduit_lineage),
        ("as_unique_per_spell_space", Existence.unique_per_spell_space),
    ],
)
def test_fluent_existence_methods(method, expected):
    binder = _binder()
    getattr(binder, method)()
    assert binder._existence is expected


def test_with_existence_sets_value():
    binder = _binder()
    binder.with_existence(Existence.unique_per_conduit)
    assert binder._existence is Existence.unique_per_conduit


def test_with_permissions_under_spellframe_and_named():
    binder = _binder()
    binder.with_permissions("block").under_spellframe("Frame").named("alias")
    assert binder._permissions == "block"
    assert binder._spellframe == "Frame"
    assert binder._binding_name == "alias"


def test_with_kwargs_merges_and_overrides():
    binder = _binder()
    binder.with_kwargs(alpha=1, beta=2)
    binder.with_kwargs(beta=3, gamma=4)
    assert binder._kwargs == {"alpha": 1, "beta": 3, "gamma": 4}


def test_with_pre_hook_and_variants_accumulate():
    binder = _binder()
    hook_a = lambda: None
    hook_b = lambda: None
    binder.with_pre_hook(hook_a).with_pre_hooks(hook_b)
    assert binder._kwargs["pre_hooks"] == [hook_a, hook_b]


def test_with_pre_hooks_noop_on_empty():
    binder = _binder()
    binder.with_pre_hooks()
    assert "pre_hooks" not in binder._kwargs


def test_activation_hooks_accumulate_and_preserve_order():
    binder = _binder()
    hooks = [lambda: 1, lambda: 2, lambda: 3]
    binder.with_activation_hook(hooks[0]).with_activation_hooks(hooks[1], hooks[2])
    assert binder._kwargs["activation_hooks"] == hooks


def test_post_hooks_accumulate_and_preserve_order():
    binder = _binder()
    hooks = [lambda: 1, lambda: 2]
    binder.with_post_hook(hooks[0]).with_post_hooks(hooks[1])
    assert binder._kwargs["post_hooks"] == hooks


def test_ensure_hook_list_rejects_non_list():
    binder = _binder()
    binder._kwargs["pre_hooks"] = "not-a-list"
    with pytest.raises(TypeError):
        binder.with_pre_hook(lambda: None)


def test_finalize_requires_bind_first():
    binder = _binder()
    with pytest.raises(RuntimeError):
        binder.finalize()


def test_finalize_calls_spellbook_bind_and_resets_state():
    spellbook = SpellbookStub()
    binder = _binder(spellbook=spellbook)
    hook = lambda: None
    binder.bind("spell", existence=Existence.unique_per_conduit, permissions="read",
                spellframe="Frame", binding_name="name", extra="x") \
        .with_pre_hook(hook)
    spell_id = binder.finalize()
    assert spell_id == "spell-id"
    call = spellbook.bind_calls[-1]
    assert call["spell"] == "spell"
    assert call["existence"] is Existence.unique_per_conduit
    assert call["permissions"] == "read"
    assert call["profile"] == "general"
    assert call["spellframe"] == "Frame"
    assert call["binding_name"] == "name"
    assert call["extra"] == "x"
    assert call["pre_hooks"] == [hook]
    # state reset for reuse
    assert binder._spell is None
    assert binder._kwargs == {}
    assert binder._existence is binder._default_existence
    assert binder._permissions == binder._default_permissions


def test_bind_profile_override_flows_through_finalize():
    spellbook = SpellbookStub()
    binder = _binder(spellbook=spellbook)
    binder.bind("spell", profile="detailed")
    binder.finalize()
    call = spellbook.bind_calls[-1]
    assert call["profile"] == "detailed"


def test_finalize_returns_spell_id_from_spellbook():
    spellbook = SpellbookStub()
    binder = _binder(spellbook=spellbook)
    binder.bind("spell")
    # SpellbookStub returns "spell-id" unless overridden in kwargs
    assert binder.finalize() == "spell-id"


def test_finalize_passes_kwargs_through_to_spellbook():
    spellbook = SpellbookStub()
    binder = _binder(spellbook=spellbook)
    binder.bind("spell", alpha=1).with_kwargs(beta=2)
    binder.finalize()
    call = spellbook.bind_calls[-1]
    assert call["alpha"] == 1
    assert call["beta"] == 2


def test_ensure_hook_list_reuses_existing_list():
    spellbook = SpellbookStub()
    binder = _binder(spellbook=spellbook)
    existing_hook = lambda: None
    binder.bind("spell", pre_hooks=[existing_hook])
    binder.with_pre_hook(lambda: None)
    assert binder._kwargs["pre_hooks"][0] is existing_hook


def test_finalize_propagates_spellbook_errors():
    err = RuntimeError("boom")
    binder = _binder(spellbook=SpellbookStub(should_raise=err))
    binder.bind("spell")
    with pytest.raises(RuntimeError, match="boom"):
        binder.finalize()


def test_cleanup_is_idempotent_and_deletes_slots():
    binder = _binder()
    binder.cleanup()
    binder.cleanup()
    assert not hasattr(binder, "_weak_spellbook")
    assert not hasattr(binder, "_spell")
    assert not hasattr(binder, "_existence")
    assert not hasattr(binder, "_permissions")
    assert not hasattr(binder, "_kwargs")
    assert not hasattr(binder, "_default_existence")
    assert not hasattr(binder, "_default_permissions")
    assert not hasattr(binder, "_default_profile")
    assert hasattr(binder, "_lock")
    assert binder._cleaned is True


def test_cleanup_swallows_weakref_cleanup_failures() -> None:
    binder = _binder()

    class _FailingWeakRef:
        def cleanup(self):
            raise RuntimeError("weakref cleanup boom")

    binder._weak_spellbook = _FailingWeakRef()

    binder.cleanup()

    assert not hasattr(binder, "_weak_spellbook")
    assert binder._cleaned is True


def test_methods_raise_after_cleanup():
    binder = _binder()
    binder.cleanup()
    with pytest.raises(RuntimeError):
        binder.bind("spell")
    with pytest.raises(RuntimeError):
        binder.with_existence(Existence.unique)
    with pytest.raises(RuntimeError):
        binder.with_permissions("read")
    with pytest.raises(RuntimeError):
        binder.with_pre_hook(lambda: None)
    with pytest.raises(RuntimeError):
        binder.finalize()


def test_reset_current_enforces_liveness():
    binder = _binder()
    binder.cleanup()
    with pytest.raises(RuntimeError):
        binder._reset_current()


def test_require_spellbook_raises_when_spellbook_dead():
    binder = _binder()
    # Drop strong reference and force gc
    spellbook_ref = binder._weak_spellbook
    del binder._weak_spellbook
    gc.collect()
    binder._weak_spellbook = spellbook_ref
    spellbook_ref.cleanup()
    with pytest.raises(RuntimeError):
        binder._require_spellbook()


def test_bind_discards_unfinalized_state():
    binder = _binder()
    binder.bind("first").with_pre_hook(lambda: None).with_permissions("block")
    binder.bind("second")
    assert binder._spell == "second"
    assert binder._permissions == binder._default_permissions
    assert binder._kwargs == {}


def test_with_kwargs_noop_when_empty():
    binder = _binder()
    binder.with_kwargs()
    assert binder._kwargs == {}


def test_with_activation_hooks_noop_when_empty():
    binder = _binder()
    binder.with_activation_hooks()
    assert "activation_hooks" not in binder._kwargs


def test_with_post_hooks_noop_when_empty():
    binder = _binder()
    binder.with_post_hooks()
    assert "post_hooks" not in binder._kwargs


def test_with_pre_hooks_extends_existing_list():
    binder = _binder()
    hook_a = lambda: None
    hook_b = lambda: None
    binder.with_pre_hook(hook_a)
    binder.with_pre_hooks(hook_b)
    assert binder._kwargs["pre_hooks"] == [hook_a, hook_b]


def test_with_activation_hooks_extends_existing_list():
    binder = _binder()
    hook_a = lambda: None
    hook_b = lambda: None
    binder.with_activation_hook(hook_a)
    binder.with_activation_hooks(hook_b)
    assert binder._kwargs["activation_hooks"] == [hook_a, hook_b]


def test_with_post_hooks_extends_existing_list():
    binder = _binder()
    hook_a = lambda: None
    hook_b = lambda: None
    binder.with_post_hook(hook_a)
    binder.with_post_hooks(hook_b)
    assert binder._kwargs["post_hooks"] == [hook_a, hook_b]


def test_bind_overrides_defaults_only_when_provided():
    binder = _binder(default_existence=Existence.many, default_permissions="create")
    binder.bind("s")
    assert binder._existence is Existence.many
    assert binder._permissions == "create"
    binder.bind("s", permissions="read")
    assert binder._permissions == "read"
    assert binder._existence is Existence.many


def test_finalized_binder_can_be_reused_cleanly():
    spellbook = SpellbookStub()
    binder = _binder(spellbook=spellbook)
    binder.bind("a").finalize()
    binder.bind("b").with_permissions("block").finalize()
    assert len(spellbook.bind_calls) == 2
    assert spellbook.bind_calls[0]["spell"] == "a"
    assert spellbook.bind_calls[1]["spell"] == "b"
    assert spellbook.bind_calls[1]["permissions"] == "block"


def test_finalize_includes_hook_lists_from_kwargs_passthrough():
    spellbook = SpellbookStub()
    binder = _binder(spellbook=spellbook)
    hook = lambda: None
    binder.bind("spell", pre_hooks=[hook], activation_hooks=[hook], post_hooks=[hook])
    binder.finalize()
    call = spellbook.bind_calls[-1]
    assert call["pre_hooks"] == [hook]
    assert call["activation_hooks"] == [hook]
    assert call["post_hooks"] == [hook]


def test_finalize_uses_current_state_after_fluent_changes():
    spellbook = SpellbookStub()
    binder = _binder(spellbook=spellbook, default_existence=Existence.many, default_permissions="create")
    binder.bind("spell").as_unique_per_conduit_cluster().with_permissions("block").named("n").under_spellframe("F")
    binder.finalize()
    call = spellbook.bind_calls[-1]
    assert call["existence"] is Existence.unique_per_conduit_cluster
    assert call["permissions"] == "block"
    assert call["binding_name"] == "n"
    assert call["spellframe"] == "F"


def test_with_hooks_after_spellbook_cleaned_raises():
    binder = _binder()
    binder._weak_spellbook.cleanup()
    with pytest.raises(RuntimeError):
        binder.with_post_hook(lambda: None)


def test_finalize_raises_when_spellbook_dead():
    binder = _binder()
    # Simulate dead spellbook by nulling the weakref wrapper.
    binder._weak_spellbook = None
    with pytest.raises(RuntimeError):
        binder.bind("spell")


def test_bind_after_cleanup_raises_runtime():
    binder = _binder()
    binder.cleanup()
    with pytest.raises(RuntimeError):
        binder.bind("spell")


def test_finalize_reset_does_not_remove_defaults():
    binder = _binder(default_existence=Existence.unique_per_spell_space, default_permissions="read")
    binder.bind("a").finalize()
    assert binder._existence is Existence.unique_per_spell_space
    assert binder._permissions == "read"


def test_with_kwargs_respects_live_spellbook_guard():
    binder = _binder()
    binder._weak_spellbook.cleanup()
    with pytest.raises(RuntimeError):
        binder.with_kwargs(a=1)


def test_with_permissions_respects_live_spellbook_guard():
    binder = _binder()
    binder._weak_spellbook.cleanup()
    with pytest.raises(RuntimeError):
        binder.with_permissions("read")


def test_named_respects_live_spellbook_guard():
    binder = _binder()
    binder._weak_spellbook.cleanup()
    with pytest.raises(RuntimeError):
        binder.named("x")


def test_under_spellframe_respects_live_spellbook_guard():
    binder = _binder()
    binder._weak_spellbook.cleanup()
    with pytest.raises(RuntimeError):
        binder.under_spellframe("frame")


def test_with_pre_hook_respects_live_spellbook_guard():
    binder = _binder()
    binder._weak_spellbook.cleanup()
    with pytest.raises(RuntimeError):
        binder.with_pre_hook(lambda: None)
