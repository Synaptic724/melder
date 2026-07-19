# Component Patch: Codegen Validator And Compiler

## Objective
Compile validator-facing codegen ACL answers into the existing compiled access
surface and make the runtime validator consume them through
`CodegenProjection`.

## Compiler Responsibilities
- compile import posture:
  - imports enabled
  - allowed module roots
  - denied module roots
- compile builtin denylist
- compile dunder/reflection booleans

## Validator Responsibilities
- accept clean scripts under the selected profile
- use projection/compiled-surface answers directly
- keep normal Python work patterns available
- validate:
  - imports
  - dangerous builtins
  - dunder access
  - reflection/meta behavior

## Namespace Responsibilities
- expose `viewer`, `command`, `workstation`, `codegen`
- stop exposing `rift`, `space`, `target`, `frame_name`
