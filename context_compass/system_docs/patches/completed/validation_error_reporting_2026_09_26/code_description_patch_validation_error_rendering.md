# Code description patch: SpellbookValidationError rendering (2026-09-26)

## Control flow
1. No spells and no diagnostics -> the existing fallback text.
2. Per spell: read name, id, frame; collect error-severity issues from `validation_result_phase4.issues` (falling
   back to `.errors`/`.warnings`) and `validation_result_phase6.errors`; count Phase-4 warnings.
3. Per handed-in diagnostic: warnings ignored; errors attributed to the matching spell id, else whole-graph.
4. Dedupe exact (code, message) per block; drop superseded and restating codes as stated; internal codes deduped by
   code.
5. Emit header, spell blocks (spells with errors; a spell with none is listed with "no validation error was
   recorded" only when no diagnostics were handed in), whole-graph block, warning footer, internal footer.

## Edge and error semantics
- Every attribute read is guarded; a failing read degrades that field, never the message.
- Frame text: strings as-is, classes by qualified name, else repr; None omitted.

## Invariants / idempotency
- Pure function of its inputs at construction; `str(error)` is stable.

## Non-goals
- No structured error object beyond the existing attributes; no localisation; no change to logging calls.
