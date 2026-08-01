# Configuration Diff Catalogue

- Created: 2026-08-01T14:05:00Z
- Author: examples_0
- Ticket: TASK-2026-08-01-config-structural-survey
- Purpose: catalogue what actually differs across every configuration object in
  `src/melder`, so the uniformity work is aimed at real divergence rather than
  assumed divergence.
- Method: source-read per axis. Nothing inferred from filenames.

---

## 1. The verb matrix

`Y` = present, `-` = absent. Verb names are the ACTUAL names in source.

| config | validate | freeze | finalize | activate | cleanup | describe | property API | defaults loader | recorded reload |
|---|---|---|---|---|---|---|---|---|---|
| aether | Y | Y | Y | Y | Y | - | - | - | `from_recorded_payload` |
| aetheric_frame | Y | Y | - | - | Y | Y | - | - | `from_recorded_posture` |
| spellbook | Y | Y | Y | - | Y | - | Y | `load_default_dictionary` | `load_recorded_dictionary` |
| crystallizer | Y | Y | Y | Y | Y | - | Y | - | `load_recorded_dictionary` |
| mutation_research | Y | Y | Y | Y | Y | Y | Y | - | `load_recorded_dictionary` |
| nexus | Y | Y | Y | - | Y | - | Y | `load_default_dictionary` | `load_recorded_dictionary` |
| rift | Y | Y | Y | - | Y | - | Y | `load_default_dictionary` | - |
| external_persistence_manager | Y | Y | - | - | Y | Y | - | - | - |

Only `validate`, `freeze` and `cleanup` are universal. Everything else is optional
in practice, with no stated rule for who gets what.

---

## 2. DIFF-1: the same job has three different verb names

Reloading a recorded configuration is one job. It is spelled three ways:

- `from_recorded_payload` - aether
- `from_recorded_posture` - aetheric_frame
- `load_recorded_dictionary` - spellbook, crystallizer, mutation_research, nexus

And two configs cannot do it at all (rift, external_persistence_manager).

A user or agent who learns the restore lane on one object cannot find it on the
next. This is pure naming drift - the underlying job is identical.

---

## 3. DIFF-2: four storage models, not two

The earlier survey said three. Reading the property API changed that.

| model | storage | public accessors | configs |
|---|---|---|---|
| A | `_properties` dict + `available_properties` type registry | `set/get/has_property` | spellbook, crystallizer, mutation_research, nexus, rift |
| B | `_properties` dict, NO registry, NO public accessors | fluent only | aether |
| C | direct named slots, no dict | fluent only | aetheric_frame, nexus_frame |
| D | direct named slots, no dict, no defaults verb at all | fluent only | external_persistence_manager |

Model B is the surprise: aether carries a property dict (18 references) but exposes
no property API at all, so the dict is private machinery while every other
dict-backed config publishes it. Same storage, opposite exposure.

---

## 4. DIFF-3: `with_defaults()` means two opposite things

This is the highest-severity diff in the catalogue, because it is the one users hit
first and the only one already proven to cause damage.

- SPELLBOOK - PRESERVING. `load_default_dictionary` writes only absent keys
  (`if key not in self._properties`). Existing values survive.
- AETHERIC_FRAME - DESTRUCTIVE. Its own docs say a later `with_defaults()`
  "silently RECOMPUTES this back to the..." and describe a preset as "DESTRUCTIVE.
  This is `with_defaults()` followed by...".

Same verb. Opposite semantics. On the two objects a user meets first.

Compounding it, the spellbook docstring documents the FRAME behavior:
"applies the standard local rich-config defaults in place, OVERWRITING anything set
earlier, so call it FIRST and override afterwards." That sentence is false for the
object it is attached to, and it is what sent four UX/AIX examples into a refusal
on 2026-08-01.

---

## 5. DIFF-4: `with_defaults` exists without a defaults loader

`with_defaults()` is on 7 configs. `load_default_dictionary()` is on only 3
(spellbook, nexus, rift). So on aether, crystallizer, mutation_research and
aetheric_frame the same public verb is backed by a different private mechanism.

One public promise, four private implementations, no shared contract.

---

## 6. DIFF-5: `activate()` marks a hidden class distinction

`activate()` exists on exactly three configs: aether, crystallizer,
mutation_research. Those are precisely the three HOSTED SINGLETON ROOTS owned by
`Aether`.

This divergence is INTENTIONAL and should be kept - but it is undocumented, so it
currently reads as inconsistency. The rule "configs for hosted singleton roots
carry activate(); configs for user-constructed objects do not" is real and simply
never written down.

---

## 7. DIFF-6: idempotency is a one-off

`_idempotent_keys` exists on exactly ONE config: spellbook, holding `disposal` and
`disposal_method_names`. No other config has a set-once concept.

Given the defect it produced on 2026-08-01, the question is not "why don't the
others have it" but "is set-once the right rule at all, or is it a frozen-flag
duplicate". Recorded here as a diff, not yet judged.

---

## 8. DIFF-7: lock discipline is wildly uneven

Lock references per file: aetheric_frame 73, external_persistence_manager 14,
codegen_namespace 14, frame_acl 14, spellbook 10, aether 8, mutation_research 8,
crystallizer 7, nexus 5, rift 4.

The frame posture's 73 is not automatically wrong - it is live-read by the
transaction plane and identity-critical, so heavy guarding is defensible. But a 73
vs 4 spread across objects of the same nominal kind is worth one deliberate look
rather than an assumption either way. NOT yet classified.

---

## 9. DIFF-8: `describe()` on 3 of 8

Present on aetheric_frame, mutation_research, external_persistence_manager. Absent
elsewhere. For a runtime whose pitch is that it is inspectable by agents, a
detached describe payload being optional is a notable gap - the crystallizer twin
model depends on `describe()` being the interface everywhere it records.

---

## 10. What is INTENTIONAL vs ACCIDENTAL

INTENTIONAL - keep, but DOCUMENT the rule:
- Storage model C/D for aetheric_frame (identity-critical, live-read on transaction
  paths, settle-once, mutated in place with donors cleaned up).
- `activate()` restricted to the three hosted singleton roots.

ACCIDENTAL - safe to converge:
- Three names for the recorded-reload job (DIFF-1).
- `with_defaults()` semantic collision (DIFF-3) - and the false spellbook docstring.
- Model B's private-only property dict on aether (DIFF-2).
- `describe()` coverage gap (DIFF-8).

UNCLASSIFIED - needs a read before judging:
- Lock spread (DIFF-7).
- Whether `_idempotent_keys` should exist at all (DIFF-6).
- Per-knob semantics of nexus (1847 LOC), crystallizer (1063), epm (919),
  aether (771), rift (568), and the ACL/codegen family (~3,600 LOC).

---

## 10b. THE ONE FUNDAMENTAL DIFFERENCE (added 2026-08-01T14:55:00Z)

The owner pushed back on my "aetheric_frame is fundamentally different" claim and
asked what is FUNCTIONALLY different, discounting extra methods and describers.
Re-tested. Most of what I cited was structural, not functional:

- STORAGE (slots vs dict): NOT fundamental. An implementation choice. Both hold a
  fixed knob set; the registry validates at runtime what mypy could validate
  statically. Withdrawn as a fundamental difference.
- METHOD COUNTS, `describe()`, property API: NOT fundamental. All addable
  everywhere with no functional obstacle. The owner is right on both counts.
- LIVE-READ ON TRANSACTION PATHS: weak. Once a value is fetched it is an attribute
  read either way. Not sufficient to force a different model.

WHAT IS ACTUALLY FUNDAMENTAL - and it is exactly one thing:

**`AethericFrameConfiguration` is CONSUMED ON HANDOFF. Every other config survives.**

Hand an `AethericFrameConfiguration` to a frame and the frame copies its values onto
the canonical retained posture and then calls `cleanup()` on YOUR object. Three
separate call sites do this (`aetheric_frame.py:714, 730, 743`). Your reference is
dead after the call. There is exactly one live posture per frame and it is not
yours.

Every other config survives handoff. Spellbook's is not merely retained but
explicitly SHARED - the tier lesson asserts
`book_a.get_configuration() is book_b.get_configuration() is shared` and keeps
using the object afterwards. The hosted roots (crystallizer, aether,
mutation_research) do NOT clean the config passed to `configure()`.

So the real axis is OWNERSHIP TRANSFER, not structure:

| handoff semantic | configs |
|---|---|
| CONSUMED - callee destroys your object, one canonical instance exists | aetheric_frame |
| RETAINED - you keep a live, usable reference | spellbook, aether, crystallizer, mutation_research, nexus, rift, epm |

This is a genuine user trap: two objects that look identical, one of which kills
your copy when you pass it. It is also the correct thing to express AS A DECLARED
PROPERTY of the uniform model - `handoff: consumed | retained` - rather than
leaving it to be discovered as a structural accident. Uniformity does not have to
erase it; it has to NAME it.

## 11. The one-line summary

Storage divergence is mostly justified. VERB divergence is mostly not. Users are
not confused by how a value is stored - they never see that. They are confused
because the same job has three names, the same name has two meanings, and there is
no written rule for which object gets which verb.
