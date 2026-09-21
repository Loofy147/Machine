# Grounded research note — predecessor access and bidirectional scheduling

> Scope: (1) what the literature establishes about the model your original statement lives in, (2) new experiments designed against it, (3) verdicts on the earlier claims. Every number comes from `bidir_harness_v3.zip`; nothing is hand-entered. Sources I read in full or in part are marked; nothing else is used as evidence.

## 1. Sources and what was actually read

| Source | Read | Establishes (as used here) |
| :-- | :-- | :-- |
| Haeupler, Hladík, Rozhoň, Tarjan, Tětek, *Bidirectional Dijkstra's Algorithm is Instance-Optimal*, arXiv:2410.14638 (v4, Sept 2026) | Introduction, related work, errata, model, Algorithm 2, Theorem 3 proof | Instance-optimality **in edges accessed** on positively weighted multigraphs; Dantzig (alternate vertices), Nicholson (smaller key) and Pohl (fewer open vertices) rules are **not** instance-optimal; the equal-work rule (alternate single edge relaxations) is; μ must be updated without a "closed" guard (errata); Theorem 2: with out-edges only and no degree queries unidirectional Dijkstra is instance-optimal |
| Bertram, Jensen, Thorup, Wang, Yan, *Instance-Optimality of Bidirectional Dijkstra on Simple Graphs*, arXiv:2608.24380 (2026) | Abstract, model, Tables 1–2, §9 | Query model = in/out **degree** queries + i-th in/out **neighbour** queries (i.e. our `offs` + `src` fibers); simple graphs: constant ratio for undirected order-oblivious input, Θ(⌈m/n⌉) for directed; most non-optimality comes from degree queries |
| Ahmadi et al., *Networks* 84(1), 2024, [doi:10.1002/net.22210](https://doi.org/10.1002/net.22210) | one passage | min-cost interleaving can run one direction for long stretches when its frontier reaches a dense part of the graph |
| Valmari & Lehtinen, arXiv:0802.2826 | one excerpt (web search) | DFA minimisation work bounded by \|δ\| lg \|Q\| for partial transition functions; transitions grouped by label with a counting-style pass |
| Eckerle et al. (NBS, arXiv:1703.03868); Požar (arXiv:2608.26952); Valmari 2012 (IPL) | abstract / not read | **not used as evidence** (cited only where [2] describes them) |

Coverage note: the Wiley-based scholarly search returned mostly off-topic material for this query, so the core sources come from arXiv.

## 2. Mapping to our artifacts

* `alternate` = Dantzig, `min_key` = Nicholson, `cardinality_true` = Pohl (as characterised in [2], §2); new `equal_work_edge` = corrected Algorithm 2 of [2]; `equal_work_vertex` is its vertex-granular approximation.
* The harness's μ update (whenever the other side has a finite tentative distance) is the errata version.
* The substrate's fibers provide exactly the queries of [3]: `deg⁻(u)=offs[u+1]-offs[u]`, `i`-th predecessor = `src[offs[u]+i]`. Labeled fibers make parallel actions parallel edges (**multigraph** regime of [2]); de-duplicated fibers are the **simple-digraph** regime of [3] (ratio up to Θ(⌈m/n⌉), and m/n ≤ |Σ| here).

## 3. Experiments

**Declared before running:** primary metric = total edge scans; primary contrasts = {alternate, min_key, open_work, equal_work_vertex, equal_work_edge} vs cardinality_true, Holm-corrected Wilcoxon per dataset; CIs by bootstrap over analysis units (graphs for the clustered ensemble, pairs otherwise).

**Verification.** v3 reproduces the earlier harness exactly on 1 350 runs; all 8 variants return optimal costs on 5 656 random directed-multigraph runs and 1 181 structured runs. *A bug was found and fixed on the way:* my first edge-granular stopping rule ignored the key of a vertex that a side had closed but not finished relaxing and stopped early (83 wrong answers in 5 656 runs). The paper's own stopping rule was unaffected; the lesson is general — a lower bound for interruptible expansions must include the in-progress vertex.

**Datasets** (weights 1..9 random, seeded; real graphs from `networkit/input`, undirected, so successor and predecessor lists coincide there):

| Graph | n | m | max deg | pairs |
| :-- | --: | --: | --: | --: |
| Router-level Internet (caidaRouterLevel) | 192 244 | 609 066 | 1 071 | 60 |
| PGP trust network | 10 680 | 24 316 | 205 | 150 |
| Political blogs (giant comp. 1 222) | 1 490 | 16 715 | 351 | 150 |
| US power grid | 4 941 | 6 594 | 19 | 150 |
| Directed hub multigraph (substrate generator, 3 seeds) | 20 000 | 80 000 arcs | in-deg 5 277–5 349 | 180 |
| Clustered bottleneck (frozen seeds) | 600 | ≈1 800–4 500 | — | 270 (90 graphs) |

**Edge scans relative to Pohl's rule (95 % CI where shown):**

| Graph | min-key | alternate | equal-work (edge) | equal-work (vertex) | work-aware | heap-proxy |
| :-- | --: | --: | --: | --: | --: | --: |
| Router-level | **29.8** (19.4–45.0) | 1.10 (0.99–1.20) | 1.03 (0.93–1.11) | 1.03 | 1.01 | 1.02 |
| PGP | **6.64** (5.53–7.82) | 1.25 (1.17–1.34) | 1.00 (0.97–1.03) | 1.01 | 0.98 | 1.00 |
| Blogs | **3.87** (3.07–4.75) | 0.96 (0.90–1.03) | 0.98 (0.92–1.04) | 0.96 | 1.01 | 0.97 |
| Power grid | 1.12 (1.09–1.15) | 1.04 (1.03–1.05) | 1.03 (1.02–1.04) | 1.03 | 0.99 | 1.00 |
| Directed hub | 1.63 (1.47–1.80) | 1.00 (0.98–1.02) | 0.97 (0.95–0.99) | 0.99 | 0.98 | 1.00 |
| Clustered | 2.55 (2.28–2.82) | 1.83 (1.67–1.99) | 1.23 (1.19–1.27) | 1.23 | 0.99 | 1.01 |

Backward search (Pohl) needs this fraction of forward-only Dijkstra's edge scans: router 0.010, directed hub 0.024, PGP 0.051, blogs 0.052, power grid 0.336, clustered 0.397.

**Worst-instance regret** (max ratio to the per-instance best of the 7 rules): equal-work (edge) is smallest on 4 of 6 datasets — hub multigraph 1.20 vs 5.29 for Pohl, PGP 1.62 vs 1.83, blogs 1.94 vs 3.73, router 1.73 vs 2.58; Pohl is smallest on the clustered ensemble (1.17 vs 1.71) and the power grid (1.10 vs 1.22). Min-key's worst instances: router 675×, blogs 59×, PGP 509×.

**Scaling** (clustered ensemble, n_per_cluster 75→1 200, 3 fresh seeds per size): all stages grow ≈ linearly — total expansions exponent 0.98–1.00, E_res 0.95–0.98 (sd 0.06–0.08), forward-only 1.02. Edge-scan ratio to Pohl grows slowly: min-key 2.08→2.79, alternate 1.59→1.91, equal-work (edge) 1.13→1.29.

## 4. Verdicts on earlier claims

| Claim | Verdict |
| :-- | :-- |
| Policy choice changes efficiency on identical instances | **Supported** (all datasets) |
| "min-key gives no saving over forward Dijkstra" | **Refined:** true only on the clustered ensemble; on real graphs it saves 62–80 % (vs 66–99 % for Pohl) |
| min-key's pre-contact penalty grows with degree density | **Strengthened:** on real heavy-tailed graphs it is 4–30× in edge scans |
| alternate pays a certification tax | **Refined:** +83 % only under strong side asymmetry; ≈ Pohl on hub multigraph and 2 of 4 real graphs |
| "balance by frontier work" (open-set degree sum) | **Not supported:** ≤ 1.9 % better than Pohl, significant on two graphs only |
| Heap length ≈ exact open count | **Replicated** (no significant difference anywhere) |
| Phase 2 is a constant ≈ 24 expansions | **Refuted:** scales ≈ linearly with n |
| Equal-work rule is a good default | **Supported with caveat:** mean ≈ Pohl (+23 % on the clustered ensemble), best worst-case regret on 4/6 datasets |

## 5. The original statement, made precise

"Direct predecessor access shifts the resource-bounded frontier" is true under every contract tried, but its *meaning* changes:

* **Sublinear query contract** (unit-cost neighbour/degree queries, no preprocessing): a **new capability**. Without in-edge access unidirectional Dijkstra is instance-optimal ([2], Thm 2, restricted model); with it bidirectional Dijkstra is instance-optimal on multigraphs ([2], Thm 3) and here scans 1–34 % of the edges. (This sentence is my synthesis of the cited theorems.)
* **Preprocessing contract** (build once, query many): a **reallocation of computation**. The build is Θ(n+E) (1.07 ms vs a 118 µs scan step in C) and is repaid within ≈ 9 scan steps or one layered-scan query.
* **Multiplicity matters in both**: labeled (multigraph) fibers keep the instance-optimality guarantee; de-duplicating them moves the substrate into the simple-digraph regime where the guarantee weakens by up to Θ(⌈m/n⌉).

## 6. Limits and what to do next

* Real graphs are undirected with synthetic weights and uniform random pairs; one graph per dataset, so inference is over pairs, not graphs. No real *directed* graph was tested (the directed evidence is generator-based).
* Regret is relative to the 7 implemented rules, not to all algorithms; the literature's guarantee is a constant factor, not a mean-cost win.
* Suggested next steps: (a) directed real graphs (web/citation) for genuine in-degree skew; (b) the adversarial constructions of [3] to see whether the Θ(Δ²/n) gap is reachable by hub-heavy instances; (c) C port of the edge-granular equal-work rule on CSR fibers for wall-clock numbers; (d) a real automata benchmark for the per-action index.
