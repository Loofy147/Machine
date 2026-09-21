#!/bin/sh
# Real graphs used in exp_policies.py (METIS format, unweighted; source: github.com/networkit/networkit, input/)
for f in PGPgiantcompo power polblogs caidaRouterLevel; do
  curl -sL -o real_$f.graph "https://raw.githubusercontent.com/networkit/networkit/master/input/$f.graph"
done
