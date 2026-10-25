"""
The import roots and denied builtins the standard codegen presets read.

Purpose:
    Keep the name tuples the safe, hybrid, precision and permissive codegen presets put in their
    capability rulesets in one place, so presets that share a posture share one tuple and cannot
    drift apart.

Contract:
    - Values only: every public name is a tuple of str built at import and never mutated, and the
      module imports nothing, so a preset or the codegen engine imports it without an import cycle.
    - Import roots: `HYBRID_IMPORT_MODULE_ROOTS` is the common list, `PRECISION_IMPORT_MODULE_ROOTS`
      a narrower one, and `PERMISSIVE_IMPORT_MODULE_ROOTS` the common list plus the permissive
      extras, sorted. `io`, `os` and `pathlib` are permissive extras rather than common roots, so of
      the presets with an allow list only permissive admits them. `HYBRID_DENIED_IMPORT_MODULE_ROOTS`
      (which precision aliases) names roots the compiler refuses even where an allow list admits them.
    - Denied builtins: `SAFE_DENIED_BUILTIN_NAMES` is the one tuple safe, hybrid and precision deny
      (`HYBRID_DENIED_BUILTIN_NAMES` and `PRECISION_DENIED_BUILTIN_NAMES` are the same object), and
      the codegen engine's no-projection default denies it plus `__import__`. `open` is on it, so
      those postures refuse file access through that builtin; permissive and full_access do not use
      it and keep `open`.
    - Policy, not isolation: these names feed checks that run in the room's own process, as defence
      in depth.
"""

_COMMON_SAFE_IMPORT_MODULE_ROOTS = (
    "base64",
    "collections",
    "copy",
    "csv",
    "dataclasses",
    "datetime",
    "decimal",
    "enum",
    "fractions",
    "functools",
    "hashlib",
    "inspect",
    "itertools",
    "json",
    "math",
    "pprint",
    "re",
    "statistics",
    "string",
    "textwrap",
    "time",
    "typing",
    "uuid",
)

_PERMISSIVE_EXTRA_IMPORT_MODULE_ROOTS = (
    "asyncio",
    "builtins",
    "glob",
    "importlib",
    "io",
    "os",
    "pathlib",
    "random",
    "shutil",
    "socket",
    "subprocess",
    "sys",
    "tempfile",
    "traceback",
)

HYBRID_IMPORT_MODULE_ROOTS = _COMMON_SAFE_IMPORT_MODULE_ROOTS
PRECISION_IMPORT_MODULE_ROOTS = (
    "base64",
    "collections",
    "copy",
    "datetime",
    "decimal",
    "enum",
    "fractions",
    "functools",
    "hashlib",
    "itertools",
    "json",
    "math",
    "re",
    "statistics",
    "string",
    "textwrap",
    "typing",
    "uuid",
)
PERMISSIVE_IMPORT_MODULE_ROOTS = tuple(
    sorted(
        set(_COMMON_SAFE_IMPORT_MODULE_ROOTS).union(
            _PERMISSIVE_EXTRA_IMPORT_MODULE_ROOTS
        )
    )
)

HYBRID_DENIED_IMPORT_MODULE_ROOTS = (
    "asyncio",
    "builtins",
    "ctypes",
    "importlib",
    "socket",
    "subprocess",
)
PRECISION_DENIED_IMPORT_MODULE_ROOTS = HYBRID_DENIED_IMPORT_MODULE_ROOTS

# The builtins the safe posture denies; hybrid and precision deny the same tuple, and the codegen engine's
# default posture (a request naming a frame with no codegen projection) denies it plus `__import__`.
# `open` is on it so these postures refuse file reads and writes through that builtin: room code that calls
# or names it is refused at validation, and the room's runtime `__builtins__` leaves it out. This is policy in
# the room's own process, not isolation. Permissive and full_access do not use this tuple and keep `open`.
SAFE_DENIED_BUILTIN_NAMES = (
    "breakpoint",
    "compile",
    "dir",
    "eval",
    "exec",
    "getattr",
    "globals",
    "input",
    "locals",
    "open",
    "setattr",
    "delattr",
    "vars",
)

HYBRID_DENIED_BUILTIN_NAMES = SAFE_DENIED_BUILTIN_NAMES
PRECISION_DENIED_BUILTIN_NAMES = SAFE_DENIED_BUILTIN_NAMES

# The import builtins the static gates refuse wherever an import list applies (D-11, 0.2.8271). These names are
# refused by the builtin gate (a call) and name resolution (a bare reference) but are NOT removed from the room's
# runtime `__builtins__`: an import statement needs `__import__` present, and the runtime builtins strategy wraps
# it to check each import's root against the compiled roots. The compiler puts these in
# `static_only_denied_builtin_names` when imports are on and an allow or deny list applies (hybrid, precision,
# permissive), and leaves it empty for full_access (no list) and safe (imports off, where `__import__` is already a
# denied builtin). The compiler and the runtime builtins strategy both read this tuple, so they cannot drift. This
# is policy in the room's own process, not isolation.
IMPORT_BUILTIN_NAMES = (
    "__import__",
)

# The protected core root for codegen generation (D-20): `materialize_codegen` refuses a module name under it under
# every posture, so room code cannot add to or replace Melder's own package. Policy in the room's own process - defence
# in depth, not isolation.
PROTECTED_GENERATION_MODULE_ROOTS = (
    "melder",
)
