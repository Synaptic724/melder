# Open Questions

## 1. Mutation Intent Classifier
- Which AST or operation patterns are sufficient to mark mutation intent?
- Should intent be explicit-only (`mutate` op) or classifier-assisted?

## 2. Lock Granularity
- Spell-level lock, graph-region lock, or domain-scope lock?
- How do lock conflicts resolve in multi-agent campaigns?

## 3. Validation Profiles
- What is minimum required validation in strict enterprise production domains?
- What can be skipped in lab-only domains?

## 4. Promotion Policy
- Who decides promotion in shared environments:
- agent role policy
- human approval gate
- hybrid policy with thresholds

## 5. Persistence Contract
- Canonical event schema for lineage nodes, incidents, and release plans.
- Replay guarantees across zones.

## 6. Unsafe Mode Interaction
- Should unsafe mode allow mutation without full validation?
- If yes, what hard floor is still mandatory?

