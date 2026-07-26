"""
GENERATED DURABLE BUILD ASSET - DO NOT EDIT MANUALLY.

Thin loader for agent-facing class metadata. The payload is a marshal
bundle beside this file, matching the `.melc` convention used by
`caching_system` and the internal-bind manifest.

AGENT_METADATA maps (module, qualname) -> (access, purpose).
EXEMPT lists classes deliberately ruled out of agent tooling.
PENDING lists classes not yet marked - fill these in over time.
CLASS_BASES is DIAGNOSTIC ONLY; inheritance resolves through
inspect.getmro at runtime because direct bases drop grandparents.

Regenerate with:
    python src/melder/_build_assets/_build_asset_runner.py
"""
import marshal

MANIFEST_VERSION = "1.0.0"
BUILT_FOR_VERSION = "0.1.1"
SOURCE_SHA256 = "aaa84c862515ebb88ed45f7492d1bfc4dabfd0f2d70a8f7e38831dd5a82a7d07"
MARKED_COUNT = 404
EXEMPT_COUNT = 163
PENDING_COUNT = 10

_PAYLOAD = marshal.loads(open(__file__[:-3] + ".melc", "rb").read())

AGENT_METADATA = _PAYLOAD["agent_metadata"]
EXEMPT = _PAYLOAD["exempt"]
PENDING = _PAYLOAD["pending"]
CLASS_BASES = _PAYLOAD["class_bases"]
