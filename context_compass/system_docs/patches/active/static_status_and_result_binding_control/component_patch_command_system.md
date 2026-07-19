# Component Patch: CommandSystem

## Before
- `execute_target_method(...)` could bind the result, but only through room
  default workstation reference-mode behavior.

## After
- `execute_target_method(...)` can choose the result-binding weak/strong mode
  explicitly.

## Contract
- binding override is optional
- when omitted, room/workstation defaults still apply
- when provided, it wins for that bound result only
