# Ticket Update: Rich AI Profile Inventory (Object-Surface Complete)

Labels: melder-core, ai-profile, introspection, tools-surface, design-rfc

---

## Summary

This update extends the existing AI profile inventory ticket to fully cover
the object surface that will be exposed through downstream ACL filtering.
The focus remains strictly on the object itself (class, callable, instance).
No system identity, lineage, or spellbook context is included here.

The goal is a complete, unfiltered, object-local artifact map:
methods, properties, descriptors, data attributes, dunders, inherited members,
and instance-bound attributes when the profiled object is an instance.

---

## Scope

In scope (object-level only):
- Full surface inventory for classes and callables, including dunders.
- Full provenance (file path, start line, end line, full source text).
- Full docstring capture for class, methods, properties, and descriptors.
- Tool-shaped member records for all member kinds.
- Properties and descriptors as first-class members, with getter/setter visibility.
- Instance-bound objects: include instance attribute inventory.
- Dynamic attribute access signals (e.g., __getattr__ / __getattribute__).
- Derived text fields (docstring summary, behavior summary, tags), even if empty.

Out of scope (explicit):
- Identity, lineage, or spellbook context.
- Capability semantics beyond the object surface (policy/ACL logic is downstream).
- Size/perf controls, caching, or storage strategy.
- System-level graphs, dependencies, or cross-object topology.

---

## Current State (Gap Summary)

- Dunders are filtered by default.
- Provenance is preview-only (no end line, no full source text).
- Only callables are promoted to structured profiles; non-callables remain raw.
- Properties are not first-class endpoints with full provenance/docstrings.
- No instance attribute inventory for instance-bound objects.
- No dynamic attribute access flags.

---

## Desired State

### 1) Dunders Always Included
- Member inventory must include dunders by default.
- No filtering at profile stage; downstream ACLs decide visibility.

### 2) Full Provenance for Class + Every Member
For each object and each member (method/property/descriptor/data/dunder):
- file_path (or null if unavailable)
- start_line (or null)
- end_line (or null)
- source_text (full definition block or null)

For classes:
- full class source text + line span
- module, qualname, bases, MRO, slots

### 3) Tool-Shaped Member Records for All Member Kinds
Every member becomes a structured record with a consistent schema, not just
callables. Member kinds include:
- method
- classmethod
- staticmethod
- property
- descriptor
- data attribute
- dunder
- inherited members

Each member record should include:
- name
- kind
- defined_on (class in MRO where it is defined)
- inherited (bool)
- module, qualname (when applicable)
- callable (bool)
- signature + parameter list (for callables)
- return annotation (best effort)
- docstring_raw
- docstring_summary (derived field, can be empty)
- behavior_summary (derived field, can be empty)
- tags (derived field, can be empty)
- provenance fields (file_path, start_line, end_line, source_text)

### 4) Properties and Descriptors as First-Class Members
Properties/descriptors must include:
- has_getter / has_setter / has_deleter (booleans)
- docstring capture for accessor (when available)
- provenance for getter/setter where possible

### 5) Instance-Bound Objects (Instance Attribute Inventory)
If the profiled object is an instance (existing creation, callable object, etc.):
- Capture instance attributes as a dedicated list/map (e.g., instance_members).
- Include name, repr, type, and docstring if available.
- Provenance may be null for instance attrs (no source block).
- Keep instance attributes separate from class members, but under the same profile.

### 6) Dynamic Attribute Access Signals
Record object-level flags if dynamic access is present:
- has_getattr (bool)
- has_getattribute (bool)
- has_setattr (bool)

These do not add members; they signal that runtime attributes may exist.

---

## Non-Goals (Re-stated)

- No lineage/identity mapping, no spellbook or conduit context.
- No ACL rules, access decisions, or capability policy.
- No size/perf limits or caching strategy.
- No cross-object graphs.

---

## Work Required (Implementation Outline)

1) Remove dunder filtering at AI profile stage (always include).
2) Promote all member kinds into structured records.
3) Add full source capture (getsourcelines) for class + members.
4) Add docstring capture for class/method/property/descriptor.
5) Add instance attribute inventory for instance-bound objects.
6) Add dynamic-attribute access flags to the class/instance header.

---

## Acceptance Criteria

- Dunders are always present in the AI profile member inventory.
- Every member has a tool-shaped record with consistent schema.
- Class and members include full provenance fields (file, start, end, source text).
- Properties/descriptors include accessor availability + docstrings.
- Instance-bound objects include an instance attribute inventory.
- Dynamic attribute access flags are reported when applicable.

---

## Suggested Test Cases

- Plain class with:
  - public methods
  - private methods
  - dunders
  - properties (read-only + read/write)
  - class attributes
  - inherited methods
- Decorated method (wrapper + unwrapped provenance)
- Callable object instance (instance attributes + __call__)
- Builtin/extension members (no source available -> provenance fields null)
- Class with __getattr__ or __getattribute__ (dynamic attribute flags set)

---

## Notes

This profile is the unfiltered object artifact map. ACL filtering and exposure
rules are applied downstream and are explicitly out of scope for this ticket.
