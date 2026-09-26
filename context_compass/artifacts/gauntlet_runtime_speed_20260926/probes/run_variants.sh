#!/bin/bash
# interleaved variants of probe_deferred.py, N reps; prints one line per run
for i in $(seq 1 $1); do
  ./venv314t/bin/python -X gil=0 probe_deferred.py base 1 2>&1 | tail -1
  ./venv314t/bin/python -X gil=0 probe_deferred.py deferred 1 kernel 2>&1 | tail -1
  ./venv314t/bin/python -X gil=0 probe_deferred.py deferred 1 kernel+functions+tuples 2>&1 | tail -1
  ./venv314t/bin/python -X gil=0 probe_deferred.py deferred 1 userfree 2>&1 | tail -1
  ./venv314t/bin/python -X gil=0 probe_deferred.py deferred 1 kernel+containers+functions 2>&1 | tail -1
done
