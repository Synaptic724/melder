# Meld entry dispatch experiment

melder 0.2.82; Python 3.14.7; GIL disabled; iters=200000 repeats=5 warmup=20000

| shape | arm | ns/call | py calls | C calls | vs today_by_name |
| --- | --- | ---: | ---: | ---: | ---: |
| solo | fast entry minted by 50 melds by name: NO - minted by one meld by id | | | | |
| solo | today_by_name | 453 | 5 | 4 |  |
| solo | today_by_class | 467 | 5 | 4 | +3% |
| solo | today_by_id | 298 | 4 | 1 | -34% |
| solo | proposed_by_name | 195 | 4 | 1 | -57% |
| solo | proposed_by_class | 197 | 4 | 1 | -57% |
| solo | proposed_inner | 180 | 3 | 1 | -60% |
| w1_singleton | fast entry minted by 50 melds by name: NO - minted by one meld by id | | | | |
| w1_singleton | today_by_name | 537 | 5 | 5 |  |
| w1_singleton | today_by_class | 533 | 5 | 5 | -1% |
| w1_singleton | today_by_id | 376 | 4 | 2 | -30% |
| w1_singleton | proposed_by_name | 269 | 4 | 2 | -50% |
| w1_singleton | proposed_by_class | 271 | 4 | 2 | -50% |
| w1_singleton | proposed_inner | 250 | 3 | 2 | -53% |
| w2_mixed | fast entry minted by 50 melds by name: NO - minted by one meld by id | | | | |
| w2_mixed | today_by_name | 683 | 6 | 5 |  |
| w2_mixed | today_by_class | 682 | 6 | 5 | -0% |
| w2_mixed | today_by_id | 726 | 5 | 2 | +6% |
| w2_mixed | proposed_by_name | 405 | 5 | 2 | -41% |
| w2_mixed | proposed_by_class | 409 | 5 | 2 | -40% |
| w2_mixed | proposed_inner | 383 | 4 | 2 | -44% |
| w4_mixed | fast entry minted by 50 melds by name: NO - minted by one meld by id | | | | |
| w4_mixed | today_by_name | 888 | 7 | 6 |  |
| w4_mixed | today_by_class | 887 | 7 | 6 | -0% |
| w4_mixed | today_by_id | 713 | 6 | 3 | -20% |
| w4_mixed | proposed_by_name | 592 | 6 | 3 | -33% |
| w4_mixed | proposed_by_class | 598 | 6 | 3 | -33% |
| w4_mixed | proposed_inner | 574 | 5 | 3 | -35% |
| wide8_singleton | fast entry minted by 50 melds by name: NO - minted by one meld by id | | | | |
| wide8_singleton | today_by_name | 957 | 5 | 12 |  |
| wide8_singleton | today_by_class | 972 | 5 | 12 | +2% |
| wide8_singleton | today_by_id | 779 | 4 | 9 | -19% |
| wide8_singleton | proposed_by_name | 651 | 4 | 9 | -32% |
| wide8_singleton | proposed_by_class | 653 | 4 | 9 | -32% |
| wide8_singleton | proposed_inner | 630 | 3 | 9 | -34% |
| singleton_direct | fast entry minted by 50 melds by name: yes | | | | |
| singleton_direct | today_by_name | 333 | 3 | 5 |  |
| singleton_direct | today_by_class | 340 | 3 | 5 | +2% |
| singleton_direct | today_by_id | 177 | 2 | 2 | -47% |
| singleton_direct | proposed_by_name | 96 | 2 | 2 | -71% |
| singleton_direct | proposed_by_class | 96 | 2 | 2 | -71% |
