
# ─────────────────────────────────────────────────────────────────────────────
# 📘 Conduit Validation Modes – Automatic vs Dynamic
#
# This system supports two distinct validation strategies depending on the
# conduit mode: `automatic` or `dynamic`. These modes determine how spell and
# object availability is checked during conduit creation and usage.
#
# ─────────────────────────────────────────────────────────────────────────────
# 🔹 AUTOMATIC MODE
# - All objects and spells must exist within the current scope at validation time.
# - Validation is strict and eager — if something is missing, the conduit cannot be instantiated.
# - Best for simple, monolithic execution environments or local workflows.
#
# Example behavior:
# - ❌ Will raise if a required spell isn't locally bound.
# - ✅ Guarantees all spells are ready to use immediately upon conjure.
#
# ─────────────────────────────────────────────────────────────────────────────
# 🔹 DYNAMIC MODE
# - Validation is relaxed during conduit creation: required components must
#   exist in the global registry, but not necessarily be linked to the conduit.
# - Missing components do NOT prevent conduit instantiation.
# - However, attempting to `meld(...)` or invoke a missing spell will raise an error
#   unless the appropriate contract has been formed.
#
# This model enables:
# - Composable factories
# - Runtime scope linking
# - Incremental, contract-based resolution
#
# Example behavior:
# - ✅ You can conjure a conduit even if not all dependencies are linked.
# - ❌ Resolution will raise if the spell isn’t explicitly contracted in.
#
# 🧠 Summary:
# - Automatic mode is for eager, strict validation (everything must be available).
# - Dynamic mode is for modular, contract-driven validation (components exist globally, but linking is required).
# ─────────────────────────────────────────────────────────────────────────────
