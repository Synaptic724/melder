from melder.aether.spellbook.spell_crafter.spell_examiner.inspectors.profiles.method_profile import (
    MethodProfile,
)


def _profile(**overrides):
    base = dict(
        name="m",
        qualname="Q.m",
        module="mod",
        id=123,
        type="function",
        repr="<fn m>",
        builtin_mod=False,
        extension_mod=False,
        file="file.py",
        preview="def m(): ...",
        src_offset=10,
        signature="(x)",
        parameters=[{"name": "x"}],
        uninspectable=False,
        func=True,
        method=False,
        builtin=False,
        classmethod=False,
        staticmethod=False,
        generator=False,
        async_gen=False,
        coroutine=False,
        lambda_fn=False,
        abstract=False,
        closure=["y"],
        decorated=True,
        wrapped_repr="wrapped",
    )
    base.update(overrides)
    return MethodProfile(**base)


def test_init_copies_mutable_fields():
    params = [{"name": "a"}]
    closure = ["c"]
    profile = _profile(parameters=params, closure=closure)
    assert profile.parameters is not params and profile.parameters == params
    assert profile.closure is not closure and profile.closure == closure
    # mutation of originals does not leak
    params.append({"name": "b"})
    closure.append("d")
    assert profile.parameters == [{"name": "a"}]
    assert profile.closure == ["c"]


def test_cleanup_clears_all_fields_and_marks_cleaned():
    profile = _profile()
    profile.cleanup()
    assert profile.cleaned is True
    assert not hasattr(profile, 'parameters')
    assert not hasattr(profile, 'closure')
    assert not hasattr(profile, 'decorated')
    assert not hasattr(profile, 'wrapped_repr')
    assert not hasattr(profile, 'name')
    assert not hasattr(profile, 'signature')
    assert not hasattr(profile, 'start_line')
    assert not hasattr(profile, 'end_line')
    assert not hasattr(profile, 'source_text')
    assert not hasattr(profile, 'docstring_raw')
    assert not hasattr(profile, 'docstring_summary')
    assert not hasattr(profile, 'behavior_summary')
    assert not hasattr(profile, 'tags')
    # idempotent
    profile.cleanup()
    assert profile.cleaned is True


def test_flags_preserved_before_cleanup():
    profile = _profile(
        func=False, method=True, builtin=True, classmethod=True, staticmethod=False, generator=True
    )
    assert profile.method is True
    assert profile.func is False
    assert profile.builtin is True
    assert profile.classmethod is True
    assert profile.staticmethod is False
    assert profile.generator is True


def test_cleanup_handles_empty_lists():
    profile = _profile(parameters=[], closure=[])
    profile.cleanup()
    assert not hasattr(profile, 'parameters')
    assert not hasattr(profile, 'closure')


def test_wrapped_repr_and_decorated_survive_then_clear():
    profile = _profile(decorated=True, wrapped_repr="wrapped")
    assert profile.decorated is True
    assert profile.wrapped_repr == "wrapped"
    profile.cleanup()
    assert not hasattr(profile, 'decorated')
    assert not hasattr(profile, 'wrapped_repr')
