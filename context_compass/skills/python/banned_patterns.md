# banned_patterns

Purpose
- Prevent unsafe or non-auditable behavior.

Attribute Access Rule (No Defensive Introspection in Owned Code)
If we own the file/module and the attribute names are visible in the code, do NOT use getattr() / hasattr() as a defensive pattern.

* Use direct access (obj.attr).
* Handle None explicitly where appropriate.
* If you genuinely need to handle a missing attribute on an external/optional dependency, call it directly and catch AttributeError instead of probing with hasattr. This keeps owned-code contracts strict while still being safe when the contract is ambiguous or external.

getattr() / hasattr() are allowed only in ambiguous situations, meaning at least one is true:
* The object is polymorphic/external and its attribute contract is not visible in our code.
* The attribute/method is optional by design (capability checks).
* The attribute name is truly dynamic.

Polymorphic lock cleanup exception (allowed):
* For lock-like objects that may be different implementations, capability checks are allowed:
  if hasattr(lock, "cleanup"): lock.cleanup()

Disallowed example (we own it / visible contract):
* getattr(self, "_foo", None) when _foo is clearly part of our class/object contract in this file.

Banned / Disallowed Patterns
* Never use type: ignore.
* Never use # noqa.
* Never use eval() or exec().
* Never use wildcard imports (e.g., from module import *).
* Never use PEP 604 union syntax (e.g., A | B, T | None); use Optional/Union.

Never use
- type: ignore
- # noqa
- eval() or exec()
- wildcard imports
- from __future__ import annotations (new files must not add this)
- PEP 604 unions (A | B, T | None); use Optional/Union

Owned-code strictness
- Do not use getattr/hasattr for owned attributes.
- Handle AttributeError only for truly optional external interfaces.

Exception
- Polymorphic lock cleanup may use hasattr(lock, "cleanup").

Examples
- context_compass/examples/python/anti_patterns.py
