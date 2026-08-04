# Codegen to Mutation Bridge

## Purpose
Describe how guarded codegen and mutation research connect as one pipeline.

## Shared Entrypoint
- Agents submit codeblocks through governed execution APIs.
- AST policy and symbol/member resolution run first.

## Route A: Safe Execution
- If block only uses approved existing capabilities:
- execute in safe lane
- return results and references
- emit audit trail

## Route B: Mutation Escalation
- If block expresses structural intent:
- require mutation permissions
- classify as mutation lane
- run mutation lifecycle and control-plane gates

## Why This Works
- Agents keep a familiar codegen workflow.
- Platform keeps strict operational boundaries.
- Mutation research becomes an explicit, managed escalation path instead of hidden behavior.

## Design Principle
- Do not force users into a full text-REPL to get value.
- Use codegen + manifest + lane routing as the practical default.

