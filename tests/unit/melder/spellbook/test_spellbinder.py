import pytest

from melder.spellbook.existence.existence import Existence
from melder.spellbook.spellbinder import SpellBinder


class DummySpellbook:
    def __init__(self):
        self.calls = []

    def bind(self, **kwargs):
        self.calls.append(kwargs)
        return "spell-id"


def make_binder(book=None, *, default_existence=Existence.unique_per_aetheric_frame, default_permissions="create"):
    book = book or DummySpellbook()
    return SpellBinder(book, default_existence=default_existence, default_permissions=default_permissions), book


def test_init_requires_spellbook():
    with pytest.raises(ValueError):
        SpellBinder(None)


def test_defaults_set_on_init():
    binder, _ = make_binder()
    assert binder._existence == Existence.unique_per_aetheric_frame
    assert binder._permissions == "create"
    assert binder._spell is None
    assert binder._binding_name is None
    assert binder._kwargs == {}


def test_still_alive_raises_after_cleanup():
    binder, _ = make_binder()
    binder.cleanup()
    with pytest.raises(RuntimeError):
        binder._still_alive()


def test_still_alive_raises_when_spellbook_dead():
    binder, _ = make_binder()
    binder._weak_spellbook.cleanup()
    with pytest.raises(RuntimeError):
        binder._still_alive()


def test_cleanup_idempotent_and_nulls_state():
    binder, _ = make_binder()
    binder.cleanup()
    binder.cleanup()
    assert binder._weak_spellbook is None
    assert binder._spell is None
    assert binder._kwargs is None


def test_bind_sets_spell_and_overrides_and_resets_previous():
    binder, _ = make_binder()
    binder._spell = "old"
    binder._kwargs = {"pre_hooks": ["x"]}
    binder.bind("spell", existence=Existence.many, permissions="read", spellframe="Frame", binding_name="name", foo=1)
    assert binder._spell == "spell"
    assert binder._existence == Existence.many
    assert binder._permissions == "read"
    assert binder._spellframe == "Frame"
    assert binder._binding_name == "name"
    assert binder._kwargs["foo"] == 1
    assert "pre_hooks" not in binder._kwargs


@pytest.mark.parametrize(
    "method,expected",
    [
        ("as_unique", Existence.unique_per_aetheric_frame),
        ("as_many", Existence.many),
        ("as_unique_per_conduit", Existence.unique_per_aetheric_frame_per_conduit),
        ("as_unique_per_conduit_cluster", Existence.unique_per_aetheric_frame_per_conduit_cluster),
        ("as_unique_per_conduit_lineage", Existence.unique_per_aetheric_frame_per_conduit_lineage),
        ("as_unique_per_spell_space", Existence.unique_per_aetheric_frame_per_spell_space),
    ],
)
def test_existence_shorthands(method, expected):
    binder, _ = make_binder()
    binder.bind("spell")
    getattr(binder, method)()
    assert binder._existence == expected


def test_with_existence_sets_custom():
    binder, _ = make_binder()
    binder.bind("spell").with_existence(Existence.unique_per_aetheric_frame_per_conduit_cluster)
    assert binder._existence == Existence.unique_per_aetheric_frame_per_conduit_cluster


def test_with_permissions_sets_value():
    binder, _ = make_binder()
    binder.bind("spell").with_permissions("block")
    assert binder._permissions == "block"


def test_under_spellframe_sets_frame():
    binder, _ = make_binder()
    binder.bind("spell").under_spellframe("FrameX")
    assert binder._spellframe == "FrameX"


def test_named_sets_binding_name():
    binder, _ = make_binder()
    binder.bind("spell").named("beta")
    assert binder._binding_name == "beta"


def test_with_kwargs_merges():
    binder, _ = make_binder()
    binder.bind("spell").with_kwargs(a=1).with_kwargs(b=2)
    assert binder._kwargs == {"a": 1, "b": 2}


def test_with_kwargs_ignores_empty():
    binder, _ = make_binder()
    binder.bind("spell").with_kwargs()
    assert binder._kwargs == {}


def test_ensure_hook_list_creates_and_reuses():
    binder, _ = make_binder()
    lst = binder._ensure_hook_list("pre_hooks")
    assert lst == []
    lst.append("h1")
    again = binder._ensure_hook_list("pre_hooks")
    assert again is lst


def test_ensure_hook_list_raises_if_not_list():
    binder, _ = make_binder()
    binder._kwargs["pre_hooks"] = "not-list"
    with pytest.raises(TypeError):
        binder._ensure_hook_list("pre_hooks")


def test_with_pre_hook_appends():
    binder, _ = make_binder()
    binder.bind("s").with_pre_hook("h1").with_pre_hook("h2")
    assert binder._kwargs["pre_hooks"] == ["h1", "h2"]


def test_with_pre_hooks_adds_multiple_and_skips_empty():
    binder, _ = make_binder()
    binder.bind("s").with_pre_hooks().with_pre_hooks("h1", "h2")
    assert binder._kwargs["pre_hooks"] == ["h1", "h2"]


def test_with_activation_hook_and_hooks():
    binder, _ = make_binder()
    binder.bind("s").with_activation_hook("a1").with_activation_hooks("a2", "a3")
    assert binder._kwargs["activation_hooks"] == ["a1", "a2", "a3"]


def test_with_post_hook_and_hooks():
    binder, _ = make_binder()
    binder.bind("s").with_post_hook("p1").with_post_hooks("p2", "p3")
    assert binder._kwargs["post_hooks"] == ["p1", "p2", "p3"]


def test_finalize_requires_spell_selected():
    binder, _ = make_binder()
    with pytest.raises(RuntimeError):
        binder.finalize()


def test_finalize_calls_spellbook_and_resets():
    binder, book = make_binder()
    binder.bind("spell", existence=Existence.many, permissions="read", spellframe="F", binding_name="b", foo=1)
    spell_id = binder.finalize()
    assert spell_id == "spell-id"
    call = book.calls[-1]
    assert call["spell"] == "spell"
    assert call["existence"] == Existence.many
    assert call["permissions"] == "read"
    assert call["spellframe"] == "F"
    assert call["binding_name"] == "b"
    assert call["foo"] == 1
    # state reset
    assert binder._spell is None
    assert binder._existence == binder._default_existence
    assert binder._permissions == binder._default_permissions
    assert binder._kwargs == {}


def test_binder_reusable_after_finalize():
    binder, book = make_binder()
    binder.bind("s1").finalize()
    binder.bind("s2", binding_name="x").finalize()
    assert len(book.calls) == 2
    assert book.calls[0]["spell"] == "s1"
    assert book.calls[1]["binding_name"] == "x"


def test_finalize_uses_defaults_when_not_overridden():
    binder, book = make_binder(default_existence=Existence.many, default_permissions="read")
    binder.bind("spell").finalize()
    call = book.calls[-1]
    assert call["existence"] == Existence.many
    assert call["permissions"] == "read"
    assert call["spellframe"] is None
    assert call["binding_name"] is None


def test_finalize_after_spellbook_dead_raises():
    binder, _ = make_binder()
    binder.bind("s")
    binder._weak_spellbook._weak = lambda: None  # simulate collected spellbook
    with pytest.raises(RuntimeError):
        binder.finalize()


def test_bind_can_override_defaults_then_finalize():
    binder, book = make_binder(default_existence=Existence.many, default_permissions="read")
    binder.bind("spell", existence=Existence.unique_per_aetheric_frame_per_conduit, permissions="block").finalize()
    call = book.calls[-1]
    assert call["existence"] == Existence.unique_per_aetheric_frame_per_conduit
    assert call["permissions"] == "block"


def test_cleanup_prevents_bind():
    binder, _ = make_binder()
    binder.cleanup()
    with pytest.raises(RuntimeError):
        binder.bind("spell")


def test_cleanup_prevents_finalize():
    binder, _ = make_binder()
    binder.cleanup()
    with pytest.raises(RuntimeError):
        binder.finalize()


def test_cleanup_prevents_other_fluent_methods():
    binder, _ = make_binder()
    binder.cleanup()
    methods = [
        binder.with_existence,
        binder.as_unique,
        binder.as_many,
        binder.as_unique_per_conduit,
        binder.as_unique_per_conduit_cluster,
        binder.as_unique_per_conduit_lineage,
        binder.as_unique_per_spell_space,
        binder.with_permissions,
        binder.under_spellframe,
        binder.named,
        binder.with_kwargs,
        binder.with_pre_hook,
        binder.with_pre_hooks,
        binder.with_activation_hook,
        binder.with_activation_hooks,
        binder.with_post_hook,
        binder.with_post_hooks,
    ]
    for method in methods:
        with pytest.raises(RuntimeError):
            try:
                method(None)
            except TypeError:
                method()


def test_named_chain_with_hooks_and_finalize():
    binder, book = make_binder()
    binder.bind("s").named("n").with_pre_hook("h").with_activation_hook("a").with_post_hook("p").finalize()
    call = book.calls[-1]
    assert call["binding_name"] == "n"
    assert call["pre_hooks"] == ["h"]
    assert call["activation_hooks"] == ["a"]
    assert call["post_hooks"] == ["p"]


def test_with_pre_hooks_preserves_list_reference():
    binder, _ = make_binder()
    binder.bind("s")
    hooks = binder._ensure_hook_list("pre_hooks")
    binder.with_pre_hooks("a")
    assert hooks == ["a"]


def test_with_activation_hooks_preserves_reference():
    binder, _ = make_binder()
    binder.bind("s")
    hooks = binder._ensure_hook_list("activation_hooks")
    binder.with_activation_hooks("a", "b")
    assert hooks == ["a", "b"]


def test_with_post_hooks_preserves_reference():
    binder, _ = make_binder()
    binder.bind("s")
    hooks = binder._ensure_hook_list("post_hooks")
    binder.with_post_hooks("x")
    assert hooks == ["x"]


def test_reset_current_resets_all_fields():
    binder, _ = make_binder()
    binder.bind("s").with_permissions("block").named("n").under_spellframe("F").with_kwargs(x=1)
    binder._reset_current()
    assert binder._spell is None
    assert binder._existence == binder._default_existence
    assert binder._permissions == binder._default_permissions
    assert binder._spellframe is None
    assert binder._binding_name is None
    assert binder._kwargs == {}


def test_bind_allows_kwargs_passthrough():
    binder, book = make_binder()
    binder.bind("s", foo="bar", baz=2).finalize()
    call = book.calls[-1]
    assert call["foo"] == "bar"
    assert call["baz"] == 2


def test_finalize_multiple_times_reuses_same_binder():
    binder, book = make_binder()
    binder.bind("s1").finalize()
    binder.bind("s2").finalize()
    binder.bind("s3").finalize()
    assert [c["spell"] for c in book.calls] == ["s1", "s2", "s3"]


def test_with_pre_hooks_and_activation_and_post_hooks_all_together():
    binder, book = make_binder()
    binder.bind("s").with_pre_hooks("p1").with_activation_hooks("a1").with_post_hooks("o1").finalize()
    call = book.calls[-1]
    assert call["pre_hooks"] == ["p1"]
    assert call["activation_hooks"] == ["a1"]
    assert call["post_hooks"] == ["o1"]


def test_bind_overwrites_previous_kwargs_on_reset():
    binder, _ = make_binder()
    binder.bind("s1", foo=1)
    binder.bind("s2")
    assert "foo" not in binder._kwargs


def test_finalize_resets_hooks_and_binding_name():
    binder, book = make_binder()
    binder.bind("s").named("n").with_pre_hook("p").with_activation_hook("a").with_post_hook("o").finalize()
    binder.bind("s2").finalize()
    call = book.calls[-1]
    assert call["binding_name"] is None
    assert "pre_hooks" not in call
    assert "activation_hooks" not in call
    assert "post_hooks" not in call


def test_with_activation_hooks_empty_noop():
    binder, _ = make_binder()
    binder.bind("s").with_activation_hooks()
    assert "activation_hooks" not in binder._kwargs


def test_with_post_hooks_empty_noop():
    binder, _ = make_binder()
    binder.bind("s").with_post_hooks()
    assert "post_hooks" not in binder._kwargs


def test_named_overrides_previous_binding_name_on_new_bind():
    binder, _ = make_binder()
    binder.bind("s1").named("first")
    binder.bind("s2")
    assert binder._binding_name is None


def test_spellframe_overwrite_on_new_bind():
    binder, _ = make_binder()
    binder.bind("s1").under_spellframe("A")
    binder.bind("s2")
    assert binder._spellframe is None


def test_permissions_overwrite_on_new_bind():
    binder, _ = make_binder()
    binder.bind("s1").with_permissions("block")
    binder.bind("s2")
    assert binder._permissions == binder._default_permissions


def test_existence_overwrite_on_new_bind():
    binder, _ = make_binder()
    binder.bind("s1").as_many()
    binder.bind("s2")
    assert binder._existence == binder._default_existence
