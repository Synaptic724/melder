# Plain order matrix, 3000 iterations, 3 threads, -X gil=0, VM (2 vCPU), 3 interleaved rounds

Source: runs/plain_matrix_3000it.jsonl (order_probe.py without --state-probe via run_matrix.py, seeds 11-13).
Every configuration is its own fresh process; position 1 includes the library run alone.

## Loop total by position (ms)

| library | position 1 | position 2 | position 3 | pos 2-3 vs pos 1 |
| --- | --- | --- | --- | --- |
| dependency-injector | n=9 median 5009 (4911-5140) | n=6 median 5243 (5018-5380) | n=6 median 5605 (5320-5772) | +5% / +12% |
| dishka | n=9 median 4269 (4081-4401) | n=6 median 4525 (4277-4577) | n=6 median 4568 (4299-4681) | +6% / +7% |
| melder | n=9 median 4507 (4311-4550) | n=6 median 5060 (4972-5229) | n=6 median 5058 (4970-5135) | +12% / +12% |

## Threaded phase average per iteration by position (ms)

| library | position 1 | position 2 | position 3 |
| --- | --- | --- | --- |
| dependency-injector | median 1.420 (1.391-1.460) | median 1.496 (1.441-1.528) | median 1.618 (1.547-1.659) |
| dishka | median 1.171 (1.155-1.217) | median 1.246 (1.175-1.304) | median 1.259 (1.208-1.294) |
| melder | median 1.235 (1.207-1.242) | median 1.408 (1.388-1.452) | median 1.410 (1.393-1.435) |

## Loop total by what ran before (ms, sorted samples)

- dependency-injector:
  - after dishka: [5204, 5241, 5245]
  - after melder: [5018, 5297, 5380]
  - after nothing (fresh process): [4911, 4937, 4948, 5007, 5009, 5051, 5078, 5081, 5140]
  - after dishka then melder: [5534, 5583, 5626]
  - after melder then dishka: [5320, 5689, 5772]
- dishka:
  - after dependency-injector: [4277, 4292, 4546]
  - after melder: [4518, 4532, 4577]
  - after nothing (fresh process): [4081, 4226, 4256, 4267, 4269, 4328, 4337, 4350, 4401]
  - after dependency-injector then melder: [4569, 4582, 4681]
  - after melder then dependency-injector: [4299, 4358, 4568]
- melder:
  - after dependency-injector: [4972, 5083, 5100]
  - after dishka: [4976, 5037, 5229]
  - after nothing (fresh process): [4311, 4449, 4495, 4498, 4507, 4507, 4521, 4538, 4550]
  - after dependency-injector then dishka: [5046, 5101, 5135]
  - after dishka then dependency-injector: [4970, 5016, 5070]

## The owner's order and its reverse (ms, 3 runs each)

| order | dependency-injector | dishka | melder |
| --- | --- | --- | --- |
| dependency-injector,dishka,melder | 5009 [4948, 5009, 5051] | 4292 [4277, 4292, 4546] | 5101 [5046, 5101, 5135] |
| melder,dishka,dependency-injector | 5689 [5320, 5689, 5772] | 4532 [4518, 4532, 4577] | 4507 [4507, 4507, 4521] |
