# UX_and_AIX_experiences (AGENTS.md)

Purpose: the living exploration of how HUMANS (UX) and AGENTS (AIX) use melder,
tiered beginner -> intermediate -> expert -> master. Every example is written
against `import melder as md` ONLY - any example forced to reach a deep path is,
by definition, an init-surface gap and must be recorded on the owning epic.

Layout:
- 01_beginner/      first-contact + registration: bind, SpellBinder fluent, meld, lifecycles,
                    hooks, disposal, frames, errors, agent first-read.
                    TIER LAW: static conjure only - no dynamic, no Nexus, no MutationResearch,
                    no spellspaces. Existences: unique, many, unique_per_conduit
                    ONLY (lineage/spellspace -> tier 02; cluster -> tier 03).
                    DESIGN PRINCIPLE: teach a 4B-model agent with a 64k window
                    to be USEFUL - shared/fresh/scoped, frames as dicts, typed
                    melds, Protocols, one bootstrap function. Fun and simple
                    beats complete.
- 02_intermediate/  fluent binding, scopes, spellframes, configuration, persistence basics
- 03_expert/        AR rooms, viewers, workstations, research lanes, diff/impact foresight
- 04_master/        pod restart, external DB meshes, group composition, campaign evolution, custom decorators

Laws:
- Examples are RUNNABLE scripts (3.14t) with a main() and honest printed asserts.
- Each file header states TIER / GOAL / SURFACE EXERCISED (the md.* names used).
- Examples never import melder submodule paths. md.* or it does not exist.
- Findings (gaps, awkward verbs, missing exports) go on the tier's epic ticket,
  then flow into the init composition story - examples are the evidence.

Tickets: context_compass/tickets/epics/2026-07-19_ux_aix_{tier}_experience_epic.md

## Verification harness

pytest_examples/ runs every example plus contract probes on 3.14t:

    pytest UX_and_AIX_experiences/pytest_examples -v

LAW (2026-07-19, after the bind(**kwargs) miss): examples may only assert
behavior VERIFIED in source or PROVEN by a probe row. Uncertain contracts get
a probe here first; the probe's printed outcome then hardens the example.

## Discovered runtime laws (harness runs 1-2, 2026-07-19)

- Callable spells (functions, lambdas, methods) are ALWAYS unique; lambdas
  additionally REQUIRE a binding_name. Fresh-per-meld factories are CLASSES
  bound "many".
- THE ADDRESS LAW: every spell lives at exactly one (frame_key, binding_key)
  address - frame_key = spellframe else normalized spell name; binding_key =
  binding_name else the default slot. Meld forms construct that key: spell
  object / spell_name derive the frame key from the NAME (so they miss framed
  binds), and a bind with binding_name answers only when the meld carries the
  same binding_name. binding_name alone is refused with ValueError.
- Spell NAMES are unique per book at conjure - CURRENT behavior refuses any
  name collision regardless of binding names, frames, or content SHA.
  DIVERGENCE FLAG: owner design intent (twice stated) is SHA256 content
  matching with binding-name disambiguation; DuplicateSpellNameStrategy
  ignores the disambiguators its own error message recommends. Tracked as a
  runtime bug candidate on the beginner epic. Until fixed: subclass-per-role
  (24) and collection-as-spell registries (33) are the working patterns.
- One book conjures ONE conduit ever (RuntimeError on the second); scopes are
  lesser conduits, extra roots are extra books.
- Unregistered meld raises one stable KeyError. Same-spell double-bind is
  refused at BIND time (RuntimeError).
- bind(**kwargs) is the hook channel and SWALLOWS unknown keys silently
  (flagged as a fail-fast design question); constructor config rides
  factories, prebuilt instances, or meld(spell_override={...}).
- Disposal (disposal_method_names) fires at conduit.cleanup().
- Harness isolation: reset the Aether singleton + rebind Spellbook/
  Conduit._aether around every test (component-suite fixture, verbatim).
