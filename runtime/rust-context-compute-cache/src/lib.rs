use moka::sync::Cache;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, BTreeSet};
use std::time::Duration;

const CACHE_SCHEMA: &str = "uws-context-pair-compatibility-cache.v0.1";

#[derive(Clone, Debug)]
pub struct CacheConfig {
    pub pair_max_capacity_bytes: u64,
    pub graph_max_capacity_bytes: u64,
    pub ttl: Duration,
}

impl Default for CacheConfig {
    fn default() -> Self {
        Self {
            pair_max_capacity_bytes: 128 * 1024 * 1024,
            graph_max_capacity_bytes: 64 * 1024 * 1024,
            ttl: Duration::from_secs(30 * 60),
        }
    }
}

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct Context {
    pub id: String,
    #[serde(default)]
    pub facts: BTreeMap<String, Value>,
    #[serde(default)]
    pub needs: BTreeMap<String, Value>,
}

#[derive(Clone, Debug, Deserialize)]
pub struct Request {
    pub op: String,
    #[serde(default)]
    pub contexts: Vec<Context>,
}

#[derive(Clone, Debug, Serialize, PartialEq)]
pub struct NeedWitness {
    pub key: String,
    pub required_value: Option<Value>,
    pub supplied_value: Value,
}

#[derive(Clone, Debug, Serialize, PartialEq)]
pub struct UnmetNeed {
    pub key: String,
    pub required_value: Option<Value>,
    pub provider_has_key: bool,
    pub supplied_value: Option<Value>,
}

#[derive(Clone, Debug, Serialize, PartialEq)]
pub struct ServiceWitness {
    pub consumer: String,
    pub provider: String,
    pub needs: Vec<NeedWitness>,
    pub unmet_needs: Vec<UnmetNeed>,
}

#[derive(Clone, Debug, Serialize, PartialEq)]
pub struct CachedEdge {
    pub left: String,
    pub right: String,
    pub services: Vec<ServiceWitness>,
}

#[derive(Clone, Debug)]
enum PairOutcome {
    Incompatible,
    Compatible(CachedEdge),
}

#[derive(Clone, Debug)]
struct CacheValue {
    outcome: PairOutcome,
    weight_bytes: u32,
}

#[derive(Clone, Debug)]
struct GraphCacheValue {
    edges: Vec<CachedEdge>,
    weight_bytes: u32,
}

#[derive(Clone, Debug, Serialize)]
pub struct CacheMetrics {
    pub pair_lookups: u64,
    pub cache_hits: u64,
    pub cache_misses: u64,
    pub entries: u64,
    pub hit_rate: f64,
    pub graph_cache_hit: bool,
    pub graph_cache_hits: u64,
    pub graph_cache_misses: u64,
    pub graph_cache_entries: u64,
}

#[derive(Clone, Debug, Serialize)]
pub struct BuildResult {
    pub schema: String,
    pub edges: Vec<CachedEdge>,
    pub cache: CacheMetrics,
}

#[derive(Serialize)]
struct ContextKey<'a> {
    schema: &'static str,
    context: &'a Context,
}

pub struct CompatibilityCache {
    entries: Cache<[u8; 64], CacheValue>,
    graphs: Cache<[u8; 32], GraphCacheValue>,
    pair_lookups: u64,
    cache_hits: u64,
    cache_misses: u64,
    graph_cache_hits: u64,
    graph_cache_misses: u64,
}

impl Default for CompatibilityCache {
    fn default() -> Self {
        Self::new()
    }
}

impl CompatibilityCache {
    pub fn new() -> Self {
        Self::new_with_config(CacheConfig::default())
    }

    pub fn new_with_config(config: CacheConfig) -> Self {
        let pair_capacity = config.pair_max_capacity_bytes.max(1);
        let graph_capacity = config.graph_max_capacity_bytes.max(1);
        let ttl = config.ttl.max(Duration::from_millis(1));

        let entries = Cache::builder()
            .max_capacity(pair_capacity)
            .weigher(|key: &[u8; 64], value: &CacheValue| {
                key.len()
                    .saturating_add(value.weight_bytes as usize)
                    .min(u32::MAX as usize) as u32
            })
            .time_to_live(ttl)
            .build();
        let graphs = Cache::builder()
            .max_capacity(graph_capacity)
            .weigher(|key: &[u8; 32], value: &GraphCacheValue| {
                key.len()
                    .saturating_add(value.weight_bytes as usize)
                    .min(u32::MAX as usize) as u32
            })
            .time_to_live(ttl)
            .build();

        Self {
            entries,
            graphs,
            pair_lookups: 0,
            cache_hits: 0,
            cache_misses: 0,
            graph_cache_hits: 0,
            graph_cache_misses: 0,
        }
    }

    pub fn build_graph(&mut self, mut contexts: Vec<Context>) -> Result<BuildResult, String> {
        contexts.sort_by(|left, right| left.id.cmp(&right.id));
        let mut seen = BTreeSet::new();
        for context in &contexts {
            if context.id.trim().is_empty() {
                return Err("context id must be a non-empty string".to_string());
            }
            if !seen.insert(context.id.clone()) {
                return Err(format!("duplicate context id: {}", context.id));
            }
            if context.facts.keys().any(|key| key.trim().is_empty())
                || context.needs.keys().any(|key| key.trim().is_empty())
            {
                return Err(format!(
                    "context {} has an empty fact or need key",
                    context.id
                ));
            }
        }

        // Fingerprint each immutable context once. The graph-cache key omits
        // utility, so changing the objective can reuse the complete graph.
        let fingerprints = contexts
            .iter()
            .map(Self::context_fingerprint)
            .collect::<Result<Vec<_>, _>>()?;
        let graph_key = Self::graph_key(&fingerprints);

        if let Some(cached) = self.graphs.get(&graph_key) {
            self.graph_cache_hits = self.graph_cache_hits.saturating_add(1);
            self.graphs.run_pending_tasks();
            return Ok(BuildResult {
                schema: CACHE_SCHEMA.to_string(),
                edges: cached.edges.clone(),
                cache: CacheMetrics {
                    pair_lookups: 0,
                    cache_hits: 0,
                    cache_misses: 0,
                    entries: self.entries.entry_count(),
                    hit_rate: 1.0,
                    graph_cache_hit: true,
                    graph_cache_hits: 1,
                    graph_cache_misses: 0,
                    graph_cache_entries: self.graphs.entry_count(),
                },
            });
        }

        self.graph_cache_misses = self.graph_cache_misses.saturating_add(1);
        let before_hits = self.cache_hits;
        let before_misses = self.cache_misses;
        let mut edges = Vec::new();

        for left_index in 0..contexts.len() {
            for right_index in (left_index + 1)..contexts.len() {
                let left = &contexts[left_index];
                let right = &contexts[right_index];
                let key = Self::pair_key(&fingerprints[left_index], &fingerprints[right_index]);

                self.pair_lookups = self.pair_lookups.saturating_add(1);
                let outcome = if let Some(cached) = self.entries.get(&key) {
                    self.cache_hits = self.cache_hits.saturating_add(1);
                    cached.outcome.clone()
                } else {
                    self.cache_misses = self.cache_misses.saturating_add(1);
                    let computed = Self::compute_pair(left, right);
                    let weight_bytes = serde_json::to_vec(&match &computed {
                        PairOutcome::Incompatible => None,
                        PairOutcome::Compatible(edge) => Some(edge),
                    })
                    .map(|bytes| bytes.len().min(u32::MAX as usize) as u32)
                    .unwrap_or(32);
                    self.entries.insert(
                        key,
                        CacheValue {
                            outcome: computed.clone(),
                            weight_bytes,
                        },
                    );
                    computed
                };

                if let PairOutcome::Compatible(edge) = outcome {
                    edges.push(edge);
                }
            }
        }

        self.entries.run_pending_tasks();
        let graph_weight = serde_json::to_vec(&edges)
            .map(|bytes| bytes.len().min(u32::MAX as usize) as u32)
            .unwrap_or(32);
        self.graphs.insert(
            graph_key,
            GraphCacheValue {
                edges: edges.clone(),
                weight_bytes: graph_weight,
            },
        );
        self.graphs.run_pending_tasks();

        let call_hits = self.cache_hits.saturating_sub(before_hits);
        let call_misses = self.cache_misses.saturating_sub(before_misses);
        let call_lookups = call_hits.saturating_add(call_misses);
        let hit_rate = if call_lookups == 0 {
            1.0
        } else {
            call_hits as f64 / call_lookups as f64
        };

        Ok(BuildResult {
            schema: CACHE_SCHEMA.to_string(),
            edges,
            cache: CacheMetrics {
                pair_lookups: call_lookups,
                cache_hits: call_hits,
                cache_misses: call_misses,
                entries: self.entries.entry_count(),
                hit_rate,
                graph_cache_hit: false,
                graph_cache_hits: 0,
                graph_cache_misses: 1,
                graph_cache_entries: self.graphs.entry_count(),
            },
        })
    }

    pub fn total_metrics(&self) -> CacheMetrics {
        let lookups = self.cache_hits.saturating_add(self.cache_misses);
        let hit_rate = if lookups == 0 {
            1.0
        } else {
            self.cache_hits as f64 / lookups as f64
        };
        CacheMetrics {
            pair_lookups: lookups,
            cache_hits: self.cache_hits,
            cache_misses: self.cache_misses,
            entries: self.entries.entry_count(),
            hit_rate,
            graph_cache_hit: false,
            graph_cache_hits: self.graph_cache_hits,
            graph_cache_misses: self.graph_cache_misses,
            graph_cache_entries: self.graphs.entry_count(),
        }
    }

    fn context_fingerprint(context: &Context) -> Result<[u8; 32], String> {
        let encoded = serde_json::to_vec(&ContextKey {
            schema: CACHE_SCHEMA,
            context,
        })
        .map_err(|error| format!("could not fingerprint context {}: {error}", context.id))?;
        Ok(Sha256::digest(&encoded).into())
    }

    fn graph_key(fingerprints: &[[u8; 32]]) -> [u8; 32] {
        let mut digest = Sha256::new();
        digest.update(CACHE_SCHEMA.as_bytes());
        for fingerprint in fingerprints {
            digest.update(fingerprint);
        }
        digest.finalize().into()
    }

    fn pair_key(left: &[u8; 32], right: &[u8; 32]) -> [u8; 64] {
        let mut key = [0_u8; 64];
        key[..32].copy_from_slice(left);
        key[32..].copy_from_slice(right);
        key
    }

    fn same_typed_value(left: &Value, right: &Value) -> bool {
        match (left, right) {
            (Value::Number(left_number), Value::Number(right_number)) => {
                left_number.is_f64() == right_number.is_f64() && left_number == right_number
            }
            _ => std::mem::discriminant(left) == std::mem::discriminant(right) && left == right,
        }
    }

    fn facts_consistent(left: &Context, right: &Context) -> bool {
        left.facts.iter().all(|(key, left_value)| {
            right
                .facts
                .get(key)
                .is_none_or(|right_value| Self::same_typed_value(left_value, right_value))
        })
    }

    fn service_witness(consumer: &Context, provider: &Context) -> Option<ServiceWitness> {
        let mut witnesses = Vec::new();
        let mut satisfied_keys = BTreeSet::new();

        for (key, expected) in &consumer.needs {
            let Some(supplied) = provider.facts.get(key) else {
                continue;
            };
            // In the Python contract model, None is a presence-only need.
            if expected.is_null() || Self::same_typed_value(expected, supplied) {
                satisfied_keys.insert(key.clone());
                witnesses.push(NeedWitness {
                    key: key.clone(),
                    required_value: if expected.is_null() {
                        None
                    } else {
                        Some(expected.clone())
                    },
                    supplied_value: supplied.clone(),
                });
            }
        }

        if witnesses.is_empty() {
            return None;
        }

        let unmet_needs = consumer
            .needs
            .iter()
            .filter(|(key, _)| !satisfied_keys.contains(*key))
            .map(|(key, expected)| {
                let supplied = provider.facts.get(key);
                UnmetNeed {
                    key: key.clone(),
                    required_value: if expected.is_null() {
                        None
                    } else {
                        Some(expected.clone())
                    },
                    provider_has_key: supplied.is_some(),
                    supplied_value: supplied.cloned(),
                }
            })
            .collect();

        Some(ServiceWitness {
            consumer: consumer.id.clone(),
            provider: provider.id.clone(),
            needs: witnesses,
            unmet_needs,
        })
    }

    fn compute_pair(left: &Context, right: &Context) -> PairOutcome {
        if !Self::facts_consistent(left, right) {
            return PairOutcome::Incompatible;
        }

        let mut services = Vec::new();
        if let Some(service) = Self::service_witness(left, right) {
            services.push(service);
        }
        if let Some(service) = Self::service_witness(right, left) {
            services.push(service);
        }

        if services.is_empty() {
            PairOutcome::Incompatible
        } else {
            PairOutcome::Compatible(CachedEdge {
                left: left.id.clone(),
                right: right.id.clone(),
                services,
            })
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn context(id: &str, facts: &[(&str, Value)], needs: &[(&str, Value)]) -> Context {
        Context {
            id: id.to_string(),
            facts: facts
                .iter()
                .map(|(key, value)| ((*key).to_string(), value.clone()))
                .collect(),
            needs: needs
                .iter()
                .map(|(key, value)| ((*key).to_string(), value.clone()))
                .collect(),
        }
    }

    #[test]
    fn caches_compatible_pair_and_reports_hit_on_repeat() {
        let mut cache = CompatibilityCache::new();
        let contexts = vec![
            context("consumer", &[], &[("deadline", Value::Null)]),
            context(
                "provider",
                &[("deadline", Value::String("friday".to_string()))],
                &[],
            ),
        ];

        let first = cache.build_graph(contexts.clone()).expect("first graph");
        let second = cache.build_graph(contexts).expect("second graph");

        assert_eq!(first.edges.len(), 1);
        assert_eq!(first.cache.cache_misses, 1);
        assert_eq!(first.cache.cache_hits, 0);
        assert_eq!(second.cache.cache_misses, 0);
        assert_eq!(second.cache.cache_hits, 0);
        assert_eq!(second.cache.graph_cache_hit, true);
        assert_eq!(second.cache.graph_cache_hits, 1);
        assert_eq!(second.cache.pair_lookups, 0);
        assert_eq!(first.edges, second.edges);
        assert_eq!(second.edges[0].services[0].needs[0].key, "deadline");
    }

    #[test]
    fn caches_negative_compatibility_results_too() {
        let mut cache = CompatibilityCache::new();
        let contexts = vec![
            context("a", &[("region", Value::String("north".into()))], &[]),
            context("b", &[("region", Value::String("south".into()))], &[]),
        ];

        let first = cache.build_graph(contexts.clone()).expect("first graph");
        let second = cache.build_graph(contexts).expect("second graph");

        assert!(first.edges.is_empty());
        assert_eq!(first.cache.cache_misses, 1);
        assert_eq!(second.cache.cache_hits, 0);
        assert_eq!(second.cache.cache_misses, 0);
        assert_eq!(second.cache.graph_cache_hit, true);
        assert_eq!(second.cache.graph_cache_hits, 1);
    }

    #[test]
    fn need_values_and_json_scalar_types_are_strict() {
        let mut cache = CompatibilityCache::new();
        let wrong_value = vec![
            context(
                "consumer",
                &[],
                &[("budget", Value::Number(serde_json::Number::from(20)))],
            ),
            context(
                "provider",
                &[("budget", Value::Number(serde_json::Number::from(10)))],
                &[],
            ),
        ];
        assert!(cache
            .build_graph(wrong_value)
            .expect("wrong value graph")
            .edges
            .is_empty());

        let bool_vs_integer = vec![
            context(
                "a",
                &[("flag", Value::Bool(true))],
                &[("x", Value::String("v".into()))],
            ),
            context(
                "b",
                &[
                    ("flag", Value::Number(serde_json::Number::from(1))),
                    ("x", Value::String("v".into())),
                ],
                &[],
            ),
        ];
        assert!(cache
            .build_graph(bool_vs_integer)
            .expect("typed graph")
            .edges
            .is_empty());

        let int_vs_float = vec![
            context(
                "a",
                &[("flag", Value::Number(serde_json::Number::from(1)))],
                &[("x", Value::String("v".into()))],
            ),
            context(
                "b",
                &[
                    (
                        "flag",
                        Value::Number(serde_json::Number::from_f64(1.0).unwrap()),
                    ),
                    ("x", Value::String("v".into())),
                ],
                &[],
            ),
        ];
        assert!(cache
            .build_graph(int_vs_float)
            .expect("number type graph")
            .edges
            .is_empty());
    }

    #[test]
    fn need_may_be_satisfied_in_either_direction_and_reports_unmet_needs() {
        let mut cache = CompatibilityCache::new();
        let contexts = vec![
            context(
                "consumer",
                &[],
                &[
                    ("deadline", Value::Null),
                    ("budget", Value::String("20k".into())),
                ],
            ),
            context(
                "provider",
                &[("deadline", Value::String("friday".into()))],
                &[],
            ),
        ];

        let result = cache.build_graph(contexts).expect("graph");
        assert_eq!(result.edges.len(), 1);
        let service = &result.edges[0].services[0];
        assert_eq!(service.needs.len(), 1);
        assert_eq!(service.unmet_needs.len(), 1);
        assert_eq!(service.unmet_needs[0].key, "budget");
        assert!(!service.unmet_needs[0].provider_has_key);
    }

    #[test]
    fn ttl_expiry_invalidates_pair_and_graph_entries() {
        let mut cache = CompatibilityCache::new_with_config(CacheConfig {
            pair_max_capacity_bytes: 1024 * 1024,
            graph_max_capacity_bytes: 1024 * 1024,
            ttl: Duration::from_millis(80),
        });
        let contexts = vec![
            context("consumer", &[], &[("deadline", Value::Null)]),
            context(
                "provider",
                &[("deadline", Value::String("friday".to_string()))],
                &[],
            ),
        ];

        let first = cache.build_graph(contexts.clone()).expect("cold graph");
        assert_eq!(first.cache.graph_cache_misses, 1);
        let warm = cache.build_graph(contexts.clone()).expect("warm graph");
        assert!(warm.cache.graph_cache_hit);

        std::thread::sleep(Duration::from_millis(180));
        let expired = cache.build_graph(contexts).expect("expired graph");
        assert!(!expired.cache.graph_cache_hit);
        assert_eq!(expired.cache.graph_cache_misses, 1);
        assert_eq!(expired.cache.cache_misses, 1);
    }

    #[test]
    fn bounded_pair_cache_evicts_under_capacity_pressure() {
        let mut cache = CompatibilityCache::new_with_config(CacheConfig {
            pair_max_capacity_bytes: 256,
            graph_max_capacity_bytes: 1,
            ttl: Duration::from_secs(60),
        });

        let pairs: Vec<Vec<Context>> = (0..20)
            .map(|index| {
                vec![
                    context(
                        &format!("consumer-{index:02}"),
                        &[("region", Value::String("north".to_string()))],
                        &[],
                    ),
                    context(
                        &format!("provider-{index:02}"),
                        &[("region", Value::String("south".to_string()))],
                        &[],
                    ),
                ]
            })
            .collect();

        for _ in 0..4 {
            let hot = cache.build_graph(pairs[0].clone()).expect("hot pair");
            assert_eq!(hot.edges.len(), 0);
        }
        for pair in &pairs[1..] {
            let result = cache.build_graph(pair.clone()).expect("pressure pair");
            assert_eq!(result.edges.len(), 0);
        }

        let before = cache.total_metrics();
        assert!(before.entries < pairs.len() as u64);
        assert_eq!(before.graph_cache_entries, 0);

        let mut second_pass_hits = 0;
        let mut second_pass_misses = 0;
        for pair in &pairs {
            let result = cache.build_graph(pair.clone()).expect("second pressure pass");
            second_pass_hits += result.cache.cache_hits;
            second_pass_misses += result.cache.cache_misses;
        }
        assert!(second_pass_misses > 0, "capacity pressure must cause recomputation");
        assert!(second_pass_hits > 0, "the bounded cache must retain some useful entries");
        assert!(cache.total_metrics().entries < pairs.len() as u64);
    }

    #[test]
    fn context_content_changes_miss_while_id_and_content_match_hits() {
        let mut cache = CompatibilityCache::new();
        let first = vec![
            context("a", &[], &[("x", Value::Null)]),
            context("b", &[("x", Value::String("one".into()))], &[]),
        ];
        let changed = vec![
            context("a", &[], &[("x", Value::Null)]),
            context("b", &[("x", Value::String("two".into()))], &[]),
        ];

        cache.build_graph(first.clone()).expect("first");
        let changed_result = cache.build_graph(changed).expect("changed");
        assert_eq!(changed_result.cache.cache_misses, 1);
    }

    #[test]
    fn duplicate_ids_are_rejected() {
        let mut cache = CompatibilityCache::new();
        let contexts = vec![context("same", &[], &[]), context("same", &[], &[])];
        assert!(cache.build_graph(contexts).is_err());
    }
}
