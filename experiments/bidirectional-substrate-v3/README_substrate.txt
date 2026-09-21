Machine Substrate Rev 2 -- reproduce (Python 3.12, numpy, scipy; gcc for the C benchmark)
  python3 test_correctness.py 400          # C1-C7 randomized correctness (all algorithms vs brute-force references)
  python3 bench.py --out bench_results.json   # B1-B10 measurements (add --quick for a fast pass)
  gcc -O2 -o substrate_bench substrate_bench.c -lm && ./substrate_bench 50000 4 7    # machine-level numbers
substrate_results.json = correctness checks + Python benchmarks + C benchmarks. Every number in the spec comes from these files.
