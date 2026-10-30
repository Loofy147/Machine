"""Bridge to the bounded Rust context-pair computation cache.

This cache memoizes only pair compatibility and its directional witnesses.
Utility and anchor filtering remain outside the cache key so the same pair
result can be reused under multiple objective policies and anchor selections.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import threading
import time
from typing import Any, Iterable, Mapping

import networkx as nx

from context_contract_distribution import (
    ContractContext,
    NeedWitness,
    ServiceWitness,
    UnmetNeed,
)


CACHE_PROTOCOL = "uws-context-pair-compatibility-cache.v0.1"


class RustComputeCacheError(RuntimeError):
    """The Rust computation-cache process failed or violated its protocol."""


class RustCompatibilityCacheClient:
    def __init__(
        self,
        binary: str | Path | None = None,
        environment: Mapping[str, str] | None = None,
    ) -> None:
        repository_root = Path(__file__).resolve().parents[2]
        default_binary = (
            repository_root
            / "runtime"
            / "rust-context-compute-cache"
            / "target"
            / "release"
            / "uws-context-compute-cache"
        )
        binary_value = binary or os.environ.get(
            "MACHINE_RUST_COMPUTE_CACHE_BIN", str(default_binary)
        )
        self.binary = Path(binary_value).expanduser().resolve()
        if not self.binary.is_file():
            raise RustComputeCacheError(
                "Rust compute-cache binary does not exist: "
                f"{self.binary}. Build runtime/rust-context-compute-cache first."
            )

        process_environment = os.environ.copy()
        if environment is not None:
            process_environment.update(environment)
        self._request_lock = threading.Lock()
        self.process = subprocess.Popen(
            [str(self.binary)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=None,
            text=True,
            encoding="utf-8",
            bufsize=1,
            env=process_environment,
        )
        self.requests = 0
        self.closed = False

    def _request(self, payload: dict[str, Any]) -> dict[str, Any]:
        # A single JSON-lines process has one request/response stream. Serialize
        # callers so concurrent threads cannot consume each other's responses.
        with self._request_lock:
            return self._request_unlocked(payload)

    def _request_unlocked(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self.closed:
            raise RustComputeCacheError("Rust cache client is already closed")
        if self.process.poll() is not None:
            raise RustComputeCacheError(
                f"Rust cache process exited early with code {self.process.returncode}"
            )
        if self.process.stdin is None or self.process.stdout is None:
            raise RustComputeCacheError("Rust cache process has no usable JSON-lines pipes")

        encoded = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        try:
            self.process.stdin.write(encoded + "\n")
            self.process.stdin.flush()
            line = self.process.stdout.readline()
        except (BrokenPipeError, OSError) as exc:
            raise RustComputeCacheError(f"Rust cache transport failed: {exc}") from exc

        if not line:
            raise RustComputeCacheError(
                f"Rust cache closed stdout unexpectedly; exit={self.process.poll()}"
            )
        try:
            response = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RustComputeCacheError(
                f"Rust cache returned invalid JSON: {line[:300]!r}"
            ) from exc
        self.requests += 1
        if not response.get("ok"):
            raise RustComputeCacheError(str(response.get("error", "unknown Rust cache error")))
        result = response.get("result")
        if not isinstance(result, dict):
            raise RustComputeCacheError("Rust cache response has no result object")
        return result

    def build_graph(
        self,
        contexts: Iterable[ContractContext],
    ) -> tuple[nx.Graph, dict[str, Any]]:
        started = time.perf_counter()
        context_list = sorted(tuple(contexts), key=lambda item: item.context_id)
        payload_contexts = [
            {
                "id": context.context_id,
                "facts": dict(context.facts),
                "needs": dict(context.needs),
            }
            for context in context_list
        ]

        result = self._request({"op": "build_graph", "contexts": payload_contexts})

        if result.get("schema") != CACHE_PROTOCOL:
            raise RustComputeCacheError(
                f"unexpected Rust cache schema: {result.get('schema')!r}"
            )

        graph = nx.Graph()
        graph.add_nodes_from(
            (context.context_id, {"utility": context.value})
            for context in context_list
        )
        primary_scale = len(context_list) + 1
        utility_by_id = {
            context.context_id: context.value for context in context_list
        }

        raw_edges = result.get("edges")
        if not isinstance(raw_edges, list):
            raise RustComputeCacheError("Rust cache graph edges must be a list")

        for raw_edge in raw_edges:
            if not isinstance(raw_edge, dict):
                raise RustComputeCacheError("Rust cache emitted a malformed edge")
            left = raw_edge.get("left")
            right = raw_edge.get("right")
            if left not in utility_by_id or right not in utility_by_id or left == right:
                raise RustComputeCacheError(
                    f"Rust cache emitted an edge with unknown endpoints: {left!r}, {right!r}"
                )

            services: list[ServiceWitness] = []
            for raw_service in raw_edge.get("services", []):
                needs = tuple(
                    NeedWitness(
                        key=need["key"],
                        required_value=need.get("required_value"),
                        supplied_value=need["supplied_value"],
                    )
                    for need in raw_service.get("needs", [])
                )
                unmet = tuple(
                    UnmetNeed(
                        key=need["key"],
                        required_value=need.get("required_value"),
                        provider_has_key=bool(need["provider_has_key"]),
                        supplied_value=need.get("supplied_value"),
                    )
                    for need in raw_service.get("unmet_needs", [])
                )
                services.append(
                    ServiceWitness(
                        consumer=raw_service["consumer"],
                        provider=raw_service["provider"],
                        needs=needs,
                        unmet_needs=unmet,
                    )
                )

            if not services:
                raise RustComputeCacheError(
                    f"Rust cache emitted an edge without service witnesses: {left!r}, {right!r}"
                )
            graph.add_edge(
                left,
                right,
                weight=(utility_by_id[left] + utility_by_id[right]) * primary_scale + 2,
                services=tuple(services),
            )

        cache_metrics = result.get("cache")
        if not isinstance(cache_metrics, dict):
            raise RustComputeCacheError("Rust cache omitted its cache metrics")
        metrics = {
            **cache_metrics,
            "elapsed_seconds": round(time.perf_counter() - started, 9),
            "contexts": len(context_list),
            "edges": graph.number_of_edges(),
        }
        return graph, metrics

    def stats(self) -> dict[str, Any]:
        result = self._request({"op": "stats"})
        cache = result.get("cache")
        if not isinstance(cache, dict):
            raise RustComputeCacheError("Rust cache stats response is malformed")
        return cache

    def process_memory_bytes(self) -> dict[str, int] | None:
        """Return Linux child-process RSS/HWM when /proc is available."""
        status_path = Path("/proc") / str(self.process.pid) / "status"
        try:
            lines = status_path.read_text(encoding="utf-8").splitlines()
        except OSError:
            return None
        values: dict[str, int] = {}
        for line in lines:
            if line.startswith(("VmRSS:", "VmHWM:", "VmPeak:")):
                key, raw_value, *_ = line.split()
                values[key.rstrip(":").lower() + "_bytes"] = int(raw_value) * 1024
        return values

    def close(self) -> None:
        # Keep shutdown and pipe closure atomic relative to concurrent callers.
        with self._request_lock:
            if self.closed:
                return
            try:
                self._request_unlocked({"op": "shutdown"})
            finally:
                self.closed = True
                if self.process.stdin is not None:
                    self.process.stdin.close()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait(timeout=5)
                if self.process.stdout is not None:
                    self.process.stdout.close()

    def __enter__(self) -> "RustCompatibilityCacheClient":
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        self.close()


def graph_signature(graph: nx.Graph) -> list[dict[str, Any]]:
    """Canonical edge/witness representation for Python-versus-Rust parity tests."""
    rows = []
    for left, right, attributes in graph.edges(data=True):
        first, second = sorted((left, right))
        services = sorted(
            (service.to_dict() for service in attributes["services"]),
            key=lambda service: (service["consumer"], service["provider"]),
        )
        rows.append({"left": first, "right": second, "services": services})
    return sorted(rows, key=lambda row: (row["left"], row["right"]))
