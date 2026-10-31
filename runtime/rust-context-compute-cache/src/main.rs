use serde_json::json;
use std::io::{self, BufRead, Write};
use std::time::Duration;
use uws_context_compute_cache::{CacheConfig, CompatibilityCache, Request};

fn env_u64(name: &str, default: u64) -> u64 {
    match std::env::var(name) {
        Ok(value) => value.parse::<u64>().unwrap_or_else(|error| {
            eprintln!("invalid {name}={value:?}: {error}");
            std::process::exit(2);
        }),
        Err(std::env::VarError::NotPresent) => default,
        Err(error) => {
            eprintln!("could not read {name}: {error}");
            std::process::exit(2);
        }
    }
}

fn main() {
    let defaults = CacheConfig::default();
    let config = CacheConfig {
        pair_max_capacity_bytes: env_u64(
            "MACHINE_CACHE_PAIR_CAPACITY_BYTES",
            defaults.pair_max_capacity_bytes,
        ),
        graph_max_capacity_bytes: env_u64(
            "MACHINE_CACHE_GRAPH_CAPACITY_BYTES",
            defaults.graph_max_capacity_bytes,
        ),
        ttl: Duration::from_millis(env_u64(
            "MACHINE_CACHE_TTL_MS",
            defaults.ttl.as_millis() as u64,
        )),
    };

    let stdin = io::stdin();
    let mut stdout = io::BufWriter::new(io::stdout().lock());
    let mut cache = CompatibilityCache::new_with_config(config);

    for line in stdin.lock().lines() {
        let line = match line {
            Ok(line) => line,
            Err(error) => {
                let response = json!({"ok": false, "error": format!("stdin read failed: {error}")});
                let _ = writeln!(stdout, "{response}");
                let _ = stdout.flush();
                break;
            }
        };

        let request: Request = match serde_json::from_str(&line) {
            Ok(request) => request,
            Err(error) => {
                let response =
                    json!({"ok": false, "error": format!("invalid request JSON: {error}")});
                let _ = writeln!(stdout, "{response}");
                let _ = stdout.flush();
                continue;
            }
        };

        let is_shutdown = request.op == "shutdown";
        let response = match request.op.as_str() {
            "build_graph" => match cache.build_graph(request.contexts) {
                Ok(result) => json!({"ok": true, "result": result}),
                Err(error) => json!({"ok": false, "error": error}),
            },
            "stats" => json!({"ok": true, "result": {"cache": cache.total_metrics()}}),
            "shutdown" => json!({"ok": true, "result": {"shutdown": true}}),
            other => json!({"ok": false, "error": format!("unsupported operation: {other}")}),
        };

        if writeln!(stdout, "{response}").is_err() || stdout.flush().is_err() {
            break;
        }
        if is_shutdown {
            break;
        }
    }
}
