"""
GENERATED DURABLE BUILD ASSET - DO NOT EDIT MANUALLY.

Thin loader for the internal-bind manifest. The payload is a marshal
bundle beside this file, mirroring the `.melc` bundles `caching_system`
already uses.

IMPORTS ONLY `marshal` - DELIBERATELY. Measured on the real 577-entry
payload, fresh interpreter, minimum of 9 runs:

    .py literals            cold 5.29 ms   warm 3.32 ms
    loader + pathlib/typing cold 5.77 ms   warm 5.09 ms   <- SLOWER
    loader, marshal only    cold 0.64 ms   warm 0.22 ms   <- 14.9x

`import pathlib` costs 3.77 ms and `from typing import ...` costs
2.88 ms on a cold interpreter, while `import marshal` is free. Adding
either one here spends more than the structure build it was meant to
avoid. Types live in the sibling .pyi stub, which costs nothing at
runtime and keeps mypy fully informed.

Regenerate with:
    python src/melder/_build_assets/_build_asset_runner.py
"""
import marshal

MANIFEST_VERSION = "1.0.0"
BUILT_FOR_VERSION = "0.1.1"
SOURCE_SHA256 = "aaa84c862515ebb88ed45f7492d1bfc4dabfd0f2d70a8f7e38831dd5a82a7d07"
MANIFEST_ENTRY_COUNT = 577

INTERNAL_MANIFEST = marshal.loads(open(__file__[:-3] + ".melc", "rb").read())
