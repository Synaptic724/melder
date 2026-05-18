# Mypyc Class Decorator Guide for a Fast Native Core

This is the practical list of class decorators and class-level markers worth using when you want mypyc to produce faster code.

The blunt truth: **there are not many class decorators that help mypyc**. Most class decorators are too dynamic. In compiled native classes, mypyc officially supports only these class decorators:

- `mypy_extensions.mypyc_attr`
- `mypy_extensions.trait`
- `dataclasses.dataclass`
- `@attr.s(auto_attribs=True)`

If a compiled class uses an unsupported class decorator, mypyc can make it a regular non-native Python class instead. That is usually a speed loss.

---

## The speed hierarchy

For a hot internal class, prefer this order:

```text
Best:
    plain native class
    + explicit attributes
    + concrete types
    + @mypyc_attr(native_class=True)
    + @mypyc_attr(acyclic=True) only when safe

Good:
    native class using traits for limited interface behavior

Okay:
    dataclass / attrs class when convenience matters

Bad for hot core:
    Protocol-heavy dispatch
    ABC-heavy dispatch
    custom decorators
    runtime mutation
    dynamic attrs
    getattr / setattr / hasattr
    object / Any surfaces
```

---

# 1. `@mypyc_attr(native_class=True)`

## Use this on hot concrete classes.

```python
from mypy_extensions import mypyc_attr


@mypyc_attr(native_class=True)
class CommandSurface:
    _command_id: str
    _frame_name: str

    def __init__(self, command_id: str, frame_name: str) -> None:
        self._command_id = command_id
        self._frame_name = frame_name

    def command_id(self) -> str:
        return self._command_id
```

## What it does

It tells mypyc:

```text
This class must be native.
If it cannot be native, fail compilation.
```

That is good. You do not want silent fallback on important classes.

## When to use

Use it on:

```text
- command systems
- schedulers
- dispatchers
- factories
- specs
- ACL/access surfaces
- resolver objects
- registry objects
- lifecycle state objects
- hot object creation classes
```

## Melder rule

For the hot core, this should be your default class decorator.

---

# 2. `@mypyc_attr(acyclic=True)`

## Use this only when the object can never be in a reference cycle.

```python
from mypy_extensions import mypyc_attr


@mypyc_attr(native_class=True, acyclic=True)
class SpellCreationSpec:
    _spell_name: str
    _profile_id: str
    _policy_id: str

    def __init__(self, spell_name: str, profile_id: str, policy_id: str) -> None:
        self._spell_name = spell_name
        self._profile_id = profile_id
        self._policy_id = policy_id
```

## What it does

Native classes normally participate in CPython cyclic GC. `acyclic=True` opts the class out of cyclic GC.

This can improve allocation/deallocation speed and reduce memory overhead.

## The danger

Do **not** use this if the object can be part of a cycle.

Bad candidate:

```text
Parent -> Child -> Parent
Scheduler -> Job -> Scheduler
Container -> Item -> Container
Owner -> Callback -> Owner
```

Good candidate:

```text
small immutable-ish spec objects
leaf value objects
temporary command descriptors
flat resolved routing records
flat ACL records
```

## Melder rule

Use `acyclic=True` for leaf specs and hot tiny data carriers. Do not use it on lifecycle owners, schedulers, registries, graph nodes, or anything that can hold callbacks back into an owner.

---

# 3. `@mypyc_attr(allow_interpreted_subclasses=True)`

## Use this for public extension base classes.

```python
from mypy_extensions import mypyc_attr


@mypyc_attr(native_class=True, allow_interpreted_subclasses=True)
class BaseSpellHandler:
    def handle(self, spell_name: str) -> None:
        raise NotImplementedError
```

## What it does

By default, normal interpreted Python code cannot subclass a native class outside the compilation unit. This flag allows interpreted subclasses.

## Cost

Instances of the native base class remain mostly fine, but accessing methods/attributes through interpreted subclasses or subclasses from another compilation unit is slower.

## When to use

Use it on:

```text
- public extension base classes
- plugin base classes
- user-overridable hook classes
- API classes meant to be subclassed outside Melder's compiled core
```

## When not to use

Do not use it on private hot classes that should never be subclassed externally.

---

# 4. `@mypyc_attr(serializable=True)`

## Use this only if the native class must support pickle/copy.

```python
from mypy_extensions import mypyc_attr


@mypyc_attr(native_class=True, serializable=True)
class SerializableSpec:
    _name: str

    def __init__(self, name: str) -> None:
        self._name = name
```

## What it does

It allows native-class instances to be pickled/copied even when `__init__` cannot be called with no arguments.

## Cost

This can slow attribute access because compiled code has to be prepared for missing attributes at runtime.

## Melder rule

Do not put this on hot internal classes unless you actually need pickle/copy. For hot object creation, this is usually not what you want.

---

# 5. `@mypyc_attr(native_class=False)`

## Use this as an explicit dynamic escape hatch.

```python
from mypy_extensions import mypyc_attr


@mypyc_attr(native_class=False)
class DynamicPluginObject:
    def __init__(self) -> None:
        self.attr = 1
```

## What it does

It explicitly marks the class as a normal Python non-native class.

## Cost

Non-native classes are significantly less efficient than native classes.

## When to use

Use it only for classes that truly need Python dynamism:

```text
- arbitrary custom class decorators
- weird metaclasses
- dynamic setattr/getattr behavior
- monkey-patched plugin objects
- test/mocking escape hatches
- foreign integration objects
```

## Melder rule

This is not an optimization decorator. It is a containment decorator. It keeps dynamic garbage out of the native core.

---

# 6. `@trait`

## Use this instead of Protocols inside compiled hot paths when you need interface-like behavior.

```python
from mypy_extensions import trait


@trait
class ResolverTrait:
    def resolve(self, name: str) -> object:
        ...


class SpellResolver(ResolverTrait):
    def resolve(self, name: str) -> object:
        return object()
```

## What it does

Traits are mypyc's limited multiple-inheritance/interface mechanism for native classes.

Traits can define:

```text
- methods
- properties
- attributes
- abstract methods
```

They can also be generic.

## Cost

Access through a trait type is somewhat slower than access through a concrete native class type.

But it is much faster than going through normal Python class types, erased types, `Protocol`, `object`, or `Any`.

## Base order rule

If a class inherits a real base class and traits, traits go last:

```python
class Base:
    pass


class Good(Base, ResolverTrait):
    pass
```

Do not do:

```python
class Bad(ResolverTrait, Base):
    pass
```

## Melder rule

Use traits for shared internal contracts only where concrete typing is too rigid. For max speed, concrete native class types still win.

---

# 7. `@dataclass`

## Use this for convenience, not maximum speed.

```python
from dataclasses import dataclass


@dataclass
class SpellRecord:
    spell_name: str
    profile_id: str
    policy_id: str
```

## What it does

`@dataclass` generates methods like `__init__`, `__repr__`, and comparison methods depending on settings.

Mypyc supports dataclasses with native classes, but support is partial and dataclasses are not as efficient as pure native classes.

## Melder rule

For hot core objects, prefer explicit native classes over dataclasses.

Prefer this for the hottest objects:

```python
from mypy_extensions import mypyc_attr


@mypyc_attr(native_class=True, acyclic=True)
class SpellRecord:
    spell_name: str
    profile_id: str
    policy_id: str

    def __init__(self, spell_name: str, profile_id: str, policy_id: str) -> None:
        self.spell_name = spell_name
        self.profile_id = profile_id
        self.policy_id = policy_id
```

Use dataclasses for lower-pressure DTOs where convenience is worth it.

---

# 8. `@attr.s(auto_attribs=True)`

## Use this only if your codebase is already committed to attrs.

```python
import attr


@attr.s(auto_attribs=True)
class SpellRecord:
    spell_name: str
    profile_id: str
    policy_id: str
```

## What it does

Mypyc supports `@attr.s(auto_attribs=True)` with native classes.

## Cost

Like dataclasses, attrs classes have partial native support and are not as efficient as plain native classes.

## Melder rule

Do not introduce attrs for mypyc speed. Use plain native classes.

---

# 9. `@final`

## Use this for architecture enforcement, not direct speed.

```python
from typing import final
from mypy_extensions import mypyc_attr


@final
@mypyc_attr(native_class=True)
class FinalCommandSurface:
    pass
```

## What it does

`@final` tells mypy that a class must not be subclassed.

It is enforced by mypy in typed code. It does not stop subclassing at runtime.

## Optimization value

This is not the main mypyc speed decorator.

The value is architectural: it prevents accidental subclass extension on classes that should be leaves.

## Melder rule

Use `@final` on leaf native classes that should not be subclassed:

```text
- final specs
- final compiled records
- final dispatch surfaces
- final access surfaces
- final immutable-ish value objects
```

---

# Method decorators that are safe in native classes

These are not class decorators, but they matter inside classes.

## `@property`

```python
class SpellSpec:
    _name: str

    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self) -> str:
        return self._name
```

Good for read-only API surfaces. In the hottest code, direct internal attribute access is still simpler and faster.

## `@staticmethod`

```python
class SpellNames:
    @staticmethod
    def normalize(name: str) -> str:
        return name.strip().lower()
```

Fine when no instance state is needed.

## `@classmethod`

```python
class SpellSpec:
    @classmethod
    def from_name(cls, name: str) -> "SpellSpec":
        return cls(name)
```

Fine, but do not overuse factory indirection in the hot path if a direct constructor is enough.

## `@final` on methods

```python
from typing import final


class Base:
    @final
    def cleanup(self) -> None:
        pass
```

Good for preventing override mistakes. Not a magic speed lever.

## Avoid custom method decorators in hot classes

Bad for hot code:

```python
@log_call
@validate_runtime
@trace_span
@cached_dynamic
class Something:
    pass
```

Custom decorators usually wrap functions/classes and create dynamic call layers. That fights mypyc.

---

# Class-level markers that are not decorators but matter a lot

## `ClassVar`

Use it for class variables.

```python
from typing import ClassVar


class CommandKind:
    _default_prefix: ClassVar[str] = "cmd"
```

Mypyc requires class variables to be explicitly declared as `ClassVar` if you want class-variable behavior.

## `Final`

Use it for constants.

```python
from typing import Final


MAX_DEPTH: Final = 64
```

Mypyc can early-bind final values and replace references with compile-time-known values in compiled code.

Inside classes:

```python
from typing import Final


class Limits:
    MAX_DEPTH: Final = 64
```

Do not combine `ClassVar` and `Final`. Mypy infers the scope from where the `Final` is assigned.

## `__deletable__`

Native class attributes cannot normally be deleted. If deletion is truly required, declare it explicitly:

```python
class Resettable:
    value: int = 0
    __deletable__ = ["value"]
```

Melder rule: avoid attribute deletion in hot classes. Prefer explicit cleanup methods that set fields to `None` if the type allows it.

## `__slots__`

Do not add `__slots__` just because of mypyc.

Native classes are already slot-like: they usually do not have `__dict__`, and only declared attributes are supported.

Use explicit class-body annotations instead:

```python
class Good:
    _name: str
    _count: int
```

---

# Recommended Melder templates

## Hot leaf value/spec object

```python
from typing import final
from mypy_extensions import mypyc_attr


@final
@mypyc_attr(native_class=True, acyclic=True)
class SpellCreationSpec:
    _spell_name: str
    _profile_id: str
    _policy_id: str

    def __init__(self, spell_name: str, profile_id: str, policy_id: str) -> None:
        self._spell_name = spell_name
        self._profile_id = profile_id
        self._policy_id = policy_id

    @property
    def spell_name(self) -> str:
        return self._spell_name

    @property
    def profile_id(self) -> str:
        return self._profile_id

    @property
    def policy_id(self) -> str:
        return self._policy_id
```

Use this for small objects that get created constantly and cannot cycle.

---

## Hot owner / scheduler / registry

```python
from mypy_extensions import mypyc_attr


@mypyc_attr(native_class=True)
class SpellCreationRegistry:
    _factories: dict[str, "SpellFactory"]

    def __init__(self) -> None:
        self._factories = {}

    def register(self, name: str, factory: "SpellFactory") -> None:
        self._factories[name] = factory

    def resolve(self, name: str) -> "SpellFactory":
        return self._factories[name]
```

Do not use `acyclic=True` here unless you can prove no factory points back to the registry.

---

## Public extension base

```python
from mypy_extensions import mypyc_attr


@mypyc_attr(native_class=True, allow_interpreted_subclasses=True)
class SpellPluginBase:
    def create(self, name: str) -> object:
        raise NotImplementedError
```

Use this only for external subclassing/plugin APIs.

---

## Trait contract for compiled internal polymorphism

```python
from mypy_extensions import trait


@trait
class SpellFactoryTrait:
    def create(self, spec: "SpellCreationSpec") -> object:
        ...


class StaticSpellFactory(SpellFactoryTrait):
    def create(self, spec: "SpellCreationSpec") -> object:
        return object()
```

Use traits instead of Protocols inside the compiled hot core when you need polymorphism.

---

## Dynamic escape hatch

```python
from mypy_extensions import mypyc_attr


@mypyc_attr(native_class=False)
class RuntimeDynamicPlugin:
    pass
```

Use this to isolate dynamic/plugin/reflection/codegen surfaces outside the native core.

---

# What not to use on hot native classes

Avoid these on hot mypyc-native classes:

```text
custom class decorators
custom metaclasses
runtime registration decorators
Pydantic model decorators/classes
ORM/declarative base machinery
attrs/dataclass if max speed matters
Protocol as the main internal dispatch type
ABC as the main internal dispatch type
runtime monkey patching
dynamic setattr/getattr/hasattr
```

Unsupported class decorators can force classes non-native, which defeats the point.

---

# Practical decision table

| Goal | Use |
|---|---|
| Force class to compile native | `@mypyc_attr(native_class=True)` |
| Fast leaf object allocation/deallocation | `@mypyc_attr(native_class=True, acyclic=True)` |
| Public subclassable API | `@mypyc_attr(native_class=True, allow_interpreted_subclasses=True)` |
| Pickle/copy support | `@mypyc_attr(serializable=True)` |
| Explicit dynamic Python class | `@mypyc_attr(native_class=False)` |
| Interface-like compiled contract | `@trait` |
| Convenience data carrier | `@dataclass` or `@attr.s(auto_attribs=True)` |
| Prevent subclassing | `@final` |
| Class variable | `ClassVar[...]` |
| Constant / early-bound value | `Final[...]` |
| Deletable native attr | `__deletable__ = ["attr"]` |

---

# Melder rule of thumb

For maximum speed:

```text
Hot internal core:
    @mypyc_attr(native_class=True)
    concrete native classes
    concrete return types
    direct method calls
    typed dict/list/tuple
    Final constants
    ClassVar class state

Hot leaf records/specs:
    @final
    @mypyc_attr(native_class=True, acyclic=True)

Internal polymorphism:
    @trait only where concrete classes are too rigid

Public/plugin/dynamic edge:
    allow_interpreted_subclasses=True or native_class=False
```

Do not decorator-soup the codebase. The fastest mypyc class is usually a boring explicit native class with declared attributes and precise types.

---

# Sources

- Mypyc native classes: https://mypyc.readthedocs.io/en/latest/native_classes.html
- Mypyc using type annotations: https://mypyc.readthedocs.io/en/latest/using_type_annotations.html
- Mypyc differences from Python: https://mypyc.readthedocs.io/en/latest/differences_from_python.html
- Mypy Final names, methods, classes: https://mypy.readthedocs.io/en/stable/final_attrs.html
- Python dataclasses: https://docs.python.org/3/library/dataclasses.html
- Typing ClassVar spec: https://typing.python.org/en/latest/spec/class-compat.html
