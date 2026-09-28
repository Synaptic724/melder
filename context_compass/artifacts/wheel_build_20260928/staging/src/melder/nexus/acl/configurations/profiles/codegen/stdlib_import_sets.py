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
    "pathlib",
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
    "setattr",
    "delattr",
    "vars",
)

HYBRID_DENIED_BUILTIN_NAMES = SAFE_DENIED_BUILTIN_NAMES
PRECISION_DENIED_BUILTIN_NAMES = SAFE_DENIED_BUILTIN_NAMES
