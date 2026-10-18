# Code description patch: SpellCodeDigest - the spell_id contract (spell_identity_is_the_code_2026_10_18)

## Metadata
- Patch ID: spell_identity_is_the_code_2026_10_18
- Component: SpellCodeDigest (new, `src/melder/aether/spellbook/bind/spell_code_digest.py`), owned by `Bind` and
  called by `Bind._bind_logic` and `Bind.spell_id_inspector`
- Status: approved by the owner's word to land S1 (2026-10-18T15:01:53Z); updated for decision B
- Owner: user; melder_0 (synaptic_python_developer)
- Created: 2026-10-18T13:21:00Z
- Updated: 2026-10-18T17:05:55Z
- Prototype: `context_compass/artifacts/spell_identity_20261018/probes/code_digest_v2.py` (not in src/); what this
  contract changes from it is listed under Edge/Error and Rollback Semantics.

## Trigger Justification
- The spell_id is the key every registry, record, cache and research history files a spell under, and every rule
  below decides what "the same spell" means. The encoding is written down once, exactly, so the implementation, its
  tests and any later change of the rule are checked against one text. Its edges are subtle (the docstring slot in
  3.14's constants, deoptimized bytecode, closures, cycles) and it must be deterministic on the free-threaded runtime.

## Control-Flow Description (Pseudocode Level)
1. `spell_id(target)`: `encoding = target_encoding(target)`; when that raises RecursionError (data nested past the
   interpreter's recursion limit), `encoding = repr_encoding(target)`. Return the SHA256 hex digest of
   `"v5-code\n" + sys.implementation.cache_tag + "\n" + encoding`, UTF-8 encoded.
2. `target_encoding(target)`, the first rule that matches:
   a. a class: `"class " + class_digest(target)`, or `"class " + named(target)` when it is installed third-party;
   b. a plain Python function (`types.FunctionType`): `"function " + module + " " + qualname + " " +
      function_digest(target)`, or `"function " + named(target)` when it is installed third-party;
   c. a bound method, a `functools.partial`, an enum member, a scalar, a tuple, list, set, frozenset or dict, or a
      builtin function or descriptor: `"value " + encode(target)`;
   d. an object with Python-visible state - an instance `__dict__`, or a `__slots__` entry on a class of its MRO -
      whose type is application code (not standard library, Melder or installed third-party):
      `"object " + class_digest(type(target)) + data(target)`;
   d2. an object of an installed third-party class other than Melder's: `"object " + external(target)` (the
      value table's `ext:` row);
   e. anything else: `repr_encoding(target)` = `"repr " + qualified(type(target)) + " " +
      InspectorUtility.stable_repr(target)` - today's rule for an object (its full repr, addresses removed).
3. `class_digest(cls)`: the lines `module <module>`, `qualname <qualname>`, `meta <metaclass>` (its qualified name
   when it is standard library, its qualified name and distribution version when it is installed third-party,
   else its qualified name and its class digest), `bases <qualified names of __bases__, comma-joined>`, then one
   line per class of `cls.__mro__`, in order: `own <namespace_digest(cls)>` for cls itself; `mro <qualified>` for
   a standard-library or builtin class; `mro <qualified> <dist>==<version>` for an installed third-party class;
   `mro <qualified> <namespace_digest>` for any other. The SHA256 of the lines joined by newlines.
4. `namespace_digest(klass)`: one line per entry of `klass.__dict__`: excluded keys are skipped; an opaque key gives
   `<name>=opaque:<qualified type>`; any other gives `<name>=` + `encode(value, owner=klass)`. The lines are sorted,
   joined and hashed (so the order a class body defines its members in never counts).
5. `function_digest(fn)`: the lines `fn <module>:<name>`, `code <code_digest(fn.__code__)>`,
   `defaults <encode(__defaults__)>`, `kwdefaults <encode(__kwdefaults__)>`; then `annotate <function_digest>` when
   `__annotate__` is a function; one `cell <name>=<...>` per closure cell in `co_freevars` order - `<class namespace>`
   for `__classdict__` (the class body namespace, docstring included, is encoded by its own rules), `<empty>` for an
   empty cell, else `encode(contents)`; `type_params <encode(__type_params__)>` when not empty; `dict <encode(the
   function's __dict__ without __wrapped__)>` when not empty (the wrapped function is already in the wrapper's closure).
6. `code_digest(code)`, memoized per code object: walk `code.co_code` - the deoptimized stream, so specialization,
   sys.monitoring and tracing never show - two bytes at a time, folding EXTENDED_ARG into the next argument. The
   argument of every opcode in `dis.hasconst` (LOAD_CONST on 3.14) is replaced by the order in which the stream first
   loads that constant, and the constant's text is recorded at its first use. The lines: `co_name`;
   `co_argcount,co_posonlyargcount,co_kwonlyargcount`; `co_flags` without `CO_HAS_DOCSTRING`; the opcodes (hex); the
   arguments as little-endian unsigned 32-bit integers (hex); `co_exceptiontable` (hex); `co_names`, `co_varnames`,
   `co_cellvars` and `co_freevars`, each comma-joined; the used constants' texts, "|"-joined. A constant's text: a
   code object `code:<code_digest>`; a frozenset its items' texts, sorted; a tuple its items' texts, in order;
   a number, string or bytes literal, None, Ellipsis or a bool its exact `repr()` (an integer past the
   interpreter's decimal conversion limit as `hex:<digits>`); anything else its `repr()` with " at 0x..."
   addresses removed.
7. `encode(value, owner)`: the first row of the table below that matches. A container, class, function or object
   already on the current path encodes as `cycle:<kind>`. A container is read through its builtin base type
   (`tuple.__iter__`, `dict.items`, ...), copied in one call.
8. `data(obj)`: for each class of `type(obj).__mro__`, each name its `__slots__` declares (a string or an iterable;
   `__dict__` and `__weakref__` skipped; a private name mangled with that class's name), read with
   `object.__getattribute__`: `slot <name>=<encode(value)>`, or `slot <name>=<unset>`; then the instance `__dict__`,
   read with `object.__getattribute__`, in insertion order: `attr <key>=<encode(value)>`, skipping a key whose class
   attribute (`inspect.getattr_static`) is a `functools.cached_property`. Wrapped in braces after the head
   (`objclass:<class_digest>` for the target, `obj:<qualified type>` for nested data).

| value | encoded as |
|---|---|
| None, Ellipsis, NotImplemented | its repr |
| an enum member | `enum:<qualified class>.<name>=<encode(its value)>` |
| bool, int, float, complex, str, bytes, bytearray, or a subclass | `<qualified type>:<repr through the builtin base type>`; an int past the decimal limit `hex:<digits>` |
| tuple, list | `<qualified type>[<items>]` |
| set, frozenset | `<qualified type>{<items, sorted by their text>}` |
| dict, mappingproxy | `<qualified type>{<key>:<value>, in insertion order}` |
| a class nested in the owner (same module, qualname under the owner's) | `nested:<class_digest>` |
| any other class | `class:<qualified>` |
| a plain function | `fn:<function_digest>`; an installed third-party one `fn:<qualified> <dist>==<version>` |
| staticmethod, classmethod | `<kind>(<encode(__func__)>)` |
| property | `property(<fget>,<fset>,<fdel>)` |
| functools.cached_property | `cached_property(<encode(func)>)` |
| a bound method | `method(<encode(__func__)> of <encode(__self__)>)` |
| functools.partial | `partial(<func>,<args>,<keywords>)` |
| a module | `module:<name>` |
| a code object | `code:<code_digest>` |
| a builtin function, method or slot/member descriptor | `builtin:<owner qualified>.<qualname>` |
| annotationlib.ForwardRef | `fwd:<its argument text>` |
| TypeVar, ParamSpec, TypeVarTuple | `typevar:<kind>|<name>|<variance flags>|<bound>|<constraints>|<default>`: a part given lazily is its evaluate function's encoding (never called), one given eagerly `const:<encode(the stored value)>`, an absent one `-` |
| TypeAliasType | `alias:<name>|<value>`, the value as a TypeVar part |
| any other typing, types or annotationlib object | `typing:<repr, addresses removed>` |
| date, time, timedelta, tzinfo, Decimal, Fraction, UUID, PurePath, re.Pattern, range, slice, ipaddress values | `<qualified type>:<repr, addresses removed>` |
| a weak reference or proxy | `weakref:<qualified type>` |
| any other standard-library or Melder object (a lock, a logger, a conduit) | `ref:<qualified type>` |
| an object of an installed third-party class | `ext:<qualified type> <dist>==<version> <stable_repr>` |
| an object with Python-visible state (application code) | `obj:<qualified type>{<data>}` |
| anything else (a C object without Python-visible state) | `opaque:<qualified type>` |

- Excluded class keys: `__module__` and `__qualname__` (in the header), `__doc__` (the docstring), `__dict__` and
  `__weakref__` (descriptors the interpreter makes), `__firstlineno__` (a line number), `__static_attributes__`
  (derived from the methods' code), `__annotations_cache__` (filled when annotations are read), and
  `__annotate_func__` while it is None: 3.14 writes it, with the cache, the first time anything reads the
  annotations of a class that has none, and Melder reads them at bind; a class with annotations holds its
  annotate function from creation, and that function is encoded (blast-radius probe A1-A3). Opaque key:
  `_abc_impl` (ABCMeta's registry, mutated by `register` and isinstance checks).
- Standard library: a module whose top-level name is in `sys.stdlib_module_names` or is `builtins`, or no module.
  Installed third-party (decision B): a module, not standard library, whose `__file__` lies under one of the
  interpreter's site-packages directories (`sysconfig` purelib and platlib, `site.getsitepackages()`,
  `site.getusersitepackages()`). `named(x)` is `<qualified> <dist>==<version>`: the distribution that installs
  its top-level package - `importlib.metadata.version(top)` first, `importlib.metadata.packages_distributions()`
  once per SpellCodeDigest when the import name is not a distribution name - or `?==?` when none is found;
  `external(obj)` is `ext:` + `named(type(obj))` + its `stable_repr`. Module locations and versions are memoized
  per SpellCodeDigest. Application code: everything else - the project's modules, `__main__`, editable installs,
  a module that cannot be located. Melder: `melder` and `melder.*`, for objects only (`ref:`); a Melder class in
  an MRO is code like any other - digested when Melder runs from source, named by version when it is installed.
- `qualified(x)` is `<module>.<qualname>`, read with `type.__getattribute__` for a class, "?" when absent; a
  function's module text is `str(fn.__module__)`, "None" for a function exec'd without one.

## Edge/Error and Rollback Semantics
- Never raises for a target or a value: unknown kinds encode as `opaque:<type>`, and `stable_repr` turns a failing
  repr into `<unrepr-able T>`. Bind therefore gains no refusal at digest time.
- Deep data: a RecursionError anywhere in `target_encoding` is caught in `spell_id`, and the target is encoded by
  rule 2e - an identity no finer than today's for that object.
- Cycles: a class, function, container or object already on the current path encodes as `cycle:<kind>`, so
  self-referencing data and mutually referencing classes terminate (E22).
- Mutable state: a class and an object are hashed as they are at bind - a class-level cache filled at runtime (a
  memo dict, a Flag enum's pseudo-members) moves the id (E33); reading annotations, an isinstance check and
  `ABC.register` do not (E25, E25b, E25c; for a class without annotations through the excluded
  `__annotate_func__`, probe A3).
- Generated code (dataclass methods, namedtuple, exec) is hashed like any code; a dataclass default and its
  `default_factory` count, through the generated functions' defaults and closures (E09, D1).
- A class defined in `__main__` and the same class imported from its module are two ids (their module names
  differ); the same source in another module is another id (E15).
- Python minor versions and -O compile other instructions and the cache tag is hashed in; -OO strips docstrings,
  which never count.
- An object with neither Python-visible state nor an informative repr cannot be told from another of its type
  (D6: two C `Mark` objects); today's rule has the same limit.
- An installed third-party object is its type, its distribution version and its repr (decision B): two objects
  of one library class whose repr carries no data are one spell, as under today's rule; an upgrade of the
  package moves the id of every spell that holds one or inherits from its code.
- Changed from the prototype: rule 2e (the prototype encoded such a target as `opaque:<type>`); reads through
  `object.__getattribute__`, `type.__getattribute__` and `inspect.getattr_static` (the prototype used `hasattr` and
  `getattr`, which can run a target's `__getattr__`); the constant opcodes from `dis.hasconst`; the tag `v5-code`
  (the prototype's `melder-code-digest/v2`); the RecursionError fallback; decision B (the prototype digested
  installed packages like the application); `__annotate_func__` excluded while None (the prototype excluded
  only `__annotations_cache__`, so a class without annotations changed id once they were read).
- Refined while writing SpellCodeDigest (2026-10-18; S1's DECISION note), every probe verdict unchanged:
  literal constants by exact repr (stripping " at 0x..." made a literal such as "listening at 0x1F"
  equal "listening"); an int past the decimal conversion limit in hex (`int.__repr__` raises there);
  an eagerly given type-parameter or alias part by its stored value (its `_typing._ConstEvaluator`
  would reduce to `ref:`, so a bound change would not move the id); containers through their base type.
- Rollback: none needed - a pure computation whose only state is its memo.

## Invariants and Idempotency Expectations
- The same code, data and interpreter give the same id in every process, hash seed and GIL mode (E01-E34 and D1-D10
  on 3.14.7t, hash seeds 1 and 2, GIL 0 and 1).
- The memo holds code-object digests only (code objects are immutable; `weakref.WeakKeyDictionary`, entries leave
  with their code objects). Classes, functions and objects are encoded afresh at every call.
- `spell_id(target)` called twice gives the same id unless the target, a class of its MRO or its data changed in
  between.
- No lock: the owner serializes calls (Bind holds its lock around `_bind_logic`; `spell_id_inspector` uses its own
  instance). No target code runs, except `repr()` in rule 2e and for an installed third-party object (`ext:`).

## Explicit Non-Goals
- Source text, file paths and line numbers.
- Code a target names but does not hold: the globals a function reads, a class referenced by name (D7, D8).
- Normalizing local variable names (call 4: a rename counts, E27).
- Memoizing class or object encodings (they are mutable).
- Deciding what counts as a second registration beyond the id itself (S4).

## Validation Focus Points
- One unit test per rule, from the probes: instructions and constants (P1-P10, I1-I9; the docstring slot E16, E18);
  inherited code E01; class-level values E02, E03; nested class E04; decorators E05, D2-D4; property, static and
  class methods E06-E08; dataclass default and factory E09, D1; enum value E10; annotations E11, E12; metaclass E13;
  except clause E17; local rename E27; type parameters E31; closures E18b, E18c; object data E19, E19b, E20, E28,
  D5; equal data E19, D10; runtime objects by type E21; cycles E22; cached_property E23; bound methods E29, E29b;
  partials E30; lambdas E26; standard-library targets E32, E32b; opaque targets D6 (rule 2e); specialization E24;
  runtime class state E25, E25b, E25c, E33; monitoring and tracing E34, E34b; module and qualname E14, E15;
  decision B: a class over an installed third-party base (D9's pygments lexer) named by version, an installed
  third-party object by type, version and repr, an application or `__main__` class digested.
- The annotate key (blast-radius probe A1-A3): a class without annotations keeps its id when its annotations
  are read, and a class with annotations keeps its id too (only the cache is added).
- A subprocess test: one target's id under two hash seeds; the whole suite with the GIL off and on.
- Cost: the corpus probe (782 targets of src/melder) and D9 against today's fingerprint, as the architecture
  patch's Validation Expectations and Evidence Plan list them.

## Context / Handoff Summary
- What changed: nothing in `src/`; the prototype and its probes measured every rule above (S1's MEASURE note; the D
  probe of 2026-10-18).
- Remaining unknowns: GIL versus free-threaded instructions for one Python version. Decision B is made (the
  owner, 2026-10-18).
- Next entrypoint: write `tests/unit/melder/spellbook/bind/test_spell_code_digest.py` red, from the list above.
