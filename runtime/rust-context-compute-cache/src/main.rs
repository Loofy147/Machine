use serde_json::json;
use std::io::{self, BufRead, Write};
use uws_context_compute_cache::{CompatibilityCache, Request};

fn main() {
    let stdin = io::stdin();
    let mut stdout = io::BufWriter::new(io::stdout().lock());
    let mut cache = CompatibilityCache::new();

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
