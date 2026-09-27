# Static override emission experiment

Same constructors and public gates; no production source edits.

| Graph | Case | Door | Current us | Prototype us | Speedup |
| --- | --- | --- | ---: | ---: | ---: |
| shallow | root_one_reused | public | 1.991 | 1.177 | 1.69x |
| shallow | root_one_reused | executor | 1.037 | 0.307 | 3.38x |
| shallow | root_one_fresh | public | 1.989 | 1.211 | 1.64x |
| shallow | root_one_fresh | executor | 1.038 | 0.308 | 3.37x |
| shallow | root_all_reused | public | 2.571 | 1.797 | 1.43x |
| shallow | root_all_reused | executor | 1.123 | 0.391 | 2.87x |
| shallow | original_override | public | 1.997 | 1.219 | 1.64x |
| shallow | original_override | executor | 1.047 | 0.308 | 3.40x |
| shallow | normal | public | 0.510 | 0.508 | 1.01x |
| wide | root_one_reused | public | 3.404 | 1.502 | 2.27x |
| wide | root_one_reused | executor | 2.465 | 0.616 | 4.00x |
| wide | root_one_fresh | public | 3.482 | 1.554 | 2.24x |
| wide | root_one_fresh | executor | 2.477 | 0.614 | 4.03x |
| wide | root_all_reused | public | 9.438 | 7.377 | 1.28x |
| wide | root_all_reused | executor | 3.120 | 1.260 | 2.48x |
| wide | original_override | public | 3.505 | 1.548 | 2.26x |
| wide | original_override | executor | 2.464 | 0.611 | 4.03x |
| wide | normal | public | 0.825 | 0.825 | 1.00x |
| diamond | root_one_reused | public | 2.663 | 1.295 | 2.06x |
| diamond | root_one_reused | executor | 1.699 | 0.405 | 4.19x |
| diamond | root_one_fresh | public | 2.682 | 1.344 | 2.00x |
| diamond | root_one_fresh | executor | 1.701 | 0.400 | 4.26x |
| diamond | root_all_reused | public | 3.327 | 1.970 | 1.69x |
| diamond | root_all_reused | executor | 1.812 | 0.495 | 3.66x |
| diamond | original_override | public | 2.808 | 1.470 | 1.91x |
| diamond | original_override | executor | 1.824 | 0.526 | 3.47x |
| diamond | nested_reused | public | 2.764 | 1.426 | 1.94x |
| diamond | nested_reused | executor | 1.829 | 0.521 | 3.51x |
| diamond | nested_exact | public | 2.696 | 1.317 | 2.05x |
| diamond | nested_exact | executor | 1.699 | 0.412 | 4.13x |
| diamond | normal | public | 0.612 | 0.614 | 1.00x |
| deep | root_one_reused | public | 153.220 | 32.777 | 4.67x |
| deep | root_one_reused | executor | 152.071 | 31.298 | 4.86x |
| deep | root_one_fresh | public | 153.730 | 32.646 | 4.71x |
| deep | root_one_fresh | executor | 153.078 | 31.261 | 4.90x |
| deep | root_all_reused | public | 154.048 | 33.486 | 4.60x |
| deep | root_all_reused | executor | 151.926 | 30.879 | 4.92x |
| deep | original_override | public | 155.738 | 33.292 | 4.68x |
| deep | original_override | executor | 154.122 | 31.403 | 4.91x |
| deep | nested_reused | public | 156.183 | 32.944 | 4.74x |
| deep | nested_reused | executor | 155.277 | 31.818 | 4.88x |
| deep | normal | public | 31.738 | 31.667 | 1.00x |
