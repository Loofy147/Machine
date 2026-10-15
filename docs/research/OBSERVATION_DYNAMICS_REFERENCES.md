# Observation–Dynamics Research References

## Structural mathematics

- Mike Boyle, *Factoring Factor Maps*, Journal of the London Mathematical Society 57(2), 1998, 491–502.
  https://www.cambridge.org/core/journals/journal-of-the-london-mathematical-society/article/abs/div-classtitlefactoring-factor-mapsdiv/32C554FF601E50CD0C2B3C3C629BCAF8
  Used as external context for factor-map language and non-injective dynamical factors.

- Ulrich Dorsch, Stefan Milius, Lutz Schröder, Thorsten Wißmann, *Efficient Coalgebraic Partition Refinement*, CONCUR 2017.
  https://doi.org/10.4230/LIPIcs.CONCUR.2017.32
  Used as external context for behavioural equivalence and partition-refinement machinery.

- *Efficient Deterministic Finite Automata Minimization Based on Backward Depth Information*, PLOS ONE, 2016.
  https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0165864
  Used as external context for iterative refinement and distinguishability.

## Longest repeated substring / sequence complexity

- Technical suffix-array literature notes that for uniformly random strings the expected longest repeated-substring length is
  2 log_{|Sigma|}(N) + O(1).
  One accessible source:
  https://www.dlsi.ua.es/~carrasco/aa/sa.pdf
  This is a benchmark heuristic for the random-like null, not a theorem asserted here for SplitMix64 or for balanced words.

- Oleg Merkurev, Arseny M. Shur, *Searching Long Repeats in Streams*, CPM 2019.
  https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CPM.2019.31
  Used to frame the limits of exact/approximate streaming approaches to longest repeated substrings.

## SplitMix64 implementation context

- Apache Commons RNG SplitMix64 implementation:
  https://commons.apache.org/proper/commons-rng/commons-rng-core/jacoco/org.apache.commons.rng.core.source64/SplitMix64.java.html
  Confirms the fixed-increment implementation form used by this branch.

- Haskell splitmix documentation/source:
  https://github.com/haskellari/splitmix/blob/master/src/System/Random/SplitMix.hs
  The implementation represents gamma as part of generator state and documents the practical predictability of successive outputs. This is why this branch explicitly fixes gamma as known and constant.

## Scope rule

External references establish terminology, known mathematical frameworks, and implementation context.

They do not establish the branch's concrete experimental results.

Branch-local claims must continue to carry repository + branch + commit + execution provenance where applicable.
