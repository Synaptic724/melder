# Binding Pipeline: inherited disposal candidates

<!-- BEGIN ENTRY: Bind requested inherited disposal -->
## Purpose and boundary
Bind creates canonical Spell metadata from the class profile and supplied binding policies.
Disposal discovery remains exclusively at this binding boundary.

## Before and after
Before: both candidate groups retain names only when present in ClassBindingProfile.method_names,
which lists declared callable members. Empty subclasses lose callable cleanup inherited from a base.
After: existing profile matches still pass. An unmatched requested name may match the first defining
inherited class namespace; a local declaration or non-callable inherited shadow prevents fallback.
Hidden dunder names remain excluded. Raw descriptor objects are inspected without invoking __get__.
This retains current callable eligibility, including staticmethod objects and excluding raw
classmethod/property objects that were already excluded from direct matching.

## Interface deltas
Public APIs are unchanged. Class bindings can retain additional valid inherited candidate names.
Non-class bindings, missing names and unsupported descriptor kinds retain existing behavior.

## State and lifecycle deltas
No new owned state or caches. One helper answers candidate eligibility; the existing composition loop
retains one Spell-owned ordered list. The existing fingerprint incorporates the corrected result.
No method is invoked during binding, and cleanup execution is unchanged.

## Failure modes
The first declaration always wins, even if it is None, a property or another non-callable value.
No inherited method is revived through a shadow. Metaclass-only methods are not instance methods.
No new catch-all fallback or descriptor execution is introduced.

## Dependencies and ordering
Read the architecture contract first. Add tests before changing Bind._bind_logic and its helper.
Keep the existing priority/dedup loops. Do not modify BindingProfileStrategy or the hash schema.
Promote the contract into the Binding Pipeline paragraph after tests pass.

## Validation expectations
- Explicit and configured inherited cleanup both survive binding, including both profile families.
- Child overrides and Python multiple-inheritance order select the actual runtime method.
- Local/intermediate/descriptor shadows and metaclass-only names remain excluded.
- Book/per-spell overlap, order and dedup remain correct with inherited names.
- many and unique real teardown invoke inherited cleanup exactly once.
- No-disposal fingerprints remain unchanged when an unrelated base callable is added.
- Existing non-class exclusions and all focused tests remain valid.
- Both original CommandOps registration-only tests pass without application changes.

## Unknowns and open decisions
None blocking. Async cleanup execution and broader descriptor support are outside this correction.
<!-- END ENTRY: Bind requested inherited disposal -->
