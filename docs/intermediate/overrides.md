# Flat overrides and live creation probes

Prerequisite: [addressing](../beginner/addresses.md) and
[lifetimes](../beginner/lifetimes.md). A flat `override` supplies constructor inputs
for the object being resolved. A factory can instead capture configuration at its
registration site. The saved mailer lesson demonstrates both with concrete values.

## Choose where configuration belongs

The factory returns a mailer configured for its fixed environment. The separately
registered `many` class accepts `host` and `port` through `meld(override={...})`.
Its assertions compare both resulting configurations.

An override is not a new binding or a global configuration edit. Pair the choice
with the intended instance lifetime; repeated reuse and fresh construction are
different operations. Follow the complete script's lifetime choices first.

## Inspect before constructing

`has_live_creation(...)` asks whether an addressed object already exists.
The live-probe lesson checks `False` before its first meld and `True` afterward,
then uses `describe_live_creation_status(...)` for detail. A diagnostic path can
use these reads without using a meld merely to discover whether something is alive.

Continue to [deep overrides](../advanced/overrides.md) when the target is inside
a dependency graph rather than a parameter of the object you are resolving.
