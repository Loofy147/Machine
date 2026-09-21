/* substrate_bench.c -- machine-level benchmark of the inverse-fiber substrate (spec Rev 2).
 * Same generator family as substrate_lib.gen_system (Zipf hubs), own PRNG => statistically, not bit-, identical.
 * Build: gcc -O2 -o substrate_bench substrate_bench.c -lm      Run: ./substrate_bench [n] [k] [seed]
 * Prints one JSON object. No hand-entered numbers.
 */
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <math.h>

static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + t.tv_nsec * 1e-9; }
static uint64_t st = 88172645463325252ULL;
static inline uint64_t rnd(void) { st ^= st << 13; st ^= st >> 7; st ^= st << 17; return st; }
static inline double urand(void) { return (rnd() >> 11) * (1.0 / 9007199254740992.0); }
static int cmpd(const void *a, const void *b) { double x = *(double *)a, y = *(double *)b; return (x > y) - (x < y); }
static double median(double *v, int n) { qsort(v, n, sizeof(double), cmpd); return v[n / 2]; }
static double quant(double *v, int n, double q) { return v[(int)(q * (n - 1) + 0.5)]; }

static int n, k;
static long E;
static int32_t *delta, *offs, *src;
static uint8_t *act;

static void build_csr(void) {
    int32_t *cnt = calloc(n + 1, 4);
    for (long i = 0; i < E; i++) cnt[delta[i] + 1]++;
    for (int i = 0; i < n; i++) cnt[i + 1] += cnt[i];
    memcpy(offs, cnt, (n + 1) * 4);
    int32_t *pos = malloc(n * 4);
    memcpy(pos, cnt, n * 4);
    for (int s = 0; s < n; s++)
        for (int a = 0; a < k; a++) { int t = delta[s * k + a]; int p = pos[t]++; src[p] = s; act[p] = a; }
    free(cnt); free(pos);
}

static long basin_csr(int u0, uint8_t *seen, int32_t *q, long *insp) {
    memset(seen, 0, n);
    long h = 0, t = 0, ins = 0;
    q[t++] = u0; seen[u0] = 1;
    while (h < t) {
        int u = q[h++];
        int lo = offs[u], hi = offs[u + 1];
        ins += hi - lo;
        for (int i = lo; i < hi; i++) { int v = src[i]; if (!seen[v]) { seen[v] = 1; q[t++] = v; } }
    }
    *insp = ins;
    return t;
}

static long basin_naive_pernode(int u0, uint8_t *seen, int32_t *q) {
    memset(seen, 0, n);
    long h = 0, t = 0;
    q[t++] = u0; seen[u0] = 1;
    while (h < t) {
        int u = q[h++];
        for (long i = 0; i < E; i++)
            if (delta[i] == u) { int s = (int)(i / k); if (!seen[s]) { seen[s] = 1; q[t++] = s; } }
    }
    return t;
}

static long basin_layered(int u0, uint8_t *Z, uint8_t *Z2, int *rounds) {
    memset(Z, 0, n); Z[u0] = 1;
    long cnt = 1; int r = 0;
    for (;;) {
        r++;
        memcpy(Z2, Z, n);
        long add = 0;
        for (int s = 0; s < n; s++)
            if (!Z[s])
                for (int a = 0; a < k; a++) if (Z[delta[s * k + a]]) { Z2[s] = 1; add++; break; }
        if (!add) break;
        cnt += add;
        memcpy(Z, Z2, n);
    }
    *rounds = r;
    return cnt;
}

static long scan_step(int u, int32_t *out) {          /* naive predecessor query: scan every (s,a) */
    long m = 0;
    for (long i = 0; i < E; i++) if (delta[i] == u) out[m++] = (int32_t)i;
    return m;
}

int main(int argc, char **argv) {
    n = argc > 1 ? atoi(argv[1]) : 50000;
    k = argc > 2 ? atoi(argv[2]) : 4;
    st ^= (uint64_t)(argc > 3 ? atoll(argv[3]) : 7) * 0x9E3779B97F4A7C15ULL;
    for (int i = 0; i < 10; i++) rnd();
    E = (long)n * k;
    int hubs = 50; double phub = 0.3;
    delta = malloc(E * 4); offs = malloc((n + 1) * 4); src = malloc(E * 4); act = malloc(E);
    int *hub = malloc(hubs * 4); double *cw = malloc(hubs * sizeof(double));
    for (int i = 0; i < hubs; i++) hub[i] = (int)(rnd() % n);
    double tot = 0; for (int i = 0; i < hubs; i++) tot += 1.0 / (i + 1);
    double c = 0; for (int i = 0; i < hubs; i++) { c += 1.0 / (i + 1) / tot; cw[i] = c; }
    for (long i = 0; i < E; i++) {
        if (urand() < phub) { double r = urand(); int j = 0; while (j < hubs - 1 && r > cw[j]) j++; delta[i] = hub[j]; }
        else delta[i] = (int)(rnd() % n);
    }
    /* build */
    double tb[21];
    for (int r = 0; r < 21; r++) { double t0 = now(); build_csr(); tb[r] = now() - t0; }
    double build_ms = median(tb, 21) * 1e3;
    int *indeg = malloc(n * 4);
    for (int i = 0; i < n; i++) indeg[i] = offs[i + 1] - offs[i];
    int hubu = 0; for (int i = 0; i < n; i++) if (indeg[i] > indeg[hubu]) hubu = i;
    int *idx = malloc(n * 4); for (int i = 0; i < n; i++) idx[i] = i;
    /* median-indegree node: simple selection via counting */
    int maxd = indeg[hubu]; int *hist = calloc(maxd + 1, 4); for (int i = 0; i < n; i++) hist[indeg[i]]++;
    int acc = 0, meddeg = 0; for (int d = 0; d <= maxd; d++) { acc += hist[d]; if (acc >= n / 2) { meddeg = d; break; } }
    int medu = 0; for (int i = 0; i < n; i++) if (indeg[i] == meddeg) { medu = i; break; }
    int32_t *out = malloc(E * 4);
    /* naive step (scan whole delta) */
    double ts[200];
    for (int r = 0; r < 200; r++) { int u = (int)(rnd() % n); double t0 = now(); volatile long m = scan_step(u, out); (void)m; ts[r] = now() - t0; }
    double naive_step_us = median(ts, 200) * 1e6;
    /* fiber step: median node & top hub, batch of REP lookups copying the fiber */
    long chk = 0;
    int REP = 200000;
    double t0 = now();
    for (int r = 0; r < REP; r++) { int lo = offs[medu], hi = offs[medu + 1]; for (int i = lo; i < hi; i++) chk += src[i]; }
    double fiber_med_ns = (now() - t0) / REP * 1e9;
    int REPH = 5000;
    t0 = now();
    for (int r = 0; r < REPH; r++) { int lo = offs[hubu], hi = offs[hubu + 1]; for (int i = lo; i < hi; i++) chk += src[i]; }
    double fiber_hub_ns = (now() - t0) / REPH * 1e9;
    /* full basin from random target */
    uint8_t *seen = malloc(n); int32_t *q = malloc(n * 4); uint8_t *Z2 = malloc(n);
    int U0 = (int)(rnd() % n);
    long insp; long basin = basin_csr(U0, seen, q, &insp);
    double tq[41];
    for (int r = 0; r < 41; r++) { long i2; double a = now(); basin_csr(U0, seen, q, &i2); tq[r] = now() - a; }
    double csr_ms = median(tq, 41) * 1e3;
    int rounds; double tl[11];
    for (int r = 0; r < 11; r++) { double a = now(); basin_layered(U0, seen, Z2, &rounds); tl[r] = now() - a; }
    double layered_ms = median(tl, 11) * 1e3;
    int do_pernode = argc > 4 ? atoi(argv[4]) : 1;
    long b2 = -1; double pernode_ms = -1;
    if (do_pernode) { double a = now(); b2 = basin_naive_pernode(U0, seen, q); pernode_ms = (now() - a) * 1e3; }
    /* multi-query cost: 30 random targets */
    double tqm[30], tlm[30];
    for (int r = 0; r < 30; r++) { int u = (int)(rnd() % n); long i2; double s0 = now(); basin_csr(u, seen, q, &i2); tqm[r] = now() - s0;
                                   s0 = now(); basin_layered(u, seen, Z2, &rounds); tlm[r] = now() - s0; }
    double mq_csr = median(tqm, 30) * 1e3, mq_lay = median(tlm, 30) * 1e3;
    size_t bytes = (size_t)(n + 1) * 4 + (size_t)E * 4 + (size_t)E;
    printf("{\"n\":%d,\"k\":%d,\"E\":%ld,\"compile\":\"gcc -O2\",\n", n, k, E);
    printf(" \"indeg_max\":%d,\"indeg_median\":%d,\"basin\":%ld,\"basin_check_pernode\":%ld,\"layered_rounds\":%d,\n", indeg[hubu], meddeg, basin, b2, rounds);
    printf(" \"csr_bytes\":%zu,\"csr_MiB\":%.4f,\n", bytes, bytes / 1048576.0);
    printf(" \"build_counting_sort_ms\":%.4f,\n", build_ms);
    printf(" \"naive_step_us\":%.3f,\"fiber_step_median_node_ns\":%.2f,\"fiber_step_top_hub_us\":%.3f,\n", naive_step_us, fiber_med_ns, fiber_hub_ns / 1e3);
    printf(" \"step_speedup_median_node\":%.1f,\"step_speedup_top_hub\":%.2f,\"ops_ratio_E_over_fiber_top_hub\":%.2f,\n",
           naive_step_us * 1e3 / fiber_med_ns, naive_step_us * 1e3 / fiber_hub_ns, (double)E / indeg[hubu]);
    printf(" \"basin_csr_ms\":%.4f,\"basin_naive_layered_ms\":%.4f,\"basin_naive_pernode_ms_measured\":%.2f,\n", csr_ms, layered_ms, pernode_ms);
    printf(" \"speedup_csr_vs_pernode\":%.1f,\"speedup_csr_vs_layered\":%.2f,\n", pernode_ms / csr_ms, layered_ms / csr_ms);
    printf(" \"fiber_entries_touched\":%ld,\"pernode_inspections\":%ld,\n", insp, basin * E);
    printf(" \"multi_query_ms\":{\"csr\":%.4f,\"layered\":%.4f},\"queries_to_amortise_build_vs_layered\":%.2f,\n", mq_csr, mq_lay, mq_lay > mq_csr ? build_ms / (mq_lay - mq_csr) : -1.0);
    printf(" \"steps_to_amortise_build_vs_naive_step\":%.2f,\"chk\":%ld}\n", build_ms * 1e3 / (naive_step_us - fiber_med_ns / 1e3), chk);
    return 0;
}
