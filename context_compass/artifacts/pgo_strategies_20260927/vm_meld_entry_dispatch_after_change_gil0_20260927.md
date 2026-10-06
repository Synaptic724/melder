# Meld entry dispatch experiment

melder 0.2.82; Python 3.14.7; GIL disabled; iters=60000 repeats=3 warmup=10000

| shape | arm | ns/call | py calls | C calls | vs today_by_name |
| --- | --- | ---: | ---: | ---: | ---: |
| solo | fast entry minted by 50 melds by name: NO - minted by one meld by id | | | | |
| solo | today_by_name | 269 | 4 | 1 |  |
| solo | today_by_class | 294 | 4 | 1 | +9% |
| solo | today_by_id | 282 | 4 | 1 | +5% |
| solo | proposed_by_name | 194 | 4 | 1 | -28% |
| solo | proposed_by_class | 199 | 4 | 1 | -26% |
| solo | proposed_inner | 181 | 3 | 1 | -33% |
| w1_singleton | fast entry minted by 50 melds by name: NO - minted by one meld by id | | | | |
| w1_singleton | today_by_name | 350 | 4 | 2 |  |
| w1_singleton | today_by_class | 370 | 4 | 2 | +6% |
| w1_singleton | today_by_id | 365 | 4 | 2 | +4% |
| w1_singleton | proposed_by_name | 266 | 4 | 2 | -24% |
| w1_singleton | proposed_by_class | 264 | 4 | 2 | -24% |
| w1_singleton | proposed_inner | 255 | 3 | 2 | -27% |
| w2_mixed | fast entry minted by 50 melds by name: NO - minted by one meld by id | | | | |
| w2_mixed | today_by_name | 498 | 5 | 2 |  |
| w2_mixed | today_by_class | 514 | 5 | 2 | +3% |
| w2_mixed | today_by_id | 511 | 5 | 2 | +2% |
| w2_mixed | proposed_by_name | 426 | 5 | 2 | -15% |
| w2_mixed | proposed_by_class | 409 | 5 | 2 | -18% |
| w2_mixed | proposed_inner | 385 | 4 | 2 | -23% |
| w4_mixed | fast entry minted by 50 melds by name: NO - minted by one meld by id | | | | |
| w4_mixed | today_by_name | 687 | 6 | 3 |  |
| w4_mixed | today_by_class | 691 | 6 | 3 | +1% |
| w4_mixed | today_by_id | 701 | 6 | 3 | +2% |
| w4_mixed | proposed_by_name | 585 | 6 | 3 | -15% |
| w4_mixed | proposed_by_class | 599 | 6 | 3 | -13% |
| w4_mixed | proposed_inner | 577 | 5 | 3 | -16% |
| wide8_singleton | fast entry minted by 50 melds by name: NO - minted by one meld by id | | | | |
| wide8_singleton | today_by_name | 748 | 4 | 9 |  |
| wide8_singleton | today_by_class | 744 | 4 | 9 | -1% |
| wide8_singleton | today_by_id | 764 | 4 | 9 | +2% |
| wide8_singleton | proposed_by_name | 639 | 4 | 9 | -15% |
| wide8_singleton | proposed_by_class | 644 | 4 | 9 | -14% |
| wide8_singleton | proposed_inner | 636 | 3 | 9 | -15% |
| singleton_direct | fast entry minted by 50 melds by name: yes | | | | |
| singleton_direct | today_by_name | 177 | 2 | 2 |  |
| singleton_direct | today_by_class | 183 | 2 | 2 | +3% |
| singleton_direct | today_by_id | 183 | 2 | 2 | +4% |
| singleton_direct | proposed_by_name | 95 | 2 | 2 | -46% |
| singleton_direct | proposed_by_class | 97 | 2 | 2 | -45% |
