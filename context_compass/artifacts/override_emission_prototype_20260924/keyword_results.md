# Static override emission experiment

Same constructors and public gates; no production source edits.

| Graph | Case | Door | Current us | Prototype us | Speedup |
| --- | --- | --- | ---: | ---: | ---: |
| shallow | root_one_reused | public | 1.963 | 1.281 | 1.53x |
| shallow | root_one_reused | executor | 1.059 | 0.422 | 2.51x |
| shallow | root_one_fresh | public | 2.017 | 1.340 | 1.51x |
| shallow | root_one_fresh | executor | 1.042 | 0.419 | 2.48x |
| shallow | root_all_reused | public | 2.562 | 1.926 | 1.33x |
| shallow | root_all_reused | executor | 1.121 | 0.514 | 2.18x |
| shallow | original_override | public | 2.012 | 1.342 | 1.50x |
| shallow | original_override | executor | 1.060 | 0.421 | 2.52x |
| shallow | normal | public | 0.508 | 0.508 | 1.00x |
| wide | root_one_reused | public | 3.443 | 1.800 | 1.91x |
| wide | root_one_reused | executor | 2.492 | 0.887 | 2.81x |
| wide | root_one_fresh | public | 3.496 | 1.852 | 1.89x |
| wide | root_one_fresh | executor | 2.490 | 0.881 | 2.83x |
| wide | root_all_reused | public | 9.318 | 7.663 | 1.22x |
| wide | root_all_reused | executor | 3.166 | 1.573 | 2.01x |
| wide | original_override | public | 3.503 | 1.854 | 1.89x |
| wide | original_override | executor | 2.479 | 0.877 | 2.83x |
| wide | normal | public | 0.825 | 0.826 | 1.00x |
| diamond | root_one_reused | public | 2.689 | 1.592 | 1.69x |
| diamond | root_one_reused | executor | 1.693 | 0.689 | 2.46x |
| diamond | root_one_fresh | public | 2.708 | 1.630 | 1.66x |
| diamond | root_one_fresh | executor | 1.698 | 0.682 | 2.49x |
| diamond | root_all_reused | public | 3.323 | 2.254 | 1.47x |
| diamond | root_all_reused | executor | 1.790 | 0.798 | 2.24x |
| diamond | original_override | public | 2.812 | 1.760 | 1.60x |
| diamond | original_override | executor | 1.816 | 0.824 | 2.20x |
| diamond | nested_reused | public | 2.776 | 1.705 | 1.63x |
| diamond | nested_reused | executor | 1.828 | 0.810 | 2.26x |
| diamond | nested_exact | public | 2.689 | 1.606 | 1.67x |
| diamond | nested_exact | executor | 1.694 | 0.693 | 2.44x |
| diamond | normal | public | 0.612 | 0.611 | 1.00x |
| deep | root_one_reused | public | 152.857 | 57.355 | 2.67x |
| deep | root_one_reused | executor | 151.218 | 55.140 | 2.74x |
| deep | root_one_fresh | public | 152.683 | 55.953 | 2.73x |
| deep | root_one_fresh | executor | 149.317 | 55.391 | 2.70x |
| deep | root_all_reused | public | 152.660 | 57.305 | 2.66x |
| deep | root_all_reused | executor | 152.602 | 54.840 | 2.78x |
| deep | original_override | public | 154.608 | 58.869 | 2.63x |
| deep | original_override | executor | 154.441 | 56.416 | 2.74x |
| deep | nested_reused | public | 154.693 | 56.606 | 2.73x |
| deep | nested_reused | executor | 153.785 | 56.280 | 2.73x |
| deep | normal | public | 31.762 | 31.538 | 1.01x |
