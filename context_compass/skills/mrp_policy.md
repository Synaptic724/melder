# MRP Policy (Skill)

## MRP (Most Reasonable Product)
- **Definition:** the smallest *reasonable* product that is coherent and trustworthy as a system.
- **Minimums:** minimum feature set **and** minimum system qualities to avoid a trap, but never at the cost of
  durable architecture. "Reasonable" means we do the work once and avoid rework.
- **Emphasis:** correctness of the core experience + durability (clear boundaries, predictable behavior, basic operability).
- **Ship rule:** it works reliably for intended use, and future growth will not require rewriting the core.

## MVP (Minimum Viable Product) - Disallowed
- MVP is optimized for speed to validate demand, not robustness.
- In this repo MVP is disallowed. Do not trade core quality for speed.

## MLP (Most Lovable Product) - UI Only
- MLP focuses on delight, polish, and adoption.
- Allowed only for UI/UX tasks and only after the MRP core is solid.

## Trade-offs at a Glance
- MVP: fastest learning, highest internal-debt risk (not allowed here).
- MRP: slower upfront than MVP, lowest chance of a dead-end core.
- MLP: strong adoption, higher design/polish cost (UI only).

## Decision Heuristic
- If uncertainty is foundation reliability, choose MRP.
- If success depends on love/retention/referrals, apply MLP after MRP.
- Default to MRP when in doubt.
