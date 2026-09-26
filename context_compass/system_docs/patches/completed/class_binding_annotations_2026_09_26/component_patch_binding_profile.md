# Component patch: Binding Pipeline - class binding profile annotations (2026-09-26)

## Before
- `BindingProfileStrategy._build_class_profile` reads `inspect.get_annotations(cls, eval_str=True, ...)` inside an
  undocumented `except Exception: annotations = {}`. On Python 3.14 an annotation naming a TYPE_CHECKING-only type
  raises NameError, so the whole mapping becomes `{}`: the fingerprint ignores every annotated field (adding one keeps
  the id) and the Nexus binding detail shows none.

## After
- NameError -> `SignatureReflection.class_annotations(cls)`: the class's own annotations in FORWARDREF, unavailable
  names as their source text (`'Decimal'`, `'list[Decimal]'`, `'Optional[Decimal]'`), quoted strings as written,
  evaluable values as objects.
- Any other exception, or a failure inside the fallback -> `{}`, as before, now documented as best-effort.

## Interface / state / failure deltas
- No signature change. Values may be `str` for unavailable names. No new state. No new failure: bind still never
  fails because class annotations cannot be read.

## Dependency / ordering
- Same read the detailed profile uses (ClassInspector._class_annotations), so the two profiles agree.

## Validation expectations
- Unit tests on the strategy and on the fingerprint; suites green on a worktree sync.
