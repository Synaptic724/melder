"""P5 tests: the lowering passes operands positionally only where the receiving code binds them by that name.

Usage: python apply_p5_test_edits.py <tree_root> [--check]

Unit: call-shape contracts over real classes and functions, plus a module fixture that keeps the file's
`construct(*args, **kwargs)` fakes on positional calls (they stand for plain classes). Component: a class whose
inherited `__new__` observes the call gets names in normal and override melds, both families, fresh and cached.
Anchors must match exactly once. Engine: ../s3_staging/apply_s3b1_edits.py (_apply_one) plus a local append.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "s3_staging"))

from apply_s3b1_edits import _apply_one

UNIT = "tests/unit/melder/spellbook/spell_compiler/shared_assets/test_site_plan_lowering.py"
COMPONENT = "tests/component/melder/spellbook/test_spellbook_component_override_key_set_plans.py"

UNIT_APPEND = '''

# --- Call shape (P5): positional only where the receiving code binds the position to that name ---


@pytest.fixture(autouse=True)
def _closure_fakes_are_plain_targets(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Let the fake spells' `construct(*args, **kwargs)` closures take positional operands.

    They stand for plain classes, and the plan contracts above read their `args`. Real classes and
    functions (the call-shape contracts below) go through the real `positional_run`.
    """
    real = SitePlanLowering.positional_run

    def positional_run(target: Any, names: Tuple[str, ...]) -> int:
        """Treat this file's closure fakes as plain targets; defer everything else."""
        if type(target) is FunctionType and target.__qualname__.endswith("<locals>.construct"):
            return len(names)
        return real(target, names)

    monkeypatch.setattr(SitePlanLowering, "positional_run", staticmethod(positional_run))


class _Dep:
    """A plain dependency."""

    def __init__(self) -> None:
        """Nothing to keep."""


class _PlainTarget:
    """A plain class: a positional call binds exactly as the keyword call would."""

    def __init__(self, a: _Dep, b: _Dep) -> None:
        """Keep the operands."""
        self.a = a
        self.b = b


class _NameReadingBase:
    """A base whose `__new__` records the call shape it receives."""

    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        """Record (positional count, keyword names), then allocate."""
        instance = super().__new__(cls)
        instance.shape = (len(args), tuple(sorted(kwargs)))
        return instance


class _NameReadingTarget(_NameReadingBase):
    """Its signature is its own `__init__`'s, but every call passes through the base `__new__`."""

    def __init__(self, a: _Dep, b: _Dep) -> None:
        """Keep the operands."""
        self.a = a
        self.b = b


class _PositionalOnlyNameReader(_NameReadingBase):
    """Positional-only parameters behind a name-reading `__new__`."""

    def __init__(self, a: _Dep, b: _Dep, /) -> None:
        """Keep the operands."""
        self.a = a
        self.b = b


class _RecordingMeta(type):
    """A metaclass whose `__call__` sees every construction."""

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        """Construct normally."""
        return super().__call__(*args, **kwargs)


class _MetaCallTarget(metaclass=_RecordingMeta):
    """Constructed through a custom metaclass `__call__`."""

    def __init__(self, a: _Dep, b: _Dep) -> None:
        """Keep the operands."""
        self.a = a
        self.b = b


class _Owner:
    """Owns a bound-method spell target; instances are callable too."""

    def method(self, a: _Dep, b: _Dep) -> Tuple[_Dep, _Dep]:
        """Return the operands."""
        return (a, b)

    def __call__(self, a: _Dep, b: _Dep) -> Tuple[_Dep, _Dep]:
        """Return the operands."""
        return (a, b)


def _plain_function(a: _Dep, b: _Dep) -> Tuple[_Dep, _Dep]:
    """A plain function spell target."""
    return (a, b)


def _name_reading_decorator(function: Callable[..., Any]) -> Callable[..., Any]:
    """Wrap `function` in a signature-preserving wrapper that reports the call shape it received."""

    @functools.wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """Return (positional count, keyword names, the wrapped result)."""
        return (len(args), tuple(sorted(kwargs)), function(*args, **kwargs))

    return wrapper


@_name_reading_decorator
def _wrapped_function(a: _Dep, b: _Dep) -> Tuple[_Dep, _Dep]:
    """A decorated function spell target."""
    return (a, b)


def _call_shape_plan(target: Any, keys: Tuple[str, ...] = (), arity: int = 0,
                     kind: str = "POSITIONAL_OR_KEYWORD") -> Tuple[Callable[..., Any], str]:
    """Emit and compile the plan of a root `target(a: _Dep, b: _Dep)` over two plain many dependencies."""
    built: Counter = Counter()
    dep_a = _spell("a", built)
    dep_a.spell = _Dep
    dep_b = _spell("b", built)
    dep_b.spell = _Dep
    root = _spell("root", built)
    root.spell = target
    steps = (
        _step(("a", 1), dep_a),
        _step(("b", 2), dep_b),
        _step(("root", None), root, ("a", (("a", 1),)), ("b", (("b", 2),))),
    )
    topologies = {
        "root": SpellLocalTopology("root", (_socket("root", "a", 0, kind), _socket("root", "b", 1, kind))),
        "a": SpellLocalTopology("a", ()),
        "b": SpellLocalTopology("b", ()),
    }
    graph = SitePlanLowering.build_site_graph(
        root_spell_id="root", root_instance_key=("root", None), steps=steps, topology_for=topologies.get,
    )
    resolution = OverrideKeyResolver.resolve(graph, keys, arity)
    source, namespace, _ = SitePlanLowering.emit(
        steps=steps, site_graph=graph, resolution=resolution, root_instance_key=("root", None),
        root_spell_id="root", root_spell_name="root", arity=arity,
    )
    exec(compile(source, "<test>", "exec"), namespace)
    graph.cleanup()
    return namespace[SitePlanLowering.PLAN_FUNCTION_NAME], source


def test_positional_run_follows_the_code_that_receives_the_call() -> None:
    """Plain classes, functions and bound methods of plain functions bind positions by name; nothing else does."""
    run = SitePlanLowering.positional_run
    assert run(_PlainTarget, ("a", "b")) == 2
    assert run(_PlainTarget, ("a", "c")) == 1
    assert run(_PlainTarget, ("b", "a")) == 0
    assert run(_NameReadingTarget, ("a", "b")) == 0
    assert run(_MetaCallTarget, ("a", "b")) == 0
    assert run(_plain_function, ("a", "b")) == 2
    assert run(_wrapped_function, ("a", "b")) == 0
    assert run(_Owner().method, ("a", "b")) == 2
    assert run(_Owner(), ("a", "b")) == 0


def test_plain_class_root_receives_its_dependencies_positionally() -> None:
    """The fast positional call stays for a plain class."""
    plan, source = _call_shape_plan(_PlainTarget)
    result = plan(None, {})
    assert "(v0, v1)" in source
    assert isinstance(result.a, _Dep) and isinstance(result.b, _Dep)


def test_name_reading_class_receives_names_in_normal_and_override_plans() -> None:
    """A class whose inherited `__new__` sees the call gets its dependencies and supplied values by name."""
    plan, _ = _call_shape_plan(_NameReadingTarget)
    assert plan(None, {}).shape == (0, ("a", "b"))
    plan, _ = _call_shape_plan(_NameReadingTarget, ("a",))
    supplied = _Dep()
    result = plan(None, {"a": supplied})
    assert result.shape == (0, ("a", "b")) and result.a is supplied


def test_root_positional_payload_stays_positional_for_a_name_reading_class() -> None:
    """A caller's `__args__` values keep their positions; the dependency after them goes by name."""
    plan, _ = _call_shape_plan(_NameReadingTarget, ("__args__",), arity=1)
    first = _Dep()
    result = plan(None, {"__args__": [first]})
    assert result.shape == (1, ("b",)) and result.a is first


def test_signature_preserving_wrapper_receives_names() -> None:
    """A `functools.wraps(*args, **kwargs)` wrapper sees names, as the keyword call would give it."""
    plan, _ = _call_shape_plan(_wrapped_function)
    positional_count, names, (a, b) = plan(None, {})
    assert positional_count == 0 and names == ("a", "b")
    assert isinstance(a, _Dep) and isinstance(b, _Dep)


def test_positional_only_parameters_behind_a_name_reading_new_use_the_generic_helper() -> None:
    """A positional-only operand that cannot go positionally makes the step non-direct, as before S2b."""
    _, source = _call_shape_plan(_PositionalOnlyNameReader, kind="POSITIONAL_ONLY")
    assert "_construct_spell_instance(" in source
'''

COMPONENT_APPEND = '''

class NameReadingBase:
    """A base whose `__new__` records whether it received names or positions."""

    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        """Record (positional count, keyword names), then allocate."""
        instance = super().__new__(cls)
        instance.shape = (len(args), tuple(sorted(kwargs)))
        return instance


class NamedRoot(NameReadingBase):
    """Its signature is its own `__init__`'s; every call passes through the base `__new__`."""

    def __init__(self, leaf: Leaf, b: B, limit: int = 3) -> None:
        """Keep the operands."""
        self.leaf = leaf
        self.b = b
        self.limit = limit


@FAMILIES
@CACHED
def test_a_constructor_that_observes_names_receives_names(book: Spellbook, family: str, cached: bool) -> None:
    """Normal and override melds pass values by name when the call passes through a custom `__new__` (P5)."""
    shared_b = Existence.unique_per_conduit if family == "generalized" else Existence.many
    conduit = _conjure(
        book, [(Leaf, Existence.many), (B, shared_b), (NamedRoot, Existence.many)], NamedRoot, cached,
    )
    assert conduit.meld(NamedRoot).shape == (0, ("b", "leaf"))
    assert conduit.meld(NamedRoot, override={"limit": 9}).shape == (0, ("b", "leaf", "limit"))
    supplied = Leaf()
    result = conduit.meld(NamedRoot, override={"leaf": supplied})
    assert result.shape == (0, ("b", "leaf")) and result.leaf is supplied
'''

EDITS = {
    UNIT: [
        ("replace", "import threading\n", "import functools\nimport threading\n"),
        ("replace", "from types import SimpleNamespace\n", "from types import FunctionType, SimpleNamespace\n"),
        ("append", UNIT_APPEND),
    ],
    COMPONENT: [("append", COMPONENT_APPEND)],
}


def _apply(data: str, edit: tuple, rel: str) -> str:
    """Apply one edit; `append` adds text after the file's final newline."""
    if edit[0] == "append":
        if not data.endswith("\n"):
            raise SystemExit(f"{rel}: no final newline")
        return data + edit[1]
    return _apply_one(data, edit, rel)


def main() -> None:
    """Check every anchor, then write every file (unless --check)."""
    root = pathlib.Path(sys.argv[1])
    check = "--check" in sys.argv[2:]
    pending = {}
    for rel, edits in EDITS.items():
        path = root / rel
        data = path.read_bytes().decode("utf-8")
        for edit in edits:
            data = _apply(data, edit, rel)
        compile(data, rel, "exec")
        pending[path] = data
    for path, data in pending.items():
        if not check:
            path.write_bytes(data.encode("utf-8"))
        print(("checked " if check else "edited ") + str(path))


if __name__ == "__main__":
    main()
